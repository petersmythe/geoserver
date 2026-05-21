# Implementation Plan: GeoServer API Documentation Verification

## Overview

This plan implements a comprehensive API documentation verification and generation system for GeoServer using AI agent task execution. The system will analyze existing documentation, extract endpoint definitions from source code, identify gaps, and generate complete OpenAPI 3.0 specifications for both REST APIs and OGC services.

The implementation is organized into phases, with each phase building on the previous one. Tasks produce intermediate outputs that are consumed by later tasks.

## Tasks

- [x] 1. Set up output directories and initialize analysis workspace
  - Create `.kiro/api-analysis/` directory structure
  - Create subdirectories: `rest/`, `ogc/`, `reports/`, `specs/`
  - Initialize tracking files for intermediate results
  - _Requirements: All_

- [x] 2. Parse existing OpenAPI documentation
  - [x] 2.1 Inventory existing OpenAPI spec files
    - Scan `doc/en/api/1.0.0/` directory
    - List all YAML files with file sizes and modification dates
    - Output: `.kiro/api-analysis/existing-specs-inventory.json`
    - _Requirements: 1.1_
  
  - [x] 2.2 Parse and extract REST endpoints from existing specs
    - Read each YAML file in `doc/en/api/1.0.0/`
    - Extract endpoint definitions (path, method, operation ID, parameters, responses)
    - Handle both Swagger 2.0 format
    - Report any YAML syntax errors with file name and line number
    - Output: `.kiro/api-analysis/rest/documented-endpoints.json`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [x] 2.3 Generate documented endpoints summary
    - Count total endpoints by HTTP method
    - Group endpoints by module (workspaces, layers, styles, etc.)
    - Output: `.kiro/api-analysis/reports/documented-summary.md`
    - _Requirements: 1.3_

- [x] 3. Checkpoint - Review existing documentation inventory
  - Review `.kiro/api-analysis/reports/documented-summary.md`
  - Verify all expected spec files were found and parsed
  - Ask user if questions arise

- [x] 4. Extract REST endpoints from Java source code
  - [x] 4.1 Scan REST API source directories
    - Identify all Java files in: `src/rest/`, `src/restconfig/`, `src/restconfig-wcs/`, `src/restconfig-wfs/`, `src/restconfig-wms/`, `src/restconfig-wmts/`, `src/gwc-rest/`
    - List controller classes (files containing @RestController or @Controller)
    - Output: `.kiro/api-analysis/rest/controller-files.json`
    - _Requirements: 2.5_
  
  - [x] 4.2 Extract Spring MVC endpoints from core REST modules
    - Parse Java files in `src/rest/` and `src/restconfig/`
    - Identify methods with @RequestMapping, @GetMapping, @PostMapping, @PutMapping, @DeleteMapping, @PatchMapping
    - Extract HTTP method, path pattern, parameters, return type
    - Combine class-level and method-level paths
    - Normalize Spring path variables to OpenAPI format (e.g., {workspaceName})
    - **Handle path arrays correctly** (e.g., `path = {"/styles/{styleName}", "/workspaces/{workspaceName}/styles/{styleName}"}`)
    - **Ensure all path templates have matching braces** (no malformed paths like `/styles/{styleName`)
    - Output: `.kiro/api-analysis/rest/implemented-core-endpoints.json`
    - _Requirements: 2.1, 2.3, 2.4, 2.6, 2.7_
  
  - [x] 4.3 Extract REST endpoints from service-specific modules
    - Parse Java files in `src/restconfig-wcs/`, `src/restconfig-wfs/`, `src/restconfig-wms/`, `src/restconfig-wmts/`
    - Extract endpoints using same logic as 4.2
    - Output: `.kiro/api-analysis/rest/implemented-service-endpoints.json`
    - _Requirements: 2.1, 2.3, 2.4, 2.6, 2.7_
  
  - [x] 4.4 Extract REST endpoints from GeoWebCache module
    - Parse Java files in `src/gwc-rest/`
    - Extract endpoints using same logic as 4.2
    - Output: `.kiro/api-analysis/rest/implemented-gwc-endpoints.json`
    - _Requirements: 2.1, 2.3, 2.4, 2.6, 2.7_
  
  - [x] 4.5 Scan extension modules for REST endpoints
    - Identify REST controllers in `src/extension/` subdirectories
    - Extract endpoints from extension modules
    - Output: `.kiro/api-analysis/rest/implemented-extension-endpoints.json`
    - _Requirements: 2.1, 2.3, 2.4, 2.5_
  
  - [x] 4.6 Scan community modules for REST endpoints
    - Identify REST controllers in `src/community/` subdirectories
    - Extract endpoints from community modules
    - Output: `.kiro/api-analysis/rest/implemented-community-endpoints.json`
    - _Requirements: 2.1, 2.3, 2.4, 2.5_
  
  - [x] 4.7 Consolidate all implemented REST endpoints
    - Merge endpoint data from tasks 4.2-4.6
    - Remove duplicates (same path + method)
    - Count total endpoints by module and HTTP method
    - Output: `.kiro/api-analysis/rest/implemented-all-endpoints.json`
    - Output: `.kiro/api-analysis/reports/implemented-summary.md`
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 5. Checkpoint - Review implemented endpoints inventory
  - Review `.kiro/api-analysis/reports/implemented-summary.md`
  - Verify endpoint counts seem reasonable
  - Ask user if questions arise

