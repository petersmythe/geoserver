# Design Document

## Overview

The GeoServer API Documentation Verification and Generation System is a comprehensive toolset for auditing, verifying, and generating complete OpenAPI 3.0 specifications for all GeoServer APIs. The system addresses two primary domains:

1. **REST API Documentation**: Verifies existing Swagger 2.0 specifications against actual Spring MVC implementations, identifies gaps, and generates updated OpenAPI 3.0 documentation
2. **OGC Service Documentation**: Extracts operation definitions from OGC service implementations (WMS, WFS, WCS, WMTS, CSW, WPS), cross-references against official OGC specifications, and generates comprehensive OpenAPI documentation

The system produces coverage reports, reconciliation matrices, and unified OpenAPI specifications suitable for consumption by standard tools (Swagger UI, Redoc) and MCP server generation.

### Key Design Decisions

- **Static Analysis First**: Primary approach uses AST parsing and annotation extraction rather than runtime introspection, enabling analysis without running GeoServer
- **Modular Architecture**: Separate parsers for REST endpoints, OGC services, and OpenAPI specs enable independent development and testing
- **OpenAPI 3.0 Target**: Upgrade from Swagger 2.0 to OpenAPI 3.0 for better tooling support and modern API documentation standards
- **Version-Aware OGC Documentation**: Each OGC service version (e.g., WMS 1.1.1, WMS 1.3.0) documented with distinct operation IDs but grouped under service tags
- **Extensible OGC Reference**: System parses official OGC specification documents to discover operations beyond predefined lists

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Entry Point                          │
│  (Command-line interface for all operations)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌────────▼────────┐
│  REST Pipeline  │      │  OGC Pipeline   │
└───────┬────────┘      └────────┬────────┘
        │                         │
        │                         │
┌───────▼────────────────────────▼────────┐
│         Parser Components                │
│  ┌──────────────────────────────────┐   │
│  │  OpenAPI Spec Parser             │   │
│  │  (Parses existing YAML specs)    │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  Java Annotation Parser          │   │
│  │  (Extracts REST endpoints)       │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  OGC Service Parser              │   │
│  │  (Extracts OGC operations)       │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  OGC Spec Parser                 │   │
│  │  (Parses official OGC docs)      │   │
│  └──────────────────────────────────┘   │
└──────────────┬───────────────────────────┘
               │
┌──────────────▼───────────────────────────┐
│      Analysis & Reconciliation           │
│  ┌──────────────────────────────────┐   │
│  │  Endpoint Matcher                │   │
│  │  (Matches impl vs docs)          │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  Coverage Calculator             │   │
│  │  (Computes coverage metrics)     │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  OGC Compliance Checker          │   │
│  │  (Validates against OGC specs)   │   │
│  └──────────────────────────────────┘   │
└──────────────┬───────────────────────────┘
               │
┌──────────────▼───────────────────────────┐
│      Generation & Output                 │
│  ┌──────────────────────────────────┐   │
│  │  OpenAPI 3.0 Generator           │   │
│  │  (Creates unified spec)          │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  Report Generator                │   │
│  │  (Coverage, reconciliation)      │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  Validator                       │   │
│  │  (OpenAPI schema validation)     │   │
│  └──────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

### Data Flow

1. **Input Phase**: System reads existing OpenAPI specs, Java source files, and OGC specification documents
2. **Parsing Phase**: Parsers extract endpoint/operation definitions into normalized internal representations
3. **Analysis Phase**: Matchers and calculators compare implementations against documentation and specifications
4. **Generation Phase**: Generators produce OpenAPI specs, coverage reports, and reconciliation matrices
5. **Validation Phase**: Validator ensures generated OpenAPI specs conform to schema

### Technology Stack

**Implementation Approach: AI Agent Task Execution (Option B)**

This system will be implemented as a series of AI agent tasks executed by Kiro, rather than as a standalone coded tool. This approach provides:

**Advantages**:
- No codebase to maintain or build
- Immediate execution without setup
- Flexible iteration and refinement
- Leverages Kiro's built-in file reading and analysis capabilities
- Easy to modify requirements and re-run
- Suitable for one-time or infrequent analysis

**Execution Model**:
- Each requirement becomes one or more discrete tasks
- Tasks produce intermediate outputs (JSON, CSV, Markdown files)
- Kiro reads source files, extracts information, and generates reports
- Final tasks aggregate results into unified OpenAPI specifications
- All outputs stored in `doc/en/api/` and `.kiro/api-analysis/` directories

