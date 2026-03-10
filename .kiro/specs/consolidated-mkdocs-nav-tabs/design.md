# Design Document: Consolidated MkDocs with Navigation Tabs

## Overview

This design consolidates three separate MkDocs configurations (user, developer, docguide) into a single unified configuration that uses Material for MkDocs navigation tabs for manual switching. The consolidation simplifies the build process, improves URL structure consistency, and enhances integration with mike version management.

The key architectural change is moving from three independent MkDocs builds with a custom doc_switcher component to a single MkDocs build with native Material navigation tabs. This eliminates custom code, reduces complexity, and provides a more maintainable solution.

## Architecture

### Current Architecture

```
doc/en/
├── user/
│   ├── mkdocs.yml          # Separate config
│   ├── docs/               # User manual content
│   └── target/html/        # Build output
├── developer/
│   ├── mkdocs.yml          # Separate config
│   ├── docs/               # Developer guide content
│   └── target/html/        # Build output
├── docguide/
│   ├── mkdocs.yml          # Separate config
│   ├── docs/               # Docguide content
│   └── target/html/        # Build output
└── themes/geoserver/
    ├── doc_switcher.yml    # Custom switcher config
    └── partials/
        └── header-switcher.html  # Custom switcher UI
```

Deployment: Three separate `mike deploy` commands with `--deploy-prefix` for each manual.

### Proposed Architecture

```
(workspace root)/
├── mkdocs.yml              # Single unified config (NEW location - moved from doc/en/)
├── doc/                    # docs_dir points here
│   ├── en/                 # Content directory - /en/ preserved in output!
│   │   ├── user/           # User manual content (flattened from user/docs/)
│   │   ├── developer/      # Developer guide content (flattened from developer/docs/)
│   │   ├── docguide/       # Docguide content (flattened from docguide/docs/)
│   │   └── api/            # API docs (static files, already in place)
│   └── themes/geoserver/
│       └── partials/       # Simplified theme (no doc_switcher)
└── mkdocs_output/          # Build output
    └── en/                 # /en/ preserved in output!
        ├── user/
        ├── developer/
        ├── docguide/
        └── api/

```

**Key insight**: MkDocs strips `docs_dir` from output paths but preserves directory structure WITHIN docs_dir. By setting `docs_dir: doc`, the `/en/` directory inside `doc/` is preserved in the output.

Deployment: Single `mike deploy` command from workspace root with no `--deploy-prefix`.

### Key Architectural Decisions

1. **Single Configuration**: One mkdocs.yml at workspace root builds all manuals
2. **docs_dir Setting**: `docs_dir: doc` points to doc/ directory, preserving /en/ in URLs
3. **Navigation Tabs**: Material's native tabs replace custom doc_switcher
4. **Simplified Deployment**: One mike command from workspace root deploys entire site

## Components and Interfaces

### 1. Unified MkDocs Configuration (mkdocs.yml at workspace root)

**Purpose**: Single configuration file that defines all manuals and their navigation.

**Location**: `mkdocs.yml` (at workspace root, moved from doc/en/user/)

**Key Configuration**:
```yaml
site_name: GeoServer Documentation
site_url: https://docs.geoserver.org/3.0.x/
docs_dir: doc      # Points to doc/ directory
site_dir: mkdocs_output  # Build output to mkdocs_output/

theme:
  name: material
  custom_dir: doc/themes/geoserver
  features:
    - navigation.tabs          # Enable tabs
    - navigation.tabs.sticky   # Keep tabs visible
    - navigation.top
    - navigation.tracking
    - navigation.indexes
    - navigation.path
    - search.suggest
    - search.highlight
    - content.code.copy
    - content.action.edit

nav:
  - User Manual:
      - en/user/index.md
      - Introduction:
          - en/user/introduction/index.md
          # ... rest of user manual nav
  - Developer Guide:
      - en/developer/index.md
      - en/developer/introduction.md
      # ... rest of developer guide nav
  - Documentation Guide:
      - en/docguide/index.md
      - en/docguide/background.md
      # ... rest of docguide nav
  - API Reference:
      - en/api/index.html
```

**Interface**:
- Input: Markdown files in doc/en/{manual}/ (docs_dir: doc means paths start with en/)
- Output: HTML files in mkdocs_output/en/{manual}/
- Configuration: YAML structure defining navigation hierarchy

### 2. Directory Structure Reorganization

**Purpose**: Flatten content directories so docs_dir can point to doc/.

