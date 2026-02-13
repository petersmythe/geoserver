#!/usr/bin/env python3
"""
Match implemented REST endpoints with documented endpoints.
Identifies exact matches, partial matches, and mismatches.
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime


def normalize_documented_path(path: str, base_path: str = "") -> str:
    """
    Normalize documented endpoint paths by combining with base_path
    and stripping the /geoserver prefix.
    
    Examples:
      - base_path="/geoserver/rest", path="/workspaces" -> "/rest/workspaces"
      - base_path="/geoserver/gwc/rest", path="/layers" -> "/gwc/rest/layers"
      - base_path="", path="/authfilters" -> "/authfilters"
    """
    # Combine base_path and path
    if base_path:
        full_path = base_path.rstrip('/') + '/' + path.lstrip('/')
    else:
        full_path = path
    
    # Strip /geoserver prefix (common in OpenAPI specs)
    if full_path.startswith('/geoserver'):
        full_path = full_path[10:]  # len('/geoserver') = 10
    
    # Ensure path starts with /
    if not full_path.startswith('/'):
        full_path = '/' + full_path
    
    return full_path


def normalize_path(path: str) -> str:
    """
    Normalize path patterns for comparison.
    Converts various path variable formats to a standard format.
    Examples:
      - {workspace} -> {var}
      - {workspaceName} -> {var}
      - /${gwc.context.suffix:} -> {var}
      - /PROVIDER_PATH -> {var}
    """
    # Replace Spring property placeholders
    path = re.sub(r'\$\{[^}]+\}', '{var}', path)
    
    # Replace path variables with standard placeholder
    path = re.sub(r'\{[^}]+\}', '{var}', path)
    
    # Replace constant placeholders (like PROVIDER_PATH, ROOT_PATH)
    path = re.sub(r'/[A-Z_]+(?:/|$)', '/{var}/', path)
    
    # Clean up multiple slashes
    path = re.sub(r'/+', '/', path)
    
    # Remove trailing slash unless it's the root
    if len(path) > 1 and path.endswith('/'):
        path = path[:-1]
    
    return path


def create_endpoint_key(path: str, method: str) -> str:
    """Create a unique key for an endpoint based on normalized path and method."""
    normalized = normalize_path(path)
    return f"{method}:{normalized}"


def calculate_path_similarity(path1: str, path2: str) -> float:
    """
    Calculate similarity between two paths (0.0 to 1.0).
    Used for partial matching.
    """
    norm1 = normalize_path(path1)
    norm2 = normalize_path(path2)
    
    if norm1 == norm2:
        return 1.0
    
    # Split into segments
    segments1 = [s for s in norm1.split('/') if s]
    segments2 = [s for s in norm2.split('/') if s]
    
    # Different number of segments = lower similarity
    if len(segments1) != len(segments2):
        max_len = max(len(segments1), len(segments2))
        if max_len == 0:
            return 0.0
        length_penalty = abs(len(segments1) - len(segments2)) / max_len
        base_similarity = 1.0 - length_penalty
    else:
        base_similarity = 1.0
    
    # Compare segments
    min_len = min(len(segments1), len(segments2))
    if min_len == 0:
        return 0.0
    
    matching_segments = sum(1 for i in range(min_len) if segments1[i] == segments2[i])
    segment_similarity = matching_segments / max(len(segments1), len(segments2))
    
    return base_similarity * segment_similarity


def extract_parameters(endpoint: Dict) -> Dict:
    """Extract parameter information from an endpoint."""
    params = {
        'path_variables': [],
        'query_parameters': [],
        'has_request_body': False
    }
    
    # For implemented endpoints
    if 'path_variables' in endpoint:
        params['path_variables'] = [p.get('name', '') for p in endpoint.get('path_variables', [])]
    if 'query_parameters' in endpoint:
        params['query_parameters'] = [p.get('name', '') for p in endpoint.get('query_parameters', [])]
    if endpoint.get('request_body'):
        params['has_request_body'] = True
    
    # For documented endpoints
    if 'parameters' in endpoint:
        for param in endpoint.get('parameters', []):
            param_in = param.get('in', '')
            param_name = param.get('name', '')
            if param_in == 'path':
                params['path_variables'].append(param_name)
            elif param_in == 'query':
                params['query_parameters'].append(param_name)
        # Check for request body in OpenAPI
        if endpoint.get('requestBody') or any(
            p.get('in') == 'body' for p in endpoint.get('parameters', [])
        ):
            params['has_request_body'] = True
    
    return params


def compare_parameters(impl_params: Dict, doc_params: Dict) -> List[str]:
    """Compare parameters between implemented and documented endpoints."""
    differences = []
    
    # Compare path variables
    impl_path = set(impl_params['path_variables'])
    doc_path = set(doc_params['path_variables'])
    
    if impl_path != doc_path:
        missing_in_doc = impl_path - doc_path
        extra_in_doc = doc_path - impl_path
        if missing_in_doc:
            differences.append(f"Path variables in implementation but not documented: {', '.join(missing_in_doc)}")
        if extra_in_doc:
            differences.append(f"Path variables documented but not in implementation: {', '.join(extra_in_doc)}")
    
    # Compare query parameters
    impl_query = set(impl_params['query_parameters'])
    doc_query = set(doc_params['query_parameters'])
    
    if impl_query != doc_query:
        missing_in_doc = impl_query - doc_query
        extra_in_doc = doc_query - impl_query
        if missing_in_doc:
            differences.append(f"Query parameters in implementation but not documented: {', '.join(missing_in_doc)}")
        if extra_in_doc:
            differences.append(f"Query parameters documented but not in implementation: {', '.join(extra_in_doc)}")
    
    # Compare request body
    if impl_params['has_request_body'] != doc_params['has_request_body']:
        if impl_params['has_request_body']:
            differences.append("Implementation has request body but documentation does not")
        else:
            differences.append("Documentation has request body but implementation does not")
    
    return differences


def match_endpoints(implemented: List[Dict], documented: List[Dict]) -> Dict:
    """
    Match implemented endpoints with documented endpoints.
    Returns a dictionary with match results.
    """
    # Build lookup dictionaries
    impl_by_key = {}
    for endpoint in implemented:
        key = create_endpoint_key(endpoint['path'], endpoint['http_method'])
        if key not in impl_by_key:
            impl_by_key[key] = []
        impl_by_key[key].append(endpoint)
    
    doc_by_key = {}
    for endpoint in documented:
        # Normalize documented path using base_path
        normalized_doc_path = normalize_documented_path(
            endpoint['path'], 
            endpoint.get('base_path', '')
        )
        key = create_endpoint_key(normalized_doc_path, endpoint['method'])
        if key not in doc_by_key:
            doc_by_key[key] = []
        # Store the normalized path in the endpoint for later use
        endpoint['_normalized_path'] = normalized_doc_path
        doc_by_key[key].append(endpoint)
    
    # Find matches
    exact_matches = []
    partial_matches = []
    impl_only = []
    doc_only = []
    
    matched_impl_keys = set()
    matched_doc_keys = set()
    
    # First pass: exact matches
    for key in impl_by_key:
        if key in doc_by_key:
            # Exact match found
            for impl_endpoint in impl_by_key[key]:
                for doc_endpoint in doc_by_key[key]:
                    impl_params = extract_parameters(impl_endpoint)
                    doc_params = extract_parameters(doc_endpoint)
                    differences = compare_parameters(impl_params, doc_params)
                    
                    match = {
                        'match_type': 'exact' if not differences else 'exact_with_param_mismatch',
                        'implemented': impl_endpoint,
                        'documented': doc_endpoint,
                        'normalized_path': normalize_path(impl_endpoint['path']),
                        'http_method': impl_endpoint['http_method'],
                        'differences': differences
                    }
                    exact_matches.append(match)
            
            matched_impl_keys.add(key)
            matched_doc_keys.add(key)
    
    # Second pass: find unmatched endpoints
    for key in impl_by_key:
        if key not in matched_impl_keys:
            for endpoint in impl_by_key[key]:
                impl_only.append({
                    'endpoint': endpoint,
                    'normalized_path': normalize_path(endpoint['path']),
                    'http_method': endpoint['http_method'],
                    'source_file': endpoint.get('source_file', 'unknown'),
                    'module': endpoint.get('module', 'unknown')
                })
    
    for key in doc_by_key:
        if key not in matched_doc_keys:
            for endpoint in doc_by_key[key]:
                doc_only.append({
                    'endpoint': endpoint,
                    'normalized_path': endpoint.get('_normalized_path', normalize_path(endpoint['path'])),
                    'http_method': endpoint['method'],
                    'file': endpoint.get('file', 'unknown'),
                    'operation_id': endpoint.get('operation_id', 'unknown')
                })
    
    # Calculate statistics
    total_implemented = len(implemented)
    total_documented = len(documented)
    total_matched = len(exact_matches)
    
    return {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'total_implemented': total_implemented,
            'total_documented': total_documented,
            'total_matched': total_matched,
            'exact_matches': len([m for m in exact_matches if m['match_type'] == 'exact']),
            'matches_with_param_mismatch': len([m for m in exact_matches if m['match_type'] == 'exact_with_param_mismatch']),
            'implemented_only': len(impl_only),
            'documented_only': len(doc_only)
        },
        'exact_matches': exact_matches,
        'implemented_only': impl_only,
        'documented_only': doc_only
    }


def main():
    print("Loading endpoint data...")
    
    # Load implemented endpoints
    with open('.kiro/api-analysis/rest/implemented-all-endpoints.json', 'r', encoding='utf-8') as f:
        impl_data = json.load(f)
        implemented = impl_data['endpoints']
    
    # Load documented endpoints
    with open('.kiro/api-analysis/rest/documented-endpoints.json', 'r', encoding='utf-8') as f:
        doc_data = json.load(f)
        documented = []
        for file_info in doc_data['files']:
            base_path = file_info.get('base_path', '')
            for endpoint in file_info['endpoints']:
                # Add file context and base_path to each endpoint
                endpoint['file'] = file_info['file']
                endpoint['base_path'] = base_path
                documented.append(endpoint)
    
    print(f"Loaded {len(implemented)} implemented endpoints")
    print(f"Loaded {len(documented)} documented endpoints")
    
    print("\nMatching endpoints...")
    results = match_endpoints(implemented, documented)
    
    # Save results
    output_file = '.kiro/api-analysis/rest/endpoint-matches.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to {output_file}")
    print("\nSummary:")
    print(f"  Total implemented: {results['metadata']['total_implemented']}")
    print(f"  Total documented: {results['metadata']['total_documented']}")
    print(f"  Exact matches: {results['metadata']['exact_matches']}")
    print(f"  Matches with parameter mismatches: {results['metadata']['matches_with_param_mismatch']}")
    print(f"  Implemented only (not documented): {results['metadata']['implemented_only']}")
    print(f"  Documented only (not implemented): {results['metadata']['documented_only']}")


if __name__ == '__main__':
    main()
