# Requirements Document

## Introduction

This document specifies the requirements for consolidating the GeoServer documentation from three separate MkDocs configurations into a single unified configuration that uses Material for MkDocs navigation tabs for manual switching. The consolidation will simplify the build process, improve URL structure consistency, and enhance integration with mike version management.

## Glossary

- **MkDocs**: Static site generator for project documentation
- **Material_for_MkDocs**: Material Design theme for MkDocs with advanced navigation features
- **Mike**: Version management tool for MkDocs that deploys multiple versions to GitHub Pages
- **Navigation_Tabs**: Material for MkDocs feature that displays top-level navigation items as tabs
- **Doc_Switcher**: Custom navigation component currently used to switch between documentation manuals
- **Build_System**: The MkDocs build process that converts Markdown to HTML
- **Deployment_System**: The GitHub Actions workflow that deploys documentation using mike
- **URL_Structure**: The path hierarchy for accessing documentation (e.g., /3.0.x/en/user/)

## Requirements

### Requirement 1: Single MkDocs Configuration

**User Story:** As a documentation maintainer, I want a single MkDocs configuration file, so that I can build all documentation with one command.

#### Acceptance Criteria

1. THE Build_System SHALL use a single mkdocs.yml file located at doc/en/mkdocs.yml
2. WHEN the Build_System executes, THE Build_System SHALL generate all three manuals (user, developer, docguide) plus API documentation
3. THE Build_System SHALL produce output in the site/ directory with structure site/en/{user,developer,docguide,api}/
4. WHEN building documentation, THE Build_System SHALL complete in a single mkdocs build command

### Requirement 2: Directory Structure Reorganization

**User Story:** As a documentation maintainer, I want the source files organized to produce /en/ in URLs, so that backward compatibility is maintained.

#### Acceptance Criteria

1. THE Build_System SHALL use docs_dir configuration that references the en/ subdirectory
2. THE Build_System SHALL organize source content in doc/en/en/{user,developer,docguide}/ directories
3. WHEN building documentation, THE Build_System SHALL include /en/ in the output path structure
4. THE Build_System SHALL preserve existing content file locations within each manual subdirectory

### Requirement 3: Navigation Tabs Implementation

**User Story:** As a documentation user, I want navigation tabs at the top of the page, so that I can easily switch between manuals.

#### Acceptance Criteria

1. THE Build_System SHALL enable navigation.tabs feature in Material for MkDocs theme
2. THE Build_System SHALL enable navigation.tabs.sticky feature to keep tabs visible while scrolling
3. WHEN the Build_System generates documentation, THE Build_System SHALL create tabs for User Manual, Developer Guide, Documentation Guide, and API Reference
4. THE Build_System SHALL structure the nav configuration with top-level items that become tabs
5. WHEN a user views any documentation page, THE Build_System SHALL display all four tabs in the top navigation bar

### Requirement 4: URL Structure Preservation

**User Story:** As a documentation user, I want URLs to maintain the /en/ path component, so that existing bookmarks and links continue to work.

#### Acceptance Criteria

1. WHEN documentation is deployed, THE Deployment_System SHALL produce URLs in the format {VERSION}/en/{manual}/
2. THE Deployment_System SHALL maintain /en/ in all documentation URLs for backward compatibility
3. WHEN a user accesses a versioned manual, THE Deployment_System SHALL serve content from paths like 3.0.x/en/user/
4. THE Deployment_System SHALL ensure API documentation is accessible at {VERSION}/en/api/

### Requirement 5: Mike Integration

**User Story:** As a documentation maintainer, I want mike to deploy the unified documentation, so that version management works correctly.

#### Acceptance Criteria

1. WHEN deploying with mike, THE Deployment_System SHALL use no deploy-prefix parameter
2. THE Deployment_System SHALL deploy the entire site/ directory contents to {VERSION}/
3. WHEN mike deploys documentation, THE Deployment_System SHALL preserve the /en/ structure from the build output
4. THE Deployment_System SHALL maintain mike's version selector functionality alongside navigation tabs

### Requirement 6: Doc Switcher Replacement

**User Story:** As a documentation maintainer, I want to remove the custom doc_switcher code, so that the system is simpler and uses standard Material features.

#### Acceptance Criteria

1. THE Build_System SHALL use Material for MkDocs navigation tabs instead of custom doc_switcher
2. THE Build_System SHALL remove doc_switcher.yml configuration file
3. THE Build_System SHALL remove doc_switcher processing logic from version.py
4. THE Build_System SHALL remove doc_switcher template code from the theme

### Requirement 7: Theme Configuration Consolidation

**User Story:** As a documentation maintainer, I want a single theme configuration, so that styling is consistent across all manuals.

#### Acceptance Criteria

1. THE Build_System SHALL use a single custom_dir for the Material theme
2. THE Build_System SHALL apply consistent palette, features, and styling across all manuals
3. WHEN building documentation, THE Build_System SHALL use the same markdown extensions for all manuals
4. THE Build_System SHALL maintain existing theme customizations (logo, favicon, colors)

### Requirement 8: Version Selector Integration

**User Story:** As a documentation user, I want the version selector to work with navigation tabs, so that I can switch both versions and manuals.

#### Acceptance Criteria

1. WHEN a user views documentation, THE Build_System SHALL display both the version selector and navigation tabs
2. THE Build_System SHALL maintain mike's version selector configuration in the extra section
3. WHEN a user switches versions, THE Deployment_System SHALL preserve the current manual context
4. THE Build_System SHALL ensure version selector and navigation tabs do not conflict visually

### Requirement 9: Build Performance

**User Story:** As a documentation maintainer, I want the consolidated build to complete efficiently, so that CI/CD pipelines remain fast.

#### Acceptance Criteria

1. WHEN building all documentation, THE Build_System SHALL complete within reasonable time limits
2. THE Build_System SHALL support incremental builds during local development
3. THE Build_System SHALL cache dependencies appropriately in CI/CD
4. WHEN building locally, THE Build_System SHALL support mkdocs serve for live preview

### Requirement 10: Deployment Workflow Simplification

**User Story:** As a documentation maintainer, I want a simplified deployment workflow, so that releases are easier to manage.

#### Acceptance Criteria

1. THE Deployment_System SHALL execute a single mike deploy command per version
2. THE Deployment_System SHALL remove separate deployment steps for each manual
3. WHEN deploying documentation, THE Deployment_System SHALL handle all manuals in one operation
4. THE Deployment_System SHALL maintain separate API documentation deployment for Java-generated content