- [x] 6. Analyze REST API coverage
  - [x] 6.1 Match implemented endpoints with documented endpoints
    - Load `.kiro/api-analysis/rest/implemented-all-endpoints.json`
    - Load `.kiro/api-analysis/rest/documented-endpoints.json`
    - Match endpoints by path pattern and HTTP method
    - Identify exact matches, partial matches, and mismatches
    - Output: `.kiro/api-analysis/rest/endpoint-matches.json`
    - _Requirements: 3.6_
  
  - [x] 6.2 Calculate REST API coverage metrics
    - Count total implemented endpoints
    - Count total documented endpoints
    - Count matched endpoints
    - Calculate coverage percentage: (matched / implemented) × 100
    - Break down coverage by module
    - Output: `.kiro/api-analysis/rest/coverage-metrics.json`
    - _Requirements: 3.1, 3.4_
  
  - [x] 6.3 Identify REST API documentation gaps
    - List endpoints implemented but not documented
    - List endpoints documented but not implemented
    - List endpoints with parameter mismatches
    - Output: `.kiro/api-analysis/rest/gaps.json`
    - _Requirements: 3.2, 3.3_
  
  - [x] 6.4 Generate REST API coverage report
    - Create Markdown report with:
      - Overall coverage percentage
      - Coverage by module
      - List of undocumented endpoints
      - List of unimplemented endpoints
      - List of mismatched endpoints
    - Create CSV version for spreadsheet analysis
    - Output: `.kiro/api-analysis/reports/rest-coverage-report.md`
    - Output: `.kiro/api-analysis/reports/rest-coverage-report.csv`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 7. Checkpoint - Review REST API coverage report
  - Review `.kiro/api-analysis/reports/rest-coverage-report.md`
  - Identify priority gaps to address
  - Ask user if questions arise

- [x] 8. Extract OGC service operations from implementations
  - [x] 8.1 Extract WMS operations
    - Analyze `src/wms/src/main/java/org/geoserver/wms/WebMapService.java`
    - Identify operation methods: getCapabilities, getMap, getFeatureInfo, describeLayer, getLegendGraphic
    - Extract parameters from request classes (GetMapRequest.java, etc.)
    - Identify supported versions from module structure
    - Output: `.kiro/api-analysis/ogc/wms-operations.json`
    - _Requirements: 4.1, 4.7, 4.8_
  
  - [x] 8.2 Extract WFS operations
    - Analyze WFS service interfaces in `src/wfs-core/`, `src/wfs1_x/`, `src/wfs2_x/`
    - Identify operations: GetCapabilities, DescribeFeatureType, GetFeature, LockFeature, Transaction
    - Extract parameters for each version (1.0, 1.1, 2.0)
    - Output: `.kiro/api-analysis/ogc/wfs-operations.json`
    - _Requirements: 4.2, 4.7, 4.8_
  
  - [x] 8.3 Extract WCS operations
    - Analyze WCS service interfaces in `src/wcs/`, `src/wcs2_0/`
    - Identify operations: GetCapabilities, DescribeCoverage, GetCoverage
    - Extract parameters for each version (1.0, 1.1, 2.0)
    - Output: `.kiro/api-analysis/ogc/wcs-operations.json`
    - _Requirements: 4.3, 4.7, 4.8_
  
  - [x] 8.4 Extract WMTS operations
    - Analyze WMTS implementation in `src/gwc/`
    - Identify operations: GetCapabilities, GetTile, GetFeatureInfo
    - Extract parameters
    - Output: `.kiro/api-analysis/ogc/wmts-operations.json`
    - _Requirements: 4.4, 4.7, 4.8_
  
  - [x] 8.5 Extract CSW operations
    - Analyze CSW implementation in `src/extension/csw/`
    - Identify operations: GetCapabilities, DescribeRecord, GetRecords, GetRecordById
    - Extract parameters
    - Output: `.kiro/api-analysis/ogc/csw-operations.json`
    - _Requirements: 4.5, 4.7, 4.8_
  
  - [x] 8.6 Extract WPS operations
    - Analyze WPS implementation in `src/extension/wps/`
    - Identify operations: GetCapabilities, DescribeProcess, Execute
    - Extract parameters
    - Output: `.kiro/api-analysis/ogc/wps-operations.json`
    - _Requirements: 4.6, 4.7, 4.8_
  
  - [x] 8.7 Consolidate OGC operations
    - Merge all OGC operation data
    - Organize by service type and version
    - Count operations per service
    - Output: `.kiro/api-analysis/ogc/all-operations.json`
    - Output: `.kiro/api-analysis/reports/ogc-operations-summary.md`
    - _Requirements: 4.7, 4.8_

- [x] 9. Checkpoint - Review OGC operations inventory
  - Review `.kiro/api-analysis/reports/ogc-operations-summary.md`
  - Verify all expected services and operations found
  - Ask user if questions arise

- [x] 10. Cross-reference OGC operations with specifications
  - [x] 10.1 Create OGC specification reference data
    - Document standard operations and parameters for each OGC service
    - Reference official OGC specification documents
    - Include URLs to specification documents
    - Output: `.kiro/api-analysis/ogc/spec-reference.json`
    - _Requirements: 5.1, 5.7_
  
  - [x] 10.2 Compare WMS implementation with OGC spec
    - Load WMS operations from `.kiro/api-analysis/ogc/wms-operations.json`
    - Compare against OGC WMS 1.1.1 and 1.3.0 specifications
    - Identify missing required operations
    - Identify missing required parameters
    - Identify vendor extensions (non-standard parameters)
    - Output: `.kiro/api-analysis/ogc/wms-compliance.json`
    - _Requirements: 5.2, 5.3, 5.4, 5.6_
  
  - [x] 10.3 Compare WFS implementation with OGC spec
    - Compare WFS operations against OGC WFS 1.0, 1.1, 2.0 specifications
    - Identify compliance issues and extensions
    - Output: `.kiro/api-analysis/ogc/wfs-compliance.json`
    - _Requirements: 5.2, 5.3, 5.4, 5.6_
  
  - [x] 10.4 Compare WCS implementation with OGC spec
    - Compare WCS operations against OGC WCS 1.0, 1.1, 2.0 specifications
    - Identify compliance issues and extensions
    - Output: `.kiro/api-analysis/ogc/wcs-compliance.json`
    - _Requirements: 5.2, 5.3, 5.4, 5.6_
  
  - [x] 10.5 Compare other OGC services with specifications
    - Compare WMTS, CSW, WPS against their specifications
    - Identify compliance issues and extensions
    - Output: `.kiro/api-analysis/ogc/other-services-compliance.json`
    - _Requirements: 5.2, 5.3, 5.4, 5.6_
  
  - [x] 10.6 Generate OGC compliance reports
    - Create compliance report for each service type
    - List required operations/parameters that are missing
    - List vendor extensions
    - Organize by service type and version
    - Output: `.kiro/api-analysis/reports/ogc-compliance-report.md`
    - Output: `.kiro/api-analysis/reports/ogc-compliance-report.csv`
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [x] 11. Checkpoint - Review OGC compliance reports
  - Review `.kiro/api-analysis/reports/ogc-compliance-report.md`
  - Identify any critical compliance issues
  - Ask user if questions arise

