# Requirements Document

## Introduction

This document specifies the requirements for a comprehensive GeoServer API documentation verification and generation system. The system will audit existing REST API documentation against actual implementations, identify gaps, and generate complete OpenAPI 3.0 specifications for both REST endpoints and OGC standard service endpoints (WMS, WFS, WCS, WMTS, CSW, WPS). The goal is to enable creation of an MCP (Model Context Protocol) server that provides AI assistants with complete, accurate documentation of all GeoServer functionality.

## Glossary

- **OpenAPI**: A specification standard for describing REST APIs, formerly known as Swagger
- **REST_API**: GeoServer's RESTful configuration and management API endpoints
- **OGC_Service**: Standards-based geospatial service endpoints (WMS, WFS, WCS, WMTS, CSW, WPS)
- **Endpoint**: A specific URL path and HTTP method combination that provides API functionality
- **Coverage_Report**: A document showing the percentage of implemented endpoints that are documented
- **Reconciliation_Matrix**: A comparison table showing implemented vs documented vs OGC specification requirements
- **Parser**: A component that extracts endpoint information from source code or documentation files
- **MCP_Server**: Model Context Protocol server that exposes API documentation to AI assistants
- **Spring_Annotation**: Java annotations like @RequestMapping, @GetMapping that define REST endpoints
- **JAX-RS**: Java API for RESTful Web Services, an alternative to Spring MVC
- **YAML_Spec**: OpenAPI specification file in YAML format
- **Service_Implementation**: Java classes that implement OGC service operations

## Requirements

### Requirement 1: Parse Existing OpenAPI Documentation

**User Story:** As a documentation maintainer, I want to parse all existing OpenAPI specifications, so that I can understand what endpoints are currently documented.

#### Acceptance Criteria

1. WHEN the Parser processes the doc/en/api/1.0.0/ directory, THE Parser SHALL extract all endpoint definitions from YAML files
2. WHEN an endpoint is extracted, THE Parser SHALL capture the HTTP method, path, operation ID, parameters, and response schemas
3. WHEN parsing is complete, THE Parser SHALL generate a structured inventory of all documented endpoints
4. THE Parser SHALL handle Swagger 2.0 format specifications correctly
5. WHEN a YAML file contains syntax errors, THE Parser SHALL report the error with file name and line number

### Requirement 2: Extract REST Endpoints from Java Source Code

**User Story:** As a documentation maintainer, I want to extract REST endpoint definitions from Java source code, including extensions and community modules, so that I can identify all implemented endpoints.

#### Acceptance Criteria

1. WHEN the Parser scans Java source files, THE Parser SHALL identify Spring MVC annotations (@RequestMapping, @GetMapping, @PostMapping, @PutMapping, @DeleteMapping, @PatchMapping)
2. WHEN the Parser scans Java source files, THE Parser SHALL identify JAX-RS annotations (@Path, @GET, @POST, @PUT, @DELETE, @PATCH)
3. WHEN an annotated method is found, THE Parser SHALL extract the HTTP method, path pattern, parameters, and return type
4. THE Parser SHALL resolve path variables and request parameters from method signatures
5. THE Parser SHALL scan these source directories: src/rest/, src/restconfig/, src/restconfig-wcs/, src/restconfig-wfs/, src/restconfig-wms/, src/restconfig-wmts/, src/gwc-rest/, src/extension/, src/community/
6. WHEN path patterns use Spring path variables, THE Parser SHALL normalize them to OpenAPI format (e.g., {workspaceName})
7. WHEN a class has a base path annotation, THE Parser SHALL combine it with method-level paths

### Requirement 3: Generate REST API Coverage Report

**User Story:** As a documentation maintainer, I want to see which REST endpoints are documented versus implemented, so that I can identify documentation gaps.

#### Acceptance Criteria

