# Documented REST API Endpoints Summary

**Generated:** 2026-02-12T19:12:48.693967
**Total Spec Files:** 55
**Total Endpoints:** 568

## Endpoints by HTTP Method

| HTTP Method | Count |
|-------------|-------|
| GET | 171 |
| POST | 137 |
| PUT | 128 |
| DELETE | 131 |
| HEAD | 1 |

## Endpoints by Module/Tag

| Module | Endpoint Count |
|--------|----------------|
| Templates | 48 |
| Security | 45 |
| OpenSearchEO | 38 |
| OWSServices | 36 |
| UserGroup | 22 |
| FeatureTypes | 20 |
| Styles | 20 |
| DataStores | 19 |
| Coverages | 18 |
| Roles | 18 |
| LayerGroups | 16 |
| Layers | 16 |
| WMSLayers | 16 |
| WMTSLayers | 16 |
| CoverageStores | 14 |
| Reload | 12 |
| Settings | 12 |
| StructuredCoverages | 12 |
| ImporterTasks | 11 |
| ParamsExtractor | 10 |
| ImporterData | 8 |
| Monitoring | 8 |
| Namespaces | 8 |
| Transforms | 8 |
| UrlChecks | 8 |
| WMSStores | 8 |
| WMTSStores | 8 |
| Workspaces | 8 |
| Importer | 7 |
| authproviders | 6 |
| AuthFilters | 5 |
| GwcLayers | 5 |
| ImporterTransforms | 5 |
| Metadata | 5 |
| ProxyBaseExtension | 5 |
| Resource | 5 |
| UserGroupServices | 5 |
| Fonts | 4 |
| GwcBlobStores | 4 |
| GwcGridSets | 4 |
| GwcSeed | 3 |
| Manifests | 3 |
| RasterAttributeTable | 3 |
| GwcDiskQuota | 2 |
| GwcGlobal | 2 |
| GwcMassTruncate | 2 |
| Logging | 2 |
| WPS | 2 |
| GwcBounds | 1 |
| GwcFilterUpdate | 1 |
| GwcIndex | 1 |
| GwcMemoryCacheStatistics | 1 |
| GwcReload | 1 |
| SystemStatus | 1 |

## Detailed Breakdown by Module

### Templates (48 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/templates` | templatesDelete |
| DELETE | `/templates/{template}.ftl` | templateDelete |
| DELETE | `/workspaces/{workspace}/coveragestore/{store}/coverages/{coverage}/templates` | templatesCoverageDelete |
| DELETE | `/workspaces/{workspace}/coveragestore/{store}/coverages/{coverage}/templates/{template}.ftl` | templateCoverageDelete |
| DELETE | `/workspaces/{workspace}/coveragestore/{store}/templates` | templatesDataStoreCSDelete |
| DELETE | `/workspaces/{workspace}/coveragestore/{store}/templates/{template}.ftl` | templateDataStoreCSDelete |
| DELETE | `/workspaces/{workspace}/datastores/{store}/featuretypes/{type}/templates` | templatesDataStoreFTDelete |
| DELETE | `/workspaces/{workspace}/datastores/{store}/featuretypes/{type}/templates/{template}.ftl` | templateDataStoreFTDelete |
| DELETE | `/workspaces/{workspace}/datastores/{store}/templates` | templatesDataStoreDelete |
| DELETE | `/workspaces/{workspace}/datastores/{store}/templates/{template}.ftl` | templateDataStoreDelete |
| DELETE | `/workspaces/{workspace}/templates` | templatesWorkspaceDelete |
| DELETE | `/workspaces/{workspace}/templates/{template}.ftl` | templateWorkspaceDelete |
| GET | `/templates` | templatesGet |
| GET | `/templates/{template}.ftl` | templateGet |
| GET | `/workspaces/{workspace}/coveragestore/{store}/coverages/{coverage}/templates` | templatesCoverageGet |
| GET | `/workspaces/{workspace}/coveragestore/{store}/coverages/{coverage}/templates/{template}.ftl` | templateCoverageGet |
| GET | `/workspaces/{workspace}/coveragestore/{store}/templates` | templatesDataStoreCSGet |
| GET | `/workspaces/{workspace}/coveragestore/{store}/templates/{template}.ftl` | templateDataStoreCSGet |
| GET | `/workspaces/{workspace}/datastores/{store}/featuretypes/{type}/templates` | templatesDataStoreFTGet |
| GET | `/workspaces/{workspace}/datastores/{store}/featuretypes/{type}/templates/{template}.ftl` | templateDataStoreFTGet |
| GET | `/workspaces/{workspace}/datastores/{store}/templates` | templatesDataStoreGet |
| GET | `/workspaces/{workspace}/datastores/{store}/templates/{template}.ftl` | templateDataStoreGet |
| GET | `/workspaces/{workspace}/templates` | templatesWorkspaceGet |
| GET | `/workspaces/{workspace}/templates/{template}.ftl` | templateWorkspaceGet |
| POST | `/templates` | templatesPost |
| POST | `/templates/{template}.ftl` | templatePost |
| POST | `/workspaces/{workspace}/coveragestore/{store}/coverages/{coverage}/templates` | templatesCoveragePost |
| POST | `/workspaces/{workspace}/coveragestore/{store}/coverages/{coverage}/templates/{template}.ftl` | templateCoveragePost |
| POST | `/workspaces/{workspace}/coveragestore/{store}/templates` | templatesDataStoreCSPost |
| POST | `/workspaces/{workspace}/coveragestore/{store}/templates/{template}.ftl` | templateDataStoreCSPost |
| POST | `/workspaces/{workspace}/datastores/{store}/featuretypes/{type}/templates` | templatesDataStoreFTPost |
| POST | `/workspaces/{workspace}/datastores/{store}/featuretypes/{type}/templates/{template}.ftl` | templateDataStoreFTPost* |
| POST | `/workspaces/{workspace}/datastores/{store}/templates` | templatesDataStorePost |
| POST | `/workspaces/{workspace}/datastores/{store}/templates/{template}.ftl` | templateDataStorePost |
| POST | `/workspaces/{workspace}/templates` | templatesWorkspacePost |
| POST | `/workspaces/{workspace}/templates/{template}.ftl` | templateWorkspacePost |
| PUT | `/templates` | templatesPut |
| PUT | `/templates/{template}.ftl` | templatePut |
| PUT | `/workspaces/{workspace}/coveragestore/{store}/coverages/{coverage}/templates` | templatesCoveragePut |
| PUT | `/workspaces/{workspace}/coveragestore/{store}/coverages/{coverage}/templates/{template}.ftl` | templateCoveragePut |
| PUT | `/workspaces/{workspace}/coveragestore/{store}/templates` | templatesDataStoreCSPut |
| PUT | `/workspaces/{workspace}/coveragestore/{store}/templates/{template}.ftl` | templateDataStoreCSPut |
| PUT | `/workspaces/{workspace}/datastores/{store}/featuretypes/{type}/templates` | templatesDataStoreFTPut |
| PUT | `/workspaces/{workspace}/datastores/{store}/featuretypes/{type}/templates/{template}.ftl` | templateDataStoreFTPut |
| PUT | `/workspaces/{workspace}/datastores/{store}/templates` | templatesDataStorePut |
| PUT | `/workspaces/{workspace}/datastores/{store}/templates/{template}.ftl` | templateDataStorePut |
| PUT | `/workspaces/{workspace}/templates` | templatesWorkspacePut |
| PUT | `/workspaces/{workspace}/templates/{template}.ftl` | templateWorkspacePut |

