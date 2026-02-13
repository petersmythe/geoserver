# OGC OpenAPI 3.0 Specifications - Generation Summary

Generated: D:\DATA\Projects\Geoserver\ALL-SOURCE-CODE\geoserver-main

## Generated Specifications

### GeoServer Web Map Service API

- **File**: `ogc/wms.yaml`
- **Service**: WMS
- **Versions**: 1.0.0, 1.1.0, 1.1.1, 1.3.0
- **Operations**: 48
- **Description**: OGC Web Map Service for rendering maps from geospatial data

### GeoServer Web Feature Service API

- **File**: `ogc/wfs.yaml`
- **Service**: WFS
- **Versions**: 1.0.0, 1.1.0, 2.0.0
- **Operations**: 48
- **Description**: OGC Web Feature Service for vector data access and editing

### GeoServer Web Coverage Service API

- **File**: `ogc/wcs.yaml`
- **Service**: WCS
- **Versions**: 1.0.0, 1.1.0, 1.1.1, 2.0.0, 2.0.1
- **Operations**: 30
- **Description**: OGC Web Coverage Service for raster data access

### GeoServer Web Map Tile Service API

- **File**: `ogc/wmts.yaml`
- **Service**: WMTS
- **Versions**: 1.0.0
- **Operations**: 4
- **Description**: OGC Web Map Tile Service for tiled map access

### GeoServer Catalog Service for the Web API

- **File**: `ogc/csw.yaml`
- **Service**: CSW
- **Versions**: 2.0.2
- **Operations**: 12
- **Description**: OGC Catalog Service for metadata discovery

### GeoServer Web Processing Service API

- **File**: `ogc/wps.yaml`
- **Service**: WPS
- **Versions**: 1.0.0
- **Operations**: 8
- **Description**: OGC Web Processing Service for geospatial processing

## Summary Statistics

- **Total Services**: 6
- **Total Operations**: 150
- **Total Version Variants**: 15

## OpenAPI 3.0 Features

- Version-specific operation IDs (e.g., WMS_1_3_0_GetMap, WMS_1_1_1_GetMap)
- Service type tags for organization
- Complete parameter definitions with types, descriptions, and constraints
- Vendor extension parameters clearly marked
- CRS/EPSG parameter documentation
- Error response schemas (OGCException)
- Multiple server configurations (local and production)
- Separate paths per operation/version for documentation clarity

## Implementation Notes

OGC services typically use a single endpoint (e.g., `/wms`) with the REQUEST parameter
to distinguish operations. For documentation clarity, this specification uses separate
paths for each operation and version combination.

## Files Generated

- `.kiro/api-analysis/specs/ogc/wms.yaml`
- `.kiro/api-analysis/specs/ogc/wfs.yaml`
- `.kiro/api-analysis/specs/ogc/wcs.yaml`
- `.kiro/api-analysis/specs/ogc/wmts.yaml`
- `.kiro/api-analysis/specs/ogc/csw.yaml`
- `.kiro/api-analysis/specs/ogc/wps.yaml`