1. WHEN the Coverage_Report is generated, THE System SHALL calculate the percentage of implemented endpoints that have documentation
2. WHEN the Coverage_Report is generated, THE System SHALL list endpoints that exist in code but not in documentation
3. WHEN the Coverage_Report is generated, THE System SHALL list endpoints that exist in documentation but not in code
4. THE Coverage_Report SHALL include endpoint counts by module (workspaces, layers, styles, etc.)
5. THE Coverage_Report SHALL be output in both human-readable (Markdown) and machine-readable (JSON) formats
6. WHEN endpoints are matched, THE System SHALL consider path patterns and HTTP methods together as the unique identifier

### Requirement 4: Extract OGC Service Endpoints from Implementation

**User Story:** As a documentation maintainer, I want to extract OGC service operation definitions from service implementations, so that I can document all standard operations.

#### Acceptance Criteria

1. WHEN the Parser scans WMS service implementations, THE Parser SHALL identify GetCapabilities, GetMap, GetFeatureInfo, DescribeLayer, and GetLegendGraphic operations
2. WHEN the Parser scans WFS service implementations, THE Parser SHALL identify GetCapabilities, DescribeFeatureType, GetFeature, LockFeature, Transaction operations
3. WHEN the Parser scans WCS service implementations, THE Parser SHALL identify GetCapabilities, DescribeCoverage, GetCoverage operations
4. WHEN the Parser scans WMTS service implementations, THE Parser SHALL identify GetCapabilities, GetTile, GetFeatureInfo operations
5. WHEN the Parser scans CSW service implementations, THE Parser SHALL identify GetCapabilities, DescribeRecord, GetRecords, GetRecordById operations
6. WHEN the Parser scans WPS service implementations, THE Parser SHALL identify GetCapabilities, DescribeProcess, Execute operations
7. FOR ALL OGC service operations, THE Parser SHALL extract all supported parameters including required/optional status and valid values
8. THE Parser SHALL identify which OGC standard versions are supported (e.g., WMS 1.1.1, WMS 1.3.0)

### Requirement 5: Cross-Reference Against OGC Specifications

**User Story:** As a documentation maintainer, I want to compare extracted OGC operations against official OGC specifications, so that I can verify completeness.

#### Acceptance Criteria

1. THE System SHALL parse official OGC specification documents to extract standard operations and parameters
2. WHEN generating the Reconciliation_Matrix, THE System SHALL compare implemented operations against OGC specification requirements
3. WHEN an OGC-required parameter is missing from implementation, THE System SHALL flag it in the report
4. WHEN an implementation includes non-standard parameters, THE System SHALL document them as extensions
5. THE Reconciliation_Matrix SHALL be organized by service type (WMS, WFS, WCS, WMTS, CSW, WPS) and version
6. WHEN the System discovers OGC operations not in the predefined list, THE System SHALL include them in the documentation with a flag indicating they were discovered from specifications
7. THE System SHALL reference official OGC specification documents for each service type and version

### Requirement 6: Generate Unified OpenAPI 3.0 Specification

**User Story:** As an API consumer, I want a single OpenAPI 3.0 specification file covering all GeoServer APIs, so that I can use standard tools to explore and interact with the API.

#### Acceptance Criteria

1. THE System SHALL generate OpenAPI 3.0 format specifications (not Swagger 2.0)
2. THE System SHALL create separate tags for REST API endpoints and each OGC service type
3. WHEN documenting OGC service operations, THE System SHALL use separate operation IDs for different versions (e.g., WMS_1_1_GetMap, WMS_1_3_GetMap)
4. WHEN documenting OGC service operations, THE System SHALL group operations by service type using tags (e.g., WMS, WFS, WCS)
5. WHEN generating the specification, THE System SHALL include complete parameter definitions with types, descriptions, and constraints
6. WHEN generating the specification, THE System SHALL include response schemas for successful and error responses
7. THE System SHALL place the generated specification in doc/en/api/ directory
8. THE generated specification SHALL be valid according to OpenAPI 3.0 schema validation
9. THE generated specification SHALL be consumable by Swagger UI, Redoc, and other standard OpenAPI tools

### Requirement 7: Document REST API Endpoints

**User Story:** As an API consumer, I want complete documentation for all REST configuration endpoints, so that I can programmatically manage GeoServer.

#### Acceptance Criteria