### Security (45 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/rest/security/acl/catalog` | deleteCatalogMode |
| DELETE | `/rest/security/acl/layers` | deleteACLLayers |
| DELETE | `/rest/security/acl/layers/{rule}` | deleteACLLayer |
| DELETE | `/rest/security/acl/rest` | deleteACLRESTRules |
| DELETE | `/rest/security/acl/rest/{rule}` | deleteACLRESTRule |
| DELETE | `/rest/security/acl/services` | deleteACLServices |
| DELETE | `/rest/security/acl/services/{rule}` | deleteACLService |
| DELETE | `/rest/security/masterpw` | deleteMasterPW |
| DELETE | `/rest/security/self/password` | deleteSelfPassword |
| DELETE | `/security/authproviders/order` | N/A |
| DELETE | `/security/filterchain/{chain_name}` | N/A |
| GET | `/rest/security/acl/catalog` | getCatalogMode |
| GET | `/rest/security/acl/layers` | getACLLayers |
| GET | `/rest/security/acl/layers/{rule}` | getACLLayer |
| GET | `/rest/security/acl/rest` | getACLRESTRules |
| GET | `/rest/security/acl/rest/{rule}` | getACLRESTRule |
| GET | `/rest/security/acl/services` | getACLServices |
| GET | `/rest/security/acl/services/{rule}` | getACLService |
| GET | `/rest/security/masterpw` | getMasterPW |
| GET | `/rest/security/self/password` | getSelfPassword |
| GET | `/security/authproviders/order` | N/A |
| GET | `/security/filterchain` | N/A |
| GET | `/security/filterchain/{chain_name}` | N/A |
| POST | `/rest/security/acl/catalog` | postCatalogMode |
| POST | `/rest/security/acl/layers` | postACLLayers |
| POST | `/rest/security/acl/layers/{rule}` | postACLLayer |
| POST | `/rest/security/acl/rest` | postACLRESTRules |
| POST | `/rest/security/acl/rest/{rule}` | postACLRESTRule |
| POST | `/rest/security/acl/services` | postACLServices |
| POST | `/rest/security/acl/services/{rule}` | postACLService |
| POST | `/rest/security/masterpw` | postMasterPW |
| POST | `/rest/security/self/password` | postSelfPassword |
| POST | `/security/authproviders/order` | N/A |
| POST | `/security/filterchain` | N/A |
| PUT | `/rest/security/acl/catalog` | N/A |
| PUT | `/rest/security/acl/layers` | putACLLayers |
| PUT | `/rest/security/acl/layers/{rule}` | putACLLayer |
| PUT | `/rest/security/acl/rest` | putACLRESTRules |
| PUT | `/rest/security/acl/rest/{rule}` | putACLRESTRule |
| PUT | `/rest/security/acl/services` | putACLServices |
| PUT | `/rest/security/acl/services/{rule}` | putACLService |
| PUT | `/rest/security/masterpw` | putMasterPW |
| PUT | `/rest/security/self/password` | putSelfPassword |
| PUT | `/security/filterchain/order` | N/A |
| PUT | `/security/filterchain/{chain_name}` | N/A |

### OpenSearchEO (38 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/collections/{collection}` | N/A |
| DELETE | `/collections/{collection}/layer` | N/A |
| DELETE | `/collections/{collection}/layers/{layer}` | N/A |
| DELETE | `/collections/{collection}/metadata` | N/A |
| DELETE | `/collections/{collection}/ogcLinks` | N/A |
| DELETE | `/collections/{collection}/products/{product}` | N/A |
| DELETE | `/collections/{collection}/products/{product}/granules` | N/A |
| DELETE | `/collections/{collection}/products/{product}/metadata` | N/A |
| DELETE | `/collections/{collection}/products/{product}/ogcLinks` | N/A |
| DELETE | `/collections/{collection}/products/{product}/thumbnail` | N/A |
| DELETE | `/collections/{collection}/thumbnail` | N/A |
| GET | `/collections` | N/A |
| GET | `/collections/{collection}` | N/A |
| GET | `/collections/{collection}/layer` | N/A |
| GET | `/collections/{collection}/layers` | N/A |
| GET | `/collections/{collection}/layers/{layer}` | N/A |
| GET | `/collections/{collection}/metadata` | N/A |
| GET | `/collections/{collection}/ogcLinks` | N/A |
| GET | `/collections/{collection}/products` | N/A |
| GET | `/collections/{collection}/products/{product}` | N/A |
| GET | `/collections/{collection}/products/{product}/granules` | N/A |
| GET | `/collections/{collection}/products/{product}/metadata` | N/A |
| GET | `/collections/{collection}/products/{product}/ogcLinks` | N/A |
| GET | `/collections/{collection}/products/{product}/thumbnail` | N/A |
| GET | `/collections/{collection}/thumbnail` | N/A |
| POST | `/collections` | N/A |
| POST | `/collections/{collection}/products` | N/A |
| PUT | `/collections/{collection}` | N/A |
| PUT | `/collections/{collection}/layer` | N/A |
| PUT | `/collections/{collection}/layers/{layer}` | N/A |
| PUT | `/collections/{collection}/metadata` | N/A |
| PUT | `/collections/{collection}/ogcLinks` | N/A |
| PUT | `/collections/{collection}/products/{product}` | N/A |
| PUT | `/collections/{collection}/products/{product}/granules` | N/A |
| PUT | `/collections/{collection}/products/{product}/metadata` | N/A |
| PUT | `/collections/{collection}/products/{product}/ogcLinks` | N/A |
| PUT | `/collections/{collection}/products/{product}/thumbnail` | N/A |
| PUT | `/collections/{collection}/thumbnail` | N/A |