- [x] 12. Generate reconciliation matrix
  - [x] 12.1 Create comprehensive reconciliation matrix
    - Combine REST and OGC analysis results
    - For each endpoint/operation, determine:
      - Implemented: Yes/No
      - Documented: Yes/No
      - OGC Required: Yes/No/N/A
      - Status: Complete, Needs Documentation, Needs Investigation
    - Calculate row counts for each status combination
    - Output: `.kiro/api-analysis/reconciliation-matrix.json`
    - _Requirements: 10.1, 10.3, 10.5, 10.6, 10.7_
  
  - [x] 12.2 Generate reconciliation matrix reports
    - Create Markdown report with sortable tables
    - Create CSV version for spreadsheet analysis
    - Include summary statistics
    - Output: `.kiro/api-analysis/reports/reconciliation-matrix.md`
    - Output: `.kiro/api-analysis/reports/reconciliation-matrix.csv`
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

- [x] 13. Checkpoint - Review reconciliation matrix
  - Review `.kiro/api-analysis/reports/reconciliation-matrix.md`
  - Prioritize which gaps to address first
  - Ask user if questions arise

- [x] 14. Generate unified OpenAPI 3.0 specification (modular approach)
  - [x] 14.1 Convert REST endpoints to OpenAPI 3.0 format (modular)
    - Load all REST endpoint data
    - Generate modular OpenAPI 3.0 specifications organized by module:
      - Core REST endpoints (restconfig module) → `rest/rest-core.yaml`
      - GeoWebCache REST endpoints → `rest/rest-gwc.yaml`
      - Security endpoints → `rest/rest-security.yaml`
      - Extension modules → `rest/rest-extensions.yaml`
      - Community modules → `rest/rest-community.yaml`
    - Create common reusable components:
      - Common schemas → `common/schemas.yaml`
      - Reusable parameters → `common/parameters.yaml`
      - Common responses → `common/responses.yaml`
    - Include complete parameter definitions (type, description, required, defaults)
    - Include request body schemas where applicable
    - Include response schemas (success and error)
    - Add REST API tag to all REST endpoints
    - Output: Modular files in `.kiro/api-analysis/specs/rest/` and `.kiro/api-analysis/specs/common/`
    - _Requirements: 6.1, 6.2, 6.5, 6.6, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_
  
  - [x] 14.2 Convert OGC operations to OpenAPI 3.0 format (modular)
    - Load all OGC operation data
    - Generate separate OpenAPI 3.0 specification for each service type:
      - WMS operations → `ogc/wms.yaml`
      - WFS operations → `ogc/wfs.yaml`
      - WCS operations → `ogc/wcs.yaml`
      - WMTS operations → `ogc/wmts.yaml`
      - CSW operations → `ogc/csw.yaml`
      - WPS operations → `ogc/wps.yaml`
    - For each service:
      - Create separate operation IDs for each version (e.g., WMS_1_1_GetMap, WMS_1_3_GetMap)
      - Add service type tag (e.g., WMS, WFS)
      - Document all parameters with complete metadata
      - Document supported output formats
      - Mark vendor extensions clearly
      - Document CRS parameters and EPSG codes
      - Document error response formats
    - Output: Modular files in `.kiro/api-analysis/specs/ogc/`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_
  
  - [x] 14.3 Create unified specification entry point with $ref
    - Create main entry point files (modular with $ref):
      - `.kiro/api-analysis/specs/geoserver.yaml`
      - `.kiro/api-analysis/specs/geoserver.json`
    - Use $ref to reference all modular REST specifications
    - Use $ref to reference all modular OGC specifications
    - Ensure all tags are properly defined
    - Add info section with title, version, description
    - Add servers section
    - Organize paths alphabetically
    - Generate both YAML and JSON versions
    - _Requirements: 6.1, 6.2, 6.7, 12.1, 12.2_
  
  - [x] 14.4 Bundle modular specs into single-file distribution versions
    - Resolve all $ref references from the modular spec
    - Generate bundled single-file versions (self-contained):
      - `doc/en/api/geoserver-bundled.yaml`
      - `doc/en/api/geoserver-bundled.json`
    - Use pretty-printing with 2-space indentation for JSON
    - Validate bundled specs are self-contained (no external $ref)
    - **Apply validation fixes automatically:**
      - Fix duplicate operationIds (make all unique)
      - Remove path parameters not in path templates
      - Ensure all paths start with '/'
      - Fix malformed path templates (missing closing braces)
    - Output: Single-file versions in `doc/en/api/` ready for Swagger UI and distribution
    - _Requirements: 6.1, 6.2, 6.7, 11.1, 11.2, 11.3, 11.4, 12.1, 12.2, 12.5_

