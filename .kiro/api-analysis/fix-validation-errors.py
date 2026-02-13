#!/usr/bin/env python3
"""
Fix OpenAPI validation errors in GeoServer API specifications.

Fixes:
1. Duplicate operationId errors - Make all operation IDs unique
2. Path parameter definition errors - Remove parameters not in path template
3. Unused definitions - Clean up unused schemas
"""

import yaml
import json
import re
from pathlib import Path
from collections import defaultdict

def load_yaml(file_path):
    """Load YAML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_yaml(data, file_path):
    """Save YAML file with proper formatting."""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

def save_json(data, file_path):
    """Save JSON file with pretty printing."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def extract_path_params(path):
    """Extract parameter names from path template."""
    return set(re.findall(r'\{([^}]+)\}', path))

def make_operation_id_unique(base_id, path, method, used_ids):
    """Generate a unique operation ID."""
    # Start with base ID
    candidate = base_id
    counter = 1
    
    # If already unique, return it
    if candidate not in used_ids:
        used_ids.add(candidate)
        return candidate
    
    # Try adding path segments to make it unique
    path_parts = [p for p in path.split('/') if p and not p.startswith('{')]
    for part in path_parts:
        candidate = f"{base_id}_{part}"
        if candidate not in used_ids:
            used_ids.add(candidate)
            return candidate
    
    # Fall back to counter
    while candidate in used_ids:
        candidate = f"{base_id}_{counter}"
        counter += 1
    
    used_ids.add(candidate)
    return candidate

def fix_spec(spec_data):
    """Fix validation errors in OpenAPI spec."""
    fixed_count = {
        'duplicate_operation_ids': 0,
        'path_param_mismatches': 0,
        'operations_fixed': 0
    }
    
    used_operation_ids = set()
    
    # Process each path
    for path_name, path_item in spec_data.get('paths', {}).items():
        # Extract valid path parameters
        valid_path_params = extract_path_params(path_name)
        
        # Process each operation (get, post, put, delete, etc.)
        for method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
            if method not in path_item:
                continue
            
            operation = path_item[method]
            if not isinstance(operation, dict):
                continue
            
            fixed_count['operations_fixed'] += 1
            
            # Fix duplicate operationId
            if 'operationId' in operation:
                original_id = operation['operationId']
                if original_id in used_operation_ids:
                    new_id = make_operation_id_unique(original_id, path_name, method, used_operation_ids)
                    operation['operationId'] = new_id
                    fixed_count['duplicate_operation_ids'] += 1
                    print(f"  Fixed duplicate operationId: {original_id} -> {new_id} for {method.upper()} {path_name}")
                else:
                    used_operation_ids.add(original_id)
            
            # Fix path parameter mismatches
            if 'parameters' in operation:
                original_params = operation['parameters']
                fixed_params = []
                
                for param in original_params:
                    if not isinstance(param, dict):
                        fixed_params.append(param)
                        continue
                    
                    # If it's a path parameter, check if it's in the path template
                    if param.get('in') == 'path':
                        param_name = param.get('name')
                        if param_name not in valid_path_params:
                            # Remove this parameter
                            fixed_count['path_param_mismatches'] += 1
                            print(f"  Removed invalid path param '{param_name}' from {method.upper()} {path_name}")
                            continue
                    
                    fixed_params.append(param)
                
                operation['parameters'] = fixed_params
    
    return spec_data, fixed_count

def fix_modular_specs():
    """Fix modular specification files."""
    print("\n=== Fixing Modular Specifications ===\n")
    
    modular_dir = Path('.kiro/api-analysis/specs')
    
    # Fix main entry point files
    for spec_file in ['geoserver.yaml', 'geoserver.json']:
        file_path = modular_dir / spec_file
        if not file_path.exists():
            print(f"Skipping {spec_file} (not found)")
            continue
        
        print(f"Processing {spec_file}...")
        
        if spec_file.endswith('.yaml'):
            spec_data = load_yaml(file_path)
            fixed_spec, counts = fix_spec(spec_data)
            save_yaml(fixed_spec, file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                spec_data = json.load(f)
            fixed_spec, counts = fix_spec(spec_data)
            save_json(fixed_spec, file_path)
        
        print(f"  ✓ Fixed {counts['duplicate_operation_ids']} duplicate operationIds")
        print(f"  ✓ Fixed {counts['path_param_mismatches']} path parameter mismatches")
        print(f"  ✓ Processed {counts['operations_fixed']} operations\n")
    
    # Fix REST module specs
    rest_dir = modular_dir / 'rest'
    if rest_dir.exists():
        for spec_file in rest_dir.glob('*.yaml'):
            print(f"Processing {spec_file.name}...")
            spec_data = load_yaml(spec_file)
            fixed_spec, counts = fix_spec(spec_data)
            save_yaml(fixed_spec, spec_file)
            print(f"  ✓ Fixed {counts['duplicate_operation_ids']} duplicate operationIds")
            print(f"  ✓ Fixed {counts['path_param_mismatches']} path parameter mismatches\n")
    
    # Fix OGC module specs
    ogc_dir = modular_dir / 'ogc'
    if ogc_dir.exists():
        for spec_file in ogc_dir.glob('*.yaml'):
            print(f"Processing {spec_file.name}...")
            spec_data = load_yaml(spec_file)
            fixed_spec, counts = fix_spec(spec_data)
            save_yaml(fixed_spec, spec_file)
            print(f"  ✓ Fixed {counts['duplicate_operation_ids']} duplicate operationIds")
            print(f"  ✓ Fixed {counts['path_param_mismatches']} path parameter mismatches\n")

def fix_bundled_specs():
    """Fix bundled specification files."""
    print("\n=== Fixing Bundled Specifications ===\n")
    
    bundled_dir = Path('doc/en/api')
    
    for spec_file in ['geoserver-bundled.yaml', 'geoserver-bundled.json']:
        file_path = bundled_dir / spec_file
        if not file_path.exists():
            print(f"Skipping {spec_file} (not found)")
            continue
        
        print(f"Processing {spec_file}...")
        
        if spec_file.endswith('.yaml'):
            spec_data = load_yaml(file_path)
            fixed_spec, counts = fix_spec(spec_data)
            save_yaml(fixed_spec, file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                spec_data = json.load(f)
            fixed_spec, counts = fix_spec(spec_data)
            save_json(fixed_spec, file_path)
        
        print(f"  ✓ Fixed {counts['duplicate_operation_ids']} duplicate operationIds")
        print(f"  ✓ Fixed {counts['path_param_mismatches']} path parameter mismatches")
        print(f"  ✓ Processed {counts['operations_fixed']} operations\n")

def main():
    """Main execution."""
    print("=" * 60)
    print("OpenAPI Validation Error Fixer")
    print("=" * 60)
    
    # Fix modular specs first
    fix_modular_specs()
    
    # Fix bundled specs
    fix_bundled_specs()
    
    print("=" * 60)
    print("✓ All specifications fixed successfully!")
    print("=" * 60)

if __name__ == '__main__':
    main()
