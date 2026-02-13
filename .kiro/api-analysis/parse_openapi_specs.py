#!/usr/bin/env python3
"""
Parse existing OpenAPI/Swagger 2.0 specifications and extract REST endpoint definitions.
Outputs structured JSON with all endpoint metadata.
"""

import json
import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


def parse_yaml_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Parse a YAML file and return its contents.
    Returns None if parsing fails.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        # Extract line number if available
        line_num = None
        if hasattr(e, 'problem_mark'):
            line_num = e.problem_mark.line + 1
        return {
            'error': True,
            'error_type': 'yaml_syntax',
            'message': str(e),
            'line': line_num
        }
    except Exception as e:
        return {
            'error': True,
            'error_type': 'file_read',
            'message': str(e)
        }


def extract_parameter_info(param: Dict[str, Any]) -> Dict[str, Any]:
    """Extract parameter information from OpenAPI parameter definition."""
    param_info = {
        'name': param.get('name'),
        'in': param.get('in'),  # path, query, header, body, formData
        'description': param.get('description', ''),
        'required': param.get('required', False),
        'type': param.get('type'),
        'format': param.get('format'),
        'default': param.get('default'),
        'enum': param.get('enum'),
    }
    
    # Handle body parameters with schema
    if param.get('in') == 'body' and 'schema' in param:
        param_info['schema'] = param['schema']
    
    # Remove None values
    return {k: v for k, v in param_info.items() if v is not None}


def extract_response_info(responses: Dict[str, Any]) -> Dict[str, Any]:
    """Extract response information from OpenAPI responses definition."""
    response_info = {}
    
    for status_code, response_def in responses.items():
        # Handle malformed YAML where response_def might be None
        if response_def is None:
            response_info[status_code] = {
                'description': '',
            }
            continue
        
        if not isinstance(response_def, dict):
            continue
            
        response_info[status_code] = {
            'description': response_def.get('description', ''),
        }
        
        if 'schema' in response_def:
            response_info[status_code]['schema'] = response_def['schema']
        
        if 'headers' in response_def:
            response_info[status_code]['headers'] = response_def['headers']
        
        if 'examples' in response_def:
            response_info[status_code]['examples'] = response_def['examples']
    
    return response_info


def extract_endpoints_from_spec(spec: Dict[str, Any], file_name: str) -> Dict[str, Any]:
    """
    Extract all endpoint definitions from an OpenAPI/Swagger specification.
    """
    result = {
        'file': file_name,
        'swagger_version': spec.get('swagger', spec.get('openapi')),
        'info': spec.get('info', {}),
        'base_path': spec.get('basePath', ''),
        'host': spec.get('host', ''),
        'endpoints': []
    }
    
    paths = spec.get('paths', {})
    
    if not paths:
        return result
    
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
            
        # Path-level parameters (apply to all operations)
        path_parameters = path_item.get('parameters', [])
        
        # Extract operations (GET, POST, PUT, DELETE, PATCH, etc.)
        for method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
            if method not in path_item:
                continue
            
            operation = path_item[method]
            
            # Skip if operation is not a dict (malformed YAML)
            if not isinstance(operation, dict):
                continue
            
            # Combine path-level and operation-level parameters
            all_parameters = path_parameters + operation.get('parameters', [])
            
            endpoint = {
                'path': path,
                'method': method.upper(),
                'operation_id': operation.get('operationId'),
                'summary': operation.get('summary', ''),
                'description': operation.get('description', ''),
                'tags': operation.get('tags', []),
                'consumes': operation.get('consumes', []),
                'produces': operation.get('produces', []),
                'parameters': [extract_parameter_info(p) for p in all_parameters],
                'responses': extract_response_info(operation.get('responses', {})),
                'deprecated': operation.get('deprecated', False),
            }
            
            # Remove empty lists/dicts
            endpoint = {k: v for k, v in endpoint.items() if v or k in ['deprecated', 'operation_id']}
            
            result['endpoints'].append(endpoint)
    
    return result


def main():
    """Main execution function."""
    # Read inventory file
    inventory_path = Path('.kiro/api-analysis/existing-specs-inventory.json')
    
    if not inventory_path.exists():
        print(f"Error: Inventory file not found at {inventory_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(inventory_path, 'r', encoding='utf-8') as f:
        inventory = json.load(f)
    
    results = {
        'metadata': {
            'parse_date': datetime.now().isoformat(),
            'total_files': len(inventory['files']),
            'successful_parses': 0,
            'failed_parses': 0,
            'total_endpoints': 0,
        },
        'files': [],
        'errors': []
    }
    
    # Parse each YAML file
    for file_info in inventory['files']:
        file_path = Path(file_info['path'])
        print(f"Parsing {file_path.name}...", file=sys.stderr)
        
        spec_data = parse_yaml_file(file_path)
        
        if spec_data is None:
            results['errors'].append({
                'file': file_info['name'],
                'path': str(file_path),
                'error': 'Failed to read file'
            })
            results['metadata']['failed_parses'] += 1
            continue
        
        # Check if parsing resulted in an error
        if spec_data.get('error'):
            error_info = {
                'file': file_info['name'],
                'path': str(file_path),
                'error_type': spec_data.get('error_type'),
                'message': spec_data.get('message'),
            }
            if spec_data.get('line'):
                error_info['line'] = spec_data['line']
            
            results['errors'].append(error_info)
            results['metadata']['failed_parses'] += 1
            continue
        
        # Extract endpoints
        try:
            extracted = extract_endpoints_from_spec(spec_data, file_info['name'])
            results['files'].append(extracted)
            results['metadata']['successful_parses'] += 1
            results['metadata']['total_endpoints'] += len(extracted['endpoints'])
            
            print(f"  ✓ Extracted {len(extracted['endpoints'])} endpoints", file=sys.stderr)
        except Exception as e:
            import traceback
            results['errors'].append({
                'file': file_info['name'],
                'path': str(file_path),
                'error_type': 'extraction_error',
                'message': str(e),
                'traceback': traceback.format_exc()
            })
            results['metadata']['failed_parses'] += 1
            print(f"  ✗ Error: {str(e)}", file=sys.stderr)
    
    # Write output
    output_path = Path('.kiro/api-analysis/rest/documented-endpoints.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Parsing complete!", file=sys.stderr)
    print(f"  Successful: {results['metadata']['successful_parses']}", file=sys.stderr)
    print(f"  Failed: {results['metadata']['failed_parses']}", file=sys.stderr)
    print(f"  Total endpoints: {results['metadata']['total_endpoints']}", file=sys.stderr)
    print(f"  Output: {output_path}", file=sys.stderr)
    
    if results['errors']:
        print(f"\n⚠ Errors encountered:", file=sys.stderr)
        for error in results['errors']:
            if 'line' in error:
                print(f"  - {error['file']} (line {error['line']}): {error['message']}", file=sys.stderr)
            else:
                print(f"  - {error['file']}: {error['message']}", file=sys.stderr)
    
    return 0 if results['metadata']['failed_parses'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
