# GeoServer REST API Coverage Report

**Generated:** 2026-02-12

## Executive Summary

This report analyzes the coverage of GeoServer's REST API documentation against the actual implementation found in the source code.

### Overall Coverage

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Implemented Endpoints** | 353 | 100% |
| **Total Documented Endpoints** | 568 | - |
| **Matched Endpoints** | 6 | 1.7% |
| **Undocumented Endpoints** | 347 | 98.3% |
| **Unimplemented (Doc Only)** | 562 | - |

**Coverage Percentage: 1.7%**

⚠️ **Critical Finding:** Only 1.7% of implemented REST endpoints are documented in the existing OpenAPI specifications. This represents a significant documentation gap.

## Coverage by Module

The following table shows REST API coverage broken down by module:

| Module | Implemented | Documented | Coverage % |
|--------|-------------|------------|------------|
| restconfig | 182 | 6 | 3.3% |
| importer | 22 | 0 | 0.0% |
| features-templating | 18 | 0 | 0.0% |
| oseo | 35 | 0 | 0.0% |
| gsr | 33 | 0 | 0.0% |
| geofence | 11 | 0 | 0.0% |
| params-extractor | 10 | 0 | 0.0% |
| backup-restore | 6 | 0 | 0.0% |
| sldService | 5 | 0 | 0.0% |
| gwc | 5 | 0 | 0.0% |
| proxy-base-ext | 5 | 0 | 0.0% |
| mongodb | 4 | 0 | 0.0% |
| monitor | 3 | 0 | 0.0% |
| jms-cluster | 2 | 0 | 0.0% |
| rat | 2 | 0 | 0.0% |
| wps-download | 2 | 0 | 0.0% |
| rest | 1 | 0 | 0.0% |
| restconfig-wcs | 1 | 0 | 0.0% |
| restconfig-wfs | 1 | 0 | 0.0% |
| restconfig-wms | 1 | 0 | 0.0% |
| restconfig-wmts | 1 | 0 | 0.0% |
| metadata | 1 | 0 | 0.0% |
| taskmanager | 1 | 0 | 0.0% |
| vector-mosaic | 1 | 0 | 0.0% |

### Module Analysis

- **Total Modules Analyzed:** 24
- **Modules with Full Coverage (100%):** 0
- **Modules with Partial Coverage (1-99%):** 1 (restconfig)
- **Modules with No Coverage (0%):** 23

## Matched Endpoints

The following 6 endpoints are both implemented and documented:

### 1. GET /rest/security/acl/catalog
- **Module:** restconfig
- **Source:** `src/restconfig/src/main/java/org/geoserver/rest/security/CatalogModeController.java`
- **Operation ID:** getCatalogMode
- **Status:** ⚠️ Parameter mismatch (Implementation has request body but documentation does not)

### 2. PUT /rest/security/acl/catalog
- **Module:** restconfig
- **Source:** `src/restconfig/src/main/java/org/geoserver/rest/security/CatalogModeController.java`
- **Operation ID:** (none)
- **Status:** ✅ Exact match

### 3. GET /rest/security/masterpw
- **Module:** restconfig
- **Source:** `src/restconfig/src/main/java/org/geoserver/rest/security/MasterPasswordController.java`
- **Operation ID:** getMasterPW
- **Status:** ✅ Exact match

### 4. PUT /rest/security/masterpw
- **Module:** restconfig
- **Source:** `src/restconfig/src/main/java/org/geoserver/rest/security/MasterPasswordController.java`
- **Operation ID:** putMasterPW
- **Status:** ⚠️ Parameter mismatch (Documentation has request body but implementation does not)

### 5. GET /rest/security/self/password
- **Module:** restconfig
- **Source:** `src/restconfig/src/main/java/org/geoserver/rest/security/UserPasswordController.java`
- **Operation ID:** getSelfPassword
- **Status:** ✅ Exact match

### 6. PUT /rest/security/self/password
- **Module:** restconfig
- **Source:** `src/restconfig/src/main/java/org/geoserver/rest/security/UserPasswordController.java`
- **Operation ID:** putSelfPassword
- **Status:** ⚠️ Parameter mismatch (Documentation has request body but implementation does not)

