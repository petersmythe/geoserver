#!/usr/bin/env python3
"""
Validate both YAML and JSON versions of the bundled spec
"""

import sys
from pathlib import Path

# Import the validator from the main script
sys.path.insert(0, str(Path(__file__).parent))
from validate_spec import OpenAPIValidator

def main():
    yaml_spec = Path("doc/en/api/geoserver-bundled.yaml")
    json_spec = Path("doc/en/api/geoserver-bundled.json")
    
    print("="*70)
    print("Validating Both Spec Formats")
    print("="*70)
    
    # Validate YAML
    print("\n1. Validating YAML format...")
    yaml_validator = OpenAPIValidator(yaml_spec)
    yaml_valid = yaml_validator.validate()
    
    if yaml_valid:
        print("   ✅ YAML format is valid")
    else:
        print(f"   ❌ YAML format has {len(yaml_validator.errors)} error(s)")
    
    # Validate JSON
    print("\n2. Validating JSON format...")
    json_validator = OpenAPIValidator(json_spec)
    json_valid = json_validator.validate()
    
    if json_valid:
        print("   ✅ JSON format is valid")
    else:
        print(f"   ❌ JSON format has {len(json_validator.errors)} error(s)")
    
    # Summary
    print("\n" + "="*70)
    if yaml_valid and json_valid:
        print("✅ Both formats are valid!")
        return 0
    else:
        print("❌ One or more formats have validation errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())