### OWSServices (36 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/services/oseo/settings` | deleteOSEOSettings |
| DELETE | `/services/wcs/settings` | deleteWCSSettings |
| DELETE | `/services/wcs/workspaces/{workspace}/settings` | deleteWCSWorkspaceSettings |
| DELETE | `/services/wfs/settings` | deleteWFSSettings |
| DELETE | `/services/wfs/workspaces/{workspace}/settings` | deleteWFSWorkspaceSettings |
| DELETE | `/services/wms/settings` | deleteWMSSettings |
| DELETE | `/services/wms/workspaces/{workspace}/settings` | deleteWMSWorkspaceSettings |
| DELETE | `/services/wmts/settings` | deleteWMTSSettings |
| DELETE | `/services/wmts/workspaces/{workspace}/settings` | deleteWMTSWorkspaceSettings |
| GET | `/services/oseo/settings` | getOSEOSettings |
| GET | `/services/wcs/settings` | getWCSSettings |
| GET | `/services/wcs/workspaces/{workspace}/settings` | getWCSWorkspaceSettings |
| GET | `/services/wfs/settings` | getWFSSettings |
| GET | `/services/wfs/workspaces/{workspace}/settings` | getWFSWorkspaceSettings |
| GET | `/services/wms/settings` | getWMSSettings |
| GET | `/services/wms/workspaces/{workspace}/settings` | getWMSWorkspaceSettings |
| GET | `/services/wmts/settings` | getWMTSSettings |
| GET | `/services/wmts/workspaces/{workspace}/settings` | getWMTSWorkspaceSettings |
| POST | `/services/oseo/settings` | postOSEOSettings |
| POST | `/services/wcs/settings` | postWCSSettings |
| POST | `/services/wcs/workspaces/{workspace}/settings` | postWCSWorkspaceSettings |
| POST | `/services/wfs/settings` | postWFSSettings |
| POST | `/services/wfs/workspaces/{workspace}/settings` | postWFSWorkspaceSettings |
| POST | `/services/wms/settings` | postWMSSettings |
| POST | `/services/wms/workspaces/{workspace}/settings` | postWMSWorkspaceSettings |
| POST | `/services/wmts/settings` | postWMTSSettings |
| POST | `/services/wmts/workspaces/{workspace}/settings` | postWMTSWorkspaceSettings |
| PUT | `/services/oseo/settings` | putOSEOSettings |
| PUT | `/services/wcs/settings` | putWCSSettings |
| PUT | `/services/wcs/workspaces/{workspace}/settings` | putWCSWorkspaceSettings |
| PUT | `/services/wfs/settings` | putWFSSettings |
| PUT | `/services/wfs/workspaces/{workspace}/settings` | putWFSWorkspaceSettings |
| PUT | `/services/wms/settings` | putWMSSettings |
| PUT | `/services/wms/workspaces/{workspace}/settings` | putWMSWorkspaceSettings |
| PUT | `/services/wmts/settings` | putWMTSSettings |
| PUT | `/services/wmts/workspaces/{workspace}/settings` | putWMTSWorkspaceSettings |

### UserGroup (22 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/usergroup/group/{group}` | groupDefaultDelete |
| DELETE | `/usergroup/service/{serviceName}/group/{group}` | groupDelete |
| DELETE | `/usergroup/service/{serviceName}/user/{user}` | userDelete |
| DELETE | `/usergroup/service/{serviceName}/user/{user}/group/{group}` | userGroupDelete |
| DELETE | `/usergroup/user/{user}` | userDefaultDelete |
| DELETE | `/usergroup/user/{user}/group/{group}` | userGroupDefaultDelete |
| GET | `/usergroup/group/{group}/users` | groupDefaultUserGet |
| GET | `/usergroup/groups/` | groupsDefaultGet |
| GET | `/usergroup/service/{serviceName}/group/{group}/users` | groupUserGet |
| GET | `/usergroup/service/{serviceName}/groups/` | groupsGet |
| GET | `/usergroup/service/{serviceName}/user/{user}/groups` | userGroupGet |
| GET | `/usergroup/service/{serviceName}/users/` | usersGet |
| GET | `/usergroup/user/{user}/groups` | userDefaultGroupGet |
| GET | `/usergroup/users/` | usersDefaultGet |
| POST | `/usergroup/group/{group}` | groupDefaultPost |
| POST | `/usergroup/service/{serviceName}/group/{group}` | groupPost |
| POST | `/usergroup/service/{serviceName}/user/{user}` | userPost |
| POST | `/usergroup/service/{serviceName}/user/{user}/group/{group}` | userGroupPost |
| POST | `/usergroup/service/{serviceName}/users/` | usersPost |
| POST | `/usergroup/user/{user}` | userDefaultPost |
| POST | `/usergroup/user/{user}/group/{group}` | userGroupDefaultPost |
| POST | `/usergroup/users/` | usersDefaultPost |

