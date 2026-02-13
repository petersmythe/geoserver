# GeoServer API Reconciliation Matrix

**Generated:** 2026-02-13 09:37:12

**Description:** Comprehensive reconciliation matrix combining REST and OGC analysis

## Executive Summary

- **Total Endpoints/Operations:** 220
- **REST Endpoints:** 165
- **OGC Operations:** 55
- **Complete (Implemented & Documented):** 214
- **Needs Documentation:** 5
- **Needs Investigation:** 1
- **Missing Both:** 0

**Overall Coverage:** 97.3%

## Status Breakdown

| Category | Count |
|----------|-------|
| Complete (Implemented & Documented) | 214 |
| Needs Documentation | 5 |
| Needs Investigation | 1 |
| Missing Both | 0 |

## Breakdown by Service

| Service | Count |
|---------|-------|
| REST API | 165 |
| WMS | 8 |
| WFS | 23 |
| WCS | 9 |
| WMTS | 3 |
| CSW | 7 |
| WPS | 5 |

## REST API Endpoints

### Summary

- Total REST Endpoints: 165
- Complete: 159
- Needs Documentation: 5
- Needs Investigation: 1

### REST Endpoints Detail

| Operation | Implemented | Documented | Status | Module | Issues |
|-----------|-------------|------------|--------|--------|--------|
| GET /rest/about/manifest | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| GET /rest/about/status | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/about/system-status | ✓ | ✓ | Complete | unknown | None |
| GET /rest/about/version | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| GET /rest/fonts | ✓ | ✓ | Complete | unknown | None |
| GET /rest/imports | ✓ | ✓ | Complete (with parameter mismatch) | importer | 1 issue(s) |
| GET /rest/imports/{var} | ✓ | ✓ | Complete (with parameter mismatch) | importer | 3 issue(s) |
| PUT /rest/imports/{var} | ✓ | ✓ | Complete (with parameter mismatch) | importer | 2 issue(s) |
| GET /rest/imports/{var}/tasks | ✓ | ✓ | Complete (with parameter mismatch) | importer | 2 issue(s) |
| POST /rest/imports/{var}/tasks | ✓ | ✓ | Complete (with parameter mismatch) | importer | 2 issue(s) |
| DELETE /rest/imports/{var}/tasks/{var} | ✓ | ✓ | Complete (with parameter mismatch) | importer | 1 issue(s) |
| GET /rest/imports/{var}/tasks/{var} | ✓ | ✓ | Complete (with parameter mismatch) | importer | 1 issue(s) |
| PUT /rest/imports/{var}/tasks/{var} | ✓ | ✓ | Complete (with parameter mismatch) | importer | 1 issue(s) |
| GET /rest/imports/{var}/tasks/{var}/layer | ✓ | ✓ | Complete (with parameter mismatch) | importer | 2 issue(s) |
| PUT /rest/imports/{var}/tasks/{var}/layer | ✓ | ✓ | Complete (with parameter mismatch) | importer | 3 issue(s) |
| GET /rest/imports/{var}/tasks/{var}/progress | ✓ | ✓ | Complete (with parameter mismatch) | importer | 1 issue(s) |
| GET /rest/imports/{var}/tasks/{var}/target | ✓ | ✓ | Complete (with parameter mismatch) | importer | 2 issue(s) |
| PUT /rest/imports/{var}/tasks/{var}/target | ✓ | ✓ | Complete (with parameter mismatch) | importer | 2 issue(s) |
| GET /rest/imports/{var}/data | ✓ | ✓ | Complete (with parameter mismatch) | importer | 1 issue(s) |
| GET /rest/imports/{var}/data/files | ✓ | ✓ | Complete (with parameter mismatch) | importer | 1 issue(s) |
| GET /rest/layergroups | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| POST /rest/layergroups | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| DELETE /rest/layergroups/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/layergroups/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| PUT /rest/layergroups/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/layers | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| POST /rest/layers | ✓ | ✓ | Complete (with parameter mismatch) | rat | 2 issue(s) |
| DELETE /rest/layers/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| GET /rest/layers/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| PUT /rest/layers/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| GET /rest/logging | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| PUT /rest/logging | ✓ | ✓ | Complete | unknown | None |
| GET /rest/namespaces | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| POST /rest/namespaces | ✓ | ✓ | Complete | unknown | None |
| GET /rest/namespaces/{var} | ✓ | ✓ | Complete | unknown | None |
| DELETE /rest/namespaces/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| PUT /rest/namespaces/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 3 issue(s) |
| GET /rest/oseo/collections | ✓ | ✓ | Complete | oseo | None |
| POST /rest/oseo/collections | ✓ | ✓ | Complete (with parameter mismatch) | oseo | 1 issue(s) |
| DELETE /rest/oseo/collections/{var} | ✓ | ✓ | Complete (with parameter mismatch) | oseo | 1 issue(s) |
| GET /rest/oseo/collections/{var} | ✓ | ✓ | Complete | oseo | None |
| PUT /rest/oseo/collections/{var} | ✓ | ✓ | Complete | oseo | None |
| DELETE /rest/oseo/collections/{var}/layer | ✓ | ✓ | Complete | oseo | None |
| GET /rest/oseo/collections/{var}/layer | ✓ | ✓ | Complete | oseo | None |
| PUT /rest/oseo/collections/{var}/layer | ✓ | ✓ | Complete (with parameter mismatch) | oseo | 1 issue(s) |
| GET /rest/oseo/collections/{var}/layers | ✓ | ✓ | Complete (with parameter mismatch) | oseo | 1 issue(s) |
| DELETE /rest/oseo/collections/{var}/layers/{var} | ✓ | ✓ | Complete | oseo | None |
| GET /rest/oseo/collections/{var}/layers/{var} | ✓ | ✓ | Complete | oseo | None |
| PUT /rest/oseo/collections/{var}/layers/{var} | ✓ | ✓ | Complete (with parameter mismatch) | oseo | 1 issue(s) |
| DELETE /rest/oseo/collections/{var}/ogcLinks | ✓ | ✓ | Complete | oseo | None |
| GET /rest/oseo/collections/{var}/ogcLinks | ✓ | ✓ | Complete | oseo | None |
| PUT /rest/oseo/collections/{var}/ogcLinks | ✓ | ✓ | Complete (with parameter mismatch) | oseo | 1 issue(s) |
| GET /rest/oseo/collections/{var}/products | ✓ | ✓ | Complete | oseo | None |
| POST /rest/oseo/collections/{var}/products | ✓ | ✓ | Complete | oseo | None |
| DELETE /rest/oseo/collections/{var}/products/{var} | ✓ | ✓ | Complete (with parameter mismatch) | oseo | 1 issue(s) |
| GET /rest/oseo/collections/{var}/products/{var} | ✓ | ✓ | Complete | oseo | None |
| PUT /rest/oseo/collections/{var}/products/{var} | ✓ | ✓ | Complete | oseo | None |
| DELETE /rest/oseo/collections/{var}/products/{var}/granules | ✓ | ✓ | Complete | oseo | None |
| GET /rest/oseo/collections/{var}/products/{var}/granules | ✓ | ✓ | Complete | oseo | None |
| PUT /rest/oseo/collections/{var}/products/{var}/granules | ✓ | ✓ | Complete (with parameter mismatch) | oseo | 1 issue(s) |
| DELETE /rest/oseo/collections/{var}/products/{var}/ogcLinks | ✓ | ✓ | Complete | oseo | None |
| GET /rest/oseo/collections/{var}/products/{var}/ogcLinks | ✓ | ✓ | Complete | oseo | None |
| PUT /rest/oseo/collections/{var}/products/{var}/ogcLinks | ✓ | ✓ | Complete (with parameter mismatch) | oseo | 1 issue(s) |
| DELETE /rest/oseo/collections/{var}/products/{var}/thumbnail | ✓ | ✓ | Complete | oseo | None |
| GET /rest/oseo/collections/{var}/products/{var}/thumbnail | ✓ | ✓ | Complete | oseo | None |
| PUT /rest/oseo/collections/{var}/products/{var}/thumbnail | ✓ | ✓ | Complete | oseo | None |
| GET /rest/security/roles | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| GET /rest/security/roles/group/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| DELETE /rest/security/roles/role/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/security/roles/role/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| DELETE /rest/security/roles/role/{var}/group/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/security/roles/role/{var}/group/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| DELETE /rest/security/roles/role/{var}/user/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/security/roles/role/{var}/user/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/security/roles/service/{var}/group/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/security/roles/service/{var}/user/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/security/roles/user/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| DELETE /rest/security/usergroup/group/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/security/usergroup/group/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/security/usergroup/group/{var}/users | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 3 issue(s) |
| GET /rest/security/usergroup/groups | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| DELETE /rest/security/usergroup/service/{var}/group/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/security/usergroup/service/{var}/group/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/security/usergroup/service/{var}/group/{var}/users | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/security/usergroup/service/{var}/groups | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| DELETE /rest/security/usergroup/service/{var}/user/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/security/usergroup/service/{var}/user/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| DELETE /rest/security/usergroup/service/{var}/user/{var}/group/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/security/usergroup/service/{var}/user/{var}/group/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/security/usergroup/service/{var}/user/{var}/groups | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/security/usergroup/service/{var}/users | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/security/usergroup/service/{var}/users | ✓ | ✓ | Complete | unknown | None |
| DELETE /rest/security/usergroup/user/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/security/usergroup/user/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| DELETE /rest/security/usergroup/user/{var}/group/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/security/usergroup/user/{var}/group/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/security/usergroup/user/{var}/groups | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 3 issue(s) |
| GET /rest/security/usergroup/users | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/security/usergroup/users | ✓ | ✓ | Complete | unknown | None |
| PUT /rest/services/oseo/settings | ✓ | ✓ | Complete (with parameter mismatch) | oseo | 1 issue(s) |
| PUT /rest/services/wcs/settings | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| PUT /rest/services/wfs/settings | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| PUT /rest/services/wms/settings | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| PUT /rest/services/wmts/settings | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| GET /rest/services/wps/download | ✓ | ✓ | Complete (with parameter mismatch) | wps-download | 1 issue(s) |
| PUT /rest/services/wps/download | ✓ | ✓ | Complete | wps-download | None |
| GET /rest/settings | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| PUT /rest/settings | ✓ | ✓ | Complete | unknown | None |
| GET /rest/settings/contact | ✓ | ✓ | Complete | unknown | None |
| PUT /rest/settings/contact | ✓ | ✓ | Complete | unknown | None |
| GET /rest/styles | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| POST /rest/styles | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| GET /rest/templates | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| GET /rest/urlchecks | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| POST /rest/urlchecks | ✓ | ✓ | Complete | unknown | None |
| DELETE /rest/urlchecks/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| PUT /rest/urlchecks/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/workspaces | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| POST /rest/workspaces | ✓ | ✓ | Complete | unknown | None |
| DELETE /rest/workspaces/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| GET /rest/workspaces/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| PUT /rest/workspaces/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/workspaces/{var}/appschemastores/{var}/cleanSchemas | ✓ | ✓ | Complete (with parameter mismatch) | mongodb | 2 issue(s) |
| POST /rest/workspaces/{var}/appschemastores/{var}/datastores/{var}/cleanSchemas | ✓ | ✓ | Complete (with parameter mismatch) | mongodb | 2 issue(s) |
| POST /rest/workspaces/{var}/appschemastores/{var}/datastores/{var}/rebuildMongoSchemas | ✓ | ✓ | Complete (with parameter mismatch) | mongodb | 2 issue(s) |
| POST /rest/workspaces/{var}/appschemastores/{var}/rebuildMongoSchemas | ✓ | ✓ | Complete (with parameter mismatch) | mongodb | 2 issue(s) |
| GET /rest/workspaces/{var}/coverages | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/workspaces/{var}/coverages | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/workspaces/{var}/coverages/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 3 issue(s) |
| GET /rest/workspaces/{var}/coveragestores | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/workspaces/{var}/coveragestores | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 3 issue(s) |
| DELETE /rest/workspaces/{var}/coveragestores/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/workspaces/{var}/coveragestores/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 3 issue(s) |
| PUT /rest/workspaces/{var}/coveragestores/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 3 issue(s) |
| GET /rest/workspaces/{var}/coveragestores/{var}/coverages | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| DELETE /rest/workspaces/{var}/coveragestores/{var}/coverages/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/workspaces/{var}/coveragestores/{var}/coverages/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 3 issue(s) |
| PUT /rest/workspaces/{var}/coveragestores/{var}/coverages/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/workspaces/{var}/datastores | ✓ | ✓ | Complete | unknown | None |
| POST /rest/workspaces/{var}/datastores | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| DELETE /rest/workspaces/{var}/datastores/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| GET /rest/workspaces/{var}/datastores/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| PUT /rest/workspaces/{var}/datastores/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| GET /rest/workspaces/{var}/datastores/{var}/{var}.{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 1 issue(s) |
| PUT /rest/workspaces/{var}/datastores/{var}/{var}.{var} | ✓ | ✓ | Complete | unknown | None |
| DELETE /rest/workspaces/{var}/settings | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/workspaces/{var}/settings | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/workspaces/{var}/settings | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| PUT /rest/workspaces/{var}/settings | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/workspaces/{var}/wmsstores | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/workspaces/{var}/wmsstores | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 3 issue(s) |
| DELETE /rest/workspaces/{var}/wmsstores/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/workspaces/{var}/wmsstores/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 4 issue(s) |
| PUT /rest/workspaces/{var}/wmsstores/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 3 issue(s) |
| GET /rest/workspaces/{var}/wmtsstores | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| POST /rest/workspaces/{var}/wmtsstores | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 3 issue(s) |
| DELETE /rest/workspaces/{var}/wmtsstores/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 2 issue(s) |
| GET /rest/workspaces/{var}/wmtsstores/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 4 issue(s) |
| PUT /rest/workspaces/{var}/wmtsstores/{var} | ✓ | ✓ | Complete (with parameter mismatch) | unknown | 3 issue(s) |
| DELETE  | ✓ | ✗ | Needs Documentation | metadata | 1 issue(s) |
| GET  | ✓ | ✗ | Needs Documentation | unknown | 1 issue(s) |
| POST  | ✓ | ✗ | Needs Documentation | unknown | 1 issue(s) |
| PUT  | ✓ | ✗ | Needs Documentation | params-extractor | 1 issue(s) |
| PATCH  | ✓ | ✗ | Needs Documentation | features-templating | 1 issue(s) |
|   | ✗ | ✓ | Needs Investigation | unknown | 1 issue(s) |

## OGC Service Operations

### Summary

- Total OGC Operations: 55
- Complete: 55
- Needs Implementation: 0
- Optional (Not Implemented): 0

### OGC Operations Detail

| Service | Version | Operation | Implemented | Documented | OGC Required | Status | Issues |
|---------|---------|-----------|-------------|------------|--------------|--------|--------|
| WMS | 1.1.1 | GetCapabilities | ✓ | ✓ | Yes/Optional | Complete | None |
| WMS | 1.1.1 | GetMap | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WMS | 1.1.1 | GetFeatureInfo | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WMS | 1.1.1 | DescribeLayer | ✓ | ✓ | Yes/Optional | Complete | None |
| WMS | 1.1.1 | GetLegendGraphic | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WMS | 1.3.0 | GetCapabilities | ✓ | ✓ | Yes/Optional | Complete | None |
| WMS | 1.3.0 | GetMap | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WMS | 1.3.0 | GetFeatureInfo | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WFS | 1.0.0 | GetCapabilities | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 1.0.0 | DescribeFeatureType | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 1.0.0 | GetFeature | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WFS | 1.0.0 | Transaction | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 1.0.0 | LockFeature | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 1.1.0 | GetCapabilities | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 1.1.0 | DescribeFeatureType | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 1.1.0 | GetFeature | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WFS | 1.1.0 | Transaction | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 1.1.0 | LockFeature | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 1.1.0 | GetFeatureWithLock | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 1.1.0 | GetGmlObject | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 2.0.0 | GetCapabilities | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 2.0.0 | DescribeFeatureType | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 2.0.0 | GetFeature | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WFS | 2.0.0 | ListStoredQueries | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 2.0.0 | DescribeStoredQueries | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 2.0.0 | GetPropertyValue | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 2.0.0 | Transaction | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 2.0.0 | LockFeature | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 2.0.0 | GetFeatureWithLock | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 2.0.0 | CreateStoredQuery | ✓ | ✓ | Yes/Optional | Complete | None |
| WFS | 2.0.0 | DropStoredQuery | ✓ | ✓ | Yes/Optional | Complete | None |
| WCS | 1.0.0 | GetCapabilities | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WCS | 1.0.0 | DescribeCoverage | ✓ | ✓ | Yes/Optional | Complete | None |
| WCS | 1.0.0 | GetCoverage | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WCS | 1.1.0 | GetCapabilities | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WCS | 1.1.0 | DescribeCoverage | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WCS | 1.1.0 | GetCoverage | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WCS | 2.0.0 | GetCapabilities | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WCS | 2.0.0 | DescribeCoverage | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WCS | 2.0.0 | GetCoverage | ✓ | ✓ | Yes/Optional | Complete | 1 issue(s) |
| WMTS | 1.0.0 | GetCapabilities | ✓ | ✓ | Yes/Optional | Complete (with extensions) | None |
| WMTS | 1.0.0 | GetTile | ✓ | ✓ | Yes/Optional | Complete (with extensions) | 1 issue(s) |
| WMTS | 1.0.0 | GetFeatureInfo | ✓ | ✓ | Yes/Optional | Complete | None |
| CSW | 2.0.2 | GetCapabilities | ✓ | ✓ | Yes/Optional | Complete (with extensions) | None |
| CSW | 2.0.2 | DescribeRecord | ✓ | ✓ | Yes/Optional | Complete | None |
| CSW | 2.0.2 | GetRecords | ✓ | ✓ | Yes/Optional | Complete (with extensions) | 1 issue(s) |
| CSW | 2.0.2 | GetRecordById | ✓ | ✓ | Yes/Optional | Complete | None |
| CSW | 2.0.2 | GetDomain | ✓ | ✓ | Yes/Optional | Complete | None |
| CSW | 2.0.2 | Transaction | ✓ | ✓ | Yes/Optional | Complete | None |
| CSW | 2.0.2 | Harvest | ✓ | ✓ | Yes/Optional | Complete (with extensions) | 1 issue(s) |
| WPS | 1.0.0 | GetCapabilities | ✓ | ✓ | Yes/Optional | Complete (with extensions) | None |
| WPS | 1.0.0 | DescribeProcess | ✓ | ✓ | Yes/Optional | Complete | None |
| WPS | 1.0.0 | Execute | ✓ | ✓ | Yes/Optional | Complete | None |
| WPS | 1.0.0 | GetExecutionStatus | ✓ | ✓ | No (Vendor Extension) | Complete (vendor extension) | None |
| WPS | 1.0.0 | Dismiss | ✓ | ✓ | No (Vendor Extension) | Complete (vendor extension) | None |

## Priority Actions

### High Priority: REST Endpoints Needing Documentation

- DELETE  (Module: metadata)
- GET  (Module: unknown)
- POST  (Module: unknown)
- PUT  (Module: params-extractor)
- PATCH  (Module: features-templating)

### Medium Priority: Endpoints Needing Investigation

-  

---

*Report generated from: 2026-02-13T09:34:11.643212*
