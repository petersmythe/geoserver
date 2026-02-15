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

- [ ] 2. Parse existing OpenAPI documentation
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

- [ ] 4. Extract REST endpoints from Java source code
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

- [ ] 14. Generate unified OpenAPI 3.0 specification (modular approach)
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

- [ ] 15. Validate generated OpenAPI specifications
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

- [ ] 17. Generate final summary and recommendations
  - [x] 17.1 Create executive summary
    - Summarize REST API coverage (percentage, gaps)
    - Summarize OGC service coverage (operations documented)
    - Highlight critical gaps requiring attention
    - Provide recommendations for next steps
    - Output: `.kiro/api-analysis/reports/executive-summary.md`
    - _Requirements: All_
  
  - [ ] 17.2 Create prioritized action plan
    - List documentation-only fixes (safe, quick)
    - List implementation fixes needed (requires code changes)
    - List alignment issues (requires decisions)
    - Organize by priority and effort
    - Output: `.kiro/api-analysis/reports/action-plan.md`
    - _Requirements: All_
  
  - [ ] 17.3 Generate and add request/response schemas
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

- [ ] 18. Final checkpoint - Review complete analysis
  - Review all reports in `.kiro/api-analysis/reports/`
  - Review generated OpenAPI spec in `doc/en/api/`
  - Discuss next steps with user
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with sub-tasks should complete all sub-tasks before marking the parent complete
- Intermediate outputs in `.kiro/api-analysis/` enable resuming work if interrupted
- Checkpoint tasks allow user review and course correction
- Generated OpenAPI specs in `doc/en/api/` are ready for commit to repository
- Reports provide actionable insights for improving API documentation coverage


## Parameter Mismatch Fixes

The following tasks address the 129 parameter mismatches identified in the REST API coverage analysis. These are prioritized by impact and effort, focusing on functional issues before cosmetic ones.

- [ ] 19. Fix query parameter documentation gaps (HIGH PRIORITY)
  - [ ] 19.1 Document `expand` parameter
    - Review 6 endpoints that use `expand` parameter
    - Document parameter purpose (resource expansion)
    - Add to OpenAPI specs with type, description, required flag
    - Endpoints affected: `/rest/imports`, `/rest/workspaces`, and others
    - _Reference: `.kiro/api-analysis/reports/parameter-mismatch-analysis.md`_
  
  - [ ] 19.2 Document filtering parameters (`from`, `to`)
    - Review 2 endpoints using `from`/`to` parameters
    - Document parameter purpose (filtering/versioning)
    - Add to OpenAPI specs with type, description, required flag
    - Endpoints affected: `/rest/about/manifest` and others
    - _Reference: `.kiro/api-analysis/reports/parameter-mismatch-analysis.md`_
  
  - [ ] 19.3 Document execution control parameters (`exec`, `async`)
    - Review 2 endpoints using `exec`/`async` parameters
    - Document parameter purpose (execution control)
    - Add to OpenAPI specs with type, description, required flag
    - _Reference: `.kiro/api-analysis/reports/parameter-mismatch-analysis.md`_
  
  - [ ] 19.4 Document remaining query parameters
    - Review endpoints with other missing query parameters
    - Parameters: `styleName`, `offset`, `limit`, `recalculate`, `calculate`, `purge`
    - Add to OpenAPI specs with complete metadata
    - _Reference: `.kiro/api-analysis/reports/parameter-mismatch-analysis.md`_
  
  - [ ] 19.5 Verify documented-only query parameters
    - Review 12 endpoints where docs have params but implementation doesn't
    - Determine if parameters are planned features or documentation errors
    - Either implement missing parameters or remove from documentation
    - Endpoints include: `/rest/about/status` and others
    - _Reference: `.kiro/api-analysis/reports/mismatch-analysis.json`_