### FeatureTypes (20 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/workspaces/{workspaceName}/datastores/{storeName}/featuretypes` | deleteFeatureTypes |
| DELETE | `/workspaces/{workspaceName}/datastores/{storeName}/featuretypes/{featureTypeName}` | deleteFeatureType |
| DELETE | `/workspaces/{workspaceName}/featuretypes` | deleteFeatureTypes |
| DELETE | `/workspaces/{workspaceName}/featuretypes/{featureTypeName}` | deleteFeatureType |
| GET | `/workspaces/{workspaceName}/datastores/{storeName}/featuretypes` | getFeatureTypes |
| GET | `/workspaces/{workspaceName}/datastores/{storeName}/featuretypes/{featureTypeName}` | getFeatureType |
| GET | `/workspaces/{workspaceName}/featuretypes` | getFeatureTypes |
| GET | `/workspaces/{workspaceName}/featuretypes/{featureTypeName}` | getFeatureType |
| POST | `/workspaces/{workspaceName}/datastores/{storeName}/featuretypes` | postFeatureTypes |
| POST | `/workspaces/{workspaceName}/datastores/{storeName}/featuretypes/{featureTypeName}` | postFeatureType |
| POST | `/workspaces/{workspaceName}/datastores/{storeName}/featuretypes/{featureTypeName}/reset` | postFeatureTypeReset |
| POST | `/workspaces/{workspaceName}/featuretypes` | postFeatureTypes |
| POST | `/workspaces/{workspaceName}/featuretypes/{featureTypeName}` | postFeatureType |
| POST | `/workspaces/{workspaceName}/featuretypes/{featureTypeName}/reset` | postFeatureTypeReset |
| PUT | `/workspaces/{workspaceName}/datastores/{storeName}/featuretypes` | putFeatureTypes |
| PUT | `/workspaces/{workspaceName}/datastores/{storeName}/featuretypes/{featureTypeName}` | putFeatureType |
| PUT | `/workspaces/{workspaceName}/datastores/{storeName}/featuretypes/{featureTypeName}/reset` | putFeatureTypeReset |
| PUT | `/workspaces/{workspaceName}/featuretypes` | putFeatureTypes |
| PUT | `/workspaces/{workspaceName}/featuretypes/{featureTypeName}` | putFeatureType |
| PUT | `/workspaces/{workspaceName}/featuretypes/{featureTypeName}/reset` | putFeatureTypeReset |

### Styles (20 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/rest/layers/{layer}/styles` | deleteLayerStyles |
| DELETE | `/rest/workspaces/{workspace}/styles/{style}` | deleteWorkspaceStyle |
| DELETE | `/styles` | deleteStyles |
| DELETE | `/styles/{style}` | deleteStyle |
| DELETE | `/workspaces/{workspace}/styles` | deleteWorkspaceStyles |
| GET | `/rest/layers/{layer}/styles` | getLayerStyles |
| GET | `/rest/workspaces/{workspace}/styles/{style}` | getWorkspaceStyle |
| GET | `/styles` | getStyles |
| GET | `/styles/{style}` | getStyle |
| GET | `/workspaces/{workspace}/styles` | getWorkspaceStyles |
| POST | `/rest/layers/{layer}/styles` | postLayerStyles |
| POST | `/rest/workspaces/{workspace}/styles/{style}` | postWorkspaceStyle |
| POST | `/styles` | postStyles |
| POST | `/styles/{style}` | postStyle |
| POST | `/workspaces/{workspace}/styles` | postWorkspaceStyles |
| PUT | `/rest/layers/{layer}/styles` | putLayerStyles |
| PUT | `/rest/workspaces/{workspace}/styles/{style}` | putWorkspaceStyle |
| PUT | `/styles` | putStyles |
| PUT | `/styles/{style}` | putStyle |
| PUT | `/workspaces/{workspace}/styles` | putWorkspaceStyles |

### DataStores (19 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/workspaces/{workspaceName}/datastores` | deletedatastores |
| DELETE | `/workspaces/{workspaceName}/datastores/{storeName}` | deleteDatastore |
| DELETE | `/workspaces/{workspaceName}/datastores/{storeName}/{method}.{format}` | deleteDataStoreUpload |
| GET | `/workspaces/{workspaceName}/datastores` | getDatastores |
| GET | `/workspaces/{workspaceName}/datastores/{storeName}` | getDataStore |
| GET | `/workspaces/{workspaceName}/datastores/{storeName}/{method}.{format}` | getDataStoreUpload |
| POST | `/workspaces/{workspaceName}/appschemastores/{storeName}/cleanSchemas` | cleanAllMongoSchemas |
| POST | `/workspaces/{workspaceName}/appschemastores/{storeName}/datastores/{internalStoreId}/cleanSchemas` | cleanMongoSchema |
| POST | `/workspaces/{workspaceName}/appschemastores/{storeName}/datastores/{internalStoreId}/rebuildMongoSchemas` | rebuildMongoSchema |
| POST | `/workspaces/{workspaceName}/appschemastores/{storeName}/rebuildMongoSchemas` | rebuildAllMongoSchemas |
| POST | `/workspaces/{workspaceName}/datastores` | postDatastores |
| POST | `/workspaces/{workspaceName}/datastores/{storeName}` | postDatastore |
| POST | `/workspaces/{workspaceName}/datastores/{storeName}/mosaic/{method}.{format}` | postVectorDataStoreUpload |
| POST | `/workspaces/{workspaceName}/datastores/{storeName}/reset` | postDataStoreReset |
| POST | `/workspaces/{workspaceName}/datastores/{storeName}/{method}.{format}` | postDataStoreUpload |
| PUT | `/workspaces/{workspaceName}/datastores` | putdatastores |
| PUT | `/workspaces/{workspaceName}/datastores/{storeName}` | putDatastore |
| PUT | `/workspaces/{workspaceName}/datastores/{storeName}/reset` | putDataStoreReset |
| PUT | `/workspaces/{workspaceName}/datastores/{storeName}/{method}.{format}` | putDataStoreUpload |

### Coverages (18 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/workspaces/{workspace}/coverages` | deleteCoverageStore |
| DELETE | `/workspaces/{workspace}/coverages/{coverage}` | deleteCoverage |
| DELETE | `/workspaces/{workspace}/coveragestores/{store}/coverages` | deleteWorkspaceCoverageStore |
| DELETE | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}` | deleteWorkspaceCoverage |
| GET | `/workspaces/{workspace}/coverages` | getCoverageStore |
| GET | `/workspaces/{workspace}/coverages/{coverage}` | getCoverage |
| GET | `/workspaces/{workspace}/coveragestores/{store}/coverages` | getWorkspaceCoverageStore |
| GET | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}` | getWorkspaceCoverage |
| POST | `/workspaces/{workspace}/coverages` | postCoverageStore |
| POST | `/workspaces/{workspace}/coverages/{coverage}` | postCoverage |
| POST | `/workspaces/{workspace}/coveragestores/{store}/coverages` | postWorkspaceCoverageStore |
| POST | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}` | postWorkspaceCoverage |
| POST | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/reset` | postCoverageReset |
| PUT | `/workspaces/{workspace}/coverages` | putCoverageStore |
| PUT | `/workspaces/{workspace}/coverages/{coverage}` | putCoverage |
| PUT | `/workspaces/{workspace}/coveragestores/{store}/coverages` | putWorkspaceCoverageStore |
| PUT | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}` | putWorkspaceCoverage |
| PUT | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/reset` | putCoverageReset |

