#!/usr/bin/env python3
"""
Create comprehensive reconciliation matrix combining REST and OGC analysis results.

This script combines:
- REST endpoint matches (implemented vs documented)
- OGC service compliance (implemented vs OGC specification requirements)

For each endpoint/operation, determines:
- Implemented: Yes/No
- Documented: Yes/No
- OGC Required: Yes/No/N/A
- Status: Complete, Needs Documentation, Needs Investigation
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def load_json(filepath: str) -> Dict:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_rest_entries(endpoint_matches: Dict, implemented_endpoints: Dict) -> List[Dict]:
    """Create reconciliation entries for REST endpoints."""
    entries = []
    
    # Track which endpoints we've processed
    processed_paths = set()
    
    # Process exact matches (documented and implemented)
    exact_match_count = 0
    for match in endpoint_matches.get('exact_matches', []):
        impl = match['implemented']
        doc = match['documented']
        path = match['normalized_path']
        method = match['http_method']
        key = f"{method} {path}"
        
        if key in processed_paths:
            print(f"WARNING: Duplicate key found: {key}")
            continue
        processed_paths.add(key)
        exact_match_count += 1
        
        # Determine if there are parameter mismatches
        has_mismatch = len(match.get('differences', [])) > 0
        
        entries.append({
            'endpoint_type': 'REST',
            'service': 'REST API',
            'version': 'N/A',
            'operation': f"{method} {path}",
            'http_method': method,
            'path': path,
            'implemented': True,
            'documented': True,
            'ogc_required': 'N/A',
            'status': 'Complete (with parameter mismatch)' if has_mismatch else 'Complete',
            'module': impl.get('module', 'unknown'),
            'source_file': impl.get('source_file', ''),
            'documented_file': doc.get('file', ''),
            'issues': match.get('differences', []),
            'notes': f"Match type: {match.get('match_type', 'exact')}"
        })
    
    print(f"Processed {exact_match_count} exact matches")
    
    # Process implemented-only endpoints (needs documentation)
    impl_only_count = 0
    for endpoint in endpoint_matches.get('implemented_only', []):
        path = endpoint.get('path', '')
        method = endpoint.get('http_method', '')
        key = f"{method} {path}"
        
        if key in processed_paths:
            print(f"WARNING: Duplicate key in implemented_only: {key}")
            continue
        processed_paths.add(key)
        impl_only_count += 1
        
        entries.append({
            'endpoint_type': 'REST',
            'service': 'REST API',
            'version': 'N/A',
            'operation': f"{method} {path}",
            'http_method': method,
            'path': path,
            'implemented': True,
            'documented': False,
            'ogc_required': 'N/A',
            'status': 'Needs Documentation',
            'module': endpoint.get('module', 'unknown'),
            'source_file': endpoint.get('source_file', ''),
            'documented_file': '',
            'issues': ['Not documented'],
            'notes': 'Implemented but not in OpenAPI specs'
        })
    
    print(f"Processed {impl_only_count} implemented-only endpoints")
    
    # Process documented-only endpoints (needs investigation)
    doc_only_count = 0
    for endpoint in endpoint_matches.get('documented_only', []):
        path = endpoint.get('_normalized_path', endpoint.get('path', ''))
        method = endpoint.get('method', '')
        key = f"{method} {path}"
        
        if key in processed_paths:
            print(f"WARNING: Duplicate key in documented_only: {key}")
            continue
        processed_paths.add(key)
        doc_only_count += 1
        
        entries.append({
            'endpoint_type': 'REST',
            'service': 'REST API',
            'version': 'N/A',
            'operation': f"{method} {path}",
            'http_method': method,
            'path': path,
            'implemented': False,
            'documented': True,
            'ogc_required': 'N/A',
            'status': 'Needs Investigation',
            'module': 'unknown',
            'source_file': '',
            'documented_file': endpoint.get('file', ''),
            'issues': ['Not implemented or not found in source code'],
            'notes': 'Documented but implementation not found'
        })
    
    print(f"Processed {doc_only_count} documented-only endpoints")
    print(f"Total REST entries created: {len(entries)}")
    
    return entries


def create_ogc_entries(compliance_data: Dict, service_name: str) -> List[Dict]:
    """Create reconciliation entries for OGC service operations."""
    entries = []
    
    service_title = compliance_data.get('service_title', service_name)
    version_compliance = compliance_data.get('version_compliance', {})
    
    for version, version_data in version_compliance.items():
        operations = version_data.get('operations', [])
        summary = version_data.get('summary', {})
        
        for op in operations:
            operation_name = op.get('operation', '')
            status = op.get('status', '')
            issues = op.get('issues', [])
            
            # Determine if operation is required by OGC spec
            # Check in summary for required/optional classification
            missing_required = summary.get('missing_required_operations', [])
            missing_optional = summary.get('missing_optional_operations', [])
            vendor_operations = summary.get('vendor_operations', [])
            
            # Determine OGC requirement status
            if operation_name in vendor_operations:
                ogc_required = 'No (Vendor Extension)'
            elif operation_name in missing_required:
                ogc_required = 'Yes (Missing)'
            elif operation_name in missing_optional:
                ogc_required = 'No (Optional, Missing)'
            else:
                # Operation is implemented - check if it's required or optional
                # This requires checking against spec reference
                ogc_required = 'Yes/Optional'  # We'll refine this
            
            # Determine reconciliation status
            if status == 'compliant' or status == 'FULLY_COMPLIANT':
                recon_status = 'Complete'
            elif status == 'COMPLIANT_WITH_EXTENSIONS':
                recon_status = 'Complete (with extensions)'
            elif status == 'VENDOR_EXTENSION':
                recon_status = 'Complete (vendor extension)'
            elif 'missing' in status.lower():
                recon_status = 'Needs Implementation'
            else:
                recon_status = 'Needs Investigation'
            
            # Extract issue descriptions
            issue_list = []
            for issue in issues:
                issue_type = issue.get('type', '')
                if issue_type == 'vendor_extensions':
                    params = issue.get('parameters', [])
                    issue_list.append(f"Vendor extensions: {len(params)} parameters")
                elif issue_type == 'missing_required_parameter':
                    issue_list.append(f"Missing required parameter: {issue.get('parameter', '')}")
                elif issue_type == 'missing_optional_parameter':
                    issue_list.append(f"Missing optional parameter: {issue.get('parameter', '')}")
                else:
                    issue_list.append(issue.get('description', str(issue)))
            
            entries.append({
                'endpoint_type': 'OGC',
                'service': service_name,
                'version': version,
                'operation': operation_name,
                'http_method': 'GET/POST',  # OGC services typically support both
                'path': f"/{service_name.lower()}",
                'implemented': True,  # If it's in compliance data, it's implemented
                'documented': True,  # OGC operations are documented in capabilities
                'ogc_required': ogc_required,
                'status': recon_status,
                'module': f"{service_name.lower()}",
                'source_file': f"src/{service_name.lower()}/",
                'documented_file': 'OGC Capabilities Document',
                'issues': issue_list,
                'notes': op.get('note', '')
            })
        
        # Add missing required operations
        for missing_op in summary.get('missing_required_operations', []):
            entries.append({
                'endpoint_type': 'OGC',
                'service': service_name,
                'version': version,
                'operation': missing_op,
                'http_method': 'GET/POST',
                'path': f"/{service_name.lower()}",
                'implemented': False,
                'documented': False,
                'ogc_required': 'Yes (Required)',
                'status': 'Needs Implementation (Critical)',
                'module': f"{service_name.lower()}",
                'source_file': '',
                'documented_file': '',
                'issues': ['Required by OGC specification but not implemented'],
                'notes': 'CRITICAL: Required operation missing'
            })
        
        # Add missing optional operations
        for missing_op in summary.get('missing_optional_operations', []):
            entries.append({
                'endpoint_type': 'OGC',
                'service': service_name,
                'version': version,
                'operation': missing_op,
                'http_method': 'GET/POST',
                'path': f"/{service_name.lower()}",
                'implemented': False,
                'documented': False,
                'ogc_required': 'No (Optional)',
                'status': 'Optional (Not Implemented)',
                'module': f"{service_name.lower()}",
                'source_file': '',
                'documented_file': '',
                'issues': ['Optional operation not implemented'],
                'notes': 'Optional operation - implementation not required'
            })
    
    return entries


def calculate_status_counts(entries: List[Dict]) -> Dict:
    """Calculate row counts for each status combination."""
    counts = defaultdict(int)
    
    for entry in entries:
        impl = entry['implemented']
        doc = entry['documented']
        ogc_req = entry['ogc_required']
        status = entry['status']
        
        # Create status combination key
        key = f"impl={impl}, doc={doc}, ogc_req={ogc_req}, status={status}"
        counts[key] += 1
        
        # Also count by major categories
        if impl and doc:
            counts['Complete (impl+doc)'] += 1
        elif impl and not doc:
            counts['Needs Documentation (impl only)'] += 1
        elif not impl and doc:
            counts['Needs Investigation (doc only)'] += 1
        elif not impl and not doc:
            counts['Missing (neither impl nor doc)'] += 1
        
        # Count by endpoint type
        counts[f"Type: {entry['endpoint_type']}"] += 1
        
        # Count by service
        counts[f"Service: {entry['service']}"] += 1
    
    return dict(counts)


def main():
    """Main execution function."""
    print("Creating comprehensive reconciliation matrix...")
    
    # Load REST analysis results
    print("Loading REST analysis results...")
    endpoint_matches = load_json('.kiro/api-analysis/rest/endpoint-matches.json')
    implemented_endpoints = load_json('.kiro/api-analysis/rest/implemented-all-endpoints.json')
    
    # Load OGC compliance results
    print("Loading OGC compliance results...")
    wms_compliance = load_json('.kiro/api-analysis/ogc/wms-compliance.json')
    wfs_compliance = load_json('.kiro/api-analysis/ogc/wfs-compliance.json')
    wcs_compliance = load_json('.kiro/api-analysis/ogc/wcs-compliance.json')
    other_services = load_json('.kiro/api-analysis/ogc/other-services-compliance.json')
    
    # Create reconciliation entries
    print("Creating REST reconciliation entries...")
    rest_entries = create_rest_entries(endpoint_matches, implemented_endpoints)
    
    print("Creating OGC reconciliation entries...")
    ogc_entries = []
    ogc_entries.extend(create_ogc_entries(wms_compliance, 'WMS'))
    ogc_entries.extend(create_ogc_entries(wfs_compliance, 'WFS'))
    ogc_entries.extend(create_ogc_entries(wcs_compliance, 'WCS'))
    
    # Process other services (WMTS, CSW, WPS)
    for service_name, service_data in other_services.get('services', {}).items():
        for version, version_data in service_data.get('versions', {}).items():
            # Convert to similar structure as WMS/WFS/WCS
            # The other-services structure has operation_details instead of operations
            operations = []
            for op_detail in version_data.get('operation_details', []):
                # Convert operation_detail to operation format
                issues = []
                if op_detail.get('vendor_parameters'):
                    issues.append({
                        'type': 'vendor_extensions',
                        'severity': 'info',
                        'parameters': [p['parameter'] for p in op_detail.get('vendor_parameters', [])],
                        'description': f"Implementation includes {len(op_detail.get('vendor_parameters', []))} vendor extension(s)"
                    })
                
                operations.append({
                    'operation': op_detail.get('operation', ''),
                    'version': version,
                    'status': op_detail.get('status', ''),
                    'issues': issues,
                    'note': op_detail.get('note', '')
                })
            
            # Create summary from version_data
            summary = {
                'missing_required_operations': version_data.get('missing_required_operations', []),
                'missing_optional_operations': version_data.get('missing_optional_operations', []),
                'vendor_operations': [op['operation'] for op in version_data.get('extra_operations', [])]
            }
            
            converted_data = {
                'service_title': service_name,
                'version_compliance': {
                    version: {
                        'operations': operations,
                        'summary': summary
                    }
                }
            }
            ogc_entries.extend(create_ogc_entries(converted_data, service_name))
    
    # Combine all entries
    all_entries = rest_entries + ogc_entries
    
    print(f"Total entries: {len(all_entries)}")
    print(f"  REST entries: {len(rest_entries)}")
    print(f"  OGC entries: {len(ogc_entries)}")
    
    # Calculate status counts
    print("Calculating status counts...")
    status_counts = calculate_status_counts(all_entries)
    
    # Create reconciliation matrix
    reconciliation_matrix = {
        'metadata': {
            'created_date': datetime.now().isoformat(),
            'description': 'Comprehensive reconciliation matrix combining REST and OGC analysis',
            'total_entries': len(all_entries),
            'rest_entries': len(rest_entries),
            'ogc_entries': len(ogc_entries)
        },
        'summary': {
            'total_endpoints': len(all_entries),
            'implemented_and_documented': status_counts.get('Complete (impl+doc)', 0),
            'needs_documentation': status_counts.get('Needs Documentation (impl only)', 0),
            'needs_investigation': status_counts.get('Needs Investigation (doc only)', 0),
            'missing_both': status_counts.get('Missing (neither impl nor doc)', 0),
            'rest_endpoints': status_counts.get('Type: REST', 0),
            'ogc_operations': status_counts.get('Type: OGC', 0)
        },
        'status_counts': status_counts,
        'entries': all_entries
    }
    
    # Write output
    output_file = '.kiro/api-analysis/reconciliation-matrix.json'
    print(f"Writing reconciliation matrix to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reconciliation_matrix, f, indent=2, ensure_ascii=False)
    
    print("\nReconciliation Matrix Summary:")
    print(f"  Total entries: {len(all_entries)}")
    print(f"  Complete (impl+doc): {status_counts.get('Complete (impl+doc)', 0)}")
    print(f"  Needs Documentation: {status_counts.get('Needs Documentation (impl only)', 0)}")
    print(f"  Needs Investigation: {status_counts.get('Needs Investigation (doc only)', 0)}")
    print(f"  Missing Both: {status_counts.get('Missing (neither impl nor doc)', 0)}")
    print(f"\nOutput written to: {output_file}")


if __name__ == '__main__':
    main()