**Task Dependencies**:
- Tasks execute sequentially with clear dependencies
- Early tasks produce data files consumed by later tasks
- Checkpoint tasks allow user review before proceeding
- Failed tasks can be retried without re-running entire pipeline

**No External Dependencies**:
- Uses Kiro's native capabilities for file I/O and text processing
- No Maven build, no external libraries to install
- Works immediately in any GeoServer repository clone

## Components and Interfaces

### 1. CLI Entry Point

**Purpose**: Provides command-line interface for all system operations

**Interface**:
```java
public class ApiDocCLI {
    public static void main(String[] args);
    
    // Subcommands
    void analyzeRest(RestAnalysisOptions options);
    void analyzeOgc(OgcAnalysisOptions options);
    void generateSpec(GenerationOptions options);
    void validateSpec(ValidationOptions options);
    void compareVersions(ComparisonOptions options);
}
```

**Key Operations**:
- `analyze-rest`: Parse REST endpoints and compare with documentation
- `analyze-ogc`: Extract OGC operations and cross-reference with specs
- `generate`: Create unified OpenAPI 3.0 specification
- `validate`: Validate generated OpenAPI specs
- `compare`: Compare endpoints between git tags

### 2. OpenAPI Spec Parser

**Purpose**: Parses existing Swagger 2.0 / OpenAPI specifications

**Interface**:
```java
public interface OpenApiSpecParser {
    ParsedSpec parse(Path specFile);
    List<ParsedSpec> parseDirectory(Path directory);
}

public class ParsedSpec {
    String version;  // "2.0" or "3.0.0"
    Map<String, PathItem> paths;
    Map<String, Schema> schemas;
    List<Tag> tags;
}

public class PathItem {
    String path;
    Map<HttpMethod, Operation> operations;
}

public class Operation {
    String operationId;
    List<Parameter> parameters;
    Map<String, Response> responses;
    List<String> tags;
}
```

**Implementation Notes**:
- Uses Swagger Parser library for robust YAML parsing
- Handles both Swagger 2.0 and OpenAPI 3.0 formats
- Normalizes path patterns (e.g., `/workspaces/{workspace}`)
- Extracts complete parameter and response definitions

### 3. Java Annotation Parser

**Purpose**: Extracts REST endpoint definitions from Java source code

**Interface**:
```java
public interface JavaAnnotationParser {
    List<RestEndpoint> parseDirectory(Path sourceDir);
    List<RestEndpoint> parseFile(Path javaFile);
}

public class RestEndpoint {
    String className;
    String methodName;
    HttpMethod httpMethod;
    String pathPattern;
    String basePath;  // from class-level annotation
    List<PathVariable> pathVariables;
    List<QueryParameter> queryParameters;
    RequestBody requestBody;
    ReturnType returnType;
}

public enum HttpMethod {
    GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS
}
```

**Implementation Notes**:
- Uses JavaParser library for AST-based analysis
- Recognizes Spring MVC annotations: `@RequestMapping`, `@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`, `@PatchMapping`
- Recognizes JAX-RS annotations: `@Path`, `@GET`, `@POST`, `@PUT`, `@DELETE`, `@PATCH`
- Combines class-level and method-level path patterns
- Extracts parameter information from method signatures and annotations
- Scans these directories: `src/rest/`, `src/restconfig/`, `src/restconfig-wcs/`, `src/restconfig-wfs/`, `src/restconfig-wms/`, `src/restconfig-wmts/`, `src/gwc-rest/`, `src/extension/`, `src/community/`

### 4. OGC Service Parser

**Purpose**: Extracts OGC service operation definitions from implementation classes

**Interface**:
```java
public interface OgcServiceParser {
    List<OgcOperation> parseService(ServiceType serviceType, String version);
    Map<ServiceType, Map<String, List<OgcOperation>>> parseAllServices();
}

public enum ServiceType {
    WMS, WFS, WCS, WMTS, CSW, WPS
}

public class OgcOperation {
    ServiceType serviceType;
    String version;  // e.g., "1.3.0", "2.0.0"
    String operationName;  // e.g., "GetCapabilities", "GetMap"
    List<OgcParameter> parameters;
    List<String> outputFormats;
    String requestInterface;  // Java interface/class name
}

public class OgcParameter {
    String name;
    String type;  // string, integer, bbox, crs, etc.
    boolean required;
    String defaultValue;
    List<String> validValues;
    boolean isVendorExtension;
}
```