- [x] 15. Validate generated OpenAPI specifications
  - [x] 15.1 Validate unified spec against OpenAPI 3.0 schema
    - Load `doc/en/api/geoserver-unified-3.0.yaml`
    - Validate against OpenAPI 3.0 schema
    - Check all $ref references resolve correctly
    - Verify all required fields present
    - Report any validation errors with locations
    - Output: `.kiro/api-analysis/reports/validation-report.md`
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 14_
  
  - [x] 15.2 Verify spec loads in Swagger UI
    - Attempt to load spec in Swagger UI format
    - Report any loading issues
    - Output: `.kiro/api-analysis/reports/swagger-ui-test.md`
    - _Requirements: 6.9_

- [x] 15.3 Fix metadata and contact information
  - Update version from 2.26.0 to 3.0.x in both modular and bundled specs
  - Update email from geoserver-users@lists.sourceforge.net to geoserver-user@discourse.osgeo.org
  - Apply fixes to both YAML and JSON formats
  - Files to update: `.kiro/api-analysis/specs/geoserver.yaml`, `.kiro/api-analysis/specs/geoserver.json`
  - Re-bundle specs after fixes
  - _Requirements: 6.1, 6.2_

- [x] 15.4 Fix OpenAPI validation errors
  - [x] 15.4.1 Fix duplicate operationId errors
    - Ensure all operation IDs are unique by including path segments or counters
    - Fixed 99 duplicate operationIds
    - _Requirements: 11.1, 11.2_
  
  - [x] 15.4.2 Fix malformed paths (missing/misplaced braces)
    - Fix paths with missing closing braces (e.g., `/rest/styles/{styleName`)
    - Fix paths with nested braces (e.g., `/rest/workspaces/{workspaceName/{featureTypeName}}`)
    - Fixed 14 malformed paths
    - _Requirements: 11.1, 11.3_
  
  - [x] 15.4.3 Fix path template parameter mismatches
    - Path template expressions must match Parameter Objects
    - Example issue: `/rest/workspaces/{workspaceName}` has parameters not in template
    - Remove or add parameters to match path template
    - _Requirements: 11.1, 11.3, 11.4_
  
  - [x] 15.4.4 Fix duplicate parameter names
    - Parameter names must be unique within an operation
    - Example issue: `name: USE_IMAGEN_IMAGEREAD` appears multiple times
    - Rename or remove duplicate parameters
    - _Requirements: 11.1, 11.4_
  
  - [x] 15.4.5 Remove unused definitions
    - Definitions declared but never used should be removed
    - Example issue: `OGCException` defined but never referenced
    - Clean up unused schemas, parameters, responses
    - _Requirements: 11.1, 11.4_
  
  - Apply fixes to both modular and bundled specs (YAML and JSON)
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [x] 15.5 Fix tag naming and organization
  - [x] 15.5.1 Capitalize "Gwc" to "GWC" in tag definitions
    - Updated tag definitions in modular and bundled specs
    - _Requirements: 6.2_
  
  - [x] 15.5.2 Fix remaining "Gwc" tags in operations
    - Found 5 operations still using "Gwc" tag (should be "REST GWC")
    - Located around lines 7387, 7455, 7523, 7591, 7659 in bundled YAML
    - Apply fix to both YAML and JSON bundled specs
    - _Requirements: 6.2_
  
  - [x] 15.5.3 Restructure OGC service tags to include version
    - Added version numbers to all OGC service tags (e.g., "WMS 1.3.0", "WFS 2.0.0")
    - _Requirements: 6.4, 8.7_
  
  - [x] 15.5.4 Order service versions from highest to lowest
    - Versions now ordered descending (2.0.0 before 1.0.0)
    - _Requirements: 6.4_
  
  - [x] 15.5.5 Prefix REST tags with "REST"
    - All REST tags now prefixed: "REST", "REST Extensions", "REST Community", "REST GWC", "REST Security"
    - _Requirements: 6.2_
  
  - [x] 15.5.6 Reorder tags properly
    - Tags now ordered: REST tags first, then OGC services
    - _Requirements: 6.2, 6.4_
  
  - [x] 15.5.7 Investigate and populate REST GWC endpoints
    - REST GWC tag exists but has no operations assigned
    - Found 5 GWC endpoints in extraction but they use dynamic paths (${gwc.context.suffix:})
    - Need to determine if these should be documented or if there are other GWC REST endpoints
    - Check if GWC REST API is separate from main GeoServer REST API
    - _Requirements: 2.1, 2.3, 6.1_
  
  - [x] 15.5.8 Fix malformed path `/.{ext:xml|json}` in REST Security
    - Path: `/.{ext:xml|json}` is malformed (missing closing brace)
    - Source: AuthenticationProviderRestController.java line 156
    - Actual path should be: `/security/authproviders` or `/security/authproviders.{ext:xml|json}`
    - The `.{ext:xml|json}` is a Spring path pattern for optional extension
    - This endpoint is tagged as "REST Security" but path is wrong
    - Fix in both modular and bundled specs (YAML and JSON)
    - _Requirements: 2.6, 6.1, 11.3_
  
  - [x] 15.5.9 Fix DELETE / endpoint path
    - Path: `/` is incorrect, should be `/rest/metadata`
    - Source: MetaDataRestService.java has @RequestMapping("/rest/metadata") at class level
    - Currently tagged as "REST Extensions" which is correct (metadata module)
    - Fix path to `/rest/metadata` in both modular and bundled specs
    - _Requirements: 2.6, 6.1, 11.3_
  
  - [x] 15.5.10 Sort REST Extensions endpoints alphabetically
    - All endpoints within REST Extensions tag should be ordered alphabetically by path
    - This should apply to all tag groups for consistency
    - Sort paths in bundled specs (YAML and JSON)
    - _Requirements: 6.2, 12.2_
    - Endpoint: DELETE/GET/POST/PUT /order
    - Currently tagged as "REST Security" but comes from rest module (not security module)
    - Source: AuthenticationFilterChainRestController.java and AuthenticationProviderRestController.java
    - Path pattern: /order and /order.{ext}
    - Determine correct tag: should it be "REST" or "REST Security"?
    - _Requirements: 6.2, 7.1_
  
  - [x] 15.5.9 Investigate DELETE / endpoint (DUPLICATE - COMPLETED IN 15.5.9 ABOVE)
    - Endpoint: DELETE /
    - Currently tagged as "REST Extensions"
    - Source: MetaDataRestService.java in metadata extension module
    - Full path should be /rest/metadata (not just /)
    - Verify path extraction is correct
    - Fixed: Path corrected to /rest/metadata
    - _Requirements: 2.1, 2.3, 6.1_
  
  - [x] 15.5.10 Sort REST Extensions endpoints alphabetically (DUPLICATE - COMPLETED IN 15.5.10 ABOVE)
    - All endpoints within REST Extensions tag should be ordered alphabetically by path
    - Apply to both modular and bundled specs
    - Fixed: All paths sorted alphabetically
    - _Requirements: 6.2_
  
  - [x] 15.5.11 Apply alphabetical sorting to all endpoint groups
    - Ensure all endpoints are sorted alphabetically within their tag groups
    - Apply to REST, REST Community, REST Security, REST GWC, and all OGC service versions
    - Fixed: All paths sorted alphabetically in bundled specs
    - _Requirements: 6.2_

