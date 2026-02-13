#!/usr/bin/env python3
"""
Generate modular OpenAPI 3.0 specifications from REST endpoint data.
Creates separate YAML files for different modules with common reusable components.
"""

import json
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Set

# Module categorization based on source paths
MODULE_CATEGORIES = {
    'restconfig': 'rest-core',
    'gwc': 'rest-gwc',
    'security': 'rest-security',
    'extension': 'rest-extensions',
    'community': 'rest-community'
}

def load_endpoints(file_path: str) -> Dict:
    """Load the consolidated REST endpoints JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def categorize_endpoint(endpoint: Dict) -> str:
    """Determine which module category an endpoint belongs to."""
    source_file = endpoint.get('source_file', '')
    module = endpoint.get('module', '')
    
    # Check source file path
    if '/gwc/' in source_file or module == 'gwc':
        return 'rest-gwc'
    elif '/security/' in source_file or 'security' in source_file.lower():
        return 'rest-security'
    elif '/restconfig/' in source_file:
        return 'rest-core'
    elif '/extension/' in source_file:
        return 'rest-extensions'
    elif '/community/' in source_file:
        return 'rest-community'
    else:
        # Default to core
        return 'rest-core'

def normalize_path(path: str) -> str:
    """Normalize path patterns to OpenAPI format."""
    # Remove Spring expression language patterns
    path = path.replace('${gwc.context.suffix:}', 'gwc')
    
    # Remove any newlines and collapse whitespace
    path = ' '.join(path.split())
    
    # Remove spaces around slashes
    path = path.replace(' /', '/').replace('/ ', '/')
    
    # Handle constant references
    replacements = {
        '/ROOT_PATH + "/resource': '/rest/resource',
        'ROOT_PATH + "/resource': '/rest/resource',
        '/PROVIDER_PATH': '/rest/security/authproviders/{providerName}',
        '/EchoesController.ECHOES_ROOT': '/rest/params-extractor/echoes',
        '/RulesController.RULES_ROOT': '/rest/params-extractor/rules',
        '/ProxyBaseExtensionRulesController.RULES_ROOT': '/rest/proxy-base-ext/rules'
    }
    
    for old, new in replacements.items():
        path = path.replace(old, new)
    
    # Clean up duplicate slashes
    while '//' in path:
        path = path.replace('//', '/')
    
    # Remove any remaining spaces
    path = path.replace(' ', '')
    
    # Ensure path starts with /
    if not path.startswith('/'):
        path = '/' + path
    
    return path

def get_parameter_schema(param: Dict) -> Dict:
    """Generate OpenAPI schema for a parameter."""
    param_type = param.get('type', 'string')
    
    # Map Java types to OpenAPI types
    type_mapping = {
        'string': 'string', 'String': 'string',
        'int': 'integer', 'Integer': 'integer',
        'long': 'integer', 'Long': 'integer',
        'boolean': 'boolean', 'Boolean': 'boolean',
        'double': 'number', 'Double': 'number',
        'float': 'number', 'Float': 'number'
    }
    
    openapi_type = type_mapping.get(param_type, 'string')
    schema = {'type': openapi_type}
    
    # Add format for specific types
    if openapi_type == 'integer' and param_type in ['long', 'Long']:
        schema['format'] = 'int64'
    elif openapi_type == 'number':
        schema['format'] = 'float' if param_type in ['float', 'Float'] else 'double'
    
    return schema

def create_parameter(param: Dict, location: str) -> Dict:
    """Create an OpenAPI parameter definition."""
    parameter = {
        'name': param['name'],
        'in': location,
        'required': param.get('required', location == 'path'),  # Path params always required
        'schema': get_parameter_schema(param)
    }
    
    # Add description
    if 'description' in param:
        parameter['description'] = param['description']
    else:
        parameter['description'] = f"The {param['name']} parameter"
    
    return parameter

def get_request_body_schema(request_body: Dict) -> Dict:
    """Generate OpenAPI request body schema."""
    body_type = request_body.get('type', 'object')
    return {
        'type': 'object',
        'description': f'{body_type} configuration object'
    }

def create_request_body(request_body: Dict) -> Dict:
    """Create an OpenAPI request body definition."""
    return {
        'required': True,
        'content': {
            'application/json': {
                'schema': get_request_body_schema(request_body)
            },
            'application/xml': {
                'schema': get_request_body_schema(request_body)
            }
        }
    }

def get_response_schema(return_type: str) -> Dict:
    """Generate OpenAPI response schema based on return type."""
    if return_type in ['void', 'ResponseEntity', 'ResponseEntity<Void>']:
        return None
    
    if 'List<' in return_type or 'Collection<' in return_type:
        return {'type': 'array', 'items': {'type': 'object'}}
    
    if return_type in ['String', 'string']:
        return {'type': 'string'}
    
    if return_type in ['Boolean', 'boolean']:
        return {'type': 'boolean'}
    
    if return_type in ['Integer', 'int', 'Long', 'long']:
        return {'type': 'integer'}
    
    return {'type': 'object'}

def create_responses(endpoint: Dict) -> Dict:
    """Create OpenAPI responses for an endpoint."""
    responses = {}
    return_type = endpoint.get('return_type', 'void')
    http_method = endpoint.get('http_method', 'GET')
    
    # Success response
    if http_method == 'POST':
        responses['201'] = {'description': 'Resource created successfully'}
        schema = get_response_schema(return_type)
        if schema:
            responses['201']['content'] = {
                'application/json': {'schema': schema},
                'application/xml': {'schema': schema}
            }
    elif http_method == 'DELETE':
        responses['200'] = {'description': 'Resource deleted successfully'}
    else:
        responses['200'] = {'description': 'Successful operation'}
        schema = get_response_schema(return_type)
        if schema:
            responses['200']['content'] = {
                'application/json': {'schema': schema},
                'application/xml': {'schema': schema}
            }
    
    # Common error responses - use $ref to common responses
    responses['400'] = {'$ref': '../common/responses.yaml#/BadRequest'}
    responses['401'] = {'$ref': '../common/responses.yaml#/Unauthorized'}
    responses['403'] = {'$ref': '../common/responses.yaml#/Forbidden'}
    
    if http_method in ['GET', 'PUT', 'DELETE', 'PATCH']:
        responses['404'] = {'$ref': '../common/responses.yaml#/NotFound'}
    
    responses['500'] = {'$ref': '../common/responses.yaml#/InternalServerError'}
    
    return responses

def generate_operation_id(endpoint: Dict, path: str) -> str:
    """Generate a unique operation ID for an endpoint."""
    method = endpoint['http_method'].lower()
    class_name = endpoint.get('class_name', 'Unknown')
    method_name = endpoint.get('method_name', 'unknown')
    module = endpoint.get('module', 'rest')
    
    if class_name == 'FQN':
        class_name = 'Rest'
    
    operation_id = f"{method}_{module}_{class_name}_{method_name}"
    operation_id = operation_id.replace('.', '_').replace('-', '_')
    
    return operation_id

def create_operation(endpoint: Dict, path: str, module_category: str) -> Dict:
    """Create an OpenAPI operation for an endpoint."""
    operation = {
        'operationId': generate_operation_id(endpoint, path),
        'summary': f"{endpoint['http_method']} {path}",
        'description': f"Endpoint from {endpoint.get('module', 'rest')} module",
        'tags': [module_category.replace('rest-', '').replace('-', ' ').title()],
        'responses': create_responses(endpoint)
    }
    
    # Add parameters
    parameters = []
    
    # Path parameters
    for path_var in endpoint.get('path_variables', []):
        parameters.append(create_parameter(path_var, 'path'))
    
    # Query parameters
    for query_param in endpoint.get('query_parameters', []):
        parameters.append(create_parameter(query_param, 'query'))
    
    if parameters:
        operation['parameters'] = parameters
    
    # Add request body
    request_body = endpoint.get('request_body')
    if request_body and endpoint['http_method'] in ['POST', 'PUT', 'PATCH']:
        operation['requestBody'] = create_request_body(request_body)
    
    return operation

def create_path_item(endpoints: List[Dict], path: str, module_category: str) -> Dict:
    """Create an OpenAPI path item with all operations for a path."""
    path_item = {}
    
    for endpoint in endpoints:
        method = endpoint['http_method'].lower()
        path_item[method] = create_operation(endpoint, path, module_category)
    
    return path_item

def generate_common_responses() -> Dict:
    """Generate common response definitions."""
    return {
        'BadRequest': {
            'description': 'Bad request - invalid parameters or request body',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'error': {'type': 'string'},
                            'message': {'type': 'string'}
                        }
                    }
                }
            }
        },
        'Unauthorized': {
            'description': 'Authentication required',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'error': {'type': 'string'},
                            'message': {'type': 'string'}
                        }
                    }
                }
            }
        },
        'Forbidden': {
            'description': 'Insufficient permissions',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'error': {'type': 'string'},
                            'message': {'type': 'string'}
                        }
                    }
                }
            }
        },
        'NotFound': {
            'description': 'Resource not found',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'error': {'type': 'string'},
                            'message': {'type': 'string'}
                        }
                    }
                }
            }
        },
        'InternalServerError': {
            'description': 'Internal server error',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'error': {'type': 'string'},
                            'message': {'type': 'string'},
                            'trace': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }

def generate_common_parameters() -> Dict:
    """Generate common parameter definitions."""
    return {
        'workspaceName': {
            'name': 'workspaceName',
            'in': 'path',
            'required': True,
            'schema': {'type': 'string'},
            'description': 'The name of the workspace'
        },
        'storeName': {
            'name': 'storeName',
            'in': 'path',
            'required': True,
            'schema': {'type': 'string'},
            'description': 'The name of the data store'
        },
        'layerName': {
            'name': 'layerName',
            'in': 'path',
            'required': True,
            'schema': {'type': 'string'},
            'description': 'The name of the layer'
        },
        'styleName': {
            'name': 'styleName',
            'in': 'path',
            'required': True,
            'schema': {'type': 'string'},
            'description': 'The name of the style'
        }
    }

def generate_common_schemas() -> Dict:
    """Generate common schema definitions."""
    return {
        'Error': {
            'type': 'object',
            'properties': {
                'error': {'type': 'string'},
                'message': {'type': 'string'}
            }
        },
        'Link': {
            'type': 'object',
            'properties': {
                'href': {'type': 'string', 'format': 'uri'},
                'rel': {'type': 'string'},
                'type': {'type': 'string'}
            }
        }
    }

def generate_module_spec(module_category: str, endpoints: List[Dict]) -> Dict:
    """Generate OpenAPI spec for a specific module."""
    # Group endpoints by path
    paths_dict = defaultdict(list)
    for endpoint in endpoints:
        path = normalize_path(endpoint['path'])
        paths_dict[path].append(endpoint)
    
    # Create module spec
    spec = {
        'openapi': '3.0.0',
        'info': {
            'title': f'GeoServer {module_category.replace("rest-", "").replace("-", " ").title()} API',
            'version': '1.0.0',
            'description': f'REST API endpoints for {module_category.replace("rest-", "")} module'
        },
        'paths': {}
    }
    
    # Add all paths
    for path in sorted(paths_dict.keys()):
        spec['paths'][path] = create_path_item(paths_dict[path], path, module_category)
    
    return spec

def write_yaml(data: Dict, file_path: Path):
    """Write data to YAML file with proper formatting."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

