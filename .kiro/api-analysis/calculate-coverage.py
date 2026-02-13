#!/usr/bin/env python3
"""
Calculate REST API coverage metrics.
Computes coverage percentage and breaks down by module.
"""

import json
from typing import Dict, List
from datetime import datetime
from collections import defaultdict


def calculate_coverage_metrics(matches_data: Dict, impl_data: Dict) -> Dict:
    """
    Calculate coverage metrics from match results.
    Coverage = (matched endpoints / total implemented endpoints) × 100
    """
    metadata = matches_data['metadata']
    
    total_implemented = metadata['total_implemented']
    total_documented = metadata['total_documented']
    total_matched = metadata['total_matched']
    
    # Calculate overall coverage percentage
    if total_implemented > 0:
        coverage_percentage = (total_matched / total_implemented) * 100
    else:
        coverage_percentage = 0.0
    
    # Calculate coverage by module
    module_stats = defaultdict(lambda: {
        'implemented': 0,
        'documented': 0,
        'matched': 0,
        'coverage_percentage': 0.0
    })
    
    # Count implemented endpoints by module
    for endpoint in impl_data['endpoints']:
        module = endpoint.get('module', 'unknown')
        module_stats[module]['implemented'] += 1
    
    # Count matched endpoints by module
    for match in matches_data['exact_matches']:
        impl_endpoint = match['implemented']
        module = impl_endpoint.get('module', 'unknown')
        module_stats[module]['matched'] += 1
    
    # Calculate coverage percentage for each module
    for module, stats in module_stats.items():
        if stats['implemented'] > 0:
            stats['coverage_percentage'] = (stats['matched'] / stats['implemented']) * 100
        else:
            stats['coverage_percentage'] = 0.0
    
    # Sort modules by coverage percentage (ascending) to highlight gaps
    sorted_modules = sorted(
        module_stats.items(),
        key=lambda x: (x[1]['coverage_percentage'], x[0])
    )
    
    # Calculate coverage by HTTP method
    method_stats = defaultdict(lambda: {
        'implemented': 0,
        'documented': 0,
        'matched': 0,
        'coverage_percentage': 0.0
    })
    
    # Count implemented endpoints by method
    for endpoint in impl_data['endpoints']:
        method = endpoint.get('http_method', 'UNKNOWN')
        method_stats[method]['implemented'] += 1
    
    # Count matched endpoints by method
    for match in matches_data['exact_matches']:
        method = match['http_method']
        method_stats[method]['matched'] += 1
    
    # Calculate coverage percentage for each method
    for method, stats in method_stats.items():
        if stats['implemented'] > 0:
            stats['coverage_percentage'] = (stats['matched'] / stats['implemented']) * 100
        else:
            stats['coverage_percentage'] = 0.0
    
    # Build result
    result = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'source_files': [
                '.kiro/api-analysis/rest/endpoint-matches.json',
                '.kiro/api-analysis/rest/implemented-all-endpoints.json'
            ]
        },
        'overall_coverage': {
            'total_implemented': total_implemented,
            'total_documented': total_documented,
            'total_matched': total_matched,
            'exact_matches': metadata['exact_matches'],
            'matches_with_param_mismatch': metadata['matches_with_param_mismatch'],
            'coverage_percentage': round(coverage_percentage, 2),
            'implemented_only': metadata['implemented_only'],
            'documented_only': metadata['documented_only']
        },
        'coverage_by_module': {
            module: {
                'implemented': stats['implemented'],
                'matched': stats['matched'],
                'coverage_percentage': round(stats['coverage_percentage'], 2),
                'undocumented': stats['implemented'] - stats['matched']
            }
            for module, stats in sorted_modules
        },
        'coverage_by_http_method': {
            method: {
                'implemented': stats['implemented'],
                'matched': stats['matched'],
                'coverage_percentage': round(stats['coverage_percentage'], 2),
                'undocumented': stats['implemented'] - stats['matched']
            }
            for method, stats in sorted(method_stats.items())
        }
    }
    
    return result


def main():
    print("Loading match results...")
    
    # Load match results
    with open('.kiro/api-analysis/rest/endpoint-matches.json', 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    
    # Load implemented endpoints for module breakdown
    with open('.kiro/api-analysis/rest/implemented-all-endpoints.json', 'r', encoding='utf-8') as f:
        impl_data = json.load(f)
    
    print("Calculating coverage metrics...")
    metrics = calculate_coverage_metrics(matches_data, impl_data)
    
    # Save results
    output_file = '.kiro/api-analysis/rest/coverage-metrics.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to {output_file}")
    print("\nOverall Coverage:")
    print(f"  Total implemented endpoints: {metrics['overall_coverage']['total_implemented']}")
    print(f"  Total documented endpoints: {metrics['overall_coverage']['total_documented']}")
    print(f"  Matched endpoints: {metrics['overall_coverage']['total_matched']}")
    print(f"  Coverage percentage: {metrics['overall_coverage']['coverage_percentage']}%")
    print(f"  Implemented but not documented: {metrics['overall_coverage']['implemented_only']}")
    print(f"  Documented but not implemented: {metrics['overall_coverage']['documented_only']}")
    
    print("\nCoverage by HTTP Method:")
    for method, stats in metrics['coverage_by_http_method'].items():
        print(f"  {method}: {stats['coverage_percentage']}% ({stats['matched']}/{stats['implemented']})")
    
    print("\nTop 10 Modules with Lowest Coverage:")
    module_items = list(metrics['coverage_by_module'].items())
    for i, (module, stats) in enumerate(module_items[:10]):
        print(f"  {i+1}. {module}: {stats['coverage_percentage']}% ({stats['matched']}/{stats['implemented']})")


if __name__ == '__main__':
    main()