1. FOR ALL REST endpoints, THE System SHALL document the HTTP method, path, parameters, request body schema, and response schema
2. WHEN a REST endpoint accepts multiple content types, THE System SHALL document all supported types (JSON, XML, HTML)
3. WHEN a REST endpoint has query parameters, THE System SHALL document parameter names, types, required status, and default values
4. WHEN a REST endpoint has path variables, THE System SHALL document variable names and valid value patterns
5. THE System SHALL include example requests and responses for common use cases
6. THE System SHALL document authentication and authorization requirements for each endpoint

### Requirement 8: Document OGC Service Endpoints

**User Story:** As an API consumer, I want complete documentation for all OGC service operations, so that I can use GeoServer's standards-based geospatial services.

#### Acceptance Criteria

1. FOR ALL OGC service operations, THE System SHALL document the operation name, service type, version, and purpose
2. FOR ALL OGC service parameters, THE System SHALL document parameter name, type, required status, valid values, and default value
3. WHEN an OGC operation supports multiple output formats, THE System SHALL document all supported formats
4. WHEN an OGC operation has vendor-specific extensions, THE System SHALL clearly mark them as GeoServer extensions
5. THE System SHALL document coordinate reference system (CRS) parameters and supported EPSG codes
6. THE System SHALL document exception/error response formats for each service type
7. WHEN different service versions have different parameters or responses, THE System SHALL document each version separately with distinct operation IDs
8. THE System SHALL document version-specific differences in parameter names, types, or valid values

### Requirement 9: Support Incremental Updates

**User Story:** As a documentation maintainer, I want to identify API changes since a specific release, so that I can update documentation incrementally.

#### Acceptance Criteria

1. WHEN a git tag is specified, THE System SHALL compare current code against that tagged version
2. WHEN generating a changes report, THE System SHALL identify new endpoints added since the tag
3. WHEN generating a changes report, THE System SHALL identify endpoints removed since the tag
4. WHEN generating a changes report, THE System SHALL identify endpoints with modified parameters or signatures
5. THE changes report SHALL be output in Markdown format with clear categorization

### Requirement 10: Generate Reconciliation Matrix

**User Story:** As a project manager, I want a comprehensive comparison of implemented vs documented vs specified endpoints, so that I can prioritize documentation work.

#### Acceptance Criteria

1. THE Reconciliation_Matrix SHALL have columns for: Endpoint/Operation, Implemented (Yes/No), Documented (Yes/No), OGC Required (Yes/No/N/A)
2. THE Reconciliation_Matrix SHALL be sortable and filterable by service type and status
3. THE Reconciliation_Matrix SHALL include row counts for each status combination
4. THE Reconciliation_Matrix SHALL be output in both Markdown and CSV formats
5. WHEN an endpoint is implemented and documented, THE System SHALL mark it as "Complete"
6. WHEN an endpoint is implemented but not documented, THE System SHALL mark it as "Needs Documentation"
7. WHEN an endpoint is documented but not implemented, THE System SHALL mark it as "Needs Investigation"

### Requirement 11: Validate Generated Specifications

**User Story:** As a documentation maintainer, I want generated OpenAPI specifications to be validated, so that I can ensure they are correct and usable.

#### Acceptance Criteria

1. WHEN a specification is generated, THE System SHALL validate it against the OpenAPI 3.0 schema
2. WHEN validation errors are found, THE System SHALL report them with specific error messages and locations
3. THE System SHALL verify that all $ref references resolve correctly
4. THE System SHALL verify that all required fields are present in schemas
5. WHEN validation passes, THE System SHALL output a success message with the specification file path

### Requirement 12: Support Multiple Output Formats

**User Story:** As a tool integrator, I want API documentation in multiple formats, so that I can integrate with different systems.

#### Acceptance Criteria

1. THE System SHALL generate OpenAPI specifications in YAML format
2. THE System SHALL optionally generate OpenAPI specifications in JSON format
3. THE System SHALL generate coverage reports in Markdown format
4. THE System SHALL generate reconciliation matrices in CSV format
5. WHEN generating JSON output, THE System SHALL use pretty-printing with 2-space indentation
