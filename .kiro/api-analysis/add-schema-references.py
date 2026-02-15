#!/usr/bin/env python3
"""
Add schema references to OpenAPI specification request bodies and responses.
This script updates the bundled GeoServer OpenAPI specs to reference the schemas
defined in common/schemas.yaml.
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List

# Mapping of endpoint patterns to schema names
ENDPOINT_SCHEMA_MAP = {
    # Workspace endpoints
    r'/rest/workspaces': {
        'POST': {'request': 'Workspace', 'response': 'Workspace'},
        'GET': {'response': 'Workspace'},
    },
    r'/rest/workspaces/\{[^}]+\}': {
        'GET': {'response': 'Workspace'},
        'PUT': {'request': 'Workspace', 'response': 'Workspace'},
        'DELETE': {'response': None},
    },
    
    # DataStore endpoints
    r'/rest/workspaces/\{[^}]+\}/datastores': {
        'POST': {'request': 'DataStore', 'response': 'DataStore'},
        'GET': {'response': 'DataStore'},
    },
    r'/rest/workspaces/\{[^}]+\}/datastores/\{[^}]+\}': {
        'GET': {'response': 'DataStore'},
        'PUT': {'request': 'DataStore', 'response': 'DataStore'},
        'DELETE': {'response': None},
    },
    
    # FeatureType endpoints
    r'/rest/workspaces/\{[^}]+\}/datastores/\{[^}]+\}/featuretypes': {
        'POST': {'request': 'FeatureType', 'response': 'FeatureType'},
        'GET': {'response': 'FeatureType'},
    },
    r'/rest/workspaces/\{[^}]+\}/datastores/\{[^}]+\}/featuretypes/\{[^}]+\}': {
        'GET': {'response': 'FeatureType'},
        'PUT': {'request': 'FeatureType', 'response': 'FeatureType'},
        'DELETE': {'response': None},
    },
    
    # Layer endpoints
    r'/rest/layers': {
        'POST': {'request': 'Layer', 'response': 'Layer'},
        'GET': {'response': 'Layer'},
    },
    r'/rest/layers/\{[^}]+\}': {
        'GET': {'response': 'Layer'},
        'PUT': {'request': 'Layer', 'response': 'Layer'},
        'DELETE': {'response': None},
    },
    
    # Style endpoints
    r'/rest/styles': {
        'POST': {'request': 'Style', 'response': 'Style'},
        'GET': {'response': 'Style'},
    },
    r'/rest/styles/\{[^}]+\}': {
        'GET': {'response': 'Style'},
        'PUT': {'request': 'Style', 'response': 'Style'},
        'DELETE': {'response': None},
    },
    r'/rest/workspaces/\{[^}]+\}/styles': {
        'POST': {'request': 'Style', 'response': 'Style'},
        'GET': {'response': 'Style'},
    },
    r'/rest/workspaces/\{[^}]+\}/styles/\{[^}]+\}': {
        'GET': {'response': 'Style'},
        'PUT': {'request': 'Style', 'response': 'Style'},
        'DELETE': {'response': None},
    },
    
    # LayerGroup endpoints
    r'/rest/layergroups': {
        'POST': {'request': 'LayerGroup', 'response': 'LayerGroup'},
        'GET': {'response': 'LayerGroup'},
    },
    r'/rest/layergroups/\{[^}]+\}': {
        'GET': {'response': 'LayerGroup'},
        'PUT': {'request': 'LayerGroup', 'response': 'LayerGroup'},
        'DELETE': {'response': None},
    },
    
    # Coverage endpoints
    r'/rest/workspaces/\{[^}]+\}/coveragestores/\{[^}]+\}/coverages': {
        'POST': {'request': 'Coverage', 'response': 'Coverage'},
        'GET': {'response': 'Coverage'},
    },
    r'/rest/workspaces/\{[^}]+\}/coveragestores/\{[^}]+\}/coverages/\{[^}]+\}': {
        'GET': {'response': 'Coverage'},
        'PUT': {'request': 'Coverage', 'response': 'Coverage'},
        'DELETE': {'response': None},
    },
    
    # CoverageStore endpoints
    r'/rest/workspaces/\{[^}]+\}/coveragestores': {
        'POST': {'request': 'CoverageStore', 'response': 'CoverageStore'},
        'GET': {'response': 'CoverageStore'},
    },
    r'/rest/workspaces/\{[^}]+\}/coveragestores/\{[^}]+\}': {
        'GET': {'response': 'CoverageStore'},
        'PUT': {'request': 'CoverageStore', 'response': 'CoverageStore'},
        'DELETE': {'response': None},
    },
    
    # WMSStore endpoints
    r'/rest/workspaces/\{[^}]+\}/wmsstores': {
        'POST': {'request': 'WMSStore', 'response': 'WMSStore'},
        'GET': {'response': 'WMSStore'},
    },
    r'/rest/workspaces/\{[^}]+\}/wmsstores/\{[^}]+\}': {
        'GET': {'response': 'WMSStore'},
        'PUT': {'request': 'WMSStore', 'response': 'WMSStore'},
        'DELETE': {'response': None},
    },
    
    # WMTSStore endpoints
    r'/rest/workspaces/\{[^}]+\}/wmtsstores': {
        'POST': {'request': 'WMTSStore', 'response': 'WMTSStore'},
        'GET': {'response': 'WMTSStore'},
    },
    r'/rest/workspaces/\{[^}]+\}/wmtsstores/\{[^}]+\}': {
        'GET': {'response': 'WMTSStore'},
        'PUT': {'request': 'WMTSStore', 'response': 'WMTSStore'},
        'DELETE': {'response': None},
    },
    
    # Security endpoints
    r'/rest/security/users': {
        'POST': {'request': 'User', 'response': 'User'},
        'GET': {'response': 'User'},
    },
    r'/rest/security/users/\{[^}]+\}': {
        'GET': {'response': 'User'},
        'PUT': {'request': 'User', 'response': 'User'},
        'DELETE': {'response': None},
    },
    r'/rest/security/roles': {
        'POST': {'request': 'Role', 'response': 'Role'},
        'GET': {'response': 'Role'},
    },
    r'/rest/security/roles/\{[^}]+\}': {
        'GET': {'response': 'Role'},
        'PUT': {'request': 'Role', 'response': 'Role'},
        'DELETE': {'response': None},
    },
    r'/rest/security/acl': {
        'POST': {'request': 'SecurityRule', 'response': 'SecurityRule'},
        'GET': {'response': 'SecurityRule'},
    },
    
    # Importer endpoints
    r'/rest/imports': {
        'POST': {'request': 'ImportContext', 'response': 'ImportContext'},
        'GET': {'response': 'ImportContext'},
    },
    r'/rest/imports/\{[^}]+\}': {
        'GET': {'response': 'ImportContext'},
        'PUT': {'request': 'ImportContext', 'response': 'ImportContext'},
        'DELETE': {'response': None},
    },
    r'/rest/imports/\{[^}]+\}/tasks': {
        'POST': {'request': 'ImportTask', 'response': 'ImportTask'},
        'GET': {'response': 'ImportTask'},
    },
    r'/rest/imports/\{[^}]+\}/tasks/\{[^}]+\}': {
        'GET': {'response': 'ImportTask'},
        'PUT': {'request': 'ImportTask', 'response': 'ImportTask'},
        'DELETE': {'response': None},
    },
    
    # GeoWebCache endpoints
    r'/gwc/rest/layers': {
        'POST': {'request': 'TileLayer', 'response': 'TileLayer'},
        'GET': {'response': 'TileLayer'},
    },
    r'/gwc/rest/layers/\{[^}]+\}': {
        'GET': {'response': 'TileLayer'},
        'PUT': {'request': 'TileLayer', 'response': 'TileLayer'},
        'DELETE': {'response': None},
    },
    r'/gwc/rest/gridsets': {
        'POST': {'request': 'GridSet', 'response': 'GridSet'},
        'GET': {'response': 'GridSet'},
    },
    r'/gwc/rest/gridsets/\{[^}]+\}': {
        'GET': {'response': 'GridSet'},
        'PUT': {'request': 'GridSet', 'response': 'GridSet'},
        'DELETE': {'response': None},
    },
    r'/gwc/rest/blobstores': {
        'POST': {'request': 'BlobStore', 'response': 'BlobStore'},
        'GET': {'response': 'BlobStore'},
    },
    r'/gwc/rest/blobstores/\{[^}]+\}': {
        'GET': {'response': 'BlobStore'},
        'PUT': {'request': 'BlobStore', 'response': 'BlobStore'},
        'DELETE': {'response': None},
    },
}


def match_endpoint(path: str, pattern: str) -> bool:
    """Check if a path matches a pattern with regex."""
    return re.match(f"^{pattern}$", path) is not None


def find_schema_for_endpoint(path: str, method: str) -> Dict[str, Any]:
    """Find the appropriate schema for an endpoint."""
    for pattern, methods in ENDPOINT_SCHEMA_MAP.items():
        if match_endpoint(path, pattern):
            if method in methods:
                return methods[method]
    return {}


def add_request_body_schema(operation: Dict[str, Any], schema_name: str) -> None:
    """Add schema reference to request body."""
    if 'requestBody' not in operation:
        operation['requestBody'] = {
            'required': True,
            'content': {}
        }
    
    # Add JSON content type with schema reference
    if 'application/json' not in operation['requestBody'].get('content', {}):
        if 'content' not in operation['requestBody']:
            operation['requestBody']['content'] = {}
        operation['requestBody']['content']['application/json'] = {
            'schema': {
                '$ref': f'#/components/schemas/{schema_name}'
            }
        }
    
    # Add XML content type with schema reference
    if 'application/xml' not in operation['requestBody'].get('content', {}):
        operation['requestBody']['content']['application/xml'] = {
            'schema': {
                '$ref': f'#/components/schemas/{schema_name}'
            }
        }


def add_response_schema(operation: Dict[str, Any], schema_name: str) -> None:
    """Add schema reference to response."""
    if 'responses' not in operation:
        operation['responses'] = {}
    
    # Add 200 response if not present
    if '200' not in operation['responses']:
        operation['responses']['200'] = {
            'description': 'Successful operation',
            'content': {}
        }
    
    response = operation['responses']['200']
    if 'content' not in response:
        response['content'] = {}
    
    # Add JSON content type with schema reference
    if 'application/json' not in response['content']:
        response['content']['application/json'] = {
            'schema': {
                '$ref': f'#/components/schemas/{schema_name}'
            }
        }
    
    # Add XML content type with schema reference
    if 'application/xml' not in response['content']:
        response['content']['application/xml'] = {
            'schema': {
                '$ref': f'#/components/schemas/{schema_name}'
            }
        }


def process_spec(spec_path: Path) -> int:
    """Process an OpenAPI spec file and add schema references."""
    print(f"Processing {spec_path}...")
    
    # Load the spec
    with open(spec_path, 'r', encoding='utf-8') as f:
        if spec_path.suffix == '.json':
            spec = json.load(f)
        else:
            spec = yaml.safe_load(f)
    
    changes_made = 0
    
    # Process each path
    for path, path_item in spec.get('paths', {}).items():
        for method in ['get', 'post', 'put', 'patch', 'delete']:
            if method not in path_item:
                continue
            
            operation = path_item[method]
            method_upper = method.upper()
            
            # Find schema for this endpoint
            schema_info = find_schema_for_endpoint(path, method_upper)
            
            # Add request body schema
            if 'request' in schema_info and schema_info['request']:
                add_request_body_schema(operation, schema_info['request'])
                changes_made += 1
            
            # Add response schema
            if 'response' in schema_info and schema_info['response']:
                add_response_schema(operation, schema_info['response'])
                changes_made += 1
    
    # Ensure components/schemas section exists
    if 'components' not in spec:
        spec['components'] = {}
    if 'schemas' not in spec['components']:
        spec['components']['schemas'] = {}
    
    # Load schemas from common/schemas.yaml
    schemas_path = Path('.kiro/api-analysis/specs/common/schemas.yaml')
    if schemas_path.exists():
        with open(schemas_path, 'r', encoding='utf-8') as f:
            schemas = yaml.safe_load(f)
        
        # Merge schemas into spec
        spec['components']['schemas'].update(schemas)
    
    # Write back the spec
    with open(spec_path, 'w', encoding='utf-8') as f:
        if spec_path.suffix == '.json':
            json.dump(spec, f, indent=2, ensure_ascii=False)
        else:
            yaml.dump(spec, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"  Made {changes_made} changes")
    return changes_made


def main():
    """Main function."""
    print("Adding schema references to OpenAPI specifications...")
    
    # Process bundled specs
    bundled_yaml = Path('doc/en/api/geoserver-bundled.yaml')
    bundled_json = Path('doc/en/api/geoserver-bundled.json')
    
    total_changes = 0
    
    if bundled_yaml.exists():
        total_changes += process_spec(bundled_yaml)
    else:
        print(f"Warning: {bundled_yaml} not found")
    
    if bundled_json.exists():
        total_changes += process_spec(bundled_json)
    else:
        print(f"Warning: {bundled_json} not found")
    
    print(f"\nTotal changes made: {total_changes}")
    print("Schema references added successfully!")


if __name__ == '__main__':
    main()
