#!/usr/bin/env python3
"""
Carefully add schema definitions to OpenAPI specification.
This script only adds the schemas to components/schemas section without
modifying existing operations to avoid breaking parameter definitions.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any

def load_schemas() -> Dict[str, Any]:
    """Load schemas from common/schemas.yaml"""
    schemas_path = Path('.kiro/api-analysis/specs/common/schemas.yaml')
    with open(schemas_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def add_schemas_to_spec(spec_path: Path) -> None:
    """Add schemas to components section without modifying operations."""
    print(f"Processing {spec_path}...")
    
    # Load the spec
    with open(spec_path, 'r', encoding='utf-8') as f:
        if spec_path.suffix == '.json':
            spec = json.load(f)
        else:
            spec = yaml.safe_load(f)
    
    # Ensure components section exists
    if 'components' not in spec:
        spec['components'] = {}
    if 'schemas' not in spec['components']:
        spec['components']['schemas'] = {}
    
    # Load and merge schemas
    schemas = load_schemas()
    
    # Only add schemas that don't already exist
    added = 0
    for schema_name, schema_def in schemas.items():
        if schema_name not in spec['components']['schemas']:
            spec['components']['schemas'][schema_name] = schema_def
            added += 1
    
    print(f"  Added {added} schemas to components/schemas")
    
    # Write back the spec
    with open(spec_path, 'w', encoding='utf-8') as f:
        if spec_path.suffix == '.json':
            json.dump(spec, f, indent=2, ensure_ascii=False)
        else:
            yaml.dump(spec, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"  Schemas added successfully")

def main():
    """Main function."""
    print("Adding schema definitions to OpenAPI specifications...")
    print("Note: This only adds schemas to components/schemas section.")
    print("It does NOT modify existing operations to avoid breaking parameters.\n")
    
    # Process bundled specs
    bundled_yaml = Path('doc/en/api/geoserver-bundled.yaml')
    bundled_json = Path('doc/en/api/geoserver-bundled.json')
    
    if bundled_yaml.exists():
        add_schemas_to_spec(bundled_yaml)
    else:
        print(f"Warning: {bundled_yaml} not found")
    
    if bundled_json.exists():
        add_schemas_to_spec(bundled_json)
    else:
        print(f"Warning: {bundled_json} not found")
    
    print("\n✓ Schema definitions added successfully!")
    print("\nNote: Schemas are now available in components/schemas for manual reference.")
    print("To use them, manually add $ref to specific operations as needed.")

if __name__ == '__main__':
    main()
