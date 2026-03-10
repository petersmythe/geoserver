# MkDocs Configuration Solution for GeoServer

## Problem Statement

GeoServer documentation needs to:
1. Consolidate 3 separate MkDocs configurations into one
2. Use Material navigation tabs instead of custom doc_switcher
3. Preserve `/en/` in output URLs: `{VERSION}/en/{manual}/`
4. Minimize changes to existing directory structure

## Key Discovery

**MkDocs strips `docs_dir` from output paths but preserves directory structure WITHIN docs_dir.**

This means:
- `docs_dir: en` → strips `/en/` from output ❌
- `docs_dir: doc` with content at `doc/en/` → preserves `/en/` in output ✅

## Final Solution

### Directory Structure
```
(workspace root)/
├── mkdocs.yml              # Moved from doc/en/user/mkdocs.yml
├── doc/                    # docs_dir points here
│   ├── en/                 # /en/ preserved in output!
│   │   ├── user/           # Flattened from user/docs/
│   │   ├── developer/      # Flattened from developer/docs/
│   │   ├── docguide/       # Flattened from docguide/docs/
│   │   └── api/            # Already in place (static files)
│   └── themes/geoserver/
└── site/                   # Build output
    └── en/                 # /en/ preserved!
        ├── user/
        ├── developer/
        ├── docguide/
        └── api/
```

### Configuration (mkdocs.yml at workspace root)
```yaml
site_name: GeoServer Documentation
docs_dir: doc               # Points to doc/ directory
site_dir: site              # Output to site/

theme:
  name: material
  custom_dir: doc/themes/geoserver
  features:
    - navigation.tabs
    - navigation.tabs.sticky

nav:
  - User Manual:
      - en/user/index.md
  - Developer Guide:
      - en/developer/index.md
  - Documentation Guide:
      - en/docguide/index.md
  - API Reference:
      - en/api/index.html
```

### Migration Steps
```bash
# 1. Flatten content directories
git mv doc/en/user/docs/* doc/en/user/
git mv doc/en/developer/docs/* doc/en/developer/
git mv doc/en/docguide/docs/* doc/en/docguide/
rmdir doc/en/user/docs doc/en/developer/docs doc/en/docguide/docs

# 2. Move mkdocs.yml to workspace root
git mv doc/en/user/mkdocs.yml mkdocs.yml

# 3. Update mkdocs.yml
# - Set docs_dir: doc
# - Set site_dir: site
# - Update custom_dir: doc/themes/geoserver
# - Prefix all nav paths with en/ (e.g., en/user/index.md)
```

### Build & Deploy
```bash
# Build from workspace root
mkdocs build

# Deploy with mike from workspace root
mike deploy $VERSION --push
```

### Result
- URLs: `{VERSION}/en/{manual}/` ✅
- Single unified configuration ✅
- Minimal directory changes ✅
- Navigation tabs instead of doc_switcher ✅

## Benefits

1. **Preserves /en/ in URLs**: Backward compatible with existing bookmarks
2. **Minimal changes**: Content stays in place, just flatten docs/ subdirectories
3. **Single configuration**: One mkdocs.yml instead of three
4. **Native features**: Material tabs instead of custom doc_switcher
5. **Simplified deployment**: One mike command instead of three

## Test Verification

Tested with `test_mkdocs_structure4/`:
- Input: `doc/en/user/index.md`
- Output: `site/en/user/index.html` ✅
- Confirmed: `/en/` is preserved in output structure