- [x] 15.6 Research and document authentication methods
  - Research GeoServer authentication methods from official documentation
  - Document HTTP Basic Authentication
  - Document Digest Authentication
  - Document Form-based Authentication
  - Document OAuth2 (if supported)
  - Document API Key authentication (if supported)
  - Add securitySchemes to OpenAPI spec components
  - Apply security requirements to appropriate endpoints
  - Apply to both modular and bundled specs (YAML and JSON)
  - _Requirements: 7.6_

- [x] 15.7 Investigate and populate GeoWebCache endpoints
  - Review if GeoWebCache REST endpoints are missing or incomplete
  - Check `src/gwc-rest/` source code for endpoint definitions
  - Add missing GWC endpoints if found
  - Ensure GWC tag is properly populated
  - Apply fixes to both modular and bundled specs (YAML and JSON)
  - _Requirements: 2.1, 2.3, 6.1_

- [x] 16. Checkpoint - Review validation results
  - Review `.kiro/api-analysis/reports/validation-report.md`
  - Verify all validation errors from 15.3-15.7 are fixed
  - Re-run validation to confirm fixes
  - Ask user if questions arise

- [x] 17. Generate final summary and recommendations
  - [x] 17.1 Create executive summary
    - Summarize REST API coverage (percentage, gaps)
    - Summarize OGC service coverage (operations documented)
    - Highlight critical gaps requiring attention
    - Provide recommendations for next steps
    - Output: `.kiro/api-analysis/reports/executive-summary.md`
    - _Requirements: All_
  
  - [x] 17.2 Create prioritized action plan
    - List documentation-only fixes (safe, quick)
    - List implementation fixes needed (requires code changes)
    - List alignment issues (requires decisions)
    - Organize by priority and effort
    - Output: `.kiro/api-analysis/reports/action-plan.md`
    - _Requirements: All_
  
  - [x] 17.3 Generate and add request/response schemas
    - Extract Java classes used in REST API request/response bodies
    - Generate JSON Schema definitions for common data models:
      - Workspace, DataStore, FeatureType, Layer, Style, LayerGroup
      - Coverage, CoverageStore, WMSStore, WMTSStore
      - User, Role, SecurityRule, AuthenticationFilter
      - Import, Task, Transform (importer extension)
      - GeoWebCache: TileLayer, GridSet, BlobStore, DiskQuota
    - Convert Java classes to OpenAPI 3.0 schema format
    - Add schemas to components/schemas section
    - Reference schemas in request bodies and responses using $ref
    - Include schema examples and descriptions
    - Validate schemas are properly referenced
    - Output: Updated modular and bundled specifications with complete schemas
    - _Requirements: 6.5, 6.6, 7.1, 7.5, 8.2_

- [x] 18. Final checkpoint - Review complete analysis
  - Review all reports in `.kiro/api-analysis/reports/`
  - Review generated OpenAPI spec in `doc/en/api/`
  - Discuss next steps with user
  - Ensure all tests pass, ask the user if questions arise

