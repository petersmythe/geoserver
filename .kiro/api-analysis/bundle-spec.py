#!/usr/bin/env python3
"""
Bundle modular OpenAPI specifications into single-file versions.

This script resolves all $ref references from the modular GeoServer API specification
and generates self-contained bundled versions in both YAML and JSON formats.
"""

import yaml
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Set
import copy

# =============================================================================
# CONFIGURATION
# =============================================================================

# GeoServer API version to use in bundled specifications
# This should match the GeoServer version being documented
# Set to "3.0.x" for development versions, or specific version like "3.0.1" for releases
GEOSERVER_API_VERSION = "3.0.x"

# =============================================================================


class SpecBundler:
    """Bundles modular OpenAPI specifications by resolving $ref references."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.loaded_files: Dict[str, Any] = {}
        self.visited_refs: Set[str] = set()
    
    def load_yaml_file(self, file_path: Path) -> Any:
        """Load a YAML file and cache it."""
        file_key = str(file_path.resolve())
        
        if file_key in self.loaded_files:
            return self.loaded_files[file_key]
        
        if not file_path.exists():
            raise FileNotFoundError(f"Required file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.loaded_files[file_key] = data
                return data
        except Exception as e:
            raise RuntimeError(f"Error loading {file_path}: {e}") from e
    
    def resolve_ref(self, ref: str, current_file: Path) -> Any:
        """Resolve a $ref reference to its actual content."""
        if ref in self.visited_refs:
            # Circular reference detected - return a placeholder
            return {"description": f"Circular reference: {ref}"}
        
        self.visited_refs.add(ref)
        
        try:
            # Parse the reference
            if '#' in ref:
                file_part, json_path = ref.split('#', 1)
            else:
                file_part = ref
                json_path = ''
            
            # Resolve the file path
            if file_part:
                if file_part.startswith('./'):
                    file_part = file_part[2:]
                ref_file = (current_file.parent / file_part).resolve()
            else:
                ref_file = current_file
            
            # Load the referenced file (will raise exception if file not found)
            data = self.load_yaml_file(ref_file)
            
            # Navigate to the JSON path
            if json_path:
                parts = [p for p in json_path.split('/') if p]
                for part in parts:
                    if isinstance(data, dict):
                        if part not in data:
                            raise ValueError(f"Invalid reference path '{ref}': key '{part}' not found")
                        data = data.get(part)
                    else:
                        raise ValueError(f"Invalid reference path '{ref}': cannot navigate through non-dict at '{part}'")
            
            # Recursively resolve any nested $refs
            resolved = self.resolve_refs_recursive(data, ref_file)
            
            return resolved
        finally:
            self.visited_refs.discard(ref)
    
    def resolve_refs_recursive(self, obj: Any, current_file: Path) -> Any:
        """Recursively resolve all $ref references in an object."""
        if isinstance(obj, dict):
            if '$ref' in obj:
                # This is a reference - resolve it
                ref_value = obj['$ref']
                resolved = self.resolve_ref(ref_value, current_file)
                
                # Merge any additional properties from the referencing object
                if len(obj) > 1:
                    # There are additional properties besides $ref
                    result = copy.deepcopy(resolved) if isinstance(resolved, dict) else {}
                    for key, value in obj.items():
                        if key != '$ref':
                            result[key] = self.resolve_refs_recursive(value, current_file)
                    return result
                else:
                    return resolved
            else:
                # Regular dict - process all values
                return {
                    key: self.resolve_refs_recursive(value, current_file)
                    for key, value in obj.items()
                }
        elif isinstance(obj, list):
            return [self.resolve_refs_recursive(item, current_file) for item in obj]
        else:
            return obj
    
    def bundle_spec(self, entry_file: Path) -> Dict[str, Any]:
        """Bundle a modular spec into a single self-contained specification."""
        print(f"Loading entry point: {entry_file}")
        
        # Load the main spec file
        spec = self.load_yaml_file(entry_file)
        if spec is None:
            raise ValueError(f"Failed to load entry file: {entry_file}")
        
        print(f"Loaded spec with keys: {list(spec.keys())}")
        
        # Load and merge all modular files BEFORE removing x-modular-structure
        spec = self.merge_modular_files(spec, entry_file)
        
        # Remove the modular structure metadata
        if 'x-modular-structure' in spec:
            del spec['x-modular-structure']
        
        # Override version with configured GEOSERVER_API_VERSION
        if 'info' in spec and 'version' in spec['info']:
            original_version = spec['info']['version']
            spec['info']['version'] = GEOSERVER_API_VERSION
            print(f"\nOverriding version: {original_version} → {GEOSERVER_API_VERSION}")
        
        # Resolve all $ref references
        print("\nResolving $ref references...")
        bundled = self.resolve_refs_recursive(spec, entry_file)
        
        # Remove placeholder path if it exists
        if 'paths' in bundled and '/.placeholder' in bundled['paths']:
            del bundled['paths']['/.placeholder']
        
        # Ensure paths exist
        if 'paths' not in bundled or not bundled['paths']:
            bundled['paths'] = {}
            print("Warning: No paths found in bundled specification")
        
        return bundled
    
    def merge_modular_files(self, spec: Dict[str, Any], entry_file: Path) -> Dict[str, Any]:
        """Merge all modular files referenced in x-modular-structure."""
        if 'x-modular-structure' not in spec:
            print("No x-modular-structure found in spec")
            return spec
        
        print("\nMerging modular files...")
        modules = spec['x-modular-structure'].get('modules', {})
        
        # Initialize paths if not present
        if 'paths' not in spec:
            spec['paths'] = {}
        
        # Merge REST modules
        rest_modules = modules.get('rest', [])
        print(f"Found {len(rest_modules)} REST modules")
        for rest_module in rest_modules:
            file_path = rest_module.get('file', '')
            if file_path:
                self.merge_module_file(spec, entry_file, file_path)
        
        # Merge OGC modules
        ogc_modules = modules.get('ogc', [])
        print(f"Found {len(ogc_modules)} OGC modules")
        for ogc_module in ogc_modules:
            file_path = ogc_module.get('file', '')
            if file_path:
                self.merge_module_file(spec, entry_file, file_path)
        
        # Merge common modules (for components)
        common_modules = modules.get('common', [])
        print(f"Found {len(common_modules)} common modules")
        for common_module in common_modules:
            file_path = common_module.get('file', '')
            if file_path:
                self.merge_module_file(spec, entry_file, file_path)
        
        print(f"\nTotal paths after merging: {len(spec.get('paths', {}))}")
        
        return spec
    
    def merge_module_file(self, spec: Dict[str, Any], entry_file: Path, file_ref: str):
        """Merge a single module file into the main spec."""
        if file_ref.startswith('./'):
            file_ref = file_ref[2:]
        
        module_file = (entry_file.parent / file_ref).resolve()
        
        if not module_file.exists():
            print(f"Warning: Module file not found: {module_file}")
            return
        
        print(f"Merging module: {file_ref}")
        module_data = self.load_yaml_file(module_file)
        
        if not module_data:
            print(f"Warning: No data loaded from {file_ref}")
            return
        
        # Resolve all $ref references in the module data BEFORE merging
        # This ensures references are resolved relative to the module file location
        module_data = self.resolve_refs_recursive(module_data, module_file)
        
        # Merge paths
        if 'paths' in module_data:
            path_count = len(module_data['paths'])
            print(f"  - Adding {path_count} paths from {file_ref}")
            spec['paths'].update(module_data['paths'])
        
        # Merge components
        if 'components' in module_data:
            if 'components' not in spec:
                spec['components'] = {}
            
            for component_type in ['schemas', 'parameters', 'responses', 'examples', 
                                   'requestBodies', 'headers', 'securitySchemes', 
                                   'links', 'callbacks']:
                if component_type in module_data['components']:
                    if component_type not in spec['components']:
                        spec['components'][component_type] = {}
                    comp_count = len(module_data['components'][component_type])
                    if comp_count > 0:
                        print(f"  - Adding {comp_count} {component_type} from {file_ref}")
                    spec['components'][component_type].update(
                        module_data['components'][component_type]
                    )


def main():
    """Main entry point for the bundler script."""
    # Determine paths
    script_dir = Path(__file__).parent
    specs_dir = script_dir / 'specs'
    entry_file = specs_dir / 'geoserver.yaml'
    
    # Output paths
    output_yaml = Path('doc/en/api/geoserver-bundled.yaml')
    output_json = Path('doc/en/api/geoserver-bundled.json')
    
    # Ensure output directory exists
    output_yaml.parent.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("GeoServer OpenAPI Specification Bundler")
    print("=" * 70)
    print()
    
    # Create bundler and process
    bundler = SpecBundler(specs_dir)
    
    try:
        bundled_spec = bundler.bundle_spec(entry_file)
        
        # Apply validation fixes
        bundled_spec = apply_validation_fixes(bundled_spec)
        
        # Write YAML output
        print(f"\nWriting bundled YAML: {output_yaml}")
        with open(output_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(bundled_spec, f, default_flow_style=False, sort_keys=False, 
                     allow_unicode=True, width=100)
        
        # Write JSON output with pretty printing (2-space indentation)
        print(f"Writing bundled JSON: {output_json}")
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(bundled_spec, f, indent=2, ensure_ascii=False)
        
        # Validate the bundled specs
        print("\n" + "=" * 70)
        print("Validation Summary")
        print("=" * 70)
        
        # Check for remaining $ref references
        ref_count = count_refs(bundled_spec)
        if ref_count == 0:
            print("✓ No external $ref references found - specification is self-contained")
        else:
            print(f"⚠ Warning: {ref_count} $ref references still present")
        
        # Check paths
        path_count = len(bundled_spec.get('paths', {}))
        print(f"✓ Total paths: {path_count}")
        
        # Check components
        if 'components' in bundled_spec:
            for comp_type in ['schemas', 'parameters', 'responses']:
                count = len(bundled_spec['components'].get(comp_type, {}))
                print(f"✓ {comp_type.capitalize()}: {count}")
        
        print("\n" + "=" * 70)
        print("Bundling complete!")
        print("=" * 70)
        print(f"\nOutput files:")
        print(f"  - {output_yaml}")
        print(f"  - {output_json}")
        
    except Exception as e:
        print(f"\nError during bundling: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def count_refs(obj: Any, count: int = 0) -> int:
    """Count remaining $ref references in an object."""
    if isinstance(obj, dict):
        if '$ref' in obj:
            count += 1
        for value in obj.values():
            count = count_refs(value, count)
    elif isinstance(obj, list):
        for item in obj:
            count = count_refs(item, count)
    return count


def apply_validation_fixes(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply validation fixes to the bundled specification.
    
    Fixes:
    1. Duplicate operationIds - Make all operation IDs unique
    2. Path parameter mismatches - Remove parameters not in path template
    3. Malformed paths - Fix missing closing braces
    4. Nested brace issues - Fix paths like /{workspaceName/{featureTypeName}}
    """
    import re
    
    print("\nApplying validation fixes...")
    
    fixed_count = {
        'duplicate_operation_ids': 0,
        'path_param_mismatches': 0,
        'malformed_paths': 0,
        'nested_braces': 0
    }
    
    used_operation_ids = set()
    paths_to_fix = {}
    
    # First pass: identify malformed paths and collect operation IDs
    for path_name in list(spec.get('paths', {}).keys()):
        # Check for nested brace issues like /{workspaceName/{featureTypeName}}
        if re.search(r'/\{[^}]+/\{', path_name):
            # Fix by adding closing brace after first parameter
            fixed_path = re.sub(r'/\{([^}]+)/\{', r'/{\1}/{', path_name)
            if fixed_path != path_name:
                paths_to_fix[path_name] = fixed_path
                fixed_count['nested_braces'] += 1
                print(f"  Fixed nested braces: {path_name} -> {fixed_path}")
                continue
        
        # Check for malformed paths (unmatched braces)
        open_braces = path_name.count('{')
        close_braces = path_name.count('}')
        
        if open_braces != close_braces:
            # Try to fix by adding missing closing braces
            fixed_path = path_name
            missing_braces = open_braces - close_braces
            if missing_braces > 0:
                fixed_path = path_name + ('}' * missing_braces)
                paths_to_fix[path_name] = fixed_path
                fixed_count['malformed_paths'] += 1
                print(f"  Fixed malformed path: {path_name} -> {fixed_path}")
    
    # Apply path fixes
    for old_path, new_path in paths_to_fix.items():
        spec['paths'][new_path] = spec['paths'].pop(old_path)
    
    # Second pass: fix duplicate operationIds and path parameters
    for path_name, path_item in spec.get('paths', {}).items():
        # Extract valid path parameters from template
        valid_path_params = set(re.findall(r'\{([^}]+)\}', path_name))
        
        # Process each operation
        for method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
            if method not in path_item:
                continue
            
            operation = path_item[method]
            if not isinstance(operation, dict):
                continue
            
            # Fix duplicate operationId
            if 'operationId' in operation:
                original_id = operation['operationId']
                if original_id in used_operation_ids:
                    # Make unique by appending path segments
                    path_parts = [p for p in path_name.split('/') if p and not p.startswith('{')]
                    new_id = original_id
                    counter = 1
                    
                    for part in path_parts:
                        candidate = f"{original_id}_{part}"
                        if candidate not in used_operation_ids:
                            new_id = candidate
                            break
                    
                    if new_id in used_operation_ids:
                        while new_id in used_operation_ids:
                            new_id = f"{original_id}_{counter}"
                            counter += 1
                    
                    operation['operationId'] = new_id
                    fixed_count['duplicate_operation_ids'] += 1
                    used_operation_ids.add(new_id)
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
                            continue
                    
                    fixed_params.append(param)
                
                operation['parameters'] = fixed_params
    
    print(f"  ✓ Fixed {fixed_count['nested_braces']} nested brace issues")
    print(f"  ✓ Fixed {fixed_count['malformed_paths']} malformed paths")
    print(f"  ✓ Fixed {fixed_count['duplicate_operation_ids']} duplicate operationIds")
    print(f"  ✓ Fixed {fixed_count['path_param_mismatches']} path parameter mismatches")
    
    return spec


if __name__ == '__main__':
    main()
