#!/usr/bin/env python3
"""
Generate modular OpenAPI 3.0 specifications for GeoServer OGC services.

This script converts OGC service operation data into separate OpenAPI 3.0 YAML files
for each service type (WMS, WFS, WCS, WMTS, CSW, WPS).
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any


def load_ogc_operations(service_file: Path) -> Dict[str, Any]:
    """Load OGC operations from JSON file."""
    with open(service_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def map_type_to_openapi(param_type: str) -> Dict[str, Any]:
    """Map parameter type to OpenAPI schema."""
    type_mapping = {
        'string': {'type': 'string'},
        'integer': {'type': 'integer'},
        'number': {'type': 'number'},
        'boolean': {'type': 'boolean'},
        'bbox': {'type': 'string', 'description': 'Bounding box coordinates'},
        'crs': {'type': 'string', 'description': 'Coordinate Reference System'}
    }
    return type_mapping.get(param_type, {'type': 'string'})


def create_parameter_schema(param: Dict[str, Any]) -> Dict[str, Any]:
    """Create OpenAPI parameter schema from OGC parameter definition."""
    schema = {
        'name': param['name'],
        'in': 'query',
        'description': param.get('description', ''),
        'required': param.get('required', False),
        'schema': map_type_to_openapi(param.get('type', 'string'))
    }
    
    # Add default value if present
    if 'default' in param:
        schema['schema']['default'] = param['default']
    
    # Add enum values if present
    if 'allowed_values' in param:
        schema['schema']['enum'] = param['allowed_values']
    
    # Add format if present
    if 'format' in param:
        schema['schema']['format'] = param['format']
    
    return schema


def create_operation_id(service: str, version: str, operation_name: str) -> str:
    """Create version-specific operation ID."""
    # Clean version string (remove dots)
    version_clean = version.replace('.', '_')
    return f"{service}_{version_clean}_{operation_name}"


def create_operation_spec(service: str, operation: Dict[str, Any], version: str) -> Dict[str, Any]:
    """Create OpenAPI operation specification for a specific version."""
    operation_id = create_operation_id(service, version, operation['name'])
    
    # Build parameter list for this version
    parameters = []
    op_versions = operation.get('versions', [version])
    
    for param in operation.get('parameters', []):
        # Check if parameter is version-specific
        param_versions = param.get('versions', op_versions)
        if version in param_versions:
            parameters.append(create_parameter_schema(param))
    
    # Build operation object
    op_spec = {
        'operationId': operation_id,
        'summary': f"{operation['name']} - {service} {version}",
        'description': operation.get('description', ''),
        'tags': [service],
        'parameters': parameters,
        'responses': {
            '200': {
                'description': 'Successful operation',
                'content': {
                    'application/xml': {
                        'schema': {
                            'type': 'string',
                            'format': 'binary'
                        }
                    }
                }
            },
            'default': {
                'description': 'Error response',
                'content': {
                    'application/xml': {
                        'schema': {
                            '$ref': '#/components/schemas/OGCException'
                        }
                    }
                }
            }
        }
    }
    
    # Add vendor extension note if present
    if operation.get('vendor_extension'):
        op_spec['description'] += '\n\n**GeoServer Extension**: This operation is a vendor-specific extension.'
    
    # Add vendor extension parameters note
    if 'vendor_extensions' in operation:
        vendor_params = ', '.join(operation['vendor_extensions'])
        op_spec['description'] += f'\n\n**Vendor Extension Parameters**: {vendor_params}'
    
    # Add additional notes
    if 'note' in operation:
        op_spec['description'] += f'\n\n**Note**: {operation["note"]}'
    
    return op_spec


def generate_ogc_openapi_spec(service_data: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """Generate OpenAPI 3.0 specification for an OGC service."""
    service = service_data['service']
    service_title = service_data['service_title']
    description = service_data['description']
    versions = service_data['versions']
    operations = service_data['operations']
    
    # Create OpenAPI spec structure
    spec = {
        'openapi': '3.0.0',
        'info': {
            'title': f'GeoServer {service_title} API',
            'description': f'{description}\n\nSupported versions: {", ".join(versions)}',
            'version': versions[-1] if versions else '1.0.0',
            'contact': {
                'name': 'GeoServer Project',
                'url': 'https://geoserver.org'
            },
            'license': {
                'name': 'GPL 2.0',
                'url': 'https://www.gnu.org/licenses/gpl-2.0.html'
            }
        },
        'servers': [
            {
                'url': 'http://localhost:8080/geoserver',
                'description': 'Local GeoServer instance'
            },
            {
                'url': 'https://example.com/geoserver',
                'description': 'Production GeoServer instance'
            }
        ],
        'tags': [
            {
                'name': service,
                'description': service_title,
                'externalDocs': {
                    'description': f'OGC {service} Specification',
                    'url': f'https://www.ogc.org/standards/{service.lower()}'
                }
            }
        ],
        'paths': {},
        'components': {
            'schemas': {
                'OGCException': {
                    'type': 'object',
                    'description': 'OGC Service Exception',
                    'properties': {
                        'ServiceException': {
                            'type': 'object',
                            'properties': {
                                'code': {
                                    'type': 'string',
                                    'description': 'Exception code'
                                },
                                'locator': {
                                    'type': 'string',
                                    'description': 'Parameter that caused the exception'
                                },
                                'text': {
                                    'type': 'string',
                                    'description': 'Exception message'
                                }
                            }
                        }
                    }
                }
            },
            'parameters': {}
        }
    }
    
    # Add paths for each operation and version combination
    # OGC services use a single endpoint, but we document each operation separately for clarity
    for operation in operations:
        operation_name = operation['name']
        op_versions = operation.get('versions', versions)
        http_methods = operation.get('http_methods', ['GET'])
        
        # Create a path for each operation/version combination
        for version in op_versions:
            # Create a descriptive path that includes the operation name
            # This makes the API documentation clearer even though OGC services
            # actually use a single endpoint with REQUEST parameter
            path = f'/{service.lower()}'
            
            # Ensure path exists
            if path not in spec['paths']:
                spec['paths'][path] = {
                    'description': f'{service} service endpoint. Operations are distinguished by the REQUEST parameter.'
                }
            
            # Add operation for each HTTP method
            for http_method in http_methods:
                method_lower = http_method.lower()
                
                # Create operation spec
                op_spec = create_operation_spec(service, operation, version)
                
                # For documentation purposes, we create separate entries
                # In reality, OGC services multiplex operations on the same endpoint
                # We use a path parameter approach for clarity
                version_path = f'/{service.lower()}/{operation_name.lower()}/{version.replace(".", "-")}'
                
                if version_path not in spec['paths']:
                    spec['paths'][version_path] = {}
                
                spec['paths'][version_path][method_lower] = op_spec
    
    # Write YAML file
    output_file = output_dir / f'{service.lower()}.yaml'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
    
    print(f"Generated {output_file}")
    return spec


def generate_summary_report(specs: Dict[str, Dict], output_dir: Path) -> None:
    """Generate summary report of generated OGC OpenAPI specifications."""
    report_lines = [
        "# OGC OpenAPI 3.0 Specifications - Generation Summary",
        "",
        f"Generated: {Path.cwd()}",
        "",
        "## Generated Specifications",
        ""
    ]
    
    total_operations = 0
    total_versions = 0
    
    for service, spec in specs.items():
        service_info = spec['info']
        paths = spec['paths']
        
        # Count operations (excluding the base path description)
        operation_count = 0
        for path, methods in paths.items():
            if isinstance(methods, dict):
                operation_count += len([m for m in methods if m in ['get', 'post', 'put', 'delete', 'patch']])
        
        total_operations += operation_count
        
        # Extract versions from description
        desc = service_info['description']
        versions_line = [line for line in desc.split('\n') if 'Supported versions:' in line]
        versions = versions_line[0].split(': ')[1] if versions_line else 'Unknown'
        version_count = len(versions.split(', '))
        total_versions += version_count
        
        report_lines.extend([
            f"### {service_info['title']}",
            "",
            f"- **File**: `ogc/{service.lower()}.yaml`",
            f"- **Service**: {service}",
            f"- **Versions**: {versions}",
            f"- **Operations**: {operation_count}",
            f"- **Description**: {service_info['description'].split(chr(10))[0]}",
            ""
        ])
    
    report_lines.extend([
        "## Summary Statistics",
        "",
        f"- **Total Services**: {len(specs)}",
        f"- **Total Operations**: {total_operations}",
        f"- **Total Version Variants**: {total_versions}",
        "",
        "## OpenAPI 3.0 Features",
        "",
        "- Version-specific operation IDs (e.g., WMS_1_3_0_GetMap, WMS_1_1_1_GetMap)",
        "- Service type tags for organization",
        "- Complete parameter definitions with types, descriptions, and constraints",
        "- Vendor extension parameters clearly marked",
        "- CRS/EPSG parameter documentation",
        "- Error response schemas (OGCException)",
        "- Multiple server configurations (local and production)",
        "- Separate paths per operation/version for documentation clarity",
        "",
        "## Implementation Notes",
        "",
        "OGC services typically use a single endpoint (e.g., `/wms`) with the REQUEST parameter",
        "to distinguish operations. For documentation clarity, this specification uses separate",
        "paths for each operation and version combination.",
        "",
        "## Files Generated",
        ""
    ])
    
    for service in specs.keys():
        report_lines.append(f"- `.kiro/api-analysis/specs/ogc/{service.lower()}.yaml`")
    
    report_lines.append("")
    
    # Write report
    report_file = output_dir.parent / 'reports' / 'ogc-openapi-modular-summary.md'
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"\nGenerated summary report: {report_file}")


def main():
    """Main execution function."""
    # Define paths
    base_dir = Path('.kiro/api-analysis')
    ogc_dir = base_dir / 'ogc'
    output_dir = base_dir / 'specs' / 'ogc'
    
    # Service files to process
    services = ['wms', 'wfs', 'wcs', 'wmts', 'csw', 'wps']
    
    print("Generating modular OGC OpenAPI 3.0 specifications...")
    print("=" * 70)
    
    generated_specs = {}
    
    for service in services:
        service_file = ogc_dir / f'{service}-operations.json'
        
        if not service_file.exists():
            print(f"Warning: {service_file} not found, skipping...")
            continue
        
        print(f"\nProcessing {service.upper()}...")
        service_data = load_ogc_operations(service_file)
        spec = generate_ogc_openapi_spec(service_data, output_dir)
        generated_specs[service.upper()] = spec
    
    print("\n" + "=" * 70)
    print(f"Generated {len(generated_specs)} OGC OpenAPI specifications")
    
    # Generate summary report
    print("\nGenerating summary report...")
    generate_summary_report(generated_specs, output_dir)
    
    print("\n✓ OGC OpenAPI 3.0 modular specifications generation complete!")


if __name__ == '__main__':
    main()
