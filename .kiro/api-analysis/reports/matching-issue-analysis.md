# REST API Matching Issue Analysis

**Date:** 2026-02-12  
**Issue:** Only 1.7% coverage detected when ~80% coverage expected

## Root Cause

The endpoint matching is failing because of a **path prefix mismatch** between documented and implemented endpoints.

### Documented Endpoints (from OpenAPI specs)
- Path format: `/workspaces/{workspace}/...`
- Example: `/workspaces/{workspace}/coveragestores/{store}/coverages`
- Missing the `/rest/` prefix

### Implemented Endpoints (from Java source)
- Path format: `/rest/workspaces/{workspaceName}/...`
- Example: `/rest/workspaces/{workspaceName}/coveragestores/{storeName}/coverages`
- Include the `/rest/` prefix

## Evidence

### Matched Endpoints (6 total)
All 6 matched endpoints are security-related and have `/rest/` in BOTH sources:
- `/rest/security/acl/catalog` (GET, PUT)
- `/rest/security/masterpw` (GET, PUT)
- `/rest/security/self/password` (GET, PUT)

### Unmatched Endpoints
- **347 implemented endpoints** with `/rest/` prefix not matching documentation
- **562 documented endpoints** without `/rest/` prefix not matching implementation

## OpenAPI Specification Context

Looking at the documented endpoints, they appear to use:
- `base_path`: `/geoserver/rest` (defined at the spec level)
- `path`: `/workspaces/...` (relative to base_path)

The full URL would be: `/geoserver/rest/workspaces/...`

However, the implemented endpoints show:
- `path`: `/rest/workspaces/...` (absolute path from application root)

## Solution Options

### Option 1: Prepend `/rest/` to Documented Paths (Recommended)
Modify the matching logic to prepend `/rest/` to all documented endpoint paths before comparison.

```python
# In match-endpoints.py
def normalize_documented_path(path: str, base_path: str = "") -> str:
    """Normalize documented endpoint paths by prepending /rest/ if needed."""
    # If base_path contains 'rest', extract the relevant portion
    if 'rest' in base_path.lower():
        # Extract from 'rest' onwards
        rest_index = base_path.lower().find('rest')
        prefix = base_path[rest_index:]
    else:
        prefix = "rest"
    
    # Ensure path starts with /rest/
    if not path.startswith('/rest/'):
        if path.startswith('/'):
            path = f"/{prefix}{path}"
        else:
            path = f"/{prefix}/{path}"
    
    return path
```

### Option 2: Strip `/rest/` from Implemented Paths
Remove `/rest/` prefix from implemented endpoints before comparison.

```python
def normalize_implemented_path(path: str) -> str:
    """Remove /rest/ prefix from implemented paths."""
    if path.startswith('/rest/'):
        return path[5:]  # Remove '/rest'
    return path
```

### Option 3: Use Base Path from OpenAPI Specs
Parse the `basePath` field from OpenAPI specs and combine with endpoint paths.

## Recommended Fix

**Option 1** is recommended because:
1. It preserves the actual implementation paths
2. It correctly interprets the OpenAPI spec structure (basePath + path)
3. It's less likely to break edge cases

## Implementation Steps

1. Update `match-endpoints.py`:
   - Add logic to extract base_path from documented endpoints
   - Prepend appropriate prefix to documented paths before matching
   
2. Re-run matching:
   ```bash
   python .kiro/api-analysis/match-endpoints.py
   ```

3. Re-run coverage calculation:
   ```bash
   python .kiro/api-analysis/calculate-coverage.py
   ```

4. Re-run gap identification:
   ```bash
   python .kiro/api-analysis/identify-gaps.py
   ```

5. Regenerate reports:
   ```bash
   python .kiro/api-analysis/generate-coverage-report.py
   ```

## Expected Outcome

After fixing the path prefix issue, coverage should increase from 1.7% to approximately 80%, with:
- ~280-300 matched endpoints (out of 353 implemented)
- ~50-70 undocumented endpoints
- ~260-280 documented-only endpoints (may need investigation)
