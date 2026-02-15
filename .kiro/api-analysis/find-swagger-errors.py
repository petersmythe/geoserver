#!/usr/bin/env python3
"""Find Swagger UI validation errors in the bundled spec."""

import yaml
import re
from collections import defaultdict
import os

# Load spec - handle both running from root and from .kiro/api-analysis
spec_path = '../../doc/en/api/geoserver-bundled.yaml'
if not os.path.exists(spec_path):
    spec_path = 'doc/en/api/geoserver-bundled.yaml'

with open(spec_path, 'r') as f:
    spec = yaml.safe_load(f)

print("=" * 70)
print("Swagger UI Validation Error Analysis")
print("=" * 70)

# Error 1: Path template expressions not matched with Parameter Objects
print("\n1. Path Template Parameter Mismatches")
print("-" * 70)
mismatch_count = 0
for path, path_item in spec.get('paths', {}).items():
    # Extract parameters from path template
    template_params = set(re.findall(r'\{([^}]+)\}', path))
    
    for method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
        if method not in path_item:
            continue
        
        operation = path_item[method]
        if not isinstance(operation, dict):
            continue
        
        # Extract path parameters from operation
        path_params = set()
        for param in operation.get('parameters', []):
            if isinstance(param, dict) and param.get('in') == 'path':
                path_params.add(param['name'])
        
        # Check for mismatches
        missing_in_params = template_params - path_params
        extra_in_params = path_params - template_params
        
        if missing_in_params or extra_in_params:
            mismatch_count += 1
            print(f"\n{method.upper()} {path}")
            if missing_in_params:
                print(f"  Missing in parameters: {missing_in_params}")
            if extra_in_params:
                print(f"  Extra in parameters: {extra_in_params}")
            if mismatch_count >= 10:
                print(f"\n... and more (showing first 10)")
                break
    if mismatch_count >= 10:
        break

print(f"\nTotal path template mismatches: {mismatch_count}")

# Error 2: Duplicate parameter names
print("\n\n2. Duplicate Parameter Names")
print("-" * 70)
dup_count = 0
for path, path_item in spec.get('paths', {}).items():
    for method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
        if method not in path_item:
            continue
        
        operation = path_item[method]
        if not isinstance(operation, dict):
            continue
        
        # Check for duplicate parameter names
        param_names = []
        for param in operation.get('parameters', []):
            if isinstance(param, dict):
                param_names.append(param.get('name'))
        
        # Find duplicates
        seen = set()
        duplicates = set()
        for name in param_names:
            if name in seen:
                duplicates.add(name)
            seen.add(name)
        
        if duplicates:
            dup_count += 1
            print(f"\n{method.upper()} {path}")
            print(f"  Duplicate parameters: {duplicates}")
            if dup_count >= 10:
                print(f"\n... and more (showing first 10)")
                break
    if dup_count >= 10:
        break

print(f"\nTotal operations with duplicate parameters: {dup_count}")

# Error 3: Unused definitions
print("\n\n3. Unused Definitions")
print("-" * 70)

# Collect all $ref references and security scheme usages in the spec
refs_used = set()
security_schemes_used = set()

def find_refs(obj, refs):
    """Recursively find all $ref references."""
    if isinstance(obj, dict):
        if '$ref' in obj:
            refs.add(obj['$ref'])
        for value in obj.values():
            find_refs(value, refs)
    elif isinstance(obj, list):
        for item in obj:
            find_refs(item, refs)

def find_security_schemes(obj):
    """Find all security scheme usages."""
    # Check global security
    if isinstance(obj, dict) and 'security' in obj:
        for sec_req in obj['security']:
            if isinstance(sec_req, dict):
                for scheme_name in sec_req.keys():
                    security_schemes_used.add(scheme_name)
    
    # Check operation-level security
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == 'security' and isinstance(value, list):
                for sec_req in value:
                    if isinstance(sec_req, dict):
                        for scheme_name in sec_req.keys():
                            security_schemes_used.add(scheme_name)
            elif isinstance(value, (dict, list)):
                find_security_schemes(value)
    elif isinstance(obj, list):
        for item in obj:
            find_security_schemes(item)

find_refs(spec, refs_used)
find_security_schemes(spec)

# Check components for unused definitions
components = spec.get('components', {})
unused = []

for comp_type in ['schemas', 'parameters', 'responses', 'examples', 'requestBodies', 'headers', 'securitySchemes']:
    if comp_type not in components:
        continue
    
    for name in components[comp_type].keys():
        # For securitySchemes, check if used in security declarations
        if comp_type == 'securitySchemes':
            if name not in security_schemes_used:
                unused.append((comp_type, name))
        else:
            ref = f"#/components/{comp_type}/{name}"
            if ref not in refs_used:
                unused.append((comp_type, name))

print(f"Total unused definitions: {len(unused)}")
if unused:
    print("\nUnused definitions:")
    for comp_type, name in unused[:20]:
        print(f"  {comp_type}/{name}")
    if len(unused) > 20:
        print(f"  ... and {len(unused) - 20} more")

print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print(f"Path template mismatches: {mismatch_count}")
print(f"Duplicate parameter names: {dup_count}")
print(f"Unused definitions: {len(unused)}")
print(f"Total issues: {mismatch_count + dup_count + len(unused)}")