- [ ] 20. Fix request body documentation mismatches (MEDIUM PRIORITY)
  - [ ] 20.1 Review and fix PUT endpoint body documentation
    - Review 31 PUT endpoints where implementation has body but docs don't
    - Document request body schemas for each endpoint
    - Include content type, schema definition, examples
    - Focus on importer module endpoints first (16 endpoints)
    - _Reference: `.kiro/api-analysis/reports/parameter-mismatch-analysis.md`_
  
  - [ ] 20.2 Investigate GET endpoint with request body
    - Review GET `/rest/logging` endpoint
    - Determine if request body is intentional (REST anti-pattern)
    - Either remove body from implementation or document as vendor extension
    - _Reference: `.kiro/api-analysis/reports/parameter-mismatch-analysis.md`_
  
  - [ ] 20.3 Review documented-only request bodies
    - Review 1 endpoint where docs have body but implementation doesn't
    - Determine if this is a planned feature or documentation error
    - Either implement missing body support or remove from documentation
    - _Reference: `.kiro/api-analysis/reports/mismatch-analysis.json`_

- [ ] 21. Standardize path variable names (LOW PRIORITY)
  - [ ] 21.1 Decide on path variable naming convention
    - Review current patterns: generic (`{id}`) vs descriptive (`{importId}`)
    - Consult with team on preferred convention
    - Document decision in project guidelines
    - _Reference: `.kiro/api-analysis/reports/parameter-mismatch-analysis.md`_
  
  - [ ] 21.2 Update restconfig module path variables
    - Apply chosen naming convention to 93 restconfig endpoints
    - Update either Java code or OpenAPI documentation for consistency
    - Ensure backward compatibility if changing implementation
    - _Reference: `.kiro/api-analysis/reports/mismatch-analysis.json`_
  
  - [ ] 21.3 Update extension module path variables
    - Apply naming convention to importer (16), mongodb (4), rat (1), wps-download (1)
    - Update either Java code or OpenAPI documentation for consistency
    - _Reference: `.kiro/api-analysis/reports/mismatch-analysis.json`_
  
  - [ ] 21.4 Update community module path variables
    - Apply naming convention to oseo (10) and other community modules (4)
    - Update either Java code or OpenAPI documentation for consistency
    - _Reference: `.kiro/api-analysis/reports/mismatch-analysis.json`_

- [ ] 22. Checkpoint - Review parameter mismatch fixes
  - Verify all query parameter gaps documented
  - Verify all request body mismatches resolved
  - Review path variable naming consistency
  - Re-run coverage analysis to confirm improvements
  - Ask user if questions arise

- [ ] 23. Regenerate unified OpenAPI 3.0 specification with fixes
  - [ ] 23.1 Re-run REST endpoint extraction
    - Re-scan all REST API source directories
    - Extract updated endpoint definitions with corrected parameters
    - Output: `.kiro/api-analysis/rest/implemented-all-endpoints-v2.json`
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [ ] 23.2 Re-run coverage analysis
    - Match updated implementations with updated documentation
    - Calculate new coverage metrics
    - Verify parameter mismatches are resolved
    - Output: `.kiro/api-analysis/rest/coverage-metrics-v2.json`
    - Output: `.kiro/api-analysis/reports/rest-coverage-report-v2.md`
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ] 23.3 Regenerate REST OpenAPI 3.0 specification
    - Convert updated REST endpoints to OpenAPI 3.0 format
    - Include all corrected parameter definitions
    - Include all corrected request body schemas
    - Apply standardized path variable naming
    - Output: `.kiro/api-analysis/specs/rest-openapi-3.0-v2.yaml`
    - _Requirements: 6.1, 6.2, 6.5, 6.6, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_
  
  - [ ] 23.4 Regenerate unified specification
    - Merge updated REST spec with OGC spec
    - Ensure all corrections are included
    - Validate against OpenAPI 3.0 schema
    - Output: `doc/en/api/geoserver-unified-3.0-v2.yaml`
    - Output: `doc/en/api/geoserver-unified-3.0-v2.json`
    - _Requirements: 6.1, 6.2, 6.7, 11.1, 11.2, 11.3, 11.4, 11.5, 12.1, 12.2, 12.5_
  
  - [ ] 23.5 Generate final reconciliation matrix
    - Create updated reconciliation matrix with all fixes applied
    - Verify all parameter mismatches resolved
    - Document remaining gaps (if any)
    - Output: `.kiro/api-analysis/reports/reconciliation-matrix-final.md`
    - Output: `.kiro/api-analysis/reports/reconciliation-matrix-final.csv`
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

