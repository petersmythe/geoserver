# Accurate REST API Coverage Calculation

## Summary

| Metric | Count |
|--------|-------|
| Total implemented REST endpoints (from Java source) | 426 |
| Implemented endpoints with /rest/ or /gwc/rest/ prefix | 314 |
| Total documented REST operations (from bundled YAML) | 471 |
| Exact matches (path + method identical) | 260 |
| Fuzzy matches (path pattern similar, variable names differ) | 42 |
| Total matched | 302 |
| Unmatched implemented endpoints | 124 |
| **Coverage (matched / all implemented)** | **70.9%** |
| **Coverage (matched / REST-prefixed only)** | **96.2%** |

## Implemented Endpoints by Category

| Category | Count |
|----------|-------|
| community | 152 |
| core | 195 |
| extension | 79 |

## Implemented Endpoints by HTTP Method

| Method | Implemented | Documented |
|--------|-------------|------------|
| DELETE | 62 | 86 |
| GET | 213 | 210 |
| PATCH | 3 | 2 |
| POST | 81 | 81 |
| PUT | 67 | 92 |

## Fuzzy Matches (variable name differences)

These endpoints matched after normalizing path variable names:

| Method | Implemented Path | Documented Path |
|--------|-----------------|-----------------|
| GET | `/gsr/services/{workspaceName:.*}/FeatureServer` | `/gsr/services/{workspaceName}/FeatureServer` |
| GET | `/gsr/services/{workspaceName:.*}/FeatureServer/query` | `/gsr/services/{workspaceName}/FeatureServer/query` |
| GET | `/rest/br/backup/{backupId:.+}` | `/rest/br/backup/{backupId}` |
| DELETE | `/rest/br/backup/{backupId:.+}` | `/rest/br/backup/{backupId}` |
| GET | `/rest/br/restore/{restoreId:.+}` | `/rest/br/restore/{restoreId}` |
| DELETE | `/rest/br/restore/{restoreId:.+}` | `/rest/br/restore/{restoreId}` |
| GET | `/rest/crs/{identifier:.+}.json` | `/rest/crs/{identifier}.json` |
| GET | `/rest/crs/{identifier:.+}.wkt` | `/rest/crs/{identifier}.wkt` |
| PUT | `/rest/imports/{id}/tasks/{taskId:.+}` | `/rest/imports/{id}/tasks/{taskId}` |
| DELETE | `/rest/imports/{importId}` | `/rest/imports/{id}` |
| GET | `/rest/imports/{importId}` | `/rest/imports/{id}` |
| POST | `/rest/imports/{importId}` | `/rest/imports/{id}` |
| PUT | `/rest/imports/{importId}` | `/rest/imports/{id}` |
| GET | `/rest/namespaces/{namespaceName}` | `/rest/namespaces/{prefix}` |
| GET | `/rest/oseo/collections/{collection}/products/{product:.+}` | `/rest/oseo/collections/{collection}/products/{product}` |
| PUT | `/rest/oseo/collections/{collection}/products/{product:.+}` | `/rest/oseo/collections/{collection}/products/{product}` |
| DELETE | `/rest/oseo/collections/{collection}/products/{product:.+}` | `/rest/oseo/collections/{collection}/products/{product}` |
| GET | `/rest/oseo/collections/{collection}/products/{product:.+}/description` | `/rest/oseo/collections/{collection}/products/{product}/description` |
| PUT | `/rest/oseo/collections/{collection}/products/{product:.+}/description` | `/rest/oseo/collections/{collection}/products/{product}/description` |
| DELETE | `/rest/oseo/collections/{collection}/products/{product:.+}/description` | `/rest/oseo/collections/{collection}/products/{product}/description` |
| GET | `/rest/oseo/collections/{collection}/products/{product:.+}/granules` | `/rest/oseo/collections/{collection}/products/{product}/granules` |
| PUT | `/rest/oseo/collections/{collection}/products/{product:.+}/granules` | `/rest/oseo/collections/{collection}/products/{product}/granules` |
| DELETE | `/rest/oseo/collections/{collection}/products/{product:.+}/granules` | `/rest/oseo/collections/{collection}/products/{product}/granules` |
| GET | `/rest/oseo/collections/{collection}/products/{product:.+}/ogcLinks` | `/rest/oseo/collections/{collection}/products/{product}/ogcLinks` |
| PUT | `/rest/oseo/collections/{collection}/products/{product:.+}/ogcLinks` | `/rest/oseo/collections/{collection}/products/{product}/ogcLinks` |
| DELETE | `/rest/oseo/collections/{collection}/products/{product:.+}/ogcLinks` | `/rest/oseo/collections/{collection}/products/{product}/ogcLinks` |
| GET | `/rest/oseo/collections/{collection}/products/{product:.+}/thumbnail` | `/rest/oseo/collections/{collection}/products/{product}/thumbnail` |
| PUT | `/rest/oseo/collections/{collection}/products/{product:.+}/thumbnail` | `/rest/oseo/collections/{collection}/products/{product}/thumbnail` |
| DELETE | `/rest/oseo/collections/{collection}/products/{product:.+}/thumbnail` | `/rest/oseo/collections/{collection}/products/{product}/thumbnail` |
| GET | `/rest/workspaces/{workspaceName}/coveragestores/{storeName}/coverages/{coverageName}/index/granules/{granuleId:.+}` | `/rest/workspaces/{workspaceName}/coveragestores/{storeName}/coverages/{coverageName}/index/granules/{granuleId}` |
| GET | `/rest/workspaces/{workspace}/featuretypes/{featuretype}/schemarules` | `/rest/workspaces/{workspace}/featuretypes/{featureType}/schemarules` |
| POST | `/rest/workspaces/{workspace}/featuretypes/{featuretype}/schemarules` | `/rest/workspaces/{workspace}/featuretypes/{featureType}/schemarules` |
| GET | `/rest/workspaces/{workspace}/featuretypes/{featuretype}/schemarules/{identifier}` | `/rest/workspaces/{workspace}/featuretypes/{featureType}/schemarules/{identifier}` |
| PUT | `/rest/workspaces/{workspace}/featuretypes/{featuretype}/schemarules/{identifier}` | `/rest/workspaces/{workspace}/featuretypes/{featureType}/schemarules/{identifier}` |
| DELETE | `/rest/workspaces/{workspace}/featuretypes/{featuretype}/schemarules/{identifier}` | `/rest/workspaces/{workspace}/featuretypes/{featureType}/schemarules/{identifier}` |
| PATCH | `/rest/workspaces/{workspace}/featuretypes/{featuretype}/schemarules/{identifier}` | `/rest/workspaces/{workspace}/featuretypes/{featureType}/schemarules/{identifier}` |
| GET | `/rest/workspaces/{workspace}/featuretypes/{featuretype}/templaterules` | `/rest/workspaces/{workspace}/featuretypes/{featureType}/templaterules` |
| POST | `/rest/workspaces/{workspace}/featuretypes/{featuretype}/templaterules` | `/rest/workspaces/{workspace}/featuretypes/{featureType}/templaterules` |
| GET | `/rest/workspaces/{workspace}/featuretypes/{featuretype}/templaterules/{identifier}` | `/rest/workspaces/{workspace}/featuretypes/{featureType}/templaterules/{identifier}` |
| PUT | `/rest/workspaces/{workspace}/featuretypes/{featuretype}/templaterules/{identifier}` | `/rest/workspaces/{workspace}/featuretypes/{featureType}/templaterules/{identifier}` |
| DELETE | `/rest/workspaces/{workspace}/featuretypes/{featuretype}/templaterules/{identifier}` | `/rest/workspaces/{workspace}/featuretypes/{featureType}/templaterules/{identifier}` |
| PATCH | `/rest/workspaces/{workspace}/featuretypes/{featuretype}/templaterules/{identifier}` | `/rest/workspaces/{workspace}/featuretypes/{featureType}/templaterules/{identifier}` |