- [x] 18.1 Sync specs with main branch changes (post-rebase catch-up)
  - The modular specs were generated from the codebase as of Feb 9, 2026 (commit `6eb3aff421`).
  - After rebasing to current main (May 18, 2026, commit `33ae7b19ef`), ~3 months of changes need to be incorporated.
  - [x] 18.1.1 Identify changed REST/OGC controllers since the original branch point
    - Run: `git diff --name-only 6eb3aff421..33ae7b19ef -- src/rest/ src/restconfig/ src/restconfig-wcs/ src/restconfig-wfs/ src/restconfig-wms/ src/restconfig-wmts/ src/gwc-rest/ src/extension/ src/community/ src/wms/ src/wfs-core/ src/wfs1_x/ src/wfs2_x/ src/wcs/ src/wcs2_0/ src/gwc/ src/ows/`
    - Filter to `.java` files only
    - From those, identify files containing REST annotations (`@RequestMapping`, `@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`, `@PatchMapping`, `@RestController`, `@Controller`)
    - Ignore non-code changes (docs, tests, pom.xml, properties files)
    - Output: List of controllers with REST API changes
    - **Result**: 635 changed non-test Java files, 17 with REST annotations
  - [x] 18.1.2 Categorize changes
    - New controllers (new endpoints to add to specs)
    - Modified controllers (changed paths, parameters, or request/response types)
    - Deleted controllers (endpoints to remove from specs)
    - Renamed/moved controllers (update module attribution)
    - **Result**: 1 new controller (CRSController, 4 endpoints), 1 removed endpoint (DataStoreFileController GET), 15 modified controllers (internal only), 0 deleted/renamed
  - [x] 18.1.3 Update modular specs with new/changed endpoints
    - For each new endpoint: add to appropriate modular spec file (rest-core, rest-extensions, rest-community, rest-gwc, rest-security)
    - For each modified endpoint: update path, parameters, or schemas in the modular spec
    - For each removed endpoint: delete from the modular spec
    - Maintain consistent formatting and tag assignment
    - **Result**: Added 4 CRS endpoints to rest-core.yaml, removed GET from DataStoreFileController path
  - [x] 18.1.4 Check for OGC service changes
    - Review changes to WMS/WFS/WCS/WMTS/CSW/WPS service implementations
    - If new operations or parameters were added, update the OGC modular specs
    - **Result**: No new OGC operations or parameters; changes were internal only
  - [x] 18.1.5 Re-bundle and validate
    - Run `bundle-spec.py` to regenerate `doc/en/api/geoserver-bundled.yaml` and `.json`
    - Validate the bundled spec loads cleanly in Swagger UI
    - Verify no new validation errors introduced
    - **Result**: Bundled specs regenerated (312 total paths), fixed bundler bug with internal schema refs

## Notes

- Tasks marked with sub-tasks should complete all sub-tasks before marking the parent complete
- Intermediate outputs in `.kiro/api-analysis/` enable resuming work if interrupted
- Checkpoint tasks allow user review and course correction
- Generated OpenAPI specs in `doc/en/api/` are ready for commit to repository
- Reports provide actionable insights for improving API documentation coverage


## Sprint 1: Document Missing Query Parameters (Quick Wins)

- [x] 19. Document `purge` query parameter on DELETE datastore/coveragestore endpoints
  - Add `purge` parameter (type: string, enum: [true, false, metadata]) to DELETE operations on datastores and coveragestores
  - Controls whether data files are deleted or only configuration — omission risks accidental data loss
  - Update modular specs in `.kiro/api-analysis/specs/rest/rest-core.yaml`
  - Re-bundle with `bundle-spec.py` to update `doc/en/api/geoserver-bundled.yaml` and `.json`
  - _Reference: `.kiro/api-analysis/reports/parameter-mismatch-analysis.md`, Action Plan D2_
  - _Requirements: 7.3, 7.4_

- [x] 20. Document `async` and `exec` execution control parameters on importer endpoints
  - Add `async` (boolean) and `exec` (boolean) parameters to POST/PUT importer operations
  - Controls synchronous vs asynchronous import execution (2 endpoints affected)
  - Update modular specs and re-bundle
  - _Reference: Action Plan D3_
  - _Requirements: 7.3, 7.4_

- [x] 21. Document `recalculate`/`calculate` parameters on coverage and feature type creation
  - Add `recalculate` parameter to PUT/POST feature type and coverage endpoints
  - Add `calculate` parameter to POST coverage endpoints
  - Affects spatial metadata accuracy — values: nativebbox, latlonbbox, or comma-separated combination
  - Update modular specs and re-bundle
  - _Reference: Action Plan D4_
  - _Requirements: 7.3, 7.4_

- [x] 22. Document `expand` query parameter on 6 endpoints
  - Add `expand` parameter (type: integer or string) to `/rest/imports`, `/rest/workspaces/{ws}/datastores/{ds}`, and 4 other endpoints
  - Controls response detail level (inline sub-resources vs links)
  - Update modular specs and re-bundle
  - _Reference: Action Plan D5_
  - _Requirements: 7.3, 7.4_

- [x] 23. Document `offset`/`limit` pagination and `from`/`to` filtering parameters
  - Add `offset` (integer) and `limit` (integer) to list endpoints for pagination of large result sets
  - Add `from` and `to` (string) parameters to `/rest/about/manifest` and `/rest/about/version` for version range filtering
  - Add `styleName` parameter to POST `/rest/layers` for associating a default style during layer creation
  - Update modular specs and re-bundle
  - _Reference: Action Plan D6, D7, D13_
  - _Requirements: 7.3, 7.4_

- [x] 24. Checkpoint — Validate Sprint 1 parameter additions
  - Run `bundle-spec.py` to regenerate bundled specs
  - Validate bundled spec with OpenAPI validator (zero new errors)
  - Verify new parameters render correctly in Swagger UI
  - Ensure all tests pass, ask the user if questions arise
  - _Requirements: 11.1, 11.2, 11.3_

## Sprint 2: Request Body Schemas for PUT Operations

- [x] 25. Add request body schemas for core REST PUT endpoints (workspaces, namespaces, layers)
  - Extract Java model classes: WorkspaceInfo, NamespaceInfo, LayerInfo, LayerGroupInfo
  - Generate OpenAPI 3.0 schema definitions from class fields
  - Add schemas to `common/schemas.yaml` and reference via `$ref` in PUT operations
  - Include example request bodies in JSON and XML
  - Update modular specs and re-bundle
  - _Reference: Action Plan D1_
  - _Requirements: 6.5, 6.6, 7.1, 7.5_

- [x] 26. Add request body schemas for data store PUT endpoints
  - Extract Java model classes: DataStoreInfo, CoverageStoreInfo, WMSStoreInfo, WMTSStoreInfo
  - Generate OpenAPI 3.0 schema definitions
  - Add schemas and reference in PUT operations for datastores, coveragestores, wmsstores, wmtsstores
  - Include example request bodies
  - Update modular specs and re-bundle
  - _Reference: Action Plan D1_
  - _Requirements: 6.5, 6.6, 7.1, 7.5_

