#!/usr/bin/env python3
"""
Calculate REST API coverage metrics from endpoint matching results.

This script:
1. Loads endpoint matching data
2. Counts total implemented endpoints
3. Counts total documented endpoints
4. Counts matched endpoints
5. Calculates coverage percentage: (matched / implemented) × 100
6. Breaks down coverage by module
7. Outputs coverage metrics to JSON file

Requirements: 3.1, 3.4
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def load_json(file_path):
    """Load JSON data from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_coverage_metrics():
    """Calculate REST API coverage metrics."""
    
    # Load data files
    print("Loading endpoint data...")
    matches_data = load_json('.kiro/api-analysis/rest/endpoint-matches.json')
    implemented_data = load_json('.kiro/api-analysis/rest/implemented-all-endpoints.json')
    documented_data = load_json('.kiro/api-analysis/rest/documented-endpoints.json')
    
    # Extract counts from metadata
    total_implemented = matches_data['metadata']['total_implemented']
    total_documented = matches_data['metadata']['total_documented']
    total_matched = matches_data['metadata']['total_matched']
    
    # Calculate coverage percentage: (matched / implemented) × 100
    if total_implemented > 0:
        coverage_percentage = (total_matched / total_implemented) * 100
    else:
        coverage_percentage = 0.0
    
    print(f"Total implemented endpoints: {total_implemented}")
    print(f"Total documented endpoints: {total_documented}")
    print(f"Total matched endpoints: {total_matched}")
    print(f"Coverage percentage: {coverage_percentage:.2f}%")
    
    # Calculate coverage by module
    print("\nCalculating coverage by module...")
    
    # Get endpoints by module from implemented data
    endpoints_by_module = implemented_data['metadata']['endpoints_by_module']
    
    # Count matched endpoints by module
    matched_by_module = defaultdict(int)
    
    # Count exact matches by module
    for match in matches_data.get('exact_matches', []):
        impl = match.get('implemented', {})
        module = impl.get('module', '')
        
        # If module is not set or is empty, try to extract from source_file
        if not module or module == 'unknown':
            source_file = impl.get('source_file', '')
            if 'src/restconfig/' in source_file:
                module = 'restconfig'
            elif 'src/rest/' in source_file:
                module = 'rest'
            elif 'src/gwc/' in source_file:
                module = 'gwc'
            elif 'src/extension/' in source_file:
                # Extract extension name
                parts = source_file.split('/')
                if len(parts) > 2:
                    module = parts[2]
                else:
                    module = 'unknown'
            elif 'src/community/' in source_file:
                # Extract community module name
                parts = source_file.split('/')
                if len(parts) > 2:
                    module = parts[2]
                else:
                    module = 'unknown'
            else:
                module = 'unknown'
        
        matched_by_module[module] += 1
    
    # Build module coverage breakdown
    module_coverage = {}
    for module, implemented_count in endpoints_by_module.items():
        matched_count = matched_by_module.get(module, 0)
        if implemented_count > 0:
            module_percentage = (matched_count / implemented_count) * 100
        else:
            module_percentage = 0.0
        
        module_coverage[module] = {
            'implemented': implemented_count,
            'matched': matched_count,
            'coverage_percentage': round(module_percentage, 2)
        }
    
    # Sort by module name
    module_coverage = dict(sorted(module_coverage.items()))
    
    # Build final metrics object
    metrics = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'source_files': [
                '.kiro/api-analysis/rest/endpoint-matches.json',
                '.kiro/api-analysis/rest/implemented-all-endpoints.json',
                '.kiro/api-analysis/rest/documented-endpoints.json'
            ]
        },
        'overall_coverage': {
            'total_implemented': total_implemented,
            'total_documented': total_documented,
            'total_matched': total_matched,
            'coverage_percentage': round(coverage_percentage, 2),
            'unmatched_implemented': total_implemented - total_matched,
            'unmatched_documented': total_documented - total_matched
        },
        'coverage_by_module': module_coverage,
        'summary': {
            'modules_analyzed': len(module_coverage),
            'modules_with_full_coverage': sum(1 for m in module_coverage.values() if m['coverage_percentage'] == 100.0),
            'modules_with_partial_coverage': sum(1 for m in module_coverage.values() if 0 < m['coverage_percentage'] < 100.0),
            'modules_with_no_coverage': sum(1 for m in module_coverage.values() if m['coverage_percentage'] == 0.0)
        }
    }
    
    # Write output
    output_file = '.kiro/api-analysis/rest/coverage-metrics.json'
    print(f"\nWriting coverage metrics to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Coverage metrics written to {output_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("COVERAGE SUMMARY")
    print("="*60)
    print(f"Overall Coverage: {coverage_percentage:.2f}%")
    print(f"  Implemented: {total_implemented}")
    print(f"  Documented: {total_documented}")
    print(f"  Matched: {total_matched}")
    print(f"\nModule Breakdown:")
    print(f"  Total modules: {metrics['summary']['modules_analyzed']}")
    print(f"  Full coverage (100%): {metrics['summary']['modules_with_full_coverage']}")
    print(f"  Partial coverage: {metrics['summary']['modules_with_partial_coverage']}")
    print(f"  No coverage (0%): {metrics['summary']['modules_with_no_coverage']}")
    print("="*60)
    
    return metrics

if __name__ == '__main__':
    try:
        calculate_coverage_metrics()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