## Unmatched Implemented Endpoints (NOT in spec)

These endpoints exist in Java source but are not documented in the bundled spec:

### Community (72 endpoints)

| Method | Path | Source File |
|--------|------|-------------|
| GET | `/cesium` | src/community/ogcapi/ogcapi-3d-geovolumes/src/main/java/org/geoserver/ogcapi/v1/geovolumes/GeoVolumesService.java |
| GET | `/collections/{3d-containerID}` | src/community/ogcapi/ogcapi-3d-geovolumes/src/main/java/org/geoserver/ogcapi/v1/geovolumes/GeoVolumesService.java |
| GET | `/collections/{3d-containerID}/**` | src/community/ogcapi/ogcapi-3d-geovolumes/src/main/java/org/geoserver/ogcapi/v1/geovolumes/GeoVolumesService.java |
| GET | `/collections/{collectionId}/children` | src/community/ogcapi/dggs/ogcapi-dggs/src/main/java/org/geoserver/ogcapi/v1/dggs/DGGSService.java |
| GET | `/collections/{collectionId}/coverage` | src/community/ogcapi/ogcapi-coverages/src/main/java/org/geoserver/ogcapi/v1/coverages/CoveragesService.java |
| GET | `/collections/{collectionId}/coverage/domainset` | src/community/ogcapi/ogcapi-coverages/src/main/java/org/geoserver/ogcapi/v1/coverages/CoveragesService.java |
| GET | `/collections/{collectionId}/images` | src/community/ogcapi/ogcapi-images/src/main/java/org/geoserver/ogcapi/v1/images/ImagesService.java |
| POST | `/collections/{collectionId}/images` | src/community/ogcapi/ogcapi-images/src/main/java/org/geoserver/ogcapi/v1/images/ImagesService.java |
| GET | `/collections/{collectionId}/images/{imageId:.+}` | src/community/ogcapi/ogcapi-images/src/main/java/org/geoserver/ogcapi/v1/images/ImagesService.java |
| PUT | `/collections/{collectionId}/images/{imageId:.+}` | src/community/ogcapi/ogcapi-images/src/main/java/org/geoserver/ogcapi/v1/images/ImagesService.java |
| DELETE | `/collections/{collectionId}/images/{imageId:.+}` | src/community/ogcapi/ogcapi-images/src/main/java/org/geoserver/ogcapi/v1/images/ImagesService.java |
| GET | `/collections/{collectionId}/images/{imageId:.+}/assets/{assetId:.+}` | src/community/ogcapi/ogcapi-images/src/main/java/org/geoserver/ogcapi/v1/images/ImagesService.java |
| GET | `/collections/{collectionId}/map/tiles` | src/community/ogcapi/ogcapi-tiles/src/main/java/org/geoserver/ogcapi/v1/tiles/TilesService.java |
| GET | `/collections/{collectionId}/map/tiles/{tileMatrixId}` | src/community/ogcapi/ogcapi-tiles/src/main/java/org/geoserver/ogcapi/v1/tiles/TilesService.java |
| GET | `/collections/{collectionId}/map/tiles/{tileMatrixSetId}/metadata` | src/community/ogcapi/ogcapi-tiles/src/main/java/org/geoserver/ogcapi/v1/tiles/TilesService.java |
| GET | `/collections/{collectionId}/map/tiles/{tileMatrixSetId}/{tileMatrix}/{tileRow}/{tileCol}` | src/community/ogcapi/ogcapi-tiles/src/main/java/org/geoserver/ogcapi/v1/tiles/TilesService.java |
| GET | `/collections/{collectionId}/neighbors` | src/community/ogcapi/dggs/ogcapi-dggs/src/main/java/org/geoserver/ogcapi/v1/dggs/DGGSService.java |
| GET | `/collections/{collectionId}/parents` | src/community/ogcapi/dggs/ogcapi-dggs/src/main/java/org/geoserver/ogcapi/v1/dggs/DGGSService.java |
| GET | `/collections/{collectionId}/point` | src/community/ogcapi/dggs/ogcapi-dggs/src/main/java/org/geoserver/ogcapi/v1/dggs/DGGSService.java |
| GET | `/collections/{collectionId}/polygon` | src/community/ogcapi/dggs/ogcapi-dggs/src/main/java/org/geoserver/ogcapi/v1/dggs/DGGSService.java |
| GET | `/collections/{collectionId}/processes` | src/community/ogcapi/dggs/ogcapi-dggs/src/main/java/org/geoserver/ogcapi/v1/dggs/DGGSDAPAExtension.java |
| GET | `/collections/{collectionId}/processes/area:aggregate-space` | src/community/ogcapi/dggs/ogcapi-dggs/src/main/java/org/geoserver/ogcapi/v1/dggs/DGGSDAPAExtension.java |
| GET | `/collections/{collectionId}/processes/area:aggregate-space-time` | src/community/ogcapi/dggs/ogcapi-dggs/src/main/java/org/geoserver/ogcapi/v1/dggs/DGGSDAPAExtension.java |
| GET | `/collections/{collectionId}/processes/area:aggregate-time` | src/community/ogcapi/dggs/ogcapi-dggs/src/main/java/org/geoserver/ogcapi/v1/dggs/DGGSDAPAExtension.java |
| GET | `/collections/{collectionId}/processes/area:retrieve` | src/community/ogcapi/dggs/ogcapi-dggs/src/main/java/org/geoserver/ogcapi/v1/dggs/DGGSDAPAExtension.java |
| GET | `/collections/{collectionId}/processes/position:aggregate-time` | src/community/ogcapi/dggs/ogcapi-dggs/src/main/java/org/geoserver/ogcapi/v1/dggs/DGGSDAPAExtension.java |
| GET | `/collections/{collectionId}/processes/position:retrieve` | src/community/ogcapi/dggs/ogcapi-dggs/src/main/java/org/geoserver/ogcapi/v1/dggs/DGGSDAPAExtension.java |
| GET | `/collections/{collectionId}/sortables` | src/community/oseo/oseo-stac/src/main/java/org/geoserver/ogcapi/v1/stac/STACService.java |
| GET | `/collections/{collectionId}/styles` | src/community/ogcapi/ogcapi-tiles/src/main/java/org/geoserver/ogcapi/v1/tiles/TilesService.java |
| GET | `/collections/{collectionId}/styles/{styleId}/map` | src/community/ogcapi/ogcapi-maps/src/main/java/org/geoserver/ogcapi/v1/maps/MapsService.java |
| GET | `/collections/{collectionId}/styles/{styleId}/map/info` | src/community/ogcapi/ogcapi-maps/src/main/java/org/geoserver/ogcapi/v1/maps/MapsService.java |
| GET | `/collections/{collectionId}/styles/{styleId}/map/tiles` | src/community/ogcapi/ogcapi-tiles/src/main/java/org/geoserver/ogcapi/v1/tiles/TilesService.java |
| GET | `/collections/{collectionId}/styles/{styleId}/map/tiles/{tileMatrixId}` | src/community/ogcapi/ogcapi-tiles/src/main/java/org/geoserver/ogcapi/v1/tiles/TilesService.java |
| GET | `/collections/{collectionId}/styles/{styleId}/map/tiles/{tileMatrixSetId}/metadata` | src/community/ogcapi/ogcapi-tiles/src/main/java/org/geoserver/ogcapi/v1/tiles/TilesService.java |
| GET | `/collections/{collectionId}/styles/{styleId}/map/tiles/{tileMatrixSetId}/{tileMatrix}/{tileRow}/{tileCol}` | src/community/ogcapi/ogcapi-tiles/src/main/java/org/geoserver/ogcapi/v1/tiles/TilesService.java |
| GET | `/collections/{collectionId}/tiles` | src/community/ogcapi/ogcapi-tiles/src/main/java/org/geoserver/ogcapi/v1/tiles/TilesService.java |
| GET | `/collections/{collectionId}/tiles/{tileMatrixId}` | src/community/ogcapi/ogcapi-tiles/src/main/java/org/geoserver/ogcapi/v1/tiles/TilesService.java |
| GET | `/collections/{collectionId}/tiles/{tileMatrixSetId}/metadata` | src/community/ogcapi/ogcapi-tiles/src/main/java/org/geoserver/ogcapi/v1/tiles/TilesService.java |
| GET | `/collections/{collectionId}/tiles/{tileMatrixSetId}/{tileMatrix}/{tileRow` | src/community/ogcapi/ogcapi-tiled-features/src/main/java/org/geoserver/ogcapi/v1/features/tiled/TiledFeatureService.java |
| GET | `/collections/{collectionId}/tiles/{tileMatrixSetId}/{tileMatrix}/{tileRow}/{tileCol}` | src/community/ogcapi/ogcapi-tiles/src/main/java/org/geoserver/ogcapi/v1/tiles/TilesService.java |
| GET | `/collections/{collectionId}/variables` | src/community/ogcapi/dggs/ogcapi-dggs/src/main/java/org/geoserver/ogcapi/v1/dggs/DGGSDAPAExtension.java |
| GET | `/collections/{collectionId}/zone` | src/community/ogcapi/dggs/ogcapi-dggs/src/main/java/org/geoserver/ogcapi/v1/dggs/DGGSService.java |
| GET | `/collections/{collectionId}/zones` | src/community/ogcapi/dggs/ogcapi-dggs/src/main/java/org/geoserver/ogcapi/v1/dggs/DGGSService.java |
| GET | `/gsr/services/{workspaceName}/MapServer/MapServerGetService` | src/community/gsr/src/main/java/org/geoserver/gsr/api/map/MapServiceController.java |
| GET | `/i3s` | src/community/ogcapi/ogcapi-3d-geovolumes/src/main/java/org/geoserver/ogcapi/v1/geovolumes/GeoVolumesService.java |
| GET | `/jobs/{jobId}` | src/community/ogcapi/ogcapi-processes/src/main/java/org/geoserver/ogcapi/v1/processes/ProcessesService.java |
| DELETE | `/jobs/{jobId}` | src/community/ogcapi/ogcapi-processes/src/main/java/org/geoserver/ogcapi/v1/processes/ProcessesService.java |
| GET | `/jobs/{jobId}/results` | src/community/ogcapi/ogcapi-processes/src/main/java/org/geoserver/ogcapi/v1/processes/ProcessesService.java |
| GET | `/processes` | src/community/ogcapi/ogcapi-processes/src/main/java/org/geoserver/ogcapi/v1/processes/ProcessesService.java |
| GET | `/processes/{processId}` | src/community/ogcapi/ogcapi-processes/src/main/java/org/geoserver/ogcapi/v1/processes/ProcessesService.java |
| GET | `/processes/{processId}/execution` | src/community/ogcapi/ogcapi-processes/src/main/java/org/geoserver/ogcapi/v1/processes/ProcessesService.java |
| POST | `/processes/{processId}/execution` | src/community/ogcapi/ogcapi-processes/src/main/java/org/geoserver/ogcapi/v1/processes/ProcessesService.java |
| GET | `/queryables` | src/community/oseo/oseo-stac/src/main/java/org/geoserver/ogcapi/v1/stac/STACService.java |
| POST | `/rest/br/backup` | src/community/backup-restore/rest/src/main/java/org/geoserver/backuprestore/rest/BackupController.java |
| GET | `/rest/br/backup{.+}` | src/community/backup-restore/rest/src/main/java/org/geoserver/backuprestore/rest/BackupController.java |
| POST | `/rest/br/restore` | src/community/backup-restore/rest/src/main/java/org/geoserver/backuprestore/rest/RestoreController.java |
| GET | `/rest/br/restore{.+}` | src/community/backup-restore/rest/src/main/java/org/geoserver/backuprestore/rest/RestoreController.java |
| GET | `/search` | src/community/oseo/oseo-stac/src/main/java/org/geoserver/ogcapi/v1/stac/STACService.java |
| POST | `/search` | src/community/oseo/oseo-stac/src/main/java/org/geoserver/ogcapi/v1/stac/STACService.java |
| GET | `/sortables` | src/community/oseo/oseo-stac/src/main/java/org/geoserver/ogcapi/v1/stac/STACService.java |
| GET | `/styles` | src/community/ogcapi/ogcapi-styles/src/main/java/org/geoserver/ogcapi/v1/styles/StylesService.java |
| POST | `/styles` | src/community/ogcapi/ogcapi-styles/src/main/java/org/geoserver/ogcapi/v1/styles/StylesService.java |
| GET | `/styles/{styleId}` | src/community/ogcapi/ogcapi-styles/src/main/java/org/geoserver/ogcapi/v1/styles/StylesService.java |
| PUT | `/styles/{styleId}` | src/community/ogcapi/ogcapi-styles/src/main/java/org/geoserver/ogcapi/v1/styles/StylesService.java |
| DELETE | `/styles/{styleId}` | src/community/ogcapi/ogcapi-styles/src/main/java/org/geoserver/ogcapi/v1/styles/StylesService.java |
| GET | `/styles/{styleId}/metadata` | src/community/ogcapi/ogcapi-styles/src/main/java/org/geoserver/ogcapi/v1/styles/StylesService.java |
| PUT | `/styles/{styleId}/metadata` | src/community/ogcapi/ogcapi-styles/src/main/java/org/geoserver/ogcapi/v1/styles/StylesService.java |
| PATCH | `/styles/{styleId}/metadata` | src/community/ogcapi/ogcapi-styles/src/main/java/org/geoserver/ogcapi/v1/styles/StylesService.java |
| GET | `/styles/{styleId}/thumbnail` | src/community/ogcapi/ogcapi-styles/src/main/java/org/geoserver/ogcapi/v1/styles/StylesService.java |
| POST | `/taskmanager-import/{template}` | src/community/taskmanager/core/src/main/java/org/geoserver/taskmanager/util/ImportTool.java |
| GET | `/tileMatrixSets` | src/community/ogcapi/ogcapi-tiles/src/main/java/org/geoserver/ogcapi/v1/tiles/TilesService.java |
| GET | `/tileMatrixSets/{tileMatrixSetId}` | src/community/ogcapi/ogcapi-tiles/src/main/java/org/geoserver/ogcapi/v1/tiles/TilesService.java |