## Undocumented Endpoints (Sample)

The following is a sample of the 347 endpoints that are implemented but not documented. For the complete list, see `.kiro/api-analysis/rest/gaps.json`.

### Core REST Configuration (restconfig module)
- Multiple endpoints in `AuthenticationProviderRestController.java`
- Resource management endpoints in `ResourceController.java`
- Various security configuration endpoints

### Extension Modules

#### Importer Extension (22 endpoints)
- Bulk data import functionality
- Import task management
- Transform operations

#### Features Templating Extension (18 endpoints)
- Template management
- Feature output customization

#### OSEO Extension (35 endpoints)
- OpenSearch for Earth Observation
- Collection and product management

#### GSR Extension (33 endpoints)
- ArcGIS REST API compatibility layer
- Relationship management
- Feature service operations

#### GeoFence Extension (11 endpoints)
- Advanced authorization rules
- Access control management

#### Params Extractor Extension (10 endpoints)
- URL parameter extraction rules
- Echo parameter management

#### Backup/Restore Extension (6 endpoints)
- Configuration backup
- Restore operations

### Community Modules

#### MongoDB (4 endpoints)
- MongoDB data store configuration

#### Monitor (3 endpoints)
- Request monitoring and statistics

#### Proxy Base Extension (5 endpoints)
- Proxy base URL rules

#### SLD Service (5 endpoints)
- SLD generation and management

#### Task Manager (1 endpoint)
- Scheduled task management

## Unimplemented Endpoints (Documented Only)

There are 562 endpoints documented in the OpenAPI specifications that were not found in the implementation. This could indicate:

1. **Documentation for planned features** not yet implemented
2. **Outdated documentation** for removed features
3. **Parsing limitations** where the endpoint exists but wasn't detected
4. **Different path patterns** between documentation and implementation

**Recommendation:** Manual review of a sample of these endpoints is needed to determine the root cause.

## Parameter Mismatches

3 endpoints have parameter mismatches between implementation and documentation:

1. **GET /rest/security/acl/catalog** - Implementation has request body but documentation does not
2. **PUT /rest/security/masterpw** - Documentation has request body but implementation does not
3. **PUT /rest/security/self/password** - Documentation has request body but implementation does not

## Recommendations

### Immediate Actions (High Priority)

1. **Document Core REST Configuration Endpoints**
   - Focus on the 182 restconfig endpoints (only 3.3% documented)
   - These are the most commonly used REST APIs

2. **Fix Parameter Mismatches**
   - Resolve the 3 endpoints with parameter discrepancies
   - Ensure implementation and documentation align

3. **Document Extension Modules**
   - Prioritize frequently used extensions: importer, monitor, geofence
   - Document community modules that have graduated to extensions

### Medium-Term Actions

4. **Investigate Unimplemented Endpoints**
   - Review the 562 documented-only endpoints
   - Remove obsolete documentation or implement missing features

5. **Establish Documentation Standards**
   - Create guidelines for documenting new REST endpoints
   - Require OpenAPI documentation for all new endpoints

6. **Automate Documentation Generation**
   - Use annotations to generate OpenAPI specs from code
   - Implement CI checks to detect undocumented endpoints

### Long-Term Actions

7. **Complete Coverage**
   - Document all 353 implemented endpoints
   - Achieve 100% coverage across all modules

8. **Maintain Documentation**
   - Keep documentation synchronized with code changes
   - Regular audits to prevent documentation drift

## Data Sources

- **Implemented Endpoints:** `.kiro/api-analysis/rest/implemented-all-endpoints.json`
- **Documented Endpoints:** `.kiro/api-analysis/rest/documented-endpoints.json`
- **Endpoint Matches:** `.kiro/api-analysis/rest/endpoint-matches.json`
- **Coverage Metrics:** `.kiro/api-analysis/rest/coverage-metrics.json`
- **Gaps Analysis:** `.kiro/api-analysis/rest/gaps.json`

## Notes

- Analysis performed on source code in `src/` directory
- Existing documentation from `doc/en/api/1.0.0/` directory
- Includes core modules, extensions, and community modules
- Path normalization applied for consistent matching