- [ ] 24. Add OGC API endpoints documentation
  - [ ] 24.1 Extract OGC API - Features endpoints
    - Scan `src/community/ogcapi/` and `src/extension/ogcapi/` directories
    - Identify OGC API - Features 1.0 endpoints (collections, items, conformance)
    - Extract endpoint paths, parameters, and response schemas
    - Output: `.kiro/api-analysis/ogc/ogcapi-features-operations.json`
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [ ] 24.2 Extract OGC API - Tiles endpoints
    - Identify OGC API - Tiles endpoints (tilesets, tiles)
    - Extract endpoint paths, parameters, and response schemas
    - Output: `.kiro/api-analysis/ogc/ogcapi-tiles-operations.json`
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [ ] 24.3 Extract other OGC API endpoints
    - Identify OGC API - Coverages, Processes, Styles, Maps endpoints if present
    - Extract endpoint paths, parameters, and response schemas
    - Output: `.kiro/api-analysis/ogc/ogcapi-other-operations.json`
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [ ] 24.4 Generate OGC API OpenAPI specifications
    - Create modular OpenAPI 3.0 specifications for each OGC API service:
      - `ogc/ogcapi-features.yaml` - OGC API - Features endpoints
      - `ogc/ogcapi-tiles.yaml` - OGC API - Tiles endpoints
      - `ogc/ogcapi-other.yaml` - Other OGC API endpoints
    - Add OGC API tags (sibling to WMS, WFS, WCS, etc.):
      - "OGC API - Features 1.0"
      - "OGC API - Tiles 1.0"
      - Additional tags as needed
    - Include complete parameter and response definitions
    - Document conformance classes supported
    - Output: Modular files in `.kiro/api-analysis/specs/ogc/`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  
  - [ ] 24.5 Update unified specification with OGC API endpoints
    - Add OGC API tags to main specification
    - Reference OGC API modular specs in unified entry point
    - Re-bundle specifications to include OGC API endpoints
    - Validate bundled specs include all OGC API operations
    - Output: Updated `doc/en/api/geoserver-bundled.yaml` and `.json`
    - _Requirements: 6.1, 6.2, 6.7, 12.1, 12.2_
  
  - [ ] 24.6 Document OGC API coverage
    - Count OGC API endpoints by service type
    - Compare against OGC API specifications
    - Generate coverage report
    - Output: `.kiro/api-analysis/reports/ogcapi-coverage-report.md`
    - _Requirements: 3.1, 3.4, 5.2_

- [ ] 25. Final validation and summary
  - [ ] 25.1 Validate final unified specification
    - Validate against OpenAPI 3.0 schema
    - Verify all $ref references resolve
    - Test loading in Swagger UI
    - Output: `.kiro/api-analysis/reports/validation-report-final.md`
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 6.9_
  
  - [ ] 25.2 Generate final executive summary
    - Summarize final coverage metrics
    - Document all improvements made
    - List any remaining gaps
    - Provide recommendations for ongoing maintenance
    - Output: `.kiro/api-analysis/reports/executive-summary-final.md`
    - _Requirements: All_


## Phase 2: Fix Functional Documentation Gaps

These tasks address the 39 endpoints with functional discrepancies (missing request bodies, critical parameters, etc.) identified in the functional discrepancies analysis.