### Roles (18 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/roles/role/{role}` | roleDefaultDelete |
| DELETE | `/roles/role/{role}/group/{group}` | roleDefaultGroupDelete |
| DELETE | `/roles/role/{role}/user/{user}` | roleDefaultUserDelete |
| DELETE | `/service/{serviceName}/role/{role}` | roleDelete |
| DELETE | `/service/{serviceName}/roles/role/{role}/group/{group}` | roleGroupDelete |
| DELETE | `/service/{serviceName}/roles/role/{role}/user/{user}` | roleUserDelete |
| GET | `/roles` | rolesDefaultGet |
| GET | `/roles/group/{group}` | rolesDefaultGroupGet |
| GET | `/roles/service/{serviceName}/group/{group}` | rolesGroupGet |
| GET | `/roles/service/{serviceName}/roles/` | rolesGet |
| GET | `/roles/service/{serviceName}/user/{user}` | rolesUserGet |
| GET | `/roles/user/{user}` | rolesDefaultUserGet |
| POST | `/roles/role/{role}` | roleDefaultPost |
| POST | `/roles/role/{role}/group/{group}` | roleDefaultGroupPost |
| POST | `/roles/role/{role}/user/{user}` | roleDefaultUserPost |
| POST | `/service/{serviceName}/role/{role}` | rolePost |
| POST | `/service/{serviceName}/roles/role/{role}/group/{group}` | roleGroupPost |
| POST | `/service/{serviceName}/roles/role/{role}/user/{user}` | roleUserPost |

### LayerGroups (16 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/layergroups` | deleteLayergroups |
| DELETE | `/layergroups/{layergroupName}` | deleteLayergroup |
| DELETE | `/workspaces/{workspace}/layergroups` | deleteWorkspaceLayergroups |
| DELETE | `/workspaces/{workspace}/layergroups/{layergroup}` | deleteWorkspaceLayergroup |
| GET | `/layergroups` | getLayergroups |
| GET | `/layergroups/{layergroupName}` | getLayergroup |
| GET | `/workspaces/{workspace}/layergroups` | getWorkspaceLayergroups |
| GET | `/workspaces/{workspace}/layergroups/{layergroup}` | getWorkspaceLayergroup |
| POST | `/layergroups` | postLayergroups |
| POST | `/layergroups/{layergroupName}` | postLayergroup |
| POST | `/workspaces/{workspace}/layergroups` | postWorkspaceLayergroups |
| POST | `/workspaces/{workspace}/layergroups/{layergroup}` | postWorkspaceLayergroup |
| PUT | `/layergroups` | putLayergroups |
| PUT | `/layergroups/{layergroupName}` | putLayergroup |
| PUT | `/workspaces/{workspace}/layergroups` | putWorkspaceLayergroups |
| PUT | `/workspaces/{workspace}/layergroups/{layergroup}` | putWorkspaceLayergroup |

### Layers (16 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/layers` | layersDelete |
| DELETE | `/layers/{layerName}` | layersNameDelete |
| DELETE | `/workspaces/{workspaceName}/layers` | layersWorkspaceDelete |
| DELETE | `/workspaces/{workspaceName}/layers/{layerName}` | layersNameWorkspaceDelete |
| GET | `/layers` | layersGet |
| GET | `/layers/{layerName}` | layersNameGet |
| GET | `/workspaces/{workspaceName}/layers` | layersWorkspaceGet |
| GET | `/workspaces/{workspaceName}/layers/{layerName}` | layersNameWorkspaceGet |
| POST | `/layers` | layersPost |
| POST | `/layers/{layerName}` | layersNamePost |
| POST | `/workspaces/{workspaceName}/layers` | layersWorkspacePost |
| POST | `/workspaces/{workspaceName}/layers/{layerName}` | layersNameWorkspacePost |
| PUT | `/layers` | layersPut |
| PUT | `/layers/{layerName}` | layersNamePut |
| PUT | `/workspaces/{workspaceName}/layers` | layersWorkspacePut |
| PUT | `/workspaces/{workspaceName}/layers/{layerName}` | layersNameWorkspacePut |

### WMSLayers (16 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/workspaces/{workspace}/wmslayers` | deleteWMSStoreLayers |
| DELETE | `/workspaces/{workspace}/wmslayers/{wmslayer}` | deleteWMSStoreLayer |
| DELETE | `/workspaces/{workspace}/wmsstores/{wmsstore}/wmslayers` | deleteWMSStoreStoreLayers |
| DELETE | `/workspaces/{workspace}/wmsstores/{wmsstore}/wmslayers/{wmslayer}` | deleteWMSStoreStoreLayer |
| GET | `/workspaces/{workspace}/wmslayers` | getWMSStoreLayers |
| GET | `/workspaces/{workspace}/wmslayers/{wmslayer}` | getWMSStoreLayer |
| GET | `/workspaces/{workspace}/wmsstores/{wmsstore}/wmslayers` | getWMSStoreStoreLayers |
| GET | `/workspaces/{workspace}/wmsstores/{wmsstore}/wmslayers/{wmslayer}` | getWMSStoreStoreLayer |
| POST | `/workspaces/{workspace}/wmslayers` | postWMSStoreLayers |
| POST | `/workspaces/{workspace}/wmslayers/{wmslayer}` | postWMSStoreLayer |
| POST | `/workspaces/{workspace}/wmsstores/{wmsstore}/wmslayers` | postWMSStoreStoreLayers |
| POST | `/workspaces/{workspace}/wmsstores/{wmsstore}/wmslayers/{wmslayer}` | postWMSStoreStoreLayer |
| PUT | `/workspaces/{workspace}/wmslayers` | putWMSStoreLayers |
| PUT | `/workspaces/{workspace}/wmslayers/{wmslayer}` | putWMSStoreLayer |
| PUT | `/workspaces/{workspace}/wmsstores/{wmsstore}/wmslayers` | putWMSStoreStoreLayers |
| PUT | `/workspaces/{workspace}/wmsstores/{wmsstore}/wmslayers/{wmslayer}` | putWMSStoreStoreLayer |

