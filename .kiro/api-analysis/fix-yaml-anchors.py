#!/usr/bin/env python3
"""
Fix YAML anchor/alias issues by converting JSON to YAML properly.
This ensures no YAML anchors (*id001) are created which cause validation errors.
"""

import json
import yaml
from pathlib import Path

class NoAliasDumper(yaml.SafeDumper):
    """Custom YAML dumper that doesn't use anchors/aliases."""
    def ignore_aliases(self, data):
        return True

def fix_yaml_file():
    """Convert JSON to YAML without anchors."""
    print("Fixing YAML file by converting from JSON...")
    
    # Load the JSON version (which is correct)
    json_path = Path('doc/en/api/geoserver-bundled.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    
    # Write YAML without anchors
    yaml_path = Path('doc/en/api/geoserver-bundled.yaml')
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(spec, f, Dumper=NoAliasDumper, default_flow_style=False, 
                  allow_unicode=True, sort_keys=False, width=120)
    
    print("✓ YAML file regenerated without anchors")
    print("✓ Validation errors should be resolved")

if __name__ == '__main__':
    fix_yaml_file()
