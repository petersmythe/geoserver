#!/usr/bin/env python3
"""
Identify REST API documentation gaps by analyzing endpoint matches.

This script:
1. Loads endpoint matching results
2. Identifies endpoints implemented but not documented
3. Identifies endpoints documented but not implemented
4. Identifies endpoints with parameter mismatches
5. Outputs gaps.json with detailed gap information
"""

import json
from datetime import datetime
from pathlib import Path

def load_json(filepath):
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """Save data as JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def identify_gaps():
    """Identify REST API documentation gaps."""
    
    # Load endpoint matching results
    matches_file = Path('.kiro/api-analysis/rest/endpoint-matches.json')
    matches_data = load_json(matches_file)
    
    # Extract metadata
    metadata = matches_data.get('metadata', {})
    
    # Initialize gap categories
    gaps = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'source_file': str(matches_file),
            'total_implemented': metadata.get('total_implemented', 0),
            'total_documented': metadata.get('total_documented', 0),
            'total_matched': metadata.get('total_matched', 0),
            'implemented_only_count': metadata.get('implemented_only', 0),
            'documented_only_count': metadata.get('documented_only', 0),
            'parameter_mismatch_count': metadata.get('matches_with_param_mismatch', 0)
        },
        'implemented_but_not_documented': [],
        'documented_but_not_implemented': [],
        'parameter_mismatches': []
    }
    
    # Process implemented-only endpoints (not documented)
    implemented_only = matches_data.get('implemented_only', [])
    for item in implemented_only:
        endpoint = item.get('endpoint', {})
        gap_entry = {
            'path': endpoint.get('path', item.get('normalized_path', 'unknown')),
            'http_method': endpoint.get('http_method', item.get('http_method', 'unknown')),
            'source_file': endpoint.get('source_file', item.get('source_file', 'unknown')),
            'module': endpoint.get('module', item.get('module', 'unknown')),
            'class_name': endpoint.get('class_name', 'unknown'),
            'method_name': endpoint.get('method_name', 'unknown'),
            'normalized_path': item.get('normalized_path', endpoint.get('path', 'unknown')),
            'path_variables': endpoint.get('path_variables', []),
            'query_parameters': endpoint.get('query_parameters', []),
            'request_body': endpoint.get('request_body'),
            'return_type': endpoint.get('return_type', 'unknown')
        }
        gaps['implemented_but_not_documented'].append(gap_entry)
    
    # Process documented-only endpoints (not implemented)
    documented_only = matches_data.get('documented_only', [])
    for item in documented_only:
        endpoint = item.get('endpoint', {})
        gap_entry = {
            'path': endpoint.get('path', item.get('normalized_path', 'unknown')),
            'http_method': endpoint.get('method', item.get('http_method', 'unknown')),
            'operation_id': endpoint.get('operation_id'),
            'description': endpoint.get('description', endpoint.get('summary', '')),
            'tags': endpoint.get('tags', []),
            'file': endpoint.get('file', 'unknown'),
            'normalized_path': item.get('normalized_path', endpoint.get('path', 'unknown')),
            'parameters': endpoint.get('parameters', []),
            'responses': endpoint.get('responses', {})
        }
        gaps['documented_but_not_implemented'].append(gap_entry)
    
    # Process parameter mismatches
    exact_matches = matches_data.get('exact_matches', [])
    for match in exact_matches:
        if match.get('match_type') == 'exact_with_param_mismatch':
            implemented = match.get('implemented', {})
            documented = match.get('documented', {})
            differences = match.get('differences', [])
            
            mismatch_entry = {
                'path': match.get('normalized_path', implemented.get('path', 'unknown')),
                'http_method': match.get('http_method', implemented.get('http_method', 'unknown')),
                'differences': differences,
                'implemented': {
                    'source_file': implemented.get('source_file', 'unknown'),
                    'class_name': implemented.get('class_name', 'unknown'),
                    'method_name': implemented.get('method_name', 'unknown'),
                    'path_variables': implemented.get('path_variables', []),
                    'query_parameters': implemented.get('query_parameters', []),
                    'request_body': implemented.get('request_body'),
                    'return_type': implemented.get('return_type', 'unknown')
                },
                'documented': {
                    'operation_id': documented.get('operation_id'),
                    'description': documented.get('description', documented.get('summary', '')),
                    'file': documented.get('file', 'unknown'),
                    'parameters': documented.get('parameters', []),
                    'consumes': documented.get('consumes', []),
                    'produces': documented.get('produces', []),
                    'responses': documented.get('responses', {})
                }
            }
            gaps['parameter_mismatches'].append(mismatch_entry)
    
    # Sort gaps by path and method for easier review
    gaps['implemented_but_not_documented'].sort(
        key=lambda x: (x['normalized_path'], x['http_method'])
    )
    gaps['documented_but_not_implemented'].sort(
        key=lambda x: (x['normalized_path'], x['http_method'])
    )
    gaps['parameter_mismatches'].sort(
        key=lambda x: (x['path'], x['http_method'])
    )
    
    # Save gaps to file
    output_file = Path('.kiro/api-analysis/rest/gaps.json')
    save_json(gaps, output_file)
    
    # Print summary
    print(f"Gap Analysis Complete")
    print(f"=" * 60)
    print(f"Total Implemented Endpoints: {gaps['metadata']['total_implemented']}")
    print(f"Total Documented Endpoints: {gaps['metadata']['total_documented']}")
    print(f"Total Matched Endpoints: {gaps['metadata']['total_matched']}")
    print(f"")
    print(f"Gaps Identified:")
    print(f"  - Implemented but NOT documented: {len(gaps['implemented_but_not_documented'])}")
    print(f"  - Documented but NOT implemented: {len(gaps['documented_but_not_implemented'])}")
    print(f"  - Parameter mismatches: {len(gaps['parameter_mismatches'])}")
    print(f"")
    print(f"Output: {output_file}")
    
    return gaps

if __name__ == '__main__':
    identify_gaps()