### WMTSLayers (16 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/workspaces/{workspace}/wmtslayers` | deleteWMTSStoreLayers |
| DELETE | `/workspaces/{workspace}/wmtslayers/{wmtslayer}` | deleteWMTSStoreLayer |
| DELETE | `/workspaces/{workspace}/wmtsstores/{wmtsstore}/layers` | deleteWMTSStoreStoreLayers |
| DELETE | `/workspaces/{workspace}/wmtsstores/{wmtsstore}/layers/{wmtslayer}` | deleteWMTSStoreStoreLayer |
| GET | `/workspaces/{workspace}/wmtslayers` | getWMTSStoreLayers |
| GET | `/workspaces/{workspace}/wmtslayers/{wmtslayer}` | getWMTSStoreLayer |
| GET | `/workspaces/{workspace}/wmtsstores/{wmtsstore}/layers` | getWMTSStoreStoreLayers |
| GET | `/workspaces/{workspace}/wmtsstores/{wmtsstore}/layers/{wmtslayer}` | getWMTSStoreStoreLayer |
| POST | `/workspaces/{workspace}/wmtslayers` | postWMTSStoreLayers |
| POST | `/workspaces/{workspace}/wmtslayers/{wmtslayer}` | postWMTSStoreLayer |
| POST | `/workspaces/{workspace}/wmtsstores/{wmtsstore}/layers` | postWMTSStoreStoreLayers |
| POST | `/workspaces/{workspace}/wmtsstores/{wmtsstore}/layers/{wmtslayer}` | postWMTSStoreStoreLayer |
| PUT | `/workspaces/{workspace}/wmtslayers` | putWMTSStoreLayers |
| PUT | `/workspaces/{workspace}/wmtslayers/{wmtslayer}` | putWMTSStoreLayer |
| PUT | `/workspaces/{workspace}/wmtsstores/{wmtsstore}/layers` | putWMTSStoreStoreLayers |
| PUT | `/workspaces/{workspace}/wmtsstores/{wmtsstore}/layers/{wmtslayer}` | putWMTSStoreStoreLayer |

### CoverageStores (14 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/workspaces/{workspace}/coveragestores` | deleteCoverageStores |
| DELETE | `/workspaces/{workspace}/coveragestores/{store}` | deleteCoverageStore |
| DELETE | `/workspaces/{workspace}/coveragestores/{store}/{method}.{format}` | deleteCoverageStoreUpload |
| GET | `/workspaces/{workspace}/coveragestores` | getCoverageStores |
| GET | `/workspaces/{workspace}/coveragestores/{store}` | getCoverageStore |
| GET | `/workspaces/{workspace}/coveragestores/{store}/{method}.{format}` | getCoverageStoreUpload |
| POST | `/workspaces/{workspace}/coveragestores` | postCoverageStores |
| POST | `/workspaces/{workspace}/coveragestores/{store}` | postCoverageStore |
| POST | `/workspaces/{workspace}/coveragestores/{store}/reset` | postCoverageStoreReset |
| POST | `/workspaces/{workspace}/coveragestores/{store}/{method}.{format}` | postCoverageStoreUpload |
| PUT | `/workspaces/{workspace}/coveragestores` | putCoverageStores |
| PUT | `/workspaces/{workspace}/coveragestores/{store}` | putCoverageStore |
| PUT | `/workspaces/{workspace}/coveragestores/{store}/reset` | putCoverageStoreReset |
| PUT | `/workspaces/{workspace}/coveragestores/{store}/{method}.{format}` | putCoverageStoreUpload |

### Reload (12 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/reload` | deleteReload |
| DELETE | `/reset` | deleteReset |
| DELETE | `/rest/security/acl/catalog/reload` | deleteReload |
| GET | `/reload` | getReload |
| GET | `/reset` | getReset |
| GET | `/rest/security/acl/catalog/reload` | getReload |
| POST | `/reload` | postReload |
| POST | `/reset` | postReset |
| POST | `/rest/security/acl/catalog/reload` | postReload |
| PUT | `/reload` | putReload |
| PUT | `/reset` | putReset |
| PUT | `/rest/security/acl/catalog/reload` | putReload |

### Settings (12 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/settings` | deleteSettings |
| DELETE | `/settings/contact` | deleteContactSettings |
| DELETE | `/workspaces/{workspace}/settings` | deleteWorkspaceSettings |
| GET | `/settings` | getSettings |
| GET | `/settings/contact` | getContactSettings |
| GET | `/workspaces/{workspace}/settings` | getWorkspaceSettings |
| POST | `/settings` | postSettings |
| POST | `/settings/contact` | postContactSettings |
| POST | `/workspaces/{workspace}/settings` | postWorkspaceSettings |
| PUT | `/settings` | putSettings* |
| PUT | `/settings/contact` | putContactSettings |
| PUT | `/workspaces/{workspace}/settings` | putWorkspaceSettings |

### StructuredCoverages (12 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/index` | deleteCoverageStores |
| DELETE | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/index/granules` | deleteStructuredCoverageGranules |
| DELETE | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/index/granules/{granuleId}` | deleteStructuredCoverageGranule |
| GET | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/index` | getStructuredCoverageIndex |
| GET | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/index/granules` | getStructuredCoverageGranules |
| GET | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/index/granules/{granuleId}` | getStructuredCoverageGranule |
| POST | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/index` | postStructuredCoverageIndex |
| POST | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/index/granules` | postStructuredCoverageGranules |
| POST | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/index/granules/{granuleId}` | postStructuredCoverageGranule |
| PUT | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/index` | putStructuredCoverageIndex |
| PUT | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/index/granules` | putStructuredCoverageGranules |
| PUT | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/index/granules/{granuleId}` | putStructuredCoverageGranule |

### ImporterTasks (11 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/imports/{importId}/tasks/{taskId}` | deleteTask |
| GET | `/imports/{importId}/tasks` | getTasks |
| GET | `/imports/{importId}/tasks/{taskId}` | getTask |
| GET | `/imports/{importId}/tasks/{taskId}/layer` | getTaskLayer |
| GET | `/imports/{importId}/tasks/{taskId}/progress` | getTaskProgress |
| GET | `/imports/{importId}/tasks/{taskId}/target` | getTaskTarget |
| POST | `/imports/{importId}/tasks` | postTask |
| PUT | `/imports/{importId}/tasks/{filename}` | putTaskFile |
| PUT | `/imports/{importId}/tasks/{taskId}` | putTask |
| PUT | `/imports/{importId}/tasks/{taskId}/layer` | putTaskLayer |
| PUT | `/imports/{importId}/tasks/{taskId}/target` | putTaskTarget |

