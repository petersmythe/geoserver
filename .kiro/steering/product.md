---
inclusion: always
---

# GeoServer Product Overview

GeoServer is an open source Java-based geospatial server that publishes spatial data using OGC standards. It's designed for interoperability and supports multiple data sources and output formats.

## Core Standards (OGC Certified)

When working with GeoServer code, understand these primary service standards ([https://www.ogc.org/standards/](https://www.ogc.org/standards/)):

- WMS (Web Map Service) - Map rendering, revisions 1.3, 1.1, 1.0
- WFS (Web Feature Service) - Vector data access/editing, revisions 2.0, 1.1, 1.0 (reference implementation)
- WCS (Web Coverage Service) - Raster data access, revisions 2.0, 1.1, 1.0 (reference implementation)
- WMTS (Web Map Tile Service) - Tiled map serving, revision 1.0
- OGC API - Features - Modern REST API, revision 1.0
- CSW (Catalog Service) - Metadata catalog, revision 2.0
- WPS (Web Processing Service) - Geospatial processing, revision 1.0
- GeoTIFF - revision 1.1
- GPKG (GeoPackage) - revision 1.2

Community standards: TMS (Tile Map Service), WMS-C

## Supported Data Formats

Vector outputs: KML, GML, Shapefile, GeoJSON, GeoRSS
Raster outputs: JPEG, PNG, GIF, SVG, GeoTIFF
Document outputs: PDF

## Key Architectural Components

### GeoTools Integration
- Core dependency for geospatial operations
- Provides format readers/writers, coordinate transformations, and geometry operations
- Repository: https://github.com/geotools/geotools
- License: LGPL (note: different from GeoServer's GPL 2.0)

### GeoWebCache Integration
- Integrated tile caching layer for performance
- Supports WMS-C, TMS, WMTS, Google Maps, Bing tile formats
- Repository: https://github.com/GeoWebCache/geowebcache

### Service Architecture
- Each OGC service (WMS, WFS, WCS, etc.) is implemented as a separate module
- REST API provides configuration and management capabilities
- Catalog system manages workspaces, stores, layers, and styles

## Deployment Options

### Platform-Independent Binary
- GeoServer bundled with Jetty application server
- Works consistently across all operating systems

### WAR (Web Archive)
- Deploy to existing servlet containers (Apache Tomcat recommended, Jetty supported)
- Built from source: `mvn clean install` produces WAR in `web/target/` directory

### Docker
- Official containerized deployment
- Repository: https://github.com/geoserver/docker

## Development Conventions

### Standards Compliance
- Maintain strict OGC specification compliance for certified services
- Reference official OGC specifications when implementing service endpoints
- Preserve backward compatibility across standard versions

### Interoperability Focus
- Support multiple coordinate reference systems (EPSG database)
- Enable on-demand reprojection between CRS
- Ensure output format flexibility

### Performance Considerations
- Leverage GeoWebCache for tile-based services
- Optimize spatial queries and filtering
- Consider memory usage for large raster operations

## Resources

### Documentation & Support
- Website: https://geoserver.org/
- Documentation: https://docs.geoserver.org/
- Source Code: https://github.com/geoserver/geoserver
- Blog: https://geoserver.org/blog/
- Community Forum: https://discourse.osgeo.org/c/geoserver/50/

### Issue Tracking
- JIRA: https://osgeo-org.atlassian.net/projects/GEOS

## AI Assistant Guidelines

When working with this codebase:
- Respect OGC standard specifications and maintain compliance
- Consider both GeoTools (LGPL) and GeoServer (GPL 2.0) licensing
- Test against multiple data formats and coordinate systems
- Verify backward compatibility with older standard versions
- Check integration points with GeoWebCache for tile-based operations
- Reference official documentation for standard-specific behavior
