# Version Selector Fix

## Problem
The version selector was not showing up in the deployed documentation even though `versions.json` contained multiple versions (3.0.x and 3.1.x).

## Root Cause
Material for MkDocs requires `extra.version.provider: mike` to be configured in `mkdocs.yml` to enable the version selector in the header. The configuration only had `extra.version_selector` (custom data), but not the provider setting that tells Material to render the selector.

## Solution
Added the following configuration to `mkdocs.yml` on both 3.0.x and 3.1.x branches:

```yaml
extra:
  version:
    provider: mike
  version_selector:
    # ... existing version data ...
```

## Changes Made

### Branch: 3.0.x
- Added `extra.version.provider: mike` to `mkdocs.yml`
- Created `doc/index.md` with card-based landing page
- Created `doc/en/index.md` with card-based landing page
- Added `Home: index.md` to nav
- Commit: 7089cebd3b

### Branch: 3.1.x
- Added `extra.version.provider: mike` to `mkdocs.yml`
- Landing pages already existed from previous work
- Commit: 38325642b7

## Expected Result
After GitHub Actions redeploys both versions:
1. Version selector will appear in the header next to the site title
2. Users can switch between 3.0.x and 3.1.x versions
3. Landing pages with documentation cards will be visible at:
   - `https://petersmythe.github.io/geoserver/3.0.x/`
   - `https://petersmythe.github.io/geoserver/3.0.x/en/`
   - `https://petersmythe.github.io/geoserver/3.1.x/`
   - `https://petersmythe.github.io/geoserver/3.1.x/en/`

## Verification
Wait for GitHub Actions to complete deployment (check: https://github.com/petersmythe/geoserver/actions), then visit:
- https://petersmythe.github.io/geoserver/3.1.x/en/user/styling/sld/extensions/composite-blend/syntax/

The version selector should now appear in the header.

## Reference
- [Material for MkDocs - Setting up versioning](https://squidfunk.github.io/mkdocs-material/setup/setting-up-versioning/)
- Mike integrates natively with Material for MkDocs when `provider: mike` is set
