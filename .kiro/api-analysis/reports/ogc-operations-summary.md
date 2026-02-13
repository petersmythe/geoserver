# OGC Service Operations Summary

**Extraction Date:** 2026-02-12

## Overview

- **Total Services:** 6
- **Total Operations:** 38

## Services

### WMS - Web Map Service

**Description:** OGC Web Map Service for rendering maps from geospatial data

**Versions:** 1.0.0, 1.1.0, 1.1.1, 1.3.0

**Operations:** 7

- **GetCapabilities**
  - Returns service metadata and available layers
  - HTTP Methods: GET, POST
  - Parameters: 7

- **GetMap**
  - Returns a map image for specified layers and area
  - HTTP Methods: GET, POST
  - Parameters: 41

- **GetFeatureInfo**
  - Returns information about features at a pixel location
  - HTTP Methods: GET, POST
  - Parameters: 8
  - Note: Includes all GetMap parameters to define the map context

- **GetLegendGraphic**
  - Returns a legend graphic for a layer style
  - HTTP Methods: GET, POST
  - Parameters: 18

- **DescribeLayer**
  - Returns layer metadata including feature type and WFS URL
  - HTTP Methods: GET, POST
  - Parameters: 5

- **reflect** *(vendor extension)*
  - GetMap reflector with simplified parameters
  - HTTP Methods: GET
  - Parameters: 2
  - Note: Vendor extension - simplified GetMap with intelligent defaults

- **kml** *(vendor extension)*
  - KML reflector for Google Earth integration
  - HTTP Methods: GET
  - Parameters: 1
  - Note: Vendor extension - generates KML/KMZ output


### WFS - Web Feature Service

**Description:** OGC Web Feature Service for vector data access and editing

**Versions:** 1.0.0, 1.1.0, 2.0.0

**Operations:** 13

- **GetCapabilities**
  - Returns service metadata and available feature types
  - HTTP Methods: GET, POST
  - Parameters: 8

- **DescribeFeatureType**
  - Returns XML schema for requested feature types
  - HTTP Methods: GET, POST
  - Parameters: 7

- **GetFeature**
  - Returns feature instances matching the query
  - HTTP Methods: GET, POST
  - Parameters: 21

- **GetFeatureWithLock** (versions: 1.1.0, 2.0.0)
  - Returns features and locks them for editing
  - HTTP Methods: GET, POST
  - Parameters: 2
  - Note: Includes all GetFeature parameters plus lock-specific parameters

- **LockFeature**
  - Locks features for exclusive editing access
  - HTTP Methods: GET, POST
  - Parameters: 9

- **Transaction**
  - Inserts, updates, or deletes features
  - HTTP Methods: POST
  - Parameters: 5
  - Note: Transaction elements (Insert, Update, Delete, Native) are specified in POST body

- **GetGmlObject** (versions: 1.1.0)
  - Returns a GML object by ID
  - HTTP Methods: GET, POST
  - Parameters: 5

- **GetPropertyValue** (versions: 2.0.0)
  - Returns values of a specific property
  - HTTP Methods: GET, POST
  - Parameters: 8

- **ListStoredQueries** (versions: 2.0.0)
  - Returns list of available stored queries
  - HTTP Methods: GET, POST
  - Parameters: 3

- **DescribeStoredQueries** (versions: 2.0.0)
  - Returns metadata for stored queries
  - HTTP Methods: GET, POST
  - Parameters: 4

- **CreateStoredQuery** (versions: 2.0.0)
  - Creates a new stored query
  - HTTP Methods: POST
  - Parameters: 3
  - Note: Query definition is specified in POST body

- **DropStoredQuery** (versions: 2.0.0)
  - Deletes a stored query
  - HTTP Methods: GET, POST
  - Parameters: 4

- **ReleaseLock** *(vendor extension)*
  - Releases a previously acquired lock
  - HTTP Methods: GET, POST
  - Parameters: 4
  - Note: Not part of official WFS specification


### WCS - Web Coverage Service

**Description:** OGC Web Coverage Service for raster data access

**Versions:** 1.0.0, 1.1.0, 1.1.1, 2.0.0, 2.0.1

