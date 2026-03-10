# Implementation Plan: Consolidated MkDocs with Navigation Tabs

## Overview

This implementation plan converts the GeoServer documentation from three separate MkDocs configurations to a single unified configuration with Material for MkDocs navigation tabs. The work is organized into discrete phases: directory reorganization, configuration creation, theme simplification, deployment workflow updates, and validation.

**Key architectural change**: Move mkdocs.yml to workspace root with `docs_dir: doc`. This preserves the `/en/` path in output URLs (since MkDocs strips `docs_dir` but preserves structure within it) while requiring minimal changes to the existing directory structure.

## Tasks

- [x] 0. CRITICAL: Verify docs_dir behavior with test build
  - **COMPLETED**: Test confirmed that `docs_dir: doc` with content at `doc/en/` preserves `/en/` in output
  - **Result**: `site/en/user/`, `site/en/developer/` structure confirmed ✅
  - **Solution**: Move mkdocs.yml to workspace root with `docs_dir: doc`
  - _Requirements: ALL - this validates the core assumption_

- [ ] 1. Reorganize directory structure
  - [ ] 1.1 Flatten user manual content
    - Move doc/en/user/docs/* to doc/en/user/
    - Use `git mv` to preserve history
    - Remove empty docs/ directory
    - _Requirements: 2.3, 2.4_
  
  - [ ] 1.2 Flatten developer guide content
    - Move doc/en/developer/docs/* to doc/en/developer/
    - Use `git mv` to preserve history
    - Remove empty docs/ directory
    - _Requirements: 2.3, 2.4_
  
  - [ ] 1.3 Flatten documentation guide content
    - Move doc/en/docguide/docs/* to doc/en/docguide/
    - Use `git mv` to preserve history
    - Remove empty docs/ directory
    - _Requirements: 2.3, 2.4_
  
  - [ ] 1.4 Verify API documentation location
    - API docs should already be at doc/en/api/
    - API docs are static files (Swagger UI + OpenAPI YAML specs)
    - No move needed - already in correct location
    - _Requirements: 2.3, 2.4_
  
  - [ ] 1.5 Move mkdocs.yml to workspace root
    - Move doc/en/user/mkdocs.yml to workspace root (mkdocs.yml)
    - Use `git mv` to preserve history
    - This will be the unified configuration file
    - _Requirements: 1.1, 2.1_

- [ ] 2. Create unified MkDocs configuration
  - [ ] 2.1 Update mkdocs.yml with basic structure
    - Set docs_dir to "doc" (points to doc/ directory)
    - Set site_dir to "site" (build output to site/)
    - Update site_name and site_url
    - Update custom_dir to "doc/themes/geoserver"
    - _Requirements: 1.1, 2.1_
  
  - [ ] 2.2 Configure navigation tabs feature
    - Enable navigation.tabs in theme features
    - Enable navigation.tabs.sticky in theme features
    - Preserve other existing features (navigation.top, search, etc.)
    - _Requirements: 3.1, 3.2_
  
  - [ ] 2.3 Merge user manual navigation structure
    - Copy nav structure from doc/en/user/mkdocs.yml
    - Prefix all paths with en/user/ (e.g., en/user/index.md)
    - Create top-level "User Manual" section
    - _Requirements: 1.2, 3.4_
  
  - [ ] 2.4 Merge developer guide navigation structure
    - Copy nav structure from doc/en/developer/mkdocs.yml
    - Prefix all paths with en/developer/ (e.g., en/developer/index.md)
    - Create top-level "Developer Guide" section
    - _Requirements: 1.2, 3.4_
  
  - [ ] 2.5 Merge documentation guide navigation structure
    - Copy nav structure from doc/en/docguide/mkdocs.yml
    - Prefix all paths with en/docguide/ (e.g., en/docguide/index.md)
    - Create top-level "Documentation Guide" section
    - _Requirements: 1.2, 3.4_
  
  - [ ] 2.6 Add API Reference navigation entry
    - Create top-level "API Reference" section
    - Point to en/api/index.html
    - _Requirements: 3.4, 3.5_
  
  - [ ] 2.7 Consolidate theme configuration
    - Merge palette settings from all three configs
    - Merge extra configuration (version_selector, social links)
    - Merge plugins configuration
    - Merge markdown_extensions configuration
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 4. Simplify theme by removing doc_switcher
  - [ ] 4.1 Remove doc_switcher configuration file
    - Delete doc/themes/geoserver/doc_switcher.yml
    - _Requirements: 6.2_
  
  - [ ] 4.2 Remove doc_switcher template files
    - Delete doc/themes/geoserver/partials/header-switcher.html
    - _Requirements: 6.4_
  
  - [ ] 4.3 Update header.html partial
    - Remove {% include "partials/header-switcher.html" %}
    - Restore standard Material header title component
    - Ensure navigation tabs section is preserved
    - _Requirements: 6.1, 6.4_
  
  - [ ] 4.4 Clean up version.py
    - Remove doc_switcher loading logic
    - Remove extract_base_path function
    - Remove construct_absolute_path function
    - Keep version variables and other shared configuration
    - _Requirements: 6.3_
  
  - [ ] 4.5 Remove doc_switcher CSS styles
    - Remove doc_switcher-related styles from extra.css
    - Keep other custom GeoServer branding styles
    - _Requirements: 6.4_

- [ ] 5. Update deployment workflow
  - [ ] 5.1 Modify docs-deploy.yml for unified build
    - Change working directory to workspace root for all steps
    - Update build step to run single mkdocs build command
    - _Requirements: 1.4, 10.1, 10.3_
  
  - [ ] 5.2 Simplify mike deployment commands
    - Remove --deploy-prefix parameter from mike deploy
    - Consolidate three deployment steps into one
    - Run from workspace root (NOT doc/ or doc/en/)
    - Command: `mike deploy $VERSION --push`
    - _Requirements: 5.1, 5.2, 10.2_
  
  - [ ] 5.3 Update API documentation handling
    - **IMPORTANT**: API docs are purely static files (NO Maven build needed)
    - API docs are already in `doc/en/api/` as static resources
    - No copying needed - they're already in the correct location
    - Remove any Maven build steps from workflow
    - API docs include: Swagger UI HTML/JS/CSS + OpenAPI YAML specs
    - _Requirements: 10.4_
  
  - [ ] 5.4 Update version and alias logic
    - Ensure version determination works with unified config
    - Update DOCS_BASE_PATH environment variable usage
    - _Requirements: 5.4_

- [ ] 6. Checkpoint - Local build and validation
  - Build documentation locally with `mkdocs build`
  - Verify site/en/{user,developer,docguide,api}/ structure exists
  - Check that all navigation tabs appear in generated HTML
  - Validate internal links with link checker
  - Test navigation tabs functionality in browser
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Create validation tests
  - [ ] 7.1 Create YAML configuration validation script
    - Write Python script to parse mkdocs.yml
    - Validate all nav paths exist in filesystem
    - Check theme configuration is valid
    - _Requirements: 1.1, 3.4_
  
  - [ ] 7.2 Create path resolution test script
    - Write Python script to verify source-to-output path mapping
    - Test that doc/en/user/index.md maps to site/en/user/index.html
    - Validate /en/ appears in all output paths
    - _Requirements: 2.1, 4.1, 4.2_
  
  - [ ] 7.3 Create build output structure validation script
    - Write shell script to verify site/ directory structure
    - Check all expected directories exist
    - Verify HTML files are generated for all nav entries
    - _Requirements: 1.2, 1.3_

- [ ] 8. Update documentation for contributors
  - [ ] 8.1 Update README.md in doc/en/
    - Document new unified build process
    - Update build commands (mkdocs build from workspace root)
    - Explain navigation tabs structure
    - _Requirements: 1.1, 1.4_
  
  - [ ] 8.2 Update developer documentation
    - Update doc/en/docguide/ content about build process
    - Document how to add new pages to navigation
    - Explain navigation tabs behavior
    - _Requirements: 1.1_

- [ ] 9. Test deployment in staging environment
  - [ ] 9.1 Deploy to test GitHub Pages site
    - Use test repository or branch for deployment
    - Run updated GitHub Actions workflow
    - Verify deployment completes successfully
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [ ] 9.2 Validate deployed site structure
    - Check {VERSION}/en/{manual}/ URL structure
    - Verify navigation tabs work on deployed site
    - Test version selector functionality
    - Validate all internal links work
    - _Requirements: 4.1, 4.3, 5.3, 8.1, 8.3_
  
  - [ ] 9.3 Test backward compatibility
    - Access old bookmarked URLs
    - Verify redirects or URL preservation works
    - Test external links to documentation
    - _Requirements: 4.2_

- [ ] 10. Final checkpoint and production deployment
  - Review all validation test results
  - Verify staging deployment is successful
  - Get approval for production deployment
  - Deploy to production GitHub Pages
  - Monitor for any issues post-deployment
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Cleanup and archival
  - [ ] 11.1 Remove old mkdocs.yml files
    - Delete doc/en/user/mkdocs.yml
    - Delete doc/en/developer/mkdocs.yml
    - Delete doc/en/docguide/mkdocs.yml
    - Keep files in git history for rollback
    - _Requirements: 1.1_
  
  - [ ] 11.2 Remove old target directories
    - Delete doc/en/user/target/
    - Delete doc/en/developer/target/
    - Delete doc/en/docguide/target/
    - _Requirements: 1.1_
  
  - [ ] 11.3 Update .gitignore
    - Add site/ to .gitignore at workspace root (NOT doc/site/)
    - Remove old target/ directory entries
    - _Requirements: 1.1_

## Notes

- All tasks involve configuration and file reorganization, not programming language-specific code
- The migration preserves all existing content in git history for easy rollback
- Navigation tabs are a native Material for MkDocs feature, no custom code required
- The unified configuration simplifies maintenance and reduces duplication
- Testing should be thorough before production deployment to ensure no broken links
- The /en/ path component is preserved for backward compatibility with existing bookmarks
- **Key insight**: MkDocs strips `docs_dir` from output but preserves structure within it
- **Solution**: mkdocs.yml at workspace root with `docs_dir: doc` → output preserves `doc/en/` as `site/en/`