- [ ] 26. Fix critical functional gaps (HIGH PRIORITY)
  - [ ] 26.1 Document request body schemas for PUT operations
    - Extract Java classes used in PUT request bodies:
      - LayerInfo, StoreInfo, NamespaceInfo (catalog operations)
      - UserInfo, GroupInfo, RoleInfo (security operations)
      - ImportContext, TaskInfo, TransformInfo (importer operations)
      - DataStoreInfo, CoverageStoreInfo, WMSStoreInfo, WMTSStoreInfo
    - Generate JSON schemas from Java classes
    - Add schemas to OpenAPI spec components/schemas section
    - Reference schemas in PUT operation request bodies
    - Add example request bodies for common use cases
    - Affected endpoints: ~31 PUT operations
    - Output: Updated modular and bundled specifications
    - _Requirements: 6.5, 6.6, 7.1, 7.5_
  
  - [ ] 26.2 Document critical query parameters
    - Add `purge` parameter to DELETE datastore operations
      - Description: "If true, delete underlying data files; if false, delete only configuration"
      - Type: boolean
      - Default: false
      - **Critical:** Prevents accidental data loss
    - Add `async` and `exec` parameters to importer operations
      - `async`: Run import asynchronously (boolean, default: false)
      - `exec`: Execute import immediately after creation (boolean, default: false)
    - Add `recalculate` and `calculate` parameters to feature type operations
      - Controls whether bounding boxes are recalculated from data
      - Type: boolean
    - Output: Updated modular and bundled specifications
    - _Requirements: 7.3, 7.4_
  
  - [ ] 26.3 Document convenience query parameters
    - Add `expand` parameter to 6 importer endpoints
      - Description: "Controls level of detail in response (e.g., expand=tasks)"
      - Type: string
      - Optional
    - Add `offset` and `limit` parameters to OSEO collection endpoints
      - Pagination for large datasets
      - Type: integer
    - Add `styleName` parameter to POST /rest/layers
      - Specifies default style when creating layer
      - Type: string
    - Add `from` and `to` parameters to manifest/version endpoints
      - Filters by version range
      - Type: string
    - Output: Updated modular and bundled specifications
    - _Requirements: 7.3, 7.4_
  
  - [ ] 26.4 Fix GET /rest/logging anti-pattern
    - Investigate if request body is actually used in implementation
    - Review LoggingController.java to understand intent
    - If body is not used: Remove @RequestBody annotation from GET method
    - If body is used: Consider changing to POST or PUT method
    - Update OpenAPI documentation to match corrected implementation
    - Document decision and rationale
    - Output: Code fix (if needed) and updated specification
    - _Requirements: 7.1_
  
  - [ ] 26.5 Remove incorrect query parameters from documentation
    - Fix GET /rest/about/status endpoint
      - Remove documented parameters: manifest, key, value
      - These don't exist in implementation
    - Review other endpoints with "documented but not implemented" parameters
    - Remove or mark as deprecated in documentation
    - Output: Updated modular and bundled specifications
    - _Requirements: 3.3_

- [ ] 27. Fix cosmetic path variable naming (LOW PRIORITY)
  - [ ] 27.1 Update path variable names to match implementation
    - Update ~90 endpoints where path variable names differ
    - Change documentation to match Java @PathVariable names
    - Examples:
      - `importId` → `id`
      - `workspace` → `workspaceName`
      - `role` → `roleName`
      - `user` → `userName`
    - Use find-and-replace for efficiency
    - Validate specifications after changes
    - Output: Updated modular and bundled specifications
    - _Requirements: 6.1, 6.5_
  
  - [ ] 27.2 Validate cosmetic fixes
    - Run OpenAPI validation on updated specs
    - Verify all path parameters match path templates
    - Test in Swagger UI to ensure no regressions
    - Output: Validation report
    - _Requirements: 11.1, 11.2, 11.3_

- [ ] 28. Regenerate specifications with all fixes
  - [ ] 28.1 Re-bundle modular specifications
    - Resolve all $ref references
    - Apply all fixes from tasks 26-27
    - Generate bundled YAML and JSON versions
    - Output: `doc/en/api/geoserver-bundled.yaml` and `.json`
    - _Requirements: 6.7, 12.1, 12.2_
  
  - [ ] 28.2 Validate final specifications
    - Validate against OpenAPI 3.0 schema
    - Verify zero validation errors
    - Test in Swagger UI
    - Output: Final validation report
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [ ] 28.3 Update coverage metrics
    - Recalculate coverage with functional fixes applied
    - Expected results:
      - Fully correct: ~127 endpoints (36%)
      - Cosmetic fixes applied: ~90 endpoints (25.5%)
      - Total functionally complete: ~166 endpoints (47%)
    - Generate updated coverage report
    - Output: `.kiro/api-analysis/reports/rest-coverage-report-final.md`
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 29. Final checkpoint - Review all fixes
  - Review functional gap fixes (task 26)
  - Review cosmetic naming fixes (task 27)
  - Verify specifications are production-ready
  - Ask user if questions arise
