#!/usr/bin/env python3
"""
Analyze parameter mismatches to identify patterns.
"""

import json
from collections import Counter, defaultdict

def analyze_mismatches():
    # Load endpoint matches
    with open('.kiro/api-analysis/rest/endpoint-matches.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    mismatches = [m for m in data['exact_matches'] if m['match_type'] == 'exact_with_param_mismatch']
    
    print(f"Total parameter mismatches: {len(mismatches)}\n")
    
    # Categorize mismatch types
    mismatch_types = Counter()
    mismatch_details = defaultdict(list)
    
    for match in mismatches:
        differences = match.get('differences', [])
        for diff in differences:
            # Categorize the difference
            if 'request body' in diff.lower():
                if 'Implementation has request body but documentation does not' in diff:
                    category = 'impl_has_body_doc_missing'
                else:
                    category = 'doc_has_body_impl_missing'
            elif 'Path variables' in diff:
                if 'implementation but not documented' in diff:
                    category = 'impl_has_path_var_doc_missing'
                else:
                    category = 'doc_has_path_var_impl_missing'
            elif 'Query parameters' in diff:
                if 'implementation but not documented' in diff:
                    category = 'impl_has_query_param_doc_missing'
                else:
                    category = 'doc_has_query_param_impl_missing'
            else:
                category = 'other'
            
            mismatch_types[category] += 1
            mismatch_details[category].append({
                'path': match['implemented']['path'],
                'method': match['implemented']['http_method'],
                'difference': diff,
                'source': match['implemented'].get('source_file', 'unknown')
            })
    
    # Print summary
    print("=" * 80)
    print("MISMATCH CATEGORIES")
    print("=" * 80)
    for category, count in mismatch_types.most_common():
        print(f"\n{category}: {count} occurrences")
        print("-" * 80)
        
        # Show first 3 examples
        for i, example in enumerate(mismatch_details[category][:3]):
            print(f"\nExample {i+1}:")
            print(f"  Path: {example['path']}")
            print(f"  Method: {example['method']}")
            print(f"  Issue: {example['difference']}")
            print(f"  Source: {example['source']}")
    
    # Analyze by module
    print("\n" + "=" * 80)
    print("MISMATCHES BY MODULE")
    print("=" * 80)
    
    module_mismatches = Counter()
    for match in mismatches:
        source = match['implemented'].get('source_file', '')
        if 'src/restconfig/' in source:
            module = 'restconfig'
        elif 'src/extension/' in source:
            module_name = source.split('src/extension/')[1].split('/')[0]
            module = f'extension/{module_name}'
        elif 'src/community/' in source:
            module_name = source.split('src/community/')[1].split('/')[0]
            module = f'community/{module_name}'
        else:
            module = 'other'
        
        module_mismatches[module] += 1
    
    for module, count in module_mismatches.most_common(10):
        print(f"  {module}: {count}")
    
    # Analyze specific query parameter mismatches
    print("\n" + "=" * 80)
    print("COMMON MISSING QUERY PARAMETERS")
    print("=" * 80)
    
    missing_params = Counter()
    for match in mismatches:
        impl_params = set(p['name'] for p in match['implemented'].get('query_parameters', []))
        
        # Try to extract documented params
        doc_params = set()
        if 'parameters' in match['documented']:
            for p in match['documented']['parameters']:
                if p.get('in') == 'query':
                    doc_params.add(p.get('name', ''))
        
        # Find params in impl but not in docs
        impl_only = impl_params - doc_params
        for param in impl_only:
            missing_params[param] += 1
    
    print("\nTop 20 parameters in implementation but not documented:")
    for param, count in missing_params.most_common(20):
        print(f"  {param}: {count} endpoints")
    
    # Save detailed report
    report = {
        'summary': {
            'total_mismatches': len(mismatches),
            'categories': dict(mismatch_types)
        },
        'by_module': dict(module_mismatches),
        'missing_parameters': dict(missing_params.most_common(50)),
        'examples_by_category': {
            category: details[:5] for category, details in mismatch_details.items()
        }
    }
    
    with open('.kiro/api-analysis/reports/mismatch-analysis.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nDetailed report saved to: .kiro/api-analysis/reports/mismatch-analysis.json")

if __name__ == '__main__':
    analyze_mismatches()