### Core (27 endpoints)

| Method | Path | Source File |
|--------|------|-------------|
| GET | `/rest` | src/rest/src/main/java/org/geoserver/rest/IndexController.java |
| PUT | `/rest` | src/restconfig/src/main/java/org/geoserver/rest/catalog/StyleController.java |
| DELETE | `/rest` | src/restconfig/src/main/java/org/geoserver/rest/catalog/StyleController.java |
| GET | `/rest/layers` | src/restconfig/src/main/java/org/geoserver/rest/catalog/LayerController.java |
| POST | `/rest/security/acl/catalog/reload` | src/restconfig/src/main/java/org/geoserver/rest/security/CatalogSecurityController.java |
| PUT | `/rest/security/acl/catalog/reload` | src/restconfig/src/main/java/org/geoserver/rest/security/CatalogSecurityController.java |
| GET | `/rest/security/authproviders` | src/restconfig/src/main/java/org/geoserver/rest/security/AuthenticationProviderRestController.java |
| POST | `/rest/security/authproviders` | src/restconfig/src/main/java/org/geoserver/rest/security/AuthenticationProviderRestController.java |
| PUT | `/rest/security/authproviders` | src/restconfig/src/main/java/org/geoserver/rest/security/AuthenticationProviderRestController.java |
| DELETE | `/rest/security/authproviders` | src/restconfig/src/main/java/org/geoserver/rest/security/AuthenticationProviderRestController.java |
| GET | `/rest/security/authproviders/order` | src/restconfig/src/main/java/org/geoserver/rest/security/AuthenticationProviderRestController.java |
| POST | `/rest/security/authproviders/order` | src/restconfig/src/main/java/org/geoserver/rest/security/AuthenticationProviderRestController.java |
| PUT | `/rest/security/authproviders/order` | src/restconfig/src/main/java/org/geoserver/rest/security/AuthenticationProviderRestController.java |
| DELETE | `/rest/security/authproviders/order` | src/restconfig/src/main/java/org/geoserver/rest/security/AuthenticationProviderRestController.java |
| DELETE | `/rest/security/filterchain` | src/restconfig/src/main/java/org/geoserver/rest/security/AuthenticationFilterChainRestController.java |
| GET | `/rest/urlchecks/{urlCheckName}` | src/restconfig/src/main/java/org/geoserver/rest/security/UrlCheckController.java |
| DELETE | `/rest/workspaces/{workspaceName}/coveragestores/{storeName}/coverages/{coverageName}/index` | src/restconfig/src/main/java/org/geoserver/rest/catalog/StructuredCoverageController.java |
| POST | `/rest/workspaces/{workspaceName}/coveragestores/{storeName}/coverages/{coverageName}/reset` | src/restconfig/src/main/java/org/geoserver/rest/catalog/CoverageController.java |
| PUT | `/rest/workspaces/{workspaceName}/coveragestores/{storeName}/coverages/{coverageName}/reset` | src/restconfig/src/main/java/org/geoserver/rest/catalog/CoverageController.java |
| POST | `/rest/workspaces/{workspaceName}/coveragestores/{storeName}/reset` | src/restconfig/src/main/java/org/geoserver/rest/catalog/CoverageStoreController.java |
| PUT | `/rest/workspaces/{workspaceName}/coveragestores/{storeName}/reset` | src/restconfig/src/main/java/org/geoserver/rest/catalog/CoverageStoreController.java |
| POST | `/rest/workspaces/{workspaceName}/datastores/{storeName}/reset` | src/restconfig/src/main/java/org/geoserver/rest/catalog/DataStoreController.java |
| PUT | `/rest/workspaces/{workspaceName}/datastores/{storeName}/reset` | src/restconfig/src/main/java/org/geoserver/rest/catalog/DataStoreController.java |
| POST | `/rest/workspaces/{workspaceName}/featuretypes/{featureTypeName}/reset` | src/restconfig/src/main/java/org/geoserver/rest/catalog/FeatureTypeController.java |
| PUT | `/rest/workspaces/{workspaceName}/featuretypes/{featureTypeName}/reset` | src/restconfig/src/main/java/org/geoserver/rest/catalog/FeatureTypeController.java |
| GET | `/settings` | src/restconfig/src/main/java/org/geoserver/rest/service/ServiceSettingsController.java |
| DELETE | `/workspaces/{workspaceName}/settings` | src/restconfig/src/main/java/org/geoserver/rest/service/ServiceSettingsController.java |