### ParamsExtractor (10 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/params-extractor/echoes/{parameterId}` | deleteEchoParameter |
| DELETE | `/params-extractor/rules/{ruleId}` | deleteRule |
| GET | `/params-extractor/echoes` | getEchoParameters |
| GET | `/params-extractor/echoes/{parameterId}` | getEchoParameter |
| GET | `/params-extractor/rules` | getRules |
| GET | `/params-extractor/rules/{ruleId}` | getRule |
| POST | `/params-extractor/echoes` | postEchoParameter |
| POST | `/params-extractor/rules` | postRule |
| PUT | `/params-extractor/echoes/{parameterId}` | putEchoParameter |
| PUT | `/params-extractor/rules/{ruleId}` | putRule |

### ImporterData (8 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/imports/{importId}/data/files/{filename}` | deleteImportDataFile |
| DELETE | `/imports/{importId}/tasks/{taskId}/data/files/{filename}` | deleteTaskDataFile |
| GET | `/imports/{importId}/data` | getData |
| GET | `/imports/{importId}/data/files` | getDataFiles |
| GET | `/imports/{importId}/data/files/{filename}` | getDataFile |
| GET | `/imports/{importId}/tasks/{taskId}/data` | getTaskData |
| GET | `/imports/{importId}/tasks/{taskId}/data/files` | getTaskDataFiles |
| GET | `/imports/{importId}/tasks/{taskId}/data/files/{filename}` | getTaskDataFile |

### Monitoring (8 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/monitor/requests` | deleteMonitorRequests |
| DELETE | `/monitor/requests/{request}` | deleteMonitorRequest |
| GET | `/monitor/requests` | getMonitorRequests |
| GET | `/monitor/requests/{request}` | getMonitorRequest |
| POST | `/monitor/requests` | postMonitorRequests |
| POST | `/monitor/requests/{request}` | postMonitorRequest |
| PUT | `/monitor/requests` | putMonitorRequests |
| PUT | `/monitor/requests/{request}` | putMonitorRequest |

### Namespaces (8 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/namespaces` | deleteNamespaces |
| DELETE | `/namespaces/{namespaceName}` | deleteNamespace |
| GET | `/namespaces` | getNamespaces |
| GET | `/namespaces/{namespaceName}` | getNamespace |
| POST | `/namespaces` | postNamespaces |
| POST | `/namespaces/{namespaceName}` | postNamespace |
| PUT | `/namespaces` | putNamespaces |
| PUT | `/namespaces/{namespaceName}` | putNamespace |

### Transforms (8 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/services/wfs/transforms` | deleteTransform |
| DELETE | `/services/wfs/transforms/{transform}` | deleteTranform |
| GET | `/services/wfs/transforms` | getTransforms |
| GET | `/services/wfs/transforms/{transform}` | getTransform |
| POST | `/services/wfs/transforms` | postTransform |
| POST | `/services/wfs/transforms/{transform}` | postTranform |
| PUT | `/services/wfs/transforms` | putTransform |
| PUT | `/services/wfs/transforms/{transform}` | putTranform |

### UrlChecks (8 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/urlchecks` | deleteUrlChecks |
| DELETE | `/urlchecks/{urlcheckname}` | deleteUrlCheck |
| GET | `/urlchecks` | getUrlChecks |
| GET | `/urlchecks/{urlcheckname}` | getUrlCheck |
| POST | `/urlchecks` | postUrlChecks |
| POST | `/urlchecks/{urlcheckname}` | postUrlCheck |
| PUT | `/urlchecks` | putUrlChecks |
| PUT | `/urlchecks/{urlcheckname}` | putUrlCheck |

### WMSStores (8 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/workspaces/{workspace}/wmsstores` | deleteWMSStores |
| DELETE | `/workspaces/{workspace}/wmsstores/{store}` | deleteWMSStore |
| GET | `/workspaces/{workspace}/wmsstores` | getWMSStores |
| GET | `/workspaces/{workspace}/wmsstores/{store}` | getWMSStore |
| POST | `/workspaces/{workspace}/wmsstores` | postWMSStores |
| POST | `/workspaces/{workspace}/wmsstores/{store}` | postWMSStore |
| PUT | `/workspaces/{workspace}/wmsstores` | putWMSStores |
| PUT | `/workspaces/{workspace}/wmsstores/{store}` | putWMSStore |

### WMTSStores (8 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/workspaces/{workspace}/wmtsstores` | deleteWMTSStores |
| DELETE | `/workspaces/{workspace}/wmtsstores/{store}` | deleteWMTSStore |
| GET | `/workspaces/{workspace}/wmtsstores` | getWMTSStores |
| GET | `/workspaces/{workspace}/wmtsstores/{store}` | getWMTSStore |
| POST | `/workspaces/{workspace}/wmtsstores` | postWMTSStores |
| POST | `/workspaces/{workspace}/wmtsstores/{store}` | postWMTSStore |
| PUT | `/workspaces/{workspace}/wmtsstores` | putWMTSStores |
| PUT | `/workspaces/{workspace}/wmtsstores/{store}` | putWMTSStore |

### Workspaces (8 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/workspaces` | deleteWorkspaces |
| DELETE | `/workspaces/{workspaceName}` | deleteWorkspace |
| GET | `/workspaces` | getWorkspaces |
| GET | `/workspaces/{workspaceName}` | getWorkspace |
| POST | `/workspaces` | postWorkspaces |
| POST | `/workspaces/{workspaceName}` | postWorkspace |
| PUT | `/workspaces` | putWorkspaces |
| PUT | `/workspaces/{workspaceName}` | putWorkspace |

