#!/usr/bin/env python3
"""
Fix tag naming and organization in OpenAPI specifications.

Task 15.5:
- Capitalize "Gwc" to "GWC" in all tags and headings
- Restructure OGC service tags to include version (e.g., "WMS 1.3.0", "WMS 1.1.0", "WFS 2.0.0")
- Order service versions from highest to lowest (2.0.0 before 1.0.0)
- Prefix REST tags with "REST" (e.g., "REST", "REST Extensions", "REST Community", "REST GWC")
- Reorder tags: REST, REST Extensions, REST Community, REST GWC, then OGC services
- Apply fixes to both modular and bundled specs (YAML and JSON)
"""

import json
import yaml
import re
from pathlib import Path
from collections import OrderedDict

# Tag name mappings
TAG_MAPPINGS = {
    'Core': 'REST',
    'GeoWebCache': 'REST GWC',
    'Security': 'REST Security',
    'Extensions': 'REST Extensions',
    'Community': 'REST Community',
}

# OGC service version patterns to extract
OGC_VERSION_PATTERN = re.compile(r'(WMS|WFS|WCS|WMTS|CSW|WPS)_(\d+)_(\d+)(?:_(\d+))?_')

def parse_version(version_str):
    """Parse version string into tuple for sorting."""
    parts = version_str.split('.')
    return tuple(int(p) for p in parts)

def extract_versions_from_operations(spec_data):
    """Extract unique versions for each OGC service from operation IDs."""
    service_versions = {}
    
    if 'paths' not in spec_data:
        return service_versions
    
    for path, path_item in spec_data['paths'].items():
        for method, operation in path_item.items():
            if method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                operation_id = operation.get('operationId', '')
                match = OGC_VERSION_PATTERN.match(operation_id)
                if match:
                    service = match.group(1)
                    major = match.group(2)
                    minor = match.group(3)
                    patch = match.group(4) or '0'
                    version = f"{major}.{minor}.{patch}"
                    
                    if service not in service_versions:
                        service_versions[service] = set()
                    service_versions[service].add(version)
    
    return service_versions

def create_new_tags(service_versions):
    """Create new tag list with proper ordering and naming."""
    tags = []
    
    # REST tags first (in order)
    rest_tags = [
        {
            'name': 'REST',
            'description': 'Core REST API endpoints for server management and configuration'
        },
        {
            'name': 'REST Extensions',
            'description': 'REST API endpoints from extension modules'
        },
        {
            'name': 'REST Community',
            'description': 'REST API endpoints from community modules'
        },
        {
            'name': 'REST GWC',
            'description': 'REST API endpoints for GeoWebCache tile caching'
        },
        {
            'name': 'REST Security',
            'description': 'REST API endpoints for security and authentication management'
        }
    ]
    tags.extend(rest_tags)
    
    # OGC service tags with versions (sorted by service, then version descending)
    ogc_services = {
        'WMS': {
            'description': 'Web Map Service - OGC standard for rendering maps',
            'url': 'https://www.ogc.org/standards/wms'
        },
        'WFS': {
            'description': 'Web Feature Service - OGC standard for vector data access',
            'url': 'https://www.ogc.org/standards/wfs'
        },
        'WCS': {
            'description': 'Web Coverage Service - OGC standard for raster data access',
            'url': 'https://www.ogc.org/standards/wcs'
        },
        'WMTS': {
            'description': 'Web Map Tile Service - OGC standard for tiled map serving',
            'url': 'https://www.ogc.org/standards/wmts'
        },
        'CSW': {
            'description': 'Catalog Service for the Web - OGC standard for metadata catalogs',
            'url': 'https://www.ogc.org/standards/cat'
        },
        'WPS': {
            'description': 'Web Processing Service - OGC standard for geospatial processing',
            'url': 'https://www.ogc.org/standards/wps'
        }
    }
    
    for service in ['WMS', 'WFS', 'WCS', 'WMTS', 'CSW', 'WPS']:
        if service in service_versions and service_versions[service]:
            # Sort versions descending (highest first)
            versions = sorted(service_versions[service], key=parse_version, reverse=True)
            for version in versions:
                tag_name = f"{service} {version}"
                tag = {
                    'name': tag_name,
                    'description': f"{ogc_services[service]['description']} (version {version})",
                    'externalDocs': {
                        'description': f'OGC {service} Specification',
                        'url': ogc_services[service]['url']
                    }
                }
                tags.append(tag)
        else:
            # No versions found, add generic tag
            tag = {
                'name': service,
                'description': ogc_services[service]['description'],
                'externalDocs': {
                    'description': f'OGC {service} Specification',
                    'url': ogc_services[service]['url']
                }
            }
            tags.append(tag)
    
    return tags

