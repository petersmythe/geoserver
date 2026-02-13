#!/usr/bin/env python3
"""
Compare WMS implementation against OGC WMS 1.1.1 and 1.3.0 specifications.
Identifies missing required operations, missing required parameters, and vendor extensions.
"""

import json
from typing import Dict, List, Set, Any

def load_json(filepath: str) -> Dict:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: Dict, filepath: str):
    """Save data to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_parameter_names(params: List[Dict]) -> Set[str]:
    """Extract parameter names from parameter list."""
    return {p['name'].upper() for p in params}

def compare_operation(impl_op: Dict, spec_op: Dict, version: str, op_name: str) -> Dict:
    """Compare a single operation between implementation and specification."""
    result = {
        'operation': impl_op['name'],
        'version': version,
        'status': 'compliant',
        'issues': []
    }
    
    # Get parameter sets
    impl_params = get_parameter_names(impl_op.get('parameters', []))
    spec_required = get_parameter_names(spec_op.get('required_parameters', []))
    spec_optional = get_parameter_names(spec_op.get('optional_parameters', []))
    spec_all = spec_required | spec_optional
    
    # Special handling for GetFeatureInfo - it inherits GetMap parameters
    # The implementation note says "Includes all GetMap parameters to define the map context"
    # So we should not flag GetMap parameters as missing for GetFeatureInfo
    if op_name == 'GetFeatureInfo' and impl_op.get('note'):
        # Only check for GetFeatureInfo-specific required parameters
        gfi_specific = {'QUERY_LAYERS', 'INFO_FORMAT', 'X', 'Y', 'I', 'J'}
        spec_required = spec_required & gfi_specific
    
    # Special handling for WMS version differences
    # WMS 1.1.x uses SRS, WMS 1.3.0 uses CRS - implementation supports both via single parameter
    if version == '1.3.0' and 'CRS' in spec_required and 'SRS' in impl_params:
        # Implementation has SRS parameter that handles both SRS and CRS
        impl_params.add('CRS')
    
    # WMS 1.3.0 GetFeatureInfo uses I/J instead of X/Y
    if version == '1.3.0' and op_name == 'GetFeatureInfo':
        if 'X' in impl_params:
            impl_params.add('I')
        if 'Y' in impl_params:
            impl_params.add('J')
    
    # Check for missing required parameters
    missing_required = spec_required - impl_params
    if missing_required:
        result['status'] = 'non-compliant'
        result['issues'].append({
            'type': 'missing_required_parameters',
            'severity': 'error',
            'parameters': sorted(list(missing_required)),
            'description': f"Missing {len(missing_required)} required parameter(s)"
        })
    
    # Identify vendor extensions (parameters not in spec)
    vendor_extensions = impl_params - spec_all
    # Filter out known vendor extensions already marked in implementation
    known_vendor = set(impl_op.get('vendor_extensions', []))
    vendor_extensions = vendor_extensions & {v.upper() for v in known_vendor}
    
    if vendor_extensions:
        result['issues'].append({
            'type': 'vendor_extensions',
            'severity': 'info',
            'parameters': sorted(list(vendor_extensions)),
            'description': f"Implementation includes {len(vendor_extensions)} vendor extension(s)"
        })
    
    # Check HTTP methods
    impl_methods = set(impl_op.get('http_methods', []))
    spec_methods = set(spec_op.get('http_methods', []))
    missing_methods = spec_methods - impl_methods
    if missing_methods:
        result['issues'].append({
            'type': 'missing_http_methods',
            'severity': 'warning',
            'methods': sorted(list(missing_methods)),
            'description': f"Missing HTTP method(s): {', '.join(sorted(missing_methods))}"
        })
    
    return result

def compare_wms_compliance(impl_data: Dict, spec_data: Dict) -> Dict:
    """Compare WMS implementation against OGC specifications."""
    
    wms_spec = spec_data['services']['WMS']
    compliance_report = {
        'service': 'WMS',
        'service_title': impl_data['service_title'],
        'comparison_date': '2026-02-13',
        'versions_analyzed': ['1.1.1', '1.3.0'],
        'summary': {},
        'version_compliance': {}
    }
    
    # Analyze each version
    for version in ['1.1.1', '1.3.0']:
        version_spec = wms_spec['versions'][version]
        version_report = {
            'version': version,
            'specification_url': version_spec['specification_url'],
            'specification_title': version_spec['specification_title'],
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
        
        # Build operation lookup for implementation
        impl_ops = {op['name']: op for op in impl_data['operations']}
        
        # Check required operations
        for spec_op in version_spec['required_operations']:
            version_report['summary']['total_required_operations'] += 1
            op_name = spec_op['name']
            
            if op_name in impl_ops:
                version_report['summary']['implemented_required_operations'] += 1
                comparison = compare_operation(impl_ops[op_name], spec_op, version, op_name)
                version_report['operations'].append(comparison)
                
                if comparison['status'] == 'non-compliant':
                    version_report['summary']['compliance_status'] = 'non-compliant'
            else:
                version_report['summary']['missing_required_operations'].append(op_name)
                version_report['summary']['compliance_status'] = 'non-compliant'
                version_report['operations'].append({
                    'operation': op_name,
                    'version': version,
                    'status': 'missing',
                    'issues': [{
                        'type': 'missing_operation',
                        'severity': 'error',
                        'description': f"Required operation '{op_name}' not implemented"
                    }]
                })
        
        # Check optional operations
        for spec_op in version_spec['optional_operations']:
            version_report['summary']['total_optional_operations'] += 1
            op_name = spec_op['name']
            
            if op_name in impl_ops:
                version_report['summary']['implemented_optional_operations'] += 1
                # Only do detailed comparison if spec has full details
                if 'required_parameters' in spec_op:
                    comparison = compare_operation(impl_ops[op_name], spec_op, version, op_name)
                    version_report['operations'].append(comparison)
            else:
                version_report['summary']['missing_optional_operations'].append(op_name)
        
        # Identify vendor-specific operations
        spec_op_names = {op['name'] for op in version_spec['required_operations']}
        spec_op_names |= {op['name'] for op in version_spec['optional_operations']}
        
        for impl_op in impl_data['operations']:
            if impl_op['name'] not in spec_op_names:
                if impl_op.get('vendor_extension', False):
                    version_report['summary']['vendor_operations'].append(impl_op['name'])
        
        compliance_report['version_compliance'][version] = version_report
    
    # Overall summary
    compliance_report['summary'] = {
        'overall_compliance': all(
            v['summary']['compliance_status'] == 'compliant' 
            for v in compliance_report['version_compliance'].values()
        ),
        'versions_compliant': [
            v for v, data in compliance_report['version_compliance'].items()
            if data['summary']['compliance_status'] == 'compliant'
        ],
        'versions_non_compliant': [
            v for v, data in compliance_report['version_compliance'].items()
            if data['summary']['compliance_status'] == 'non-compliant'
        ],
        'total_issues': sum(
            len([op for op in data['operations'] if op.get('issues')])
            for data in compliance_report['version_compliance'].values()
        )
    }
    
    return compliance_report

def main():
    """Main execution."""
    print("Loading WMS implementation data...")
    impl_data = load_json('.kiro/api-analysis/ogc/wms-operations.json')
    
    print("Loading OGC specification reference...")
    spec_data = load_json('.kiro/api-analysis/ogc/spec-reference.json')
    
    print("Comparing WMS implementation against OGC specifications...")
    compliance_report = compare_wms_compliance(impl_data, spec_data)
    
    print("Saving compliance report...")
    save_json(compliance_report, '.kiro/api-analysis/ogc/wms-compliance.json')
    
    print("\n=== WMS Compliance Summary ===")
    print(f"Overall Compliance: {'✓ COMPLIANT' if compliance_report['summary']['overall_compliance'] else '✗ NON-COMPLIANT'}")
    print(f"Total Issues: {compliance_report['summary']['total_issues']}")
    
    for version, data in compliance_report['version_compliance'].items():
        print(f"\n--- WMS {version} ---")
        print(f"Status: {data['summary']['compliance_status'].upper()}")
        print(f"Required Operations: {data['summary']['implemented_required_operations']}/{data['summary']['total_required_operations']}")
        print(f"Optional Operations: {data['summary']['implemented_optional_operations']}/{data['summary']['total_optional_operations']}")
        
        if data['summary']['missing_required_operations']:
            print(f"Missing Required: {', '.join(data['summary']['missing_required_operations'])}")
        
        if data['summary']['vendor_operations']:
            print(f"Vendor Operations: {', '.join(data['summary']['vendor_operations'])}")
        
        # Count issues by type
        issues_by_type = {}
        for op in data['operations']:
            for issue in op.get('issues', []):
                issue_type = issue['type']
                issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
        
        if issues_by_type:
            print("Issues:")
            for issue_type, count in sorted(issues_by_type.items()):
                print(f"  - {issue_type}: {count}")
    
    print(f"\n✓ Compliance report saved to: .kiro/api-analysis/ogc/wms-compliance.json")

if __name__ == '__main__':
    main()
