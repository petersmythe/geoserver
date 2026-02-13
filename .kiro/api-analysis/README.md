# GeoServer API Analysis Workspace

This directory contains intermediate outputs and reports from the GeoServer API documentation verification and generation system.

## Directory Structure

- `rest/` - REST API endpoint analysis data
- `ogc/` - OGC service operation analysis data
- `reports/` - Human-readable analysis reports (Markdown, CSV)
- `specs/` - Generated OpenAPI specifications

## Workflow

The analysis follows this workflow:

1. Parse existing OpenAPI documentation → `rest/documented-endpoints.json`
2. Extract REST endpoints from Java source → `rest/implemented-*-endpoints.json`
3. Extract OGC operations from implementations → `ogc/*-operations.json`
4. Compare and analyze coverage → `reports/*-coverage-report.md`
5. Generate unified OpenAPI 3.0 spec → `specs/*.yaml`

## Intermediate Files

### REST Analysis
- `rest/documented-endpoints.json` - Endpoints from existing OpenAPI specs
- `rest/controller-files.json` - List of Java controller classes
- `rest/implemented-core-endpoints.json` - Core REST endpoints
- `rest/implemented-service-endpoints.json` - Service-specific REST endpoints
- `rest/implemented-gwc-endpoints.json` - GeoWebCache REST endpoints
- `rest/implemented-extension-endpoints.json` - Extension REST endpoints
- `rest/implemented-community-endpoints.json` - Community REST endpoints
- `rest/implemented-all-endpoints.json` - Consolidated implemented endpoints
- `rest/endpoint-matches.json` - Matching results
- `rest/coverage-metrics.json` - Coverage statistics
- `rest/gaps.json` - Documentation gaps

### OGC Analysis
- `ogc/wms-operations.json` - WMS operations
- `ogc/wfs-operations.json` - WFS operations
- `ogc/wcs-operations.json` - WCS operations
- `ogc/wmts-operations.json` - WMTS operations
- `ogc/csw-operations.json` - CSW operations
- `ogc/wps-operations.json` - WPS operations
- `ogc/all-operations.json` - Consolidated OGC operations
- `ogc/spec-reference.json` - OGC specification reference data
- `ogc/*-compliance.json` - Compliance analysis per service

### Reports
- `reports/documented-summary.md` - Summary of existing documentation
- `reports/implemented-summary.md` - Summary of implemented endpoints
- `reports/rest-coverage-report.md` - REST API coverage analysis
- `reports/rest-coverage-report.csv` - REST coverage (CSV format)
- `reports/ogc-operations-summary.md` - OGC operations inventory
- `reports/ogc-compliance-report.md` - OGC compliance analysis
- `reports/ogc-compliance-report.csv` - OGC compliance (CSV format)
- `reports/reconciliation-matrix.md` - Comprehensive reconciliation
- `reports/reconciliation-matrix.csv` - Reconciliation (CSV format)
- `reports/validation-report.md` - OpenAPI validation results
- `reports/swagger-ui-test.md` - Swagger UI compatibility test
- `reports/executive-summary.md` - Executive summary
- `reports/action-plan.md` - Prioritized action plan

### Generated Specifications
- `specs/rest-openapi-3.0.yaml` - REST API OpenAPI 3.0 spec
- `specs/ogc-openapi-3.0.yaml` - OGC services OpenAPI 3.0 spec

## Notes

- All JSON files use pretty-printing with 2-space indentation
- Markdown reports are human-readable with tables and summaries
- CSV reports are suitable for spreadsheet analysis
- Generated specs are placed in `doc/en/api/` for repository commit
