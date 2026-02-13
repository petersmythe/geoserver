# Implemented REST Endpoints Summary

## Overview

- **Total Unique Endpoints**: 353
- **Duplicates Removed**: 31
- **Source Files**: 5

## Endpoints by HTTP Method

| HTTP Method | Count |
|-------------|-------|
| DELETE | 63 |
| GET | 163 |
| PATCH | 2 |
| POST | 64 |
| PUT | 61 |

## Endpoints by Module

| Module | Count |
|--------|-------|
| backup-restore | 6 |
| features-templating | 18 |
| geofence | 11 |
| gsr | 33 |
| gwc | 5 |
| importer | 22 |
| jms-cluster | 2 |
| metadata | 1 |
| mongodb | 4 |
| monitor | 3 |
| oseo | 35 |
| params-extractor | 10 |
| proxy-base-ext | 5 |
| rat | 2 |
| rest | 1 |
| restconfig | 182 |
| restconfig-wcs | 1 |
| restconfig-wfs | 1 |
| restconfig-wms | 1 |
| restconfig-wmts | 1 |
| sldService | 5 |
| taskmanager | 1 |
| vector-mosaic | 1 |
| wps-download | 2 |

## Module Categories

### Core Modules

- **Total Core Endpoints**: 353
  - backup-restore: 6
  - features-templating: 18
  - geofence: 11
  - gsr: 33
  - gwc: 5
  - importer: 22
  - jms-cluster: 2
  - metadata: 1
  - mongodb: 4
  - monitor: 3
  - oseo: 35
  - params-extractor: 10
  - proxy-base-ext: 5
  - rat: 2
  - rest: 1
  - restconfig: 182
  - restconfig-wcs: 1
  - restconfig-wfs: 1
  - restconfig-wms: 1
  - restconfig-wmts: 1
  - sldService: 5
  - taskmanager: 1
  - vector-mosaic: 1
  - wps-download: 2

### Extension Modules

- **Total Extension Endpoints**: 0

### Community Modules

- **Total Community Endpoints**: 0

## Sample Endpoints

### First 10 Endpoints

| Method | Path | Module | Class |
|--------|------|--------|-------|
| DELETE | / | metadata | MetaDataRestService |
| GET | / | restconfig | FQN |
| POST | / | restconfig | FQN |
| GET | /${gwc.context.suffix:} | gwc | GeoServerGWCDispatcherController |
| GET | /${gwc.context.suffix:}/${gwc.context.suffix:} | gwc | GeoServerGWCDispatcherController |
| GET | /${gwc.context.suffix:}/demo/** | gwc | GeoServerGWCDispatcherController |
| GET | /${gwc.context.suffix:}/home | gwc | GeoServerGWCDispatcherController |
| GET | /${gwc.context.suffix:}/proxy/** | gwc | GeoServerGWCDispatcherController |
| GET | /.{ext:xml|json | restconfig | FQN |
| GET | /EchoesController.ECHOES_ROOT | params-extractor | EchoesController |

## Duplicates Removed

Found 31 duplicate endpoints:

- POST:/rest/styles (from .kiro/api-analysis/rest/implemented-core-endpoints.json)
- GET:/rest/styles/{styleName (from .kiro/api-analysis/rest/implemented-core-endpoints.json)
- PUT:/rest/styles/{styleName (from .kiro/api-analysis/rest/implemented-core-endpoints.json)
- PUT:/rest/styles/{styleName (from .kiro/api-analysis/rest/implemented-core-endpoints.json)
- GET:/rest/workspaces/{workspaceName (from .kiro/api-analysis/rest/implemented-core-endpoints.json)
- POST:/rest/workspaces/{workspaceName (from .kiro/api-analysis/rest/implemented-core-endpoints.json)
- GET:/rest/workspaces/{workspaceName (from .kiro/api-analysis/rest/implemented-core-endpoints.json)
- GET:/rest/workspaces/{workspaceName/{layerName} (from .kiro/api-analysis/rest/implemented-core-endpoints.json)
- PUT:/rest/workspaces/{workspaceName/{layerName} (from .kiro/api-analysis/rest/implemented-core-endpoints.json)
- DELETE:/rest/workspaces/{workspaceName/{layerName} (from .kiro/api-analysis/rest/implemented-core-endpoints.json)

## Source Files

- .kiro/api-analysis/rest/implemented-core-endpoints.json
- .kiro/api-analysis/rest/implemented-service-endpoints.json
- .kiro/api-analysis/rest/implemented-gwc-endpoints.json
- .kiro/api-analysis/rest/implemented-extension-endpoints.json
- .kiro/api-analysis/rest/implemented-community-endpoints.json

---

*Generated from 5 source files*