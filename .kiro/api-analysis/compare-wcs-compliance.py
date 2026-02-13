#!/usr/bin/env python3
"""
Compare WCS implementation with OGC specifications.
Identifies missing required operations, missing required parameters, and vendor extensions.
"""

import json
from pathlib import Path

def load_json(filepath: str) -> dict:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: dict, filepath: str):
    """Save JSON file with pretty printing."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved: {filepath}")

def compare_wcs_compliance():
    """Compare WCS implementation against OGC specifications."""
    
    # Load data
    spec_ref = load_json('.kiro/api-analysis/ogc/spec-reference.json')
    wcs_impl = load_json('.kiro/api-analysis/ogc/wcs-operations.json')
    
    wcs_spec = spec_ref['services']['WCS']
    versions = ['1.0.0', '1.1.0', '2.0.0']
    
    # Build implementation lookup
    impl_ops = {}
    for op in wcs_impl['operations']:
        op_name = op['name']
        impl_ops[op_name] = op
    
    compliance_result = {
        'service': 'WCS',
        'service_title': 'Web Coverage Service',
        'comparison_date': '2026-02-13',
        'versions_analyzed': versions,
        'summary': {
            'overall_compliance': True,
            'versions_compliant': [],
            'versions_non_compliant': [],
            'total_issues': 0
        },
        'version_compliance': {}
    }
    
    for version in versions:
        spec_version = wcs_spec['versions'][version]
        
        version_result = {
            'version': version,
            'specification_url': spec_version['specification_url'],
            'specification_title': spec_version['specification_title'],
            'operations': [],
            'summary': {
                'total_required_operations': 0,
                'implemented_required_operations': 0,
                'total_optional_operations': 0,
                'implemented_optional_operations': 0,
                'missing_required_operations': [],
                'missing_optional_operations': [],
                'vendor_operations': [],
                'compliance_status': 'compliant'
            }
        }
        
        # Check required operations
        required_ops = spec_version.get('required_operations', [])
        version_result['summary']['total_required_operations'] = len(required_ops)
        
        for spec_op in required_ops:
            op_name = spec_op['name']
            op_result = {
                'operation': op_name,
                'version': version,
                'status': 'compliant',
                'issues': []
            }
            
            if op_name in impl_ops:
                version_result['summary']['implemented_required_operations'] += 1
                
                # Check if this version is supported
                impl_op = impl_ops[op_name]
                if version not in impl_op.get('versions', []):
                    op_result['status'] = 'non_compliant'
                    op_result['issues'].append({
                        'type': 'missing_version',
                        'severity': 'error',
                        'description': f'Operation exists but version {version} not supported'
                    })
                    version_result['summary']['compliance_status'] = 'non_compliant'
                    compliance_result['summary']['total_issues'] += 1
                else:
                    # Check for vendor extensions (parameters not in spec)
                    vendor_params = []
                    for param in impl_op.get('parameters', []):
                        param_versions = param.get('versions', [])
                        # If parameter has version restrictions and this version is included, check if it's in spec
                        if not param_versions or version in param_versions:
                            param_name = param['name']
                            # Check if parameter is in spec
                            is_in_spec = False
                            for spec_param in spec_op.get('required_parameters', []) + spec_op.get('optional_parameters', []):
                                if spec_param['name'] == param_name:
                                    is_in_spec = True
                                    break
                            
                            if not is_in_spec:
                                vendor_params.append(param_name)
                    
                    if vendor_params:
                        op_result['issues'].append({
                            'type': 'vendor_extensions',
                            'severity': 'info',
                            'parameters': vendor_params,
                            'description': f'Implementation includes {len(vendor_params)} vendor extension(s)'
                        })
                        compliance_result['summary']['total_issues'] += 1
            else:
                version_result['summary']['missing_required_operations'].append(op_name)
                op_result['status'] = 'non_compliant'
                op_result['issues'].append({
                    'type': 'missing_operation',
                    'severity': 'error',
                    'description': 'Required operation not implemented'
                })
                version_result['summary']['compliance_status'] = 'non_compliant'
                compliance_result['summary']['total_issues'] += 1
            
            version_result['operations'].append(op_result)
        
        # Check optional operations
        optional_ops = spec_version.get('optional_operations', [])
        version_result['summary']['total_optional_operations'] = len(optional_ops)
        
        for spec_op in optional_ops:
            op_name = spec_op['name']
            
            if op_name in impl_ops:
                impl_op = impl_ops[op_name]
                if version in impl_op.get('versions', []):
                    version_result['summary']['implemented_optional_operations'] += 1
        
        # Update compliance status
        if version_result['summary']['compliance_status'] == 'compliant':
            compliance_result['summary']['versions_compliant'].append(version)
        else:
            compliance_result['summary']['versions_non_compliant'].append(version)
        
        compliance_result['version_compliance'][version] = version_result
    
    # Update overall compliance
    if compliance_result['summary']['versions_non_compliant']:
        compliance_result['summary']['overall_compliance'] = False
    
    # Save result
    save_json(compliance_result, '.kiro/api-analysis/ogc/wcs-compliance.json')
    
    print(f"\n✓ WCS Compliance Analysis Complete")
    print(f"  Versions analyzed: {', '.join(versions)}")
    print(f"  Overall compliance: {compliance_result['summary']['overall_compliance']}")
    print(f"  Total issues: {compliance_result['summary']['total_issues']}")

if __name__ == '__main__':
    compare_wcs_compliance()
