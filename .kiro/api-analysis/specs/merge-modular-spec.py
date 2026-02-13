#!/usr/bin/env python3
"""
Merge modular OpenAPI spec files into a single working specification.

This script takes the modular spec structure (geoserver.yaml + rest/*.yaml + ogc/*.yaml)
and merges them into a single spec that can be served and validated.
"""

import yaml
import json
from pathlib import Path
from collections import OrderedDict

def load_yaml(file_path):
    """Load YAML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def merge_paths(base_spec, module_file):
    """Merge paths from a module file into the base spec."""
    module_spec = load_yaml(module_file)
    
    if 'paths' in module_spec:
        if 'paths' not in base_spec:
            base_spec['paths'] = {}
        
        # Merge paths
        for path, path_item in module_spec['paths'].items():
            if path in base_spec['paths']:
                print(f"Warning: Path {path} already exists, merging operations...")
                base_spec['paths'][path].update(path_item)
            else:
                base_spec['paths'][path] = path_item
    
    return base_spec

def main():
    """Main function to merge modular specs."""
    specs_dir = Path(__file__).parent
    
    # Load base spec
    print("Loading base spec: geoserver.yaml")
    base_spec = load_yaml(specs_dir / 'geoserver.yaml')
    
    # Remove placeholder path
    if 'paths' in base_spec and '/.placeholder' in base_spec['paths']:
        del base_spec['paths']['/.placeholder']
    
    # Get module files from x-modular-structure
    if 'x-modular-structure' in base_spec and 'modules' in base_spec['x-modular-structure']:
        modules = base_spec['x-modular-structure']['modules']
        
        # Merge REST modules
        if 'rest' in modules:
            for module_info in modules['rest']:
                module_file = specs_dir / module_info['file']
                if module_file.exists():
                    print(f"Merging: {module_info['file']}")
                    base_spec = merge_paths(base_spec, module_file)
                else:
                    print(f"Warning: Module file not found: {module_file}")
        
        # Merge OGC modules
        if 'ogc' in modules:
            for module_info in modules['ogc']:
                module_file = specs_dir / module_info['file']
                if module_file.exists():
                    print(f"Merging: {module_info['file']}")
                    base_spec = merge_paths(base_spec, module_file)
                else:
                    print(f"Warning: Module file not found: {module_file}")
    
    # Sort paths alphabetically
    if 'paths' in base_spec:
        base_spec['paths'] = dict(sorted(base_spec['paths'].items()))
    
    # Write merged spec
    output_yaml = specs_dir / 'geoserver-merged.yaml'
    output_json = specs_dir / 'geoserver-merged.json'
    
    print(f"\nWriting merged YAML spec: {output_yaml}")
    with open(output_yaml, 'w', encoding='utf-8') as f:
        yaml.dump(base_spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"Writing merged JSON spec: {output_json}")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(base_spec, f, indent=2, ensure_ascii=False)
    
    # Count paths
    path_count = len(base_spec.get('paths', {}))
    print(f"\nMerge complete! Total paths: {path_count}")
    print(f"\nYou can now serve the merged spec:")
    print(f"  npx @redocly/cli preview geoserver-merged.yaml -p 8080")

if __name__ == '__main__':
    main()