### Importer (7 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/imports` | deleteImports |
| DELETE | `/imports/{importId}` | deleteImport |
| GET | `/imports` | getImports |
| GET | `/imports/{importId}` | getImport |
| POST | `/imports` | postImports |
| POST | `/imports/{importId}` | postImport |
| PUT | `/imports/{importId}` | putImport |

### authproviders (6 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/security/authproviders/{providerName}` | deleteAuthProvider |
| GET | `/security/authproviders` | listAuthProviders |
| GET | `/security/authproviders/{providerName}` | getAuthProvider |
| POST | `/security/authproviders` | createAuthProvider |
| PUT | `/security/authproviders/order` | setAuthProviderOrder |
| PUT | `/security/authproviders/{providerName}` | updateAuthProvider |

### AuthFilters (5 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/authfilters/{filterName}` | deleteAuthFilter |
| GET | `/authfilters` | listAuthFilters |
| GET | `/authfilters/{filterName}` | viewAuthFilter |
| POST | `/authfilters` | createAuthFilter |
| PUT | `/authfilters/{filterName}` | updateAuthFilter |

### GwcLayers (5 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/layers/{layerName}` | layersNameDelete |
| GET | `/layers` | layersGet |
| GET | `/layers/{layerName}` | layersNameGet |
| POST | `/layers/{layerName}` | layersNamePost |
| PUT | `/layers/{layerName}` | layersNamePut |

### ImporterTransforms (5 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/imports/{importId}/tasks/{taskId}/transforms/{transformId}` | deleteTransform |
| GET | `/imports/{importId}/tasks/{taskId}/transforms` | getTransforms |
| GET | `/imports/{importId}/tasks/{taskId}/transforms/{transformId}` | getTransform |
| POST | `/imports/{importId}/tasks/{taskId}/transforms` | postTransform |
| PUT | `/imports/{importId}/tasks/{taskId}/transforms/{transformId}` | putTransform |

### Metadata (5 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/metadata` | N/A |
| GET | `/metadata/fix` | N/A |
| GET | `/metadata/nativeToCustom` | N/A |
| POST | `/metadata/import` | N/A |
| POST | `/metadata/nativeToCustom` | N/A |

### ProxyBaseExtension (5 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/proxy-base-ext/rules/{id}` | deleteProxyBaseExtensionRule |
| GET | `/proxy-base-ext` | getProxyBaseExtensionRules |
| GET | `/proxy-base-ext/rules/{id}` | getProxyBaseExtensionRule |
| POST | `/proxy-base-ext` | postProxyBaseExtensionRule |
| PUT | `/proxy-base-ext/rules/{id}` | putProxyBaseExtensionRule |

### Resource (5 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/resource/{pathToResource}` | resourceDelete |
| GET | `/resource/{pathToResource}` | resourceGet |
| HEAD | `/resource/{pathToResource}` | resourceHead |
| POST | `/resource/{pathToResource}` | resourcePost |
| PUT | `/resource/{pathToResource}` | resourcePut |

### UserGroupServices (5 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/usergroupservices/{name}` | deleteUserGroupService |
| GET | `/usergroupservices` | listUserGroupServices |
| GET | `/usergroupservices/{name}` | getUserGroupService |
| POST | `/usergroupservices` | createUserGroupService |
| PUT | `/usergroupservices/{name}` | updateUserGroupService |

### Fonts (4 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/fonts` | deleteFonts |
| GET | `/fonts` | getFonts |
| POST | `/fonts` | postFonts |
| PUT | `/fonts` | putFonts |

### GwcBlobStores (4 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/blobstores/{blobstoreName}` | blobstoreDelete |
| GET | `/blobstores` | blobstoresGet |
| GET | `/blobstores/{blobstoreName}` | blobstoreGet |
| PUT | `/blobstores/{blobstoreName}` | blobstorePut |

### GwcGridSets (4 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| DELETE | `/gridsets/{gridsetName}` | gridsetDelete |
| GET | `/gridsets` | gridsetsGet |
| GET | `/gridsets/{gridsetName}` | gridsetGet |
| PUT | `/gridsets/{gridsetName}` | gridsetPut |

### GwcSeed (3 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| GET | `/seed.json` | seedGet |
| GET | `/seed/{layer}.{format}` | layerSeedGet |
| POST | `/seed/{layer}.{format}` | layerSeedPost |

### Manifests (3 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| GET | `/about/manifest` | getManifest |
| GET | `/about/status` | N/A |
| GET | `/about/version` | N/A |

### RasterAttributeTable (3 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| GET | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/pam` | getPAMDataset |
| POST | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/pam` | createStyleFromRAT |
| POST | `/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/pam/reload` | reloadPAMDataset |

### GwcDiskQuota (2 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| GET | `/diskquota` | diskQuotaGet |
| PUT | `/diskquota` | diskQuotaPut |

### GwcGlobal (2 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| GET | `/global` | globalGet |
| PUT | `/global` | globalPut |

### GwcMassTruncate (2 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| GET | `/masstruncate` | masstruncateGet |
| POST | `/masstruncate` | masstruncatePost |

### Logging (2 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| GET | `/logging` | getLogging |
| PUT | `/logging` | putLogging* |

### WPS (2 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| GET | `/services/wps/download` | getDownloadServiceConfiguration |
| PUT | `/services/wps/download` | getDownloadServiceConfiguration |

### GwcBounds (1 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| GET | `/bounds/{layer}/{srs}/{type}` | boundsGet |

### GwcFilterUpdate (1 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| POST | `/filter/{filterName}/update/{updateType}` | filterUpdatePost |

### GwcIndex (1 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| GET | `/rest` | indexGet |

### GwcMemoryCacheStatistics (1 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| GET | `/statistics` | statisticsGet |

### GwcReload (1 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| POST | `/reload` | reloadPost |

### SystemStatus (1 endpoints)

| Method | Path | Operation ID |
|--------|------|--------------|
| GET | `/about/system-status` | getMonitorRequests |

## Summary Statistics

- **Total Modules:** 54
- **Total Endpoints:** 568
- **Spec Files Parsed:** 55/55
- **Parse Failures:** 0

### HTTP Method Distribution

- **GET:** 171 (30.1%)
- **POST:** 137 (24.1%)
- **PUT:** 128 (22.5%)
- **DELETE:** 131 (23.1%)
- **HEAD:** 1 (0.2%)