### Extension (25 endpoints)

| Method | Path | Source File |
|--------|------|-------------|
| GET | `/collections` | src/extension/ogcapi/ogcapi-features/src/main/java/org/geoserver/ogcapi/v1/features/FeatureService.java |
| GET | `/collections/{collectionId}` | src/extension/ogcapi/ogcapi-features/src/main/java/org/geoserver/ogcapi/v1/features/FeatureService.java |
| GET | `/collections/{collectionId}/items` | src/extension/ogcapi/ogcapi-features/src/main/java/org/geoserver/ogcapi/v1/features/FeatureService.java |
| GET | `/collections/{collectionId}/items/{itemId:.+}` | src/extension/ogcapi/ogcapi-features/src/main/java/org/geoserver/ogcapi/v1/features/FeatureService.java |
| GET | `/collections/{collectionId}/queryables` | src/extension/ogcapi/ogcapi-features/src/main/java/org/geoserver/ogcapi/v1/features/FeatureService.java |
| GET | `/collections/{collectionId}/schemas/fg/{schemaId}.json` | src/extension/ogcapi/ogcapi-features/src/main/java/org/geoserver/ogcapi/v1/features/FeatureService.java |
| POST | `/collections/{collectionId}/search` | src/extension/ogcapi/ogcapi-features/src/main/java/org/geoserver/ogcapi/v1/features/FeatureService.java |
| GET | `/conformance` | src/extension/ogcapi/ogcapi-features/src/main/java/org/geoserver/ogcapi/v1/features/FeatureService.java |
| GET | `/functions` | src/extension/ogcapi/ogcapi-features/src/main/java/org/geoserver/ogcapi/v1/features/FeatureService.java |
| GET | `/getLandingPage` | src/extension/ogcapi/ogcapi-features/src/main/java/org/geoserver/ogcapi/v1/features/FeatureService.java |
| GET | `/mapml/js/**` | src/extension/mapml/src/main/java/org/geoserver/mapml/MapMLResourceController.java |
| GET | `/mapml/viewer/**` | src/extension/mapml/src/main/java/org/geoserver/mapml/MapMLResourceController.java |
| GET | `/openapi` | src/extension/ogcapi/ogcapi-features/src/main/java/org/geoserver/ogcapi/v1/features/FeatureService.java |
| POST | `/rest/imports` | src/extension/importer/rest/src/main/java/org/geoserver/importer/rest/ImportController.java |
| DELETE | `/rest/imports` | src/extension/importer/rest/src/main/java/org/geoserver/importer/rest/ImportController.java |
| DELETE | `/rest/metadata` | src/extension/metadata/src/main/java/org/geoserver/metadata/rest/MetaDataRestService.java |
| GET | `/rest/metadata/customToNative` | src/extension/metadata/src/main/java/org/geoserver/metadata/rest/MetaDataRestService.java |
| GET | `/rest/metadata/fix` | src/extension/metadata/src/main/java/org/geoserver/metadata/rest/MetaDataRestService.java |
| POST | `/rest/metadata/import` | src/extension/metadata/src/main/java/org/geoserver/metadata/rest/MetaDataRestService.java |
| GET | `/rest/metadata/linkedlayers` | src/extension/metadata/src/main/java/org/geoserver/metadata/rest/MetaDataRestService.java |
| GET | `/rest/metadata/nativeToCustom` | src/extension/metadata/src/main/java/org/geoserver/metadata/rest/MetaDataRestService.java |
| POST | `/rest/metadata/nativeToCustom` | src/extension/metadata/src/main/java/org/geoserver/metadata/rest/MetaDataRestService.java |
| GET | `/{id}` | src/extension/params-extractor/src/main/java/org/geoserver/params/extractor/rest/EchoesController.java |
| PUT | `/{id}` | src/extension/params-extractor/src/main/java/org/geoserver/params/extractor/rest/EchoesController.java |
| DELETE | `/{id}` | src/extension/params-extractor/src/main/java/org/geoserver/params/extractor/rest/EchoesController.java |

## Methodology

1. **Source extraction**: Scanned all Java files in core REST modules, extensions,
   and community modules for `@RestController`/`@Controller` annotations and
   `@GetMapping`/`@PostMapping`/`@PutMapping`/`@DeleteMapping`/`@PatchMapping` methods.
2. **Spec parsing**: Loaded `doc/en/api/geoserver-bundled.yaml` and extracted all
   paths starting with `/rest/`, `/gwc/rest/`, or `/gsr/` with their HTTP methods.
3. **Matching**: Three-tier matching:
   - Exact: path + method identical
   - Normalized: path variables replaced with `{var}` (e.g., `{id}` matches `{importId}`)
   - Segment-normalized: also strips format extensions (`.json`, `.xml`)
4. **Coverage**: (exact + fuzzy matches) / total implemented × 100

---
*Generated by accurate-coverage-calculation.py*