**Migration Steps**:
```bash
# Move mkdocs.yml to workspace root
git mv doc/en/user/mkdocs.yml mkdocs.yml

# Flatten content from subdirectories
git mv doc/en/user/docs/* doc/en/user/
git mv doc/en/developer/docs/* doc/en/developer/
git mv doc/en/docguide/docs/* doc/en/docguide/

# API docs are already in correct location (doc/en/api/)
# No move needed for API docs
```

**Path Mapping**:
- Source: `doc/en/user/index.md` (via docs_dir: doc)
- Build: `mkdocs_output/en/user/index.html`
- Deployed: `{VERSION}/en/user/index.html`

**Key Insight**: MkDocs strips `docs_dir` from output paths but preserves directory structure WITHIN docs_dir. Setting `docs_dir: doc` means the `/en/` directory inside `doc/` is preserved in all output URLs.

### 3. Navigation Tabs Component

**Purpose**: Provide top-level navigation between manuals using Material's native tabs.

**Configuration**:
```yaml
theme:
  features:
    - navigation.tabs          # Top-level nav items become tabs
    - navigation.tabs.sticky   # Tabs remain visible when scrolling
```

**Behavior**:
- Top-level nav items (User Manual, Developer Guide, etc.) render as tabs
- Clicking a tab navigates to that manual's index page
- Active tab is highlighted based on current page
- Tabs are sticky and remain visible during scroll

**Interface**:
- Input: Top-level nav structure in mkdocs.yml
- Output: Horizontal tab bar in page header
- Styling: Material theme CSS with custom overrides in extra.css

### 4. Theme Simplification

**Purpose**: Remove custom doc_switcher code and rely on Material's native features.

**Files to Remove**:
- `doc/themes/geoserver/doc_switcher.yml`
- `doc/themes/geoserver/partials/header-switcher.html`

**Files to Modify**:
- `doc/themes/geoserver/partials/header.html` - Remove doc_switcher include
- `doc/version.py` - Remove doc_switcher processing logic
- `doc/themes/geoserver/stylesheets/extra.css` - Remove doc_switcher styles

**Retained Theme Elements**:
- Logo and favicon
- Color palette (light/dark mode)
- Custom CSS for GeoServer branding
- Version selector integration

### 5. Version Management Integration

**Purpose**: Ensure mike version selector works alongside navigation tabs.

**Configuration**:
```yaml
extra:
  version:
    provider: mike
  version_selector:
    - version: latest
      title: Latest (3.0)
      aliases: []
    - version: "3.0.x"
      title: "3.0.x"
      aliases: []
    # ... other versions
```