**Implementation Notes**:
- Analyzes service interface definitions (e.g., `WebMapService.java`)
- Examines request classes (e.g., `GetMapRequest.java`) for parameter definitions
- Scans KVP reader classes (e.g., `GetMapKvpRequestReader.java`) for parameter parsing logic
- Identifies version-specific implementations by module structure (`src/wms/`, `src/wfs1_x/`, `src/wfs2_x/`, etc.)
- Extracts output format support from response classes

### 5. OGC Spec Parser

**Purpose**: Parses official OGC specification documents to extract standard requirements

**Interface**:
```java
public interface OgcSpecParser {
    OgcSpecification parseSpecification(ServiceType serviceType, String version, Path specDocument);
    List<OgcOperation> extractOperations(OgcSpecification spec);
}

public class OgcSpecification {
    ServiceType serviceType;
    String version;
    String title;
    URI sourceUri;
    List<OgcOperation> requiredOperations;
    List<OgcOperation> optionalOperations;
}
```

**Implementation Notes**:
- Parses OGC specification documents (typically XML or HTML)
- Extracts operation names, required parameters, and optional parameters
- Handles specification-specific formats (WMS uses different structure than WFS)
- Maintains reference URIs to official OGC documents
- Flags operations discovered beyond predefined lists

### 6. Endpoint Matcher

**Purpose**: Matches implemented endpoints with documented endpoints

**Interface**:
```java
public interface EndpointMatcher {
    MatchResult matchRestEndpoints(
        List<RestEndpoint> implemented,
        List<ParsedSpec> documented
    );
    
    MatchResult matchOgcOperations(
        List<OgcOperation> implemented,
        List<OgcOperation> specified
    );
}

public class MatchResult {
    List<EndpointMatch> matches;
    List<RestEndpoint> implementedOnly;
    List<Operation> documentedOnly;
    double coveragePercentage;
}

public class EndpointMatch {
    RestEndpoint implementation;
    Operation documentation;
    MatchQuality quality;  // EXACT, PARTIAL, MISMATCH
    List<String> differences;
}
```

**Implementation Notes**:
- Normalizes path patterns for comparison (handles different variable syntax)
- Considers HTTP method + path as unique identifier
- Detects parameter mismatches (missing, extra, type differences)
- Provides detailed difference reports for partial matches

### 7. Coverage Calculator

**Purpose**: Computes coverage metrics and generates reports

**Interface**:
```java
public interface CoverageCalculator {
    CoverageReport calculateRestCoverage(MatchResult matchResult);
    CoverageReport calculateOgcCoverage(MatchResult matchResult);
}

public class CoverageReport {
    int totalImplemented;
    int totalDocumented;
    int matched;
    double coveragePercentage;
    Map<String, ModuleCoverage> byModule;
    List<Gap> gaps;
}

public class ModuleCoverage {
    String moduleName;
    int implemented;
    int documented;
    double coverage;
}

public class Gap {
    GapType type;  // MISSING_DOCUMENTATION, MISSING_IMPLEMENTATION, MISMATCH
    String endpoint;
    String description;
}
```

**Implementation Notes**:
- Calculates overall coverage percentage
- Breaks down coverage by module (workspaces, layers, styles, etc.)
- Identifies specific gaps requiring attention
- Generates both summary and detailed reports

### 8. OGC Compliance Checker

**Purpose**: Validates GeoServer OGC implementations against official specifications

**Interface**:
```java
public interface OgcComplianceChecker {
    ComplianceReport checkCompliance(
        List<OgcOperation> implemented,
        OgcSpecification specification
    );
}

public class ComplianceReport {
    ServiceType serviceType;
    String version;
    List<ComplianceIssue> issues;
    boolean isCompliant;
}

public class ComplianceIssue {
    IssueType type;  // MISSING_REQUIRED_OPERATION, MISSING_REQUIRED_PARAMETER, etc.
    String operation;
    String parameter;
    String description;
    Severity severity;  // ERROR, WARNING, INFO
}
```