def main():
    """Main execution function."""
    # Paths
    input_file = Path('.kiro/api-analysis/rest/implemented-all-endpoints.json')
    output_base = Path('.kiro/api-analysis/specs')
    
    print(f"Loading endpoints from {input_file}...")
    endpoints_data = load_endpoints(input_file)
    
    # Categorize endpoints by module
    module_endpoints = defaultdict(list)
    for endpoint in endpoints_data['endpoints']:
        category = categorize_endpoint(endpoint)
        module_endpoints[category].append(endpoint)
    
    print(f"\nProcessing {endpoints_data['metadata']['total_endpoints']} endpoints...")
    print(f"Found {len(module_endpoints)} module categories:")
    for category, endpoints in module_endpoints.items():
        print(f"  - {category}: {len(endpoints)} endpoints")
    
    # Generate common components
    print("\nGenerating common components...")
    common_dir = output_base / 'common'
    
    write_yaml(generate_common_responses(), common_dir / 'responses.yaml')
    print(f"  ✓ {common_dir / 'responses.yaml'}")
    
    write_yaml(generate_common_parameters(), common_dir / 'parameters.yaml')
    print(f"  ✓ {common_dir / 'parameters.yaml'}")
    
    write_yaml(generate_common_schemas(), common_dir / 'schemas.yaml')
    print(f"  ✓ {common_dir / 'schemas.yaml'}")
    
    # Generate module specs
    print("\nGenerating module specifications...")
    rest_dir = output_base / 'rest'
    
    for module_category, endpoints in sorted(module_endpoints.items()):
        spec = generate_module_spec(module_category, endpoints)
        output_file = rest_dir / f'{module_category}.yaml'
        write_yaml(spec, output_file)
        print(f"  ✓ {output_file} ({len(spec['paths'])} paths)")
    
    print(f"\n✓ Successfully generated modular OpenAPI 3.0 specifications")
    print(f"  - Common components: {common_dir}")
    print(f"  - REST modules: {rest_dir}")

if __name__ == '__main__':
    main()