**Behavior**:
- Version selector appears in header (Material's native position)
- Switching versions preserves current manual context
- Mike manages version directories: {VERSION}/en/{manual}/

### 6. Deployment Workflow

**Purpose**: Simplify GitHub Actions workflow to deploy unified documentation.

**Current Workflow** (3 separate deploys):
```yaml
- name: Deploy User Manual
  working-directory: doc/en/user
  run: mike deploy --deploy-prefix "en/user" $VERSION --push

- name: Deploy Developer Guide
  working-directory: doc/en/developer
  run: mike deploy --deploy-prefix "en/developer" $VERSION --push

- name: Deploy Documentation Guide
  working-directory: doc/en/docguide
  run: mike deploy --deploy-prefix "en/docguide" $VERSION --push
```

**Proposed Workflow** (single deploy):
```yaml
- name: Build Documentation
  run: mkdocs build

- name: Deploy Documentation
  run: mike deploy $VERSION --push --update-aliases
```

**Interface**:
- Input: Built mkdocs_output/ directory
- Output: Deployed to gh-pages branch at {VERSION}/en/{manual}/
- Mike handles: Version directory creation, alias management, version selector

### 7. API Documentation Integration

**Purpose**: Include API documentation in the unified build.

**Approach**:
- **API docs are purely static files** - Swagger UI HTML/JS/CSS + OpenAPI YAML specifications
- **NO build step required** - these are hardcoded static resources in `doc/en/api/`
- **Already in correct location** - no move needed
- Include API Reference tab in navigation pointing to `en/api/index.html`

**Directory Contents**:
- `index.html` - Swagger UI entry point
- `swagger-ui-*.js` - Swagger UI JavaScript libraries
- `swagger-ui.css` - Swagger UI styles
- `1.0.0/*.yaml` - OpenAPI specification files (50+ YAML files)

**Integration**:
```bash
# 1. Build unified documentation from workspace root
mkdocs build

# 2. Deploy with mike from workspace root
mike deploy $VERSION --push
```

## Data Models

### MkDocs Configuration Structure

```yaml
site_name: string
site_url: string
docs_dir: string  # Path to content root
site_dir: string  # Path to build output

theme:
  name: string
  custom_dir: string
  logo: string
  favicon: string
  palette: list[PaletteConfig]
  features: list[string]

extra:
  doc_type: string  # No longer needed with tabs
  version_selector: list[VersionConfig]
  social: list[SocialLink]

plugins:
  - search
  - macros

nav: list[NavItem]  # Hierarchical navigation structure
```

### Navigation Item Structure

```yaml
NavItem:
  # Top-level items become tabs
  - Tab Name:
      - path/to/file.md
      - Section Name:
          - path/to/section/file.md
          - Subsection:
              - path/to/subsection/file.md
```

### Version Configuration

```yaml
VersionConfig:
  version: string      # Version identifier (e.g., "3.0.x")
  title: string        # Display name
  aliases: list[string]  # Alternative names
  archive: boolean     # Whether this is an archived version
  url: string          # Optional: External URL for archived versions
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Single Build Completeness

*For any* valid MkDocs configuration, building the documentation should produce output for all three manuals (user, developer, docguide) plus API documentation in the mkdocs_output/en/ directory structure.

**Validates: Requirements 1.2, 1.3**

### Property 2: URL Structure Preservation

*For any* documentation page in any manual, the generated URL should contain /en/ in the path between the version and the manual name (e.g., {VERSION}/en/user/page.html).

**Validates: Requirements 4.1, 4.2, 4.3**

### Property 3: Navigation Tab Visibility

*For any* documentation page, the rendered HTML should include navigation tabs for all four documentation types (User Manual, Developer Guide, Documentation Guide, API Reference) in the page header.

**Validates: Requirements 3.3, 3.5**

### Property 4: Mike Deployment Structure

*For any* version deployed with mike, the gh-pages branch should contain a directory structure {VERSION}/en/{manual}/ with no additional nesting or prefixes.

**Validates: Requirements 5.1, 5.2, 5.3**

### Property 5: Theme Consistency

*For any* page in any manual, the applied theme styling (colors, fonts, layout) should be identical, demonstrating consistent theme application across all manuals.

**Validates: Requirements 7.2, 7.3, 7.4**

### Property 6: Version Selector Functionality

*For any* documentation page with a version selector, clicking a different version should navigate to the same manual in the selected version (e.g., from 3.0.x/en/user/ to latest/en/user/).

**Validates: Requirements 8.3**

### Property 7: Content File Preservation

*For any* content file in the original manual directories, after reorganization the file should exist in the new location with identical content (no data loss during migration).

**Validates: Requirements 2.4**

## Error Handling

### Build Errors

**Missing Content Files**:
- Error: MkDocs reports "File not found" for nav entries
- Handling: Validate all nav paths before build, provide clear error messages
- Recovery: Update nav paths or restore missing files

**Invalid YAML Configuration**:
- Error: YAML parsing fails in mkdocs.yml
- Handling: Use YAML linter in CI/CD to catch syntax errors
- Recovery: Fix YAML syntax, validate with `mkdocs build --strict`

**Theme Customization Conflicts**:
- Error: Custom theme overrides conflict with Material theme updates
- Handling: Pin Material theme version, test theme updates in separate branch
- Recovery: Update custom theme files to match new Material structure

### Deployment Errors

**Mike Version Conflicts**:
- Error: Mike reports version already exists
- Handling: Use `--update-aliases` flag to update existing versions
- Recovery: Delete version with `mike delete` and redeploy

**GitHub Pages Deployment Failures**:
- Error: Push to gh-pages branch fails
- Handling: Check permissions, ensure gh-pages branch exists
- Recovery: Manually create gh-pages branch, configure GitHub Pages settings

**Broken Links After Migration**:
- Error: Internal links return 404 after deployment
- Handling: Use link checker in CI/CD to validate all internal links
- Recovery: Update link paths to match new structure

### Runtime Errors

**Navigation Tab JavaScript Errors**:
- Error: Tabs don't respond to clicks
- Handling: Test JavaScript functionality across browsers
- Recovery: Check Material theme version compatibility, review custom JS

**Version Selector Not Working**:
- Error: Version selector dropdown doesn't appear or doesn't navigate
- Handling: Validate mike's versions.json file, check version_selector config
- Recovery: Rebuild with mike, verify versions.json structure

## Testing Strategy

### Unit Testing

Unit tests will validate specific components and configurations:

1. **YAML Configuration Validation**
   - Test: Parse mkdocs.yml and verify structure
   - Validates: All nav paths exist, theme config is valid
   - Tool: Python YAML parser + custom validation script

2. **Path Resolution**
   - Test: Verify source paths map correctly to output paths
   - Example: en/user/index.md → mkdocs_output/en/user/index.html
   - Tool: Custom Python script

3. **Theme File Existence**
   - Test: Verify all required theme files exist
   - Validates: Logo, favicon, CSS files, partials
   - Tool: File system checks

### Integration Testing

Integration tests will validate the complete build and deployment process:

1. **Full Build Test**
   - Test: Run `mkdocs build` and verify output structure
   - Validates: mkdocs_output/en/{user,developer,docguide,api}/ directories exist
   - Validates: All expected HTML files are generated
   - Tool: Shell script + directory structure validation

2. **Mike Deployment Test**
   - Test: Deploy to test gh-pages branch with mike
   - Validates: {VERSION}/en/{manual}/ structure is correct
   - Validates: versions.json is updated correctly
   - Tool: GitHub Actions workflow in test environment

3. **Link Validation**
   - Test: Crawl generated site and check all internal links
   - Validates: No 404 errors for internal links
   - Validates: Navigation tabs link to correct pages
   - Tool: linkchecker or similar tool

4. **Cross-Manual Navigation**
   - Test: Verify navigation tabs work on pages at different nesting levels
   - Example: From user/services/wms/index.html, tabs should navigate correctly
   - Tool: Selenium or Playwright for browser automation

### Manual Testing

Manual testing will validate user experience and visual aspects:

1. **Visual Inspection**
   - Test: Review navigation tabs appearance and behavior
   - Validates: Tabs are visible, styled correctly, highlight active tab
   - Validates: Responsive design works on mobile/tablet

2. **Version Switching**
   - Test: Switch between versions and verify manual context is preserved
   - Example: From 3.0.x/en/user/ to latest/en/user/
   - Validates: Version selector works alongside navigation tabs

3. **Search Functionality**
   - Test: Search across all manuals and verify results
   - Validates: Search index includes all manuals
   - Validates: Search results link to correct pages

4. **Backward Compatibility**
   - Test: Access old bookmarked URLs and verify they still work
   - Example: 3.0.x/en/user/services/wms/index.html
   - Validates: URL structure is preserved

### Testing Configuration

**Property-Based Testing**: Not applicable for this feature (primarily configuration and build process changes).

**Test Execution**:
- Unit tests: Run in CI/CD on every commit
- Integration tests: Run in CI/CD before deployment
- Manual tests: Perform before major releases

**Test Environment**:
- Local: Developer machines with Python 3.x, MkDocs, mike
- CI/CD: GitHub Actions with Ubuntu 22.04
- Staging: Test deployment to separate GitHub Pages site

## Migration Plan

### Phase 1: Preparation

1. Verify current directory structure:
   ```bash
   ls -la doc/en/{user,developer,docguide,api}
   ```

2. Flatten content directories:
   ```bash
   git mv doc/en/user/docs/* doc/en/user/
   git mv doc/en/developer/docs/* doc/en/developer/
   git mv doc/en/docguide/docs/* doc/en/docguide/
   rmdir doc/en/user/docs doc/en/developer/docs doc/en/docguide/docs
   ```

3. Move mkdocs.yml to workspace root:
   ```bash
   git mv doc/en/user/mkdocs.yml mkdocs.yml
   ```

### Phase 2: Configuration

1. Update mkdocs.yml:
   - Set `docs_dir: doc`
   - Set `site_dir: site`
   - Update `custom_dir: doc/themes/geoserver`
   - Merge navigation structures from three mkdocs.yml files
   - Prefix all nav paths with `en/` (e.g., `en/user/index.md`)
   - Configure navigation tabs feature
   - Update theme configuration

2. Remove doc_switcher references from doc/version.py

### Phase 3: Testing

1. Build locally and verify output structure:
   ```bash
   mkdocs build
   ls -la mkdocs_output/en/{user,developer,docguide,api}
   ```

2. Test navigation tabs functionality
3. Validate all internal links
4. Test with mike in local gh-pages branch

### Phase 4: Deployment

1. Update GitHub Actions workflow
2. Deploy to test environment
3. Validate deployed site
4. Deploy to production

### Phase 5: Cleanup

1. Remove old mkdocs.yml files from manual directories
2. Remove doc_switcher.yml and related theme files
3. Update documentation for contributors
4. Archive old deployment workflow

## Rollback Plan

If issues are discovered after deployment:

1. **Immediate**: Revert GitHub Actions workflow to previous version
2. **Short-term**: Redeploy previous version using old workflow
3. **Long-term**: Fix issues in consolidated configuration and redeploy

The old manual directories and configurations will be retained in git history for easy rollback.