**Implementation Notes**:
- Checks for required operations mandated by OGC specifications
- Validates required parameters are present
- Identifies vendor extensions (non-standard parameters)
- Generates compliance reports suitable for certification processes

### 9. OpenAPI 3.0 Generator

**Purpose**: Generates unified OpenAPI 3.0 specification from parsed data

**Interface**:
```java
public interface OpenApiGenerator {
    OpenApiSpec generateRestSpec(List<RestEndpoint> endpoints);
    OpenApiSpec generateOgcSpec(Map<ServiceType, Map<String, List<OgcOperation>>> operations);
    OpenApiSpec generateUnifiedSpec(
        List<RestEndpoint> restEndpoints,
        Map<ServiceType, Map<String, List<OgcOperation>>> ogcOperations
    );
}

public class OpenApiSpec {
    String openapi = "3.0.0";
    Info info;
    List<Server> servers;
    Map<String, PathItem> paths;
    Components components;
    List<Tag> tags;
    
    void writeYaml(Path outputFile);
    void writeJson(Path outputFile);
}
```

**Implementation Notes**:
- Generates OpenAPI 3.0 format (not Swagger 2.0)
- Creates separate tags for REST API and each OGC service type
- Uses version-specific operation IDs (e.g., `WMS_1_1_GetMap`, `WMS_1_3_GetMap`)
- Groups operations by service type using tags
- Includes complete parameter definitions with types, descriptions, constraints
- Generates response schemas for success and error cases
- Places output in `doc/en/api/` directory

### 10. Report Generator

**Purpose**: Generates human-readable reports in multiple formats

**Interface**:
```java
public interface ReportGenerator {
    void generateCoverageReport(CoverageReport report, Path outputFile, ReportFormat format);
    void generateReconciliationMatrix(MatchResult matchResult, Path outputFile, ReportFormat format);
    void generateComplianceReport(ComplianceReport report, Path outputFile, ReportFormat format);
}

public enum ReportFormat {
    MARKDOWN, CSV, JSON, HTML
}
```

**Implementation Notes**:
- Markdown format for human readability
- CSV format for spreadsheet analysis
- JSON format for programmatic processing
- HTML format with sortable/filterable tables

### 11. Validator

**Purpose**: Validates generated OpenAPI specifications

**Interface**:
```java
public interface OpenApiValidator {
    ValidationResult validate(Path specFile);
}

public class ValidationResult {
    boolean isValid;
    List<ValidationError> errors;
    List<ValidationWarning> warnings;
}

public class ValidationError {
    String location;  // JSON path to error
    String message;
    String rule;  // OpenAPI rule violated
}
```

**Implementation Notes**:
- Uses Swagger Parser for OpenAPI 3.0 schema validation
- Verifies all `$ref` references resolve correctly
- Checks required fields are present
- Validates parameter types and constraints
- Reports errors with specific locations and messages

## Data Models

### Internal Representation

All parsers convert their inputs into normalized internal representations for consistent processing:

```java
// Unified endpoint representation
public class ApiEndpoint {
    EndpointType type;  // REST or OGC
    String path;
    HttpMethod method;
    String operationId;
    List<Parameter> parameters;
    RequestBody requestBody;
    Map<Integer, Response> responses;
    List<String> tags;
    String description;
    Map<String, Object> metadata;
}

// Unified parameter representation
public class Parameter {
    String name;
    ParameterLocation location;  // PATH, QUERY, HEADER, COOKIE
    String type;
    boolean required;
    String description;
    Object defaultValue;
    List<Object> enumValues;
    String format;
}

// Request body representation
public class RequestBody {
    boolean required;
    Map<String, MediaType> content;
}

// Response representation
public class Response {
    int statusCode;
    String description;
    Map<String, MediaType> content;
}

// Media type representation
public class MediaType {
    String mimeType;
    Schema schema;
    Map<String, Example> examples;
}
```

### Configuration

System behavior controlled by configuration file:

```yaml
# api-doc-config.yaml
sources:
  rest:
    - src/rest/
    - src/restconfig/
    - src/restconfig-wcs/
    - src/restconfig-wfs/
    - src/restconfig-wms/
    - src/restconfig-wmts/
    - src/gwc-rest/
    - src/extension/
    - src/community/
  
  ogc:
    wms:
      - src/wms/
    wfs:
      - src/wfs-core/
      - src/wfs1_x/
      - src/wfs2_x/
    wcs:
      - src/wcs/
      - src/wcs2_0/
    wmts:
      - src/gwc/
    csw:
      - src/extension/csw/
    wps:
      - src/extension/wps/

documentation:
  existing: doc/en/api/1.0.0/
  output: doc/en/api/

ogc_specifications:
  wms:
    "1.1.1": https://portal.ogc.org/files/?artifact_id=1081&version=1&format=pdf
    "1.3.0": https://portal.ogc.org/files/?artifact_id=14416
  wfs:
    "1.0.0": https://portal.ogc.org/files/?artifact_id=7176
    "1.1.0": https://portal.ogc.org/files/?artifact_id=8339
    "2.0.0": https://portal.ogc.org/files/?artifact_id=39967
  # ... other services

output:
  formats:
    - yaml
    - json
  reports:
    - coverage
    - reconciliation
    - compliance
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: OpenAPI Spec Parsing Completeness

*For any* valid OpenAPI/Swagger specification file, parsing should extract all endpoint definitions with their complete metadata (HTTP method, path, operation ID, parameters, response schemas).

**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

### Property 2: YAML Error Reporting

*For any* YAML file with syntax errors, the parser should report errors that include both the file name and line number where the error occurred.

**Validates: Requirements 1.5**

### Property 3: Spring MVC Annotation Detection

*For any* Java source file containing Spring MVC annotations (@RequestMapping, @GetMapping, @PostMapping, @PutMapping, @DeleteMapping, @PatchMapping), the parser should identify all annotated methods.

**Validates: Requirements 2.1**

### Property 4: JAX-RS Annotation Detection

*For any* Java source file containing JAX-RS annotations (@Path, @GET, @POST, @PUT, @DELETE, @PATCH), the parser should identify all annotated methods.

**Validates: Requirements 2.2**

### Property 5: REST Endpoint Metadata Extraction

*For any* annotated REST endpoint method, the parser should extract complete metadata including HTTP method, path pattern, all parameters (path variables, query parameters, request body), and return type.

**Validates: Requirements 2.3, 2.4**

### Property 6: Path Pattern Normalization and Composition

*For any* REST controller class with a base path and methods with relative paths, the parser should correctly combine them and normalize Spring path variables (e.g., `{workspaceName}`) to OpenAPI format.

**Validates: Requirements 2.6, 2.7**

### Property 7: Coverage Percentage Calculation

*For any* set of implemented endpoints and documented endpoints, the coverage percentage should equal (number of documented endpoints / number of implemented endpoints) × 100.

**Validates: Requirements 3.1**

### Property 8: Endpoint Set Difference

*For any* two sets of endpoints (implemented and documented), the system should correctly identify endpoints in one set but not the other (set difference operation).

**Validates: Requirements 3.2, 3.3, 9.2, 9.3**

### Property 9: Endpoint Grouping and Counting

*For any* set of endpoints with module/service labels, grouping by label and counting should produce correct counts for each group.

**Validates: Requirements 3.4**

### Property 10: Endpoint Matching Identity

*For any* two endpoints, they should match if and only if both their path patterns and HTTP methods are identical.

**Validates: Requirements 3.6**

### Property 11: OGC Operation Parameter Extraction

*For any* OGC service operation implementation, the parser should extract all parameters with their complete metadata (name, type, required status, valid values, default value).

**Validates: Requirements 4.7**

### Property 12: OGC Service Version Detection

*For any* OGC service implementation, the parser should correctly identify which standard version(s) it implements based on module structure and implementation classes.

**Validates: Requirements 4.8**

### Property 13: OGC Specification Parsing

*For any* official OGC specification document, the parser should extract all defined operations and their required parameters.

**Validates: Requirements 5.1**

### Property 14: Implementation vs Specification Comparison

*For any* set of implemented operations and specified operations, the comparison should identify all matches, missing implementations, and extra implementations.

**Validates: Requirements 5.2, 5.3, 5.4**

### Property 15: Vendor Extension Identification

*For any* parameter present in implementation but not in OGC specification, the system should mark it as a vendor extension.

**Validates: Requirements 5.4**

### Property 16: Discovered Operation Flagging

*For any* OGC operation found in specification documents but not in the predefined list, the system should include it in documentation with a discovery flag.

**Validates: Requirements 5.6**

### Property 17: OpenAPI 3.0 Format Generation

*For any* generated OpenAPI specification, it should validate successfully against the OpenAPI 3.0 schema (not Swagger 2.0).

**Validates: Requirements 6.1, 6.8**

### Property 18: Service Type Tag Organization

*For any* generated OpenAPI specification, operations should be grouped by service type using tags, with REST API and each OGC service type having distinct tags.

**Validates: Requirements 6.2, 6.4**

### Property 19: Version-Specific Operation IDs

*For any* OGC service operation across multiple versions, each version should have a distinct operation ID (e.g., WMS_1_1_GetMap vs WMS_1_3_GetMap).

**Validates: Requirements 6.3, 8.7**

### Property 20: Parameter Definition Completeness

*For any* endpoint parameter in the generated specification, it should include type, description, and constraints (required status, valid values, defaults).

**Validates: Requirements 6.5, 7.3, 7.4, 8.2**

### Property 21: Response Schema Completeness

*For any* operation in the generated specification, it should include response schemas for both successful responses and error responses.

**Validates: Requirements 6.6**

### Property 22: REST Endpoint Documentation Completeness

*For any* REST endpoint, the generated documentation should include HTTP method, path, all parameters, request body schema (if applicable), and response schema.

**Validates: Requirements 7.1**

### Property 23: Content Type Documentation

*For any* REST endpoint that accepts multiple content types, all supported content types should be documented in the specification.

**Validates: Requirements 7.2**

### Property 24: OGC Operation Documentation Completeness

*For any* OGC service operation, the generated documentation should include operation name, service type, version, purpose, and all parameters with their metadata.

**Validates: Requirements 8.1, 8.2**

### Property 25: Output Format Documentation

*For any* OGC operation supporting multiple output formats, all supported formats should be documented.

**Validates: Requirements 8.3**

### Property 26: Vendor Extension Marking

*For any* OGC operation parameter that is a vendor-specific extension, it should be clearly marked as a GeoServer extension in the documentation.

**Validates: Requirements 8.4**

### Property 27: Version Comparison Endpoint Detection

*For any* two git versions (current and tagged), comparing them should correctly identify all new endpoints, removed endpoints, and modified endpoints.

**Validates: Requirements 9.1, 9.2, 9.3, 9.4**

### Property 28: Reconciliation Status Classification

*For any* endpoint, its reconciliation status should be correctly classified as:
- "Complete" if implemented AND documented
- "Needs Documentation" if implemented AND NOT documented  
- "Needs Investigation" if documented AND NOT implemented

**Validates: Requirements 10.5, 10.6, 10.7**

### Property 29: Status Combination Counting

*For any* reconciliation matrix, the sum of row counts for all status combinations should equal the total number of unique endpoints.

**Validates: Requirements 10.3**

### Property 30: OpenAPI Reference Resolution

*For any* generated OpenAPI specification, all `$ref` references should resolve to valid schema definitions within the specification.

**Validates: Requirements 11.3**

### Property 31: Required Field Validation

*For any* schema in the generated OpenAPI specification, all fields marked as required in the OpenAPI 3.0 schema should be present.

**Validates: Requirements 11.4**

### Property 32: Validation Error Reporting

*For any* OpenAPI specification with validation errors, the error report should include specific error messages and JSON path locations for each error.

**Validates: Requirements 11.2**

### Property 33: JSON Pretty-Printing Format

*For any* JSON output generated by the system, it should be pretty-printed with 2-space indentation.

**Validates: Requirements 12.5**

## Error Handling

### Error Categories

1. **Parse Errors**: Invalid YAML syntax, malformed Java code, corrupted OGC specification documents
2. **Validation Errors**: Generated OpenAPI specs that don't conform to schema
3. **File System Errors**: Missing directories, permission issues, disk space
4. **Network Errors**: Failed downloads of OGC specification documents
5. **Configuration Errors**: Invalid configuration file, missing required settings

### Error Handling Strategy

**Parse Errors**:
- Report file name, line number, and specific syntax error
- Continue processing other files (fail gracefully per file)
- Include failed files in summary report with error details

**Validation Errors**:
- Report all validation errors with JSON paths
- Do not write invalid specifications to output
- Provide detailed error messages for debugging

**File System Errors**:
- Check directory existence before processing
- Verify write permissions before generating output
- Provide clear error messages with file paths

**Network Errors**:
- Retry failed downloads with exponential backoff
- Cache downloaded OGC specifications locally
- Allow operation to continue with cached/local specs if download fails

**Configuration Errors**:
- Validate configuration file on startup
- Provide default values for optional settings
- Fail fast with clear error message for required missing settings

### Error Recovery

- **Partial Results**: System should produce partial results even if some components fail
- **Error Logs**: Maintain detailed error log file for debugging
- **Exit Codes**: Use standard exit codes (0 = success, 1 = partial failure, 2 = complete failure)

## Testing Strategy

### Dual Testing Approach

The system requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests**: Verify specific examples, edge cases, and error conditions
- Parsing specific OpenAPI spec files with known structure
- Handling specific Java annotation patterns
- Processing specific OGC service implementations
- Error handling for malformed inputs
- Integration between components

**Property Tests**: Verify universal properties across all inputs
- All correctness properties defined above
- Randomized input generation for parsers
- Comprehensive coverage through 100+ iterations per property

### Property-Based Testing Configuration

- **Library**: Use QuickCheck for Java (JUnit-Quickcheck or jqwik)
- **Iterations**: Minimum 100 iterations per property test
- **Generators**: Custom generators for:
  - Valid OpenAPI specifications
  - Java source files with REST annotations
  - OGC operation definitions
  - Endpoint sets for comparison
- **Shrinking**: Enable automatic shrinking to find minimal failing examples

### Test Organization

```
src/test/java/
├── unit/
│   ├── parsers/
│   │   ├── OpenApiSpecParserTest.java
│   │   ├── JavaAnnotationParserTest.java
│   │   ├── OgcServiceParserTest.java
│   │   └── OgcSpecParserTest.java
│   ├── analysis/
│   │   ├── EndpointMatcherTest.java
│   │   ├── CoverageCalculatorTest.java
│   │   └── OgcComplianceCheckerTest.java
│   └── generation/
│       ├── OpenApiGeneratorTest.java
│       ├── ReportGeneratorTest.java
│       └── ValidatorTest.java
└── properties/
    ├── ParsingPropertiesTest.java
    ├── AnalysisPropertiesTest.java
    ├── GenerationPropertiesTest.java
    └── ValidationPropertiesTest.java