def update_operation_tags(spec_data):
    """Update tags in all operations to match new naming."""
    if 'paths' not in spec_data:
        return
    
    for path, path_item in spec_data['paths'].items():
        for method, operation in path_item.items():
            if method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                if 'tags' in operation:
                    new_tags = []
                    for tag in operation['tags']:
                        # Map old REST tag names to new ones
                        if tag in TAG_MAPPINGS:
                            new_tags.append(TAG_MAPPINGS[tag])
                        # Handle OGC service tags - extract version from operationId
                        elif tag in ['WMS', 'WFS', 'WCS', 'WMTS', 'CSW', 'WPS']:
                            operation_id = operation.get('operationId', '')
                            match = OGC_VERSION_PATTERN.match(operation_id)
                            if match:
                                service = match.group(1)
                                major = match.group(2)
                                minor = match.group(3)
                                patch = match.group(4) or '0'
                                version = f"{major}.{minor}.{patch}"
                                new_tags.append(f"{service} {version}")
                            else:
                                # Keep original if no version found
                                new_tags.append(tag)
                        else:
                            new_tags.append(tag)
                    operation['tags'] = new_tags

def fix_yaml_spec(input_path, output_path):
    """Fix tag naming in YAML spec."""
    print(f"Processing YAML: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        spec_data = yaml.safe_load(f)
    
    # Extract versions from operations
    service_versions = extract_versions_from_operations(spec_data)
    print(f"  Found service versions: {service_versions}")
    
    # Create new tags
    new_tags = create_new_tags(service_versions)
    spec_data['tags'] = new_tags
    print(f"  Created {len(new_tags)} tags")
    
    # Update operation tags
    update_operation_tags(spec_data)
    print(f"  Updated operation tags")
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(spec_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"  Written to: {output_path}")

def fix_json_spec(input_path, output_path):
    """Fix tag naming in JSON spec."""
    print(f"Processing JSON: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        spec_data = json.load(f)
    
    # Extract versions from operations
    service_versions = extract_versions_from_operations(spec_data)
    print(f"  Found service versions: {service_versions}")
    
    # Create new tags
    new_tags = create_new_tags(service_versions)
    spec_data['tags'] = new_tags
    print(f"  Created {len(new_tags)} tags")
    
    # Update operation tags
    update_operation_tags(spec_data)
    print(f"  Updated operation tags")
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(spec_data, f, indent=2)
    
    print(f"  Written to: {output_path}")

def main():
    """Main execution."""
    base_dir = Path(__file__).parent
    
    # Fix modular specs
    print("\n=== Fixing Modular Specifications ===")
    modular_yaml = base_dir / 'specs' / 'geoserver.yaml'
    modular_json = base_dir / 'specs' / 'geoserver.json'
    
    if modular_yaml.exists():
        fix_yaml_spec(modular_yaml, modular_yaml)
    else:
        print(f"Warning: {modular_yaml} not found")
    
    if modular_json.exists():
        fix_json_spec(modular_json, modular_json)
    else:
        print(f"Warning: {modular_json} not found")
    
    # Fix bundled specs
    print("\n=== Fixing Bundled Specifications ===")
    bundled_yaml = base_dir.parent.parent / 'doc' / 'en' / 'api' / 'geoserver-bundled.yaml'
    bundled_json = base_dir.parent.parent / 'doc' / 'en' / 'api' / 'geoserver-bundled.json'
    
    if bundled_yaml.exists():
        fix_yaml_spec(bundled_yaml, bundled_yaml)
    else:
        print(f"Warning: {bundled_yaml} not found")
    
    if bundled_json.exists():
        fix_json_spec(bundled_json, bundled_json)
    else:
        print(f"Warning: {bundled_json} not found")
    
    print("\n=== Tag Naming Fix Complete ===")

if __name__ == '__main__':
    main()
