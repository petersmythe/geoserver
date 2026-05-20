# Post-Rebase Sync Report

## Summary

Comparison between branch point (`6eb3aff421`, Feb 9 2026) and current main (`33ae7b19ef`, May 18 2026).

**Scope**: REST/OGC controllers in `src/rest/`, `src/restconfig/`, `src/restconfig-wcs/`, `src/restconfig-wfs/`, `src/restconfig-wms/`, `src/restconfig-wmts/`, `src/gwc-rest/`, `src/extension/`, `src/community/`, `src/wms/`, `src/wfs-core/`, `src/wfs1_x/`, `src/wfs2_x/`, `src/wcs/`, `src/wcs2_0/`, `src/gwc/`, `src/ows/`

## Changed Files

- **635** non-test Java files changed total
- **17** files contain REST annotations (`@RequestMapping`, `@GetMapping`, etc.)
- **0** deleted controllers
- **0** renamed controllers

## API Surface Changes

### New Endpoints (1 controller)

| Controller | Module | Endpoints Added |
|---|---|---|
| `CRSController` | restconfig (core) | 4 new GET endpoints |

**New CRS endpoints:**
- `GET /rest/crs` — List supported CRS codes (paginated, filterable by authority/query)
- `GET /rest/crs/authorities` — List available CRS authorities (EPSG, IAU, etc.)
- `GET /rest/crs/{identifier}.wkt` — Get CRS WKT definition
- `GET /rest/crs/{identifier}.json` — Get CRS definition as JSON (id, name, bbox, bboxWGS84, definition)

### Removed Endpoints (1 endpoint)

| Controller | Module | Endpoint Removed |
|---|---|---|
| `DataStoreFileController` | restconfig (core) | `GET /rest/workspaces/{workspaceName}/datastores/{storeName}/{method}.{format}` |

The GET endpoint that returned datastore files as a ZIP archive was removed. The PUT endpoint for uploading files remains.

### Modified Controllers (no API surface changes)

The following controllers had internal implementation changes only (library migrations, validation improvements, copy policy changes) with **no changes to endpoint paths, methods, or parameters**:

| Controller | Change Type |
|---|---|
| `FeatureLayerController` (community/gsr) | Internal refactoring |
| `ImagesService` (community/ogcapi) | Internal refactoring |
| `VectorMosaicStoreController` (community/vector-mosaic) | Method signature update |
| `ImportTaskController` (extension/importer) | Library migration (net.sf.json → org.kordamp.json) |
| `ImportTransformController` (extension/importer) | Library migration |
| `ClassifierController` (extension/sldService) | Library migration |
| `LocalSettingsController` (restconfig) | Validation improvements |
| `LoggingController` (restconfig) | Comment addition |
| `SettingsController` (restconfig) | PropertyCopyPolicy integration |
| `CoverageStoreFileController` (restconfig) | File validation enhancement |
| `DataStoreFileController` (restconfig) | GET endpoint removed (see above) |
| `TemplateController` (restconfig) | Input validation added |
| `AuthenticationFilterChainRestController` (restconfig/security) | Internal refactoring |
| `AuthenticationProviderRestController` (restconfig/security) | Allow-list caching |
| `DataAccessController` (restconfig/security) | Internal refactoring |
| `ServiceSettingsController` (restconfig/service) | PropertyCopyPolicy integration |

### OGC Service Changes

No new OGC operations or parameters were added. Changes to OGC service files were:
- `WMTSServiceInfoImpl` — New internal service info class (not a new endpoint)
- `ServiceVersionFilter` — New infrastructure filter (not a new endpoint)
- `PropertyCopyPolicy` — New utility class for property copying
- Various internal refactoring across WMS/WFS/WCS modules (no API surface changes)

## Spec Updates Applied

1. **Added** 4 new CRS endpoints to `specs/rest/rest-core.yaml`
2. **Removed** GET operation from DataStoreFileController path in `specs/rest/rest-core.yaml`
3. **Re-bundled** `doc/en/api/geoserver-bundled.yaml` and `.json` (312 total paths)
4. **Fixed** bundler bug where `#/components/schemas/` references in fragment files caused errors

## Bundler Fix

Fixed a bug in `bundle-spec.py` where internal `#/components/schemas/...` references within the `common/schemas.yaml` fragment file caused a `ValueError` during bundling. The fix preserves these references as-is in the bundled output (they resolve correctly in the final self-contained spec).
