# API Mismatch Summary

Total rows in csv/all_api_comparison.csv: 199

## Counts

- missing_in_java: 3
- extra_in_java: 45
- implemented_in_dependency: 92

## Sample entries

### missing_in_java (first 10)
|yaml_file|endpoint|yaml_methods|match_found|matching_java_files|java_methods|notes|
|---|---|---|---|---|---|---|
|coverages.yaml|/workspaces/{workspace}/coveragestores/{store}/coverages|delete,get,post,put|yes|D:\DATA\Projects\Geoserver\all-source-code\geoserver-main\src\restconfig\src\main\java\org\geoserver\rest\catalog\CoverageController.java|get|missing_in_java:post  method_not_permitted_in_yaml:delete,put|
|coverages.yaml|/workspaces/{workspace}/coverages|delete,get,post,put|yes|D:\DATA\Projects\Geoserver\all-source-code\geoserver-main\src\restconfig\src\main\java\org\geoserver\rest\catalog\CoverageController.java|get|missing_in_java:post  method_not_permitted_in_yaml:delete,put|
|structuredcoverages.yaml|/workspaces/{workspace}/coveragestores/{store}/coverages/{coverage}/index/granules/{granuleId}|delete,get,post,put|yes|D:\DATA\Projects\Geoserver\all-source-code\geoserver-main\src\restconfig\src\main\java\org\geoserver\rest\catalog\StructuredCoverageController.java|get|missing_in_java:delete  method_not_permitted_in_yaml:post,put|

### extra_in_java (first 10)
|yaml_file|endpoint|yaml_methods|match_found|matching_java_files|java_methods|notes|
|---|---|---|---|---|---|---|
|authenticationproviders.yaml|/security/authproviders|get,post|yes|D:\DATA\Projects\Geoserver\all-source-code\geoserver-main\src\restconfig\src\main\java\org\geoserver\rest\security\AuthenticationProviderRestController.java|delete,get,post,put|extra_in_java:delete,put|
|coveragestores.yaml|/workspaces/{workspace}/coveragestores|delete,get,post,put|yes|D:\DATA\Projects\Geoserver\all-source-code\geoserver-main\src\restconfig\src\main\java\org\geoserver\rest\catalog\CoverageStoreController.java|delete,get,post,put|extra_in_java:delete,put  method_not_permitted_in_yaml:delete,put|
|coveragestores.yaml|/workspaces/{workspace}/coveragestores/{store}/{method}.{format}|delete,get,post,put|yes|D:\DATA\Projects\Geoserver\all-source-code\geoserver-main\src\restconfig\src\main\java\org\geoserver\rest\catalog\CoverageStoreFileController.java|delete,get,post,put|extra_in_java:delete,get  method_not_permitted_in_yaml:delete,get|
|datastores.yaml|/workspaces/{workspaceName}/datastores|delete,get,post,put|yes|D:\DATA\Projects\Geoserver\all-source-code\geoserver-main\src\restconfig\src\main\java\org\geoserver\rest\catalog\DataStoreController.java|delete,get,post,put|extra_in_java:delete,put  method_not_permitted_in_yaml:delete,put|
|datastores.yaml|/workspaces/{workspaceName}/datastores/{storeName}/{method}.{format}|delete,get,post,put|yes|D:\DATA\Projects\Geoserver\all-source-code\geoserver-main\src\restconfig\src\main\java\org\geoserver\rest\catalog\DataStoreFileController.java|delete,get,post,put|extra_in_java:delete,post  method_not_permitted_in_yaml:delete,post|
|featuretypes.yaml|/workspaces/{workspaceName}/datastores/{storeName}/featuretypes|delete,get,post,put|yes|D:\DATA\Projects\Geoserver\all-source-code\geoserver-main\src\restconfig\src\main\java\org\geoserver\rest\catalog\FeatureTypeController.java|delete,get,post,put|extra_in_java:delete,put  method_not_permitted_in_yaml:delete,put|
|featuretypes.yaml|/workspaces/{workspaceName}/featuretypes|delete,get,post,put|yes|D:\DATA\Projects\Geoserver\all-source-code\geoserver-main\src\restconfig\src\main\java\org\geoserver\rest\catalog\FeatureTypeController.java|delete,get,post,put|extra_in_java:delete,put  method_not_permitted_in_yaml:delete,put|
|filterchains.yaml|/security/filterchain|get,post|yes|D:\DATA\Projects\Geoserver\all-source-code\geoserver-main\src\restconfig\src\main\java\org\geoserver\rest\security\AuthenticationFilterChainRestController.java|delete,get,post,put|extra_in_java:delete,put|
|fonts.yaml|/fonts|delete,get,post,put|yes|D:\DATA\Projects\Geoserver\all-source-code\geoserver-main\src\restconfig\src\main\java\org\geoserver\rest\FontListController.java|delete,get,post,put|extra_in_java:delete,post,put  method_not_permitted_in_yaml:delete,post,put|
|importer.yaml|/imports|delete,get,post|yes|D:\DATA\Projects\Geoserver\all-source-code\geoserver-main\src\extension\importer\rest\src\main\java\org\geoserver\importer\rest\ImportController.java|delete,get,post,put|extra_in_java:put|

### implemented_in_dependency (first 10)
|yaml_file|endpoint|yaml_methods|match_found|matching_java_files|java_methods|notes|
|---|---|---|---|---|---|---|
|authenticationfilterconfiguration.yaml|/authfilters|get,post|no|||implemented_in_dependency:org.geowebcache:gwc-rest|
|authenticationfilterconfiguration.yaml|/authfilters/{filterName}|delete,get,put|no|||implemented_in_dependency:org.geowebcache:gwc-rest|
|authenticationproviders.yaml|/security/authproviders/{providerName}|delete,get,put|no|||implemented_in_dependency:org.geowebcache:gwc-rest|
|authenticationproviders.yaml|/security/authproviders/order|delete,get,post,put|no|||implemented_in_dependency:org.geowebcache:gwc-rest method_not_permitted_in_yaml:delete,get,post|
|filterchains.yaml|/security/filterchain/{chain_name}|delete,get,put|no|||implemented_in_dependency:org.geowebcache:gwc-rest|
|filterchains.yaml|/security/filterchain/order|put|no|||implemented_in_dependency:org.geowebcache:gwc-rest|
|importerData.yaml|/imports/{importId}/data|get|no|||implemented_in_dependency:org.geowebcache:gwc-rest|
|importerData.yaml|/imports/{importId}/tasks/{taskId}/data|get|no|||implemented_in_dependency:org.geowebcache:gwc-rest|
|importerData.yaml|/imports/{importId}/data/files|get|no|||implemented_in_dependency:org.geowebcache:gwc-rest|
|importerData.yaml|/imports/{importId}/data/files/{filename}|delete,get|no|||implemented_in_dependency:org.geowebcache:gwc-rest|