```

### Property Test Tagging

Each property test must reference its design document property:

```java
@Property
@Tag("Feature: geoserver-api-documentation-verification, Property 1: OpenAPI Spec Parsing Completeness")
void parsingExtractsAllEndpointMetadata(@ForAll("validOpenApiSpecs") OpenApiSpec spec) {
    ParsedSpec result = parser.parse(spec);
    // Verify all endpoints have complete metadata
    assertThat(result.getPaths()).allMatch(path -> 
        path.hasHttpMethod() && 
        path.hasOperationId() && 
        path.hasParameters() && 
        path.hasResponses()
    );
}
```

### Integration Testing

- **End-to-End Tests**: Run complete pipeline on GeoServer codebase
- **Regression Tests**: Maintain known-good outputs for comparison
- **Performance Tests**: Verify system handles large codebases efficiently

### Test Data

- **Sample OpenAPI Specs**: Collection of valid and invalid specs for testing
- **Sample Java Files**: REST controllers with various annotation patterns
- **Sample OGC Implementations**: Minimal service implementations for testing
- **OGC Specification Excerpts**: Relevant sections from official specs

## Implementation Notes

### Workflow and Pull Request Integration

**Analysis and Documentation Generation**:
1. Execute tasks to analyze codebase and generate documentation
2. Review generated OpenAPI specifications and reports
3. Identify gaps and issues in both documentation AND implementation

**Types of Issues Discovered**:

1. **Documentation-Only Issues**: Endpoints exist in code but not documented
   - Fix: Add/update OpenAPI YAML files
   - PR Type: Documentation update

2. **Implementation-Only Issues**: Endpoints documented but not implemented or incorrectly implemented
   - Fix: Update Java source code to match documentation
   - PR Type: Implementation fix

3. **Mismatch Issues**: Endpoint exists in both but parameters/responses don't match
   - Fix: Update either code or documentation (or both) to align
   - PR Type: Alignment fix

**Pull Request Strategy**:

Create separate, focused PRs for each logical group of changes:

**PR 1: Documentation Additions** (Low Risk)
- Add missing OpenAPI specs for undocumented endpoints
- No code changes
- Quick review and merge

**PR 2: Documentation Corrections** (Low Risk)
- Fix incorrect parameter types, descriptions, etc.
- No code changes
- Quick review and merge

**PR 3: Implementation Fix - [Module Name]** (Higher Risk)
- Fix missing or incorrect REST endpoint implementations
- Includes tests for the fixed endpoints
- Requires careful review
- One PR per module (e.g., "Fix workspace endpoint parameters")

**PR 4: Parameter Alignment - [Service]** (Medium Risk)
- Align code and docs where they mismatch
- May involve both code and doc changes
- One PR per service or logical grouping

**PR 5: Unified OpenAPI 3.0 Specification** (Low Risk)
- Add new unified spec file
- Generated from all previous fixes
- Final PR after others are merged

**PR Description Template for Code Fixes**:
```markdown
## Implementation Fix: [Module/Endpoint Name]