**Operations:** 3

- **GetCapabilities**
  - Returns service metadata and available coverages
  - HTTP Methods: GET, POST
  - Parameters: 6

- **DescribeCoverage**
  - Returns detailed coverage metadata
  - HTTP Methods: GET, POST
  - Parameters: 6

- **GetCoverage**
  - Returns coverage data
  - HTTP Methods: GET, POST
  - Parameters: 17


### WMTS - Web Map Tile Service

**Description:** OGC Web Map Tile Service for tiled map access

**Versions:** 1.0.0

**Operations:** 3

- **GetCapabilities**
  - Returns service metadata and available tile matrix sets
  - HTTP Methods: GET, POST
  - Parameters: 6

- **GetTile**
  - Returns a tile from a tile matrix set
  - HTTP Methods: GET
  - Parameters: 12

- **GetFeatureInfo**
  - Returns information about features at a tile location
  - HTTP Methods: GET
  - Parameters: 13


### CSW - Catalog Service for the Web

**Description:** OGC Catalog Service for metadata discovery

**Versions:** 2.0.2

**Operations:** 7

- **GetCapabilities**
  - Returns service metadata
  - HTTP Methods: GET, POST
  - Parameters: 6

- **DescribeRecord**
  - Returns schema information for record types
  - HTTP Methods: GET, POST
  - Parameters: 6

- **GetRecords**
  - Searches and returns catalog records
  - HTTP Methods: GET, POST
  - Parameters: 14

- **GetRecordById**
  - Returns a specific catalog record by ID
  - HTTP Methods: GET, POST
  - Parameters: 7

- **GetDomain**
  - Returns domain values for a property
  - HTTP Methods: GET, POST
  - Parameters: 5

- **Transaction**
  - Inserts, updates, or deletes catalog records
  - HTTP Methods: POST
  - Parameters: 3
  - Note: Transaction operations (Insert, Update, Delete) specified in POST body

- **Harvest**
  - Harvests metadata from external sources
  - HTTP Methods: POST
  - Parameters: 6


### WPS - Web Processing Service

**Description:** OGC Web Processing Service for geospatial processing

**Versions:** 1.0.0

**Operations:** 5

- **GetCapabilities**
  - Returns service metadata and available processes
  - HTTP Methods: GET, POST
  - Parameters: 5

- **DescribeProcess**
  - Returns detailed process descriptions
  - HTTP Methods: GET, POST
  - Parameters: 5

- **Execute**
  - Executes a process with specified inputs
  - HTTP Methods: GET, POST
  - Parameters: 9
  - Note: Complex inputs and outputs typically specified in POST body

- **GetExecutionStatus** *(vendor extension)*
  - Returns status of asynchronous execution
  - HTTP Methods: GET
  - Parameters: 1
  - Note: GeoServer extension for checking async execution status

- **Dismiss** *(vendor extension)*
  - Dismisses a stored execution result
  - HTTP Methods: GET
  - Parameters: 1
  - Note: GeoServer extension for cleaning up stored results


## Operation Count by Service

| Service | Title | Versions | Operations |
|---------|-------|----------|------------|
| WMS | Web Map Service | 1.0.0, 1.1.0, 1.1.1, 1.3.0 | 7 |
| WFS | Web Feature Service | 1.0.0, 1.1.0, 2.0.0 | 13 |
| WCS | Web Coverage Service | 1.0.0, 1.1.0, 1.1.1, 2.0.0, 2.0.1 | 3 |
| WMTS | Web Map Tile Service | 1.0.0 | 3 |
| CSW | Catalog Service for the Web | 2.0.2 | 7 |
| WPS | Web Processing Service | 1.0.0 | 5 |

## Parameter Statistics

- **WMS**: 82 total parameters, 11.7 average per operation
- **WFS**: 83 total parameters, 6.4 average per operation
- **WCS**: 29 total parameters, 9.7 average per operation
- **WMTS**: 31 total parameters, 10.3 average per operation
- **CSW**: 47 total parameters, 6.7 average per operation
- **WPS**: 21 total parameters, 4.2 average per operation