- [x] 27. Add request body schemas for security and importer PUT endpoints
  - Extract Java model classes: UserInfo, GroupInfo, RoleInfo, SecurityRule, ImportContext, TaskInfo, TransformInfo
  - Generate OpenAPI 3.0 schema definitions
  - Add schemas and reference in PUT operations for security and importer endpoints (~16 importer endpoints)
  - Include example request bodies
  - Update modular specs and re-bundle
  - _Reference: Action Plan D1_
  - _Requirements: 6.5, 6.6, 7.1, 7.5_

- [x] 28. Add response schemas for documented endpoints
  - Add success response schemas (200/201) to all documented GET and POST operations
  - Add standard error response schemas (400, 401, 403, 404, 500)
  - Reference shared error schema from `common/responses.yaml`
  - Update modular specs and re-bundle
  - _Reference: Action Plan D10_
  - _Requirements: 6.5, 6.6, 7.1_

- [x] 29. Remove incorrect documented-only parameters and fix anti-patterns
  - Remove documented params (manifest, key, value) from GET `/rest/about/status` that don't exist in implementation
  - Review and fix GET `/rest/logging` request body anti-pattern (remove `@RequestBody` or change to POST)
  - Review 1 endpoint with documented-only request body — remove if not implemented
  - Update modular specs and re-bundle
  - _Reference: Action Plan I1, A4_
  - _Requirements: 3.3, 7.1_

- [x] 30. Checkpoint — Validate Sprint 2 schema additions
  - Run `bundle-spec.py` to regenerate bundled specs
  - Validate bundled spec (zero errors)
  - Verify request/response schemas render correctly in Swagger UI
  - Ensure all tests pass, ask the user if questions arise
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

## Sprint 3: Path Variable Naming and Decisions

- [x] 31. Decide and document path variable naming convention
  - Review current patterns: generic (`{id}`) vs descriptive (`{importId}`) across 90+ endpoints
  - Document decision: match Java `@PathVariable` names exactly (descriptive names preferred for code-gen tools)
  - Create a mapping table of current spec names → correct implementation names
  - Output: Decision documented in `.kiro/api-analysis/reports/path-variable-convention.md`
  - _Reference: Action Plan A1, D9_
  - _Requirements: 6.1, 6.5_

- [x] 32. Update path variable names in restconfig module specs (~93 endpoints)
  - Apply naming convention to all restconfig endpoints in `.kiro/api-analysis/specs/rest/rest-core.yaml`
  - Use find-and-replace: `workspace` → `workspaceName`, `layer` → `layerName`, `style` → `styleName`, etc.
  - Ensure path template `{varName}` matches the parameter definition `name: varName`
  - Validate no broken `$ref` references after changes
  - _Reference: Action Plan D9_
  - _Requirements: 6.1, 6.5_

- [x] 33. Update path variable names in extension and community module specs (~32 endpoints)
  - Apply naming convention to importer (16), mongodb (4), oseo (10), and other modules
  - Update `.kiro/api-analysis/specs/rest/rest-extensions.yaml` and `rest-community.yaml`
  - Validate path templates match parameter definitions
  - Re-bundle and validate
  - _Reference: Action Plan D9_
  - _Requirements: 6.1, 6.5_

- [x] 34. Checkpoint — Validate Sprint 3 path variable fixes
  - Run `bundle-spec.py` to regenerate bundled specs
  - Validate bundled spec (zero errors, all path params match templates)
  - Verify in Swagger UI that path parameters render correctly
  - Ensure all tests pass, ask the user if questions arise
  - _Requirements: 11.1, 11.2, 11.3_

## Sprint 4: Coverage Expansion (Undocumented Endpoints)

- [x] 35. Document remaining restconfig endpoints (79 undocumented)
  - Scan `src/restconfig/` for controllers not yet in the spec
  - Extract endpoint paths, methods, parameters, and request/response types
  - Add to `.kiro/api-analysis/specs/rest/rest-core.yaml` with proper tags and schemas
  - Re-bundle specs
  - _Reference: Action Plan D8.1_
  - _Requirements: 2.1, 3.2, 6.1, 6.5, 7.1_

- [x] 36. Document geofence REST endpoints (11 undocumented)
  - Scan `src/extension/geofence/` for REST controllers
  - Extract endpoint definitions and add to `rest-extensions.yaml`
  - Include request/response schemas for geofence rule management
  - Re-bundle specs
  - _Reference: Action Plan D8.2_
  - _Requirements: 2.1, 3.2, 6.1, 6.5, 7.1_

- [x] 37. Document features-templating REST endpoints (18 undocumented)
  - Scan `src/community/features-templating/` for REST controllers
  - Extract endpoint definitions and add to `rest-community.yaml`
  - Include request/response schemas for template management
  - Re-bundle specs
  - _Reference: Action Plan D8.3_
  - _Requirements: 2.1, 3.2, 6.1, 6.5, 7.1_

- [x] 38. Document OGC API — Features and Tiles endpoints
  - Scan `src/extension/ogcapi/` and `src/community/ogcapi/` directories
  - Extract OGC API - Features 1.0 endpoints (collections, items, conformance)
  - Extract OGC API - Tiles 1.0 endpoints (tilesets, tiles)
  - Create modular specs: `ogc/ogcapi-features.yaml`, `ogc/ogcapi-tiles.yaml`
  - Add tags: "OGC API - Features 1.0", "OGC API - Tiles 1.0"
  - Re-bundle specs
  - _Reference: Action Plan D14_
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 39. Update coverage metrics and generate final report
  - Re-run coverage analysis against updated specs
  - Calculate new coverage percentage (target: ~75% REST coverage)
  - Generate updated reconciliation matrix
  - Output: `.kiro/api-analysis/reports/rest-coverage-report-v2.md`
  - Output: `.kiro/api-analysis/reports/reconciliation-matrix-v2.md`
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 10.1, 10.3_

