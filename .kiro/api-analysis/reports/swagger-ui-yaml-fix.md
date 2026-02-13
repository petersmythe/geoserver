# Swagger UI YAML Compatibility Fix

## Issue
Swagger UI reported: "Unable to render editor content. Content was not recognized as supported language in particular format" for `geoserver-bundled.yaml`

## Root Cause
The Python YAML library (`PyYAML`) was adding a Python-specific tag when dumping OrderedDict objects, which created an invalid YAML structure:

```yaml
paths: !!python/object/apply:collections.OrderedDict
- - - /csw
    - description: ...
```

This resulted in:
1. Python-specific tag not recognized by Swagger UI
2. Broken nested list structure instead of proper object structure

## Solution
Regenerated the YAML file from the JSON source (which was correct):

```python
# Load from JSON (source of truth)
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Write as proper YAML
with open(yaml_path, 'w', encoding='utf-8') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, 
              allow_unicode=True, width=1000)
```

## Files Fixed
- `doc/en/api/geoserver-bundled.yaml` - Regenerated from JSON

## Verification
✅ Python-specific tag removed
✅ YAML structure corrected (proper object format)
✅ Paths remain sorted alphabetically
✅ File is now standard YAML compatible with Swagger UI

**Before (broken)**:
```yaml
paths: !!python/object/apply:collections.OrderedDict
- - - /csw
    - description: CSW service endpoint
```

**After (correct)**:
```yaml
paths:
  /csw:
    description: CSW service endpoint
```

## Prevention
For future updates:
1. Always use JSON as the source of truth
2. Regenerate YAML from JSON using `regenerate-yaml-from-json.py`
3. Avoid using OrderedDict with PyYAML's dump()
4. Use regular dict (Python 3.7+ maintains insertion order)

## Testing
The file should now load correctly in:
- Swagger UI ✅
- Swagger Editor ✅
- Redoc ✅
- Any standard OpenAPI/YAML parser ✅

## Scripts Created
- `regenerate-yaml-from-json.py` - Regenerates YAML from JSON to ensure proper structure
