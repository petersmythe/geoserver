#!/usr/bin/env python3
"""
Generate OpenAPI 3.0 specification from REST endpoint data.
Converts the extracted REST endpoints into a complete OpenAPI 3.0 YAML specification.
"""

import json
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

def load_endpoints(file_path: str) -> Dict:
    """Load the consolidated REST endpoints JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_path(path: str) -> str:
    """Normalize path patterns to OpenAPI format."""
    # Remove Spring expression language patterns
    path = path.replace('${gwc.context.suffix:}', 'gwc')
    
    # Handle constant references (e.g., ROOT_PATH, PROVIDER_PATH)
    if 'ROOT_PATH' in path:
        path = path.replace('/ROOT_PATH + "/resource', '/rest/resource')
        path = path.replace('ROOT_PATH + "/resource', '/rest/resource')
    if 'PROVIDER_PATH' in path:
        path = path.replace('/PROVIDER_PATH', '/rest/security/authproviders/{providerName}')
    if 'EchoesController.ECHOES_ROOT' in path:
        path = path.replace('/EchoesController.ECHOES_ROOT', '/rest/params-extractor/echoes')
    if 'RulesController.RULES_ROOT' in path:
        path = path.replace('/RulesController.RULES_ROOT', '/rest/params-extractor/rules')
    if 'ProxyBaseExtensionRulesController.RULES_ROOT' in path:
        path = path.replace('/ProxyBaseExtensionRulesController.RULES_ROOT', '/rest/proxy-base-ext/rules')
    
    # Clean up duplicate slashes
    while '//' in path:
        path = path.replace('//', '/')
    
    # Ensure path starts with /
    if not path.startswith('/'):
        path = '/' + path
    
    return path

def get_parameter_schema(param: Dict) -> Dict:
    """Generate OpenAPI schema for a parameter."""
    param_type = param.get('type', 'string')
    
    # Map Java types to OpenAPI types
    type_mapping = {
        'string': 'string',
        'String': 'string',
        'int': 'integer',
        'Integer': 'integer',
        'long': 'integer',
        'Long': 'integer',
        'boolean': 'boolean',
        'Boolean': 'boolean',
        'double': 'number',
        'Double': 'number',
        'float': 'number',
        'Float': 'number'
    }
    
    openapi_type = type_mapping.get(param_type, 'string')
    
    schema = {'type': openapi_type}
    
    # Add format for specific types
    if openapi_type == 'integer' and param_type in ['long', 'Long']:
        schema['format'] = 'int64'
    elif openapi_type == 'number' and param_type in ['float', 'Float']:
        schema['format'] = 'float'
    elif openapi_type == 'number' and param_type in ['double', 'Double']:
        schema['format'] = 'double'
    
    return schema

def create_parameter(param: Dict, location: str) -> Dict:
    """Create an OpenAPI parameter definition."""
    parameter = {
        'name': param['name'],
        'in': location,
        'required': param.get('required', False),
        'schema': get_parameter_schema(param)
    }
    
    # Add description if available
    if 'description' in param:
        parameter['description'] = param['description']
    else:
        # Generate basic description
        parameter['description'] = f"The {param['name']} parameter"
    
    return parameter

def get_request_body_schema(request_body: Dict) -> Dict:
    """Generate OpenAPI request body schema."""
    body_type = request_body.get('type', 'object')
    
    # Create a basic schema
    schema = {
        'type': 'object',
        'description': f'{body_type} object'
    }
    
    return schema

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
    # Handle common return types
    if return_type in ['void', 'ResponseEntity', 'ResponseEntity<Void>']:
        return None
    
    if 'List<' in return_type or 'Collection<' in return_type:
        return {
            'type': 'array',
            'items': {'type': 'object'}
        }
    
    if return_type in ['String', 'string']:
        return {'type': 'string'}
    
    if return_type in ['Boolean', 'boolean']:
        return {'type': 'boolean'}
    
    if return_type in ['Integer', 'int', 'Long', 'long']:
        return {'type': 'integer'}
    
    # Default to object
    return {'type': 'object'}

def create_responses(endpoint: Dict) -> Dict:
    """Create OpenAPI responses for an endpoint."""
    responses = {}
    
    # Success response
    return_type = endpoint.get('return_type', 'void')
    http_method = endpoint.get('http_method', 'GET')
    
    if http_method == 'POST':
        # POST typically returns 201 Created
        responses['201'] = {
            'description': 'Resource created successfully'
        }
        schema = get_response_schema(return_type)
        if schema:
            responses['201']['content'] = {
                'application/json': {'schema': schema},
                'application/xml': {'schema': schema}
            }
    elif http_method == 'DELETE':
        # DELETE typically returns 200 or 204
        responses['200'] = {
            'description': 'Resource deleted successfully'
        }
    else:
        # GET, PUT, PATCH return 200
        responses['200'] = {
            'description': 'Successful operation'
        }
        schema = get_response_schema(return_type)
        if schema:
            responses['200']['content'] = {
                'application/json': {'schema': schema},
                'application/xml': {'schema': schema}
            }
    
    # Common error responses
    responses['400'] = {'description': 'Bad request'}
    responses['401'] = {'description': 'Unauthorized'}
    responses['403'] = {'description': 'Forbidden'}
    
    if http_method in ['GET', 'PUT', 'DELETE', 'PATCH']:
        responses['404'] = {'description': 'Resource not found'}
    
    responses['500'] = {'description': 'Internal server error'}
    
    return responses

def generate_operation_id(endpoint: Dict, path: str) -> str:
    """Generate a unique operation ID for an endpoint."""
    method = endpoint['http_method'].lower()
    class_name = endpoint.get('class_name', 'Unknown')
    method_name = endpoint.get('method_name', 'unknown')
    module = endpoint.get('module', 'rest')
    
    # Clean up class name
    if class_name == 'FQN':
        class_name = 'Rest'
    
    # Create operation ID
    operation_id = f"{method}_{module}_{class_name}_{method_name}"
    
    # Clean up operation ID
    operation_id = operation_id.replace('.', '_').replace('-', '_')
    
    return operation_id

def create_path_item(endpoints: List[Dict], path: str) -> Dict:
    """Create an OpenAPI path item with all operations for a path."""
    path_item = {}
    
    for endpoint in endpoints:
        method = endpoint['http_method'].lower()
        
        # Create operation
        operation = {
            'operationId': generate_operation_id(endpoint, path),
            'summary': f"{endpoint['http_method']} {path}",
            'description': f"Endpoint from {endpoint.get('module', 'rest')} module",
            'tags': ['REST API'],
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
        if request_body and method in ['post', 'put', 'patch']:
            operation['requestBody'] = create_request_body(request_body)
        
        path_item[method] = operation
    
    return path_item

def generate_openapi_spec(endpoints_data: Dict) -> Dict:
    """Generate complete OpenAPI 3.0 specification."""
    
    # Group endpoints by path
    paths_dict = defaultdict(list)
    for endpoint in endpoints_data['endpoints']:
        path = normalize_path(endpoint['path'])
        paths_dict[path].append(endpoint)
    
    # Create OpenAPI spec
    spec = {
        'openapi': '3.0.0',
        'info': {
            'title': 'GeoServer REST API',
            'version': '1.0.0',
            'description': 'Complete REST API documentation for GeoServer configuration and management endpoints',
            'contact': {
                'name': 'GeoServer',
                'email': 'geoserver-users@osgeo.org',
                'url': 'https://geoserver.org/comm/'
            },
            'license': {
                'name': 'GPL 2.0',
                'url': 'https://www.gnu.org/licenses/old-licenses/gpl-2.0.html'
            }
        },
        'servers': [
            {
                'url': 'http://localhost:8080/geoserver/rest',
                'description': 'Local development server'
            },
            {
                'url': 'https://example.com/geoserver/rest',
                'description': 'Production server'
            }
        ],
        'tags': [
            {
                'name': 'REST API',
                'description': 'GeoServer REST configuration and management endpoints'
            }
        ],
        'paths': {}
    }
    
    # Add all paths
    for path in sorted(paths_dict.keys()):
        spec['paths'][path] = create_path_item(paths_dict[path], path)
    
    # Add security schemes
    spec['components'] = {
        'securitySchemes': {
            'basicAuth': {
                'type': 'http',
                'scheme': 'basic',
                'description': 'HTTP Basic Authentication'
            }
        }
    }
    
    # Apply security globally
    spec['security'] = [
        {'basicAuth': []}
    ]
    
    return spec

def main():
    """Main execution function."""
    # Paths
    input_file = Path('.kiro/api-analysis/rest/implemented-all-endpoints.json')
    output_file = Path('.kiro/api-analysis/specs/rest-openapi-3.0.yaml')
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading endpoints from {input_file}...")
    endpoints_data = load_endpoints(input_file)
    
    print(f"Processing {endpoints_data['metadata']['total_endpoints']} endpoints...")
    spec = generate_openapi_spec(endpoints_data)
    
    print(f"Writing OpenAPI 3.0 specification to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✓ Successfully generated OpenAPI 3.0 specification")
    print(f"  - Total paths: {len(spec['paths'])}")
    print(f"  - Output file: {output_file}")

if __name__ == '__main__':
    main()