- [x] 40. Checkpoint — Validate Sprint 4 coverage expansion
  - Run `bundle-spec.py` to regenerate bundled specs
  - Validate bundled spec (zero errors)
  - Review coverage report — confirm improvement from 47% toward 75%
  - Ensure all tests pass, ask the user if questions arise
  - _Requirements: 11.1, 11.2, 11.3, 3.1_

## Sprint 5: Code-First OpenAPI Annotations (Phase 3)

- [ ] 41. Evaluate Springdoc OpenAPI compatibility with GeoServer
  - Check compatibility with Spring Framework 7.x servlet-based architecture (not Spring Boot)
  - Review existing `src/community/rest-openapi/` module for prior art
  - Determine runtime vs build-time generation strategy
  - Document decision and rationale
  - Output: `.kiro/api-analysis/reports/annotation-framework-decision.md`
  - _Reference: Action Plan A2, I6_
  - _Requirements: 6.1_

- [ ] 42. Pilot Springdoc annotations on CRS and Workspace controllers
  - Add Springdoc dependency to appropriate Maven module
  - Annotate `CRSController` (4 endpoints, new and simple) with `@Operation`, `@Parameter`, `@ApiResponse`
  - Annotate `WorkspaceController` as a second pilot
  - Verify auto-generated spec matches hand-built spec for these controllers
  - Run `mvn spotless:apply` after changes
  - Document any gaps or issues
  - _Reference: Action Plan I2, I3_
  - _Requirements: 6.1, 6.5, 7.1_

- [ ] 43. Annotate core REST controllers (src/rest/, src/restconfig/)
  - Use hand-built spec as reference for descriptions, parameter metadata, and schemas
  - Add `@Operation` with summary and description to all methods
  - Add `@Parameter` for path variables and query parameters
  - Add `@ApiResponse` for success and error responses
  - Add `@Schema` annotations to request/response model classes
  - Run `mvn spotless:apply` after changes
  - _Reference: Action Plan I5_
  - _Requirements: 6.1, 6.5, 7.1_

- [ ] 44. Annotate service-specific and GWC REST controllers
  - Annotate controllers in `src/restconfig-wcs/`, `src/restconfig-wfs/`, `src/restconfig-wms/`, `src/restconfig-wmts/`
  - Annotate controllers in `src/gwc-rest/`
  - Same approach as task 43
  - Run `mvn spotless:apply` after changes
  - _Requirements: 6.1, 6.5, 7.1_

- [ ] 45. Annotate security and extension module REST controllers
  - Annotate security controllers (authentication, authorization endpoints)
  - Annotate priority extension controllers: importer, monitor, geofence, params-extractor
  - Same approach as task 43
  - Run `mvn spotless:apply` after changes
  - _Requirements: 6.1, 6.5, 7.1, 7.6_

- [ ] 46. Configure Springdoc runtime spec generation and CI validation
  - Configure Springdoc: info block, server URLs, security schemes, tag ordering
  - Set up spec generation at `/geoserver/v3/api-docs` or as Maven build artifact
  - Add CI step to validate generated spec (fail build on errors)
  - Optionally diff generated spec against baseline
  - _Reference: Action Plan I6, I7_
  - _Requirements: 6.1, 6.2, 7.6, 11.1, 11.5_

- [ ] 47. Determine and implement approach for OGC service endpoint documentation
  - OGC services use dispatcher pattern (single URL, REQUEST param selects operation) — doesn't map to annotations
  - Evaluate options: custom Springdoc plugin, static spec overlay, or hybrid approach
  - Implement chosen approach for WMS, WFS, WCS, WMTS, CSW, WPS
  - Include version-specific parameter differences and vendor extensions
  - _Reference: Action Plan A3_
  - _Requirements: 6.3, 6.4, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

- [ ] 48. Transition Swagger UI to generated spec and retire static files
  - Update `doc/en/api/index.html` to point at auto-generated spec endpoint
  - Verify all endpoints render correctly in Swagger UI
  - Verify "Try it out" works against a running GeoServer instance
  - Once verified equivalent: remove `doc/en/api/geoserver-bundled.yaml` and `.json`
  - Archive `.kiro/api-analysis/specs/` modular files as historical reference
  - _Requirements: 6.7, 6.9_

- [ ] 49. Final validation — Code is the single source of truth
  - Verify: changing a controller annotation updates the generated spec
  - Verify: adding a new endpoint automatically appears in the spec
  - Verify: removing an endpoint automatically removes it from the spec
  - Verify: generated spec can produce working client code (e.g., via openapi-generator)
  - Document the new workflow for developers (how to add docs, verify locally, CI enforcement)
  - _Requirements: All_

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["19", "20", "21", "22", "23"] },
    { "id": 1, "tasks": ["24"] },
    { "id": 2, "tasks": ["25", "26", "27"] },
    { "id": 3, "tasks": ["28", "29"] },
    { "id": 4, "tasks": ["30"] },
    { "id": 5, "tasks": ["31"] },
    { "id": 6, "tasks": ["32", "33"] },
    { "id": 7, "tasks": ["34"] },
    { "id": 8, "tasks": ["35", "36", "37", "38"] },
    { "id": 9, "tasks": ["39"] },
    { "id": 10, "tasks": ["40"] },
    { "id": 11, "tasks": ["41"] },
    { "id": 12, "tasks": ["42"] },
    { "id": 13, "tasks": ["43", "44", "45"] },
    { "id": 14, "tasks": ["46", "47"] },
    { "id": 15, "tasks": ["48"] },
    { "id": 16, "tasks": ["49"] }
  ]
}
```
