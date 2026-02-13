import yaml

spec = yaml.safe_load(open('doc/en/api/geoserver-bundled.yaml'))

print('Validation checks:')
print(f'1. Malformed paths (unmatched braces): {len([p for p in spec.get("paths", {}).keys() if p.count("{") != p.count("}")])}')
print(f'2. Paths not starting with /: {len([p for p in spec.get("paths", {}).keys() if not p.startswith("/")])}')
print(f'3. Nested brace issues: {len([p for p in spec.get("paths", {}).keys() if "/{workspaceName/{" in p or "/{storeName/{" in p])}')
print(f'4. Total paths: {len(spec.get("paths", {}))}')

# Show nested brace issues
nested = [p for p in spec.get("paths", {}).keys() if "/{workspaceName/{" in p or "/{storeName/{" in p]
if nested:
    print(f'\nNested brace issues found:')
    for p in nested:
        print(f'  {p}')