### Issue
[Description of what was wrong - missing endpoint, incorrect parameters, etc.]

### Root Cause
[Why the issue existed - annotation missing, wrong parameter type, etc.]

### Changes
- Modified: `src/[path]/[Controller].java`
- Added/Updated: Endpoint annotations
- Fixed: Parameter definitions

### Testing
- [ ] Unit tests added/updated
- [ ] Manual testing performed
- [ ] OpenAPI spec updated to match

### Validation
- [ ] Endpoint now appears in generated OpenAPI spec
- [ ] Parameters match documentation
- [ ] Response schemas correct

### Related
- Closes issue #[number]
- Related to documentation PR #[number]
```

**Prioritization**:
1. Start with documentation-only fixes (safest, fastest)
2. Then fix obvious implementation bugs (missing endpoints)
3. Finally address alignment issues (requires design decisions)

**Continuous Improvement**:
- Re-run analysis tasks after each PR merge
- Track coverage improvements over time
- Maintain high coverage percentage through regular updates

### Build Integration

The system is implemented as AI agent tasks rather than a standalone build artifact. No Maven module or build integration is required.

**Output Locations**:
- Analysis data: `.kiro/api-analysis/` (intermediate JSON/CSV files)
- Final specifications: `doc/en/api/` (OpenAPI YAML files)
- Reports: `.kiro/api-analysis/reports/` (Markdown and CSV reports)

**Execution**:
Tasks are executed through Kiro's task system. Users open the tasks.md file and click "Start task" to begin execution.

**Re-execution**:
Tasks can be re-run at any time to update documentation as the codebase evolves. Simply execute the tasks again to regenerate all outputs.

### Task Execution Interface

Tasks are executed through Kiro's task system rather than a CLI:

**Execution Flow**:
1. User opens `.kiro/specs/geoserver-api-documentation-verification/tasks.md`
2. User clicks "Start task" next to any task
3. Kiro executes the task, reading files and generating outputs
4. User reviews outputs and proceeds to next task
5. Checkpoint tasks pause for user review

**Task Outputs**:
- Intermediate data files in `.kiro/api-analysis/`
- Reports in `.kiro/api-analysis/reports/`
- Final OpenAPI specs in `doc/en/api/`

**Task Organization**:
- Phase 1: Parse existing documentation
- Phase 2: Extract REST endpoints from code
- Phase 3: Extract OGC operations from code
- Phase 4: Analyze and generate reports
- Phase 5: Generate unified OpenAPI specifications
- Phase 6: Validate generated specifications

### Performance Considerations

- **Parallel Processing**: Kiro can spawn sub-agents to process multiple files or modules concurrently
  - Multiple REST controller files can be analyzed in parallel
  - Different OGC services (WMS, WFS, WCS) can be processed simultaneously
  - OpenAPI spec files can be parsed concurrently
- **Incremental Outputs**: Each task produces outputs that can be reviewed before proceeding
- **File Streaming**: Large files are processed in chunks to manage memory
- **Caching**: Intermediate results stored in JSON files to avoid re-processing
- **Selective Analysis**: Users can choose to analyze only REST or only OGC services

### Extensibility

- **Plugin Architecture**: Allow custom parsers for additional annotation frameworks
- **Custom Generators**: Support custom output formats beyond OpenAPI
- **Hooks**: Provide hooks for custom validation rules
- **Configuration**: Externalize all configuration for easy customization
