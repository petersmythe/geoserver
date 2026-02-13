#!/usr/bin/env python3
"""
Add authkey query string authentication scheme to the bundled OpenAPI spec.

GeoServer supports authentication via an 'authkey' query parameter through
the authkey extension module.
"""

import json
import yaml

def add_authkey_security(spec):
    """Add authkey security scheme to the spec."""
    
    # Add authkey to securitySchemes
    if 'components' not in spec:
        spec['components'] = {}
    
    if 'securitySchemes' not in spec['components']:
        spec['components']['securitySchemes'] = {}
    
    # Add authkey security scheme
    spec['components']['securitySchemes']['authkey'] = {
        "type": "apiKey",
        "in": "query",
        "name": "authkey",
        "description": "Authentication via authkey query parameter (requires authkey extension)"
    }
    
    print("Added authkey security scheme to components.securitySchemes")
    
    # Add authkey to global security array
    if 'security' not in spec:
        spec['security'] = []
    
    # Check if authkey already exists in security
    authkey_exists = any('authkey' in sec for sec in spec['security'])
    
    if not authkey_exists:
        spec['security'].append({"authkey": []})
        print("Added authkey to global security array")
    
    return spec

def main():
    """Main function."""
    bundled_json = 'doc/en/api/geoserver-bundled.json'
    bundled_yaml = 'doc/en/api/geoserver-bundled.yaml'
    
    print("Loading bundled JSON spec...")
    with open(bundled_json, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    
    print("\nAdding authkey security scheme...")
    spec = add_authkey_security(spec)
    
    print("\nWriting updated JSON spec...")
    with open(bundled_json, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    
    print("Regenerating YAML from JSON...")
    with open(bundled_yaml, 'w', encoding='utf-8') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("\n✓ Authkey security scheme added successfully!")
    print("\nSecurity schemes now available:")
    print("  - basicAuth (HTTP Basic)")
    print("  - digestAuth (HTTP Digest)")
    print("  - authkey (API Key via query parameter)")

if __name__ == '__main__':
    main()
