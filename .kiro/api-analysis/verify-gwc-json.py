#!/usr/bin/env python3
import json

spec = json.load(open('doc/en/api/geoserver-bundled.json'))
gwc_paths = [p for p in spec['paths'].keys() if p.startswith('/gwc/rest')]
print(f'Total paths: {len(spec["paths"])}')
print(f'GWC paths: {len(gwc_paths)}')

gwc_tag = [t for t in spec.get('tags', []) if t.get('name') == 'REST GWC']
print(f'\nREST GWC tag present: {len(gwc_tag) > 0}')
if gwc_tag:
    print(f'Description: {gwc_tag[0].get("description")}')

# Check if basicAuth security scheme is present
if 'components' in spec and 'securitySchemes' in spec['components']:
    if 'basicAuth' in spec['components']['securitySchemes']:
        print('\nbasicAuth security scheme: Present')
    else:
        print('\nbasicAuth security scheme: Missing')
