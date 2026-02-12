---
inclusion: always
---

# Project Structure

## Repository Layout

```
geoserver/
├── src/                    # Main source code directory
│   ├── platform/          # Core platform modules
│   ├── main/              # Main GeoServer application
│   ├── security/          # Security modules
│   ├── ows/               # OGC Web Services base
│   ├── wcs/               # Web Coverage Service
│   ├── wcs2_0/            # WCS 2.0 implementation
│   ├── wfs-core/          # Web Feature Service core
│   ├── wfs1_x/            # WFS 1.x implementation
│   ├── wfs2_x/            # WFS 2.x implementation
│   ├── wms/               # Web Map Service
│   ├── wms-gml/           # WMS GML support
│   ├── gwc/               # GeoWebCache integration
│   ├── gwc-rest/          # GeoWebCache REST API
│   ├── rest/              # REST API
│   ├── restconfig/        # REST configuration API
│   ├── restconfig-wcs/    # WCS REST configuration
│   ├── restconfig-wfs/    # WFS REST configuration
│   ├── restconfig-wms/    # WMS REST configuration
│   ├── restconfig-wmts/   # WMTS REST configuration
│   ├── web/               # Web UI modules
│   ├── extension/         # Optional extensions (see below)
│   ├── community/         # Community modules (see below)
│   └── pom.xml            # Root Maven POM
├── build/                 # Build and release tooling
│   ├── cite/              # CITE compliance testing (see below)
│   ├── acceptance/        # Acceptance test configurations
│   ├── qa/                # Quality assurance scripts
│   ├── data/              # Build-time data
│   └── transifex/         # Translation management
├── data/                  # Sample data directories
│   ├── minimal/           # Minimal configuration
│   ├── release/           # Release data directory
│   ├── app-schema-tutorial/
│   ├── citecsw-2.0.2/
│   └── citensg-1.0/
├── doc/                   # Documentation source
├── licenses/              # License files
└── tools/                 # Development tools
```

## Module Organization

### Core Modules (src/)
Essential GeoServer components that form the base system. All core modules must maintain high quality standards and OGC compliance.

### Extension Modules (src/extension/)
Optional functionality maintained by core developers. Extensions follow the same quality standards as core modules.

Key extensions:
- app-schema - Complex feature support (GeoSciML, INSPIRE)
- authkey - Authentication via URL keys
- csw - Catalog Service for the Web
- db2, h2, mysql, oracle, sqlserver - Database store support
- gdal, ogr - GDAL/OGR format support
- geofence - Advanced authorization
- geopkg-output - GeoPackage output format
- importer - Bulk data import
- inspire - INSPIRE directive compliance
- kml - KML/KMZ output
- mapml - MapML format support
- mbstyle - Mapbox Style support
- monitor - Request monitoring
- netcdf, netcdf-out - NetCDF format support
- ogcapi - OGC API implementations
- printing - Map printing (MapFish Print)
- security - Advanced security modules
- vectortiles - Vector tile output (MVT)
- wcs, wcs2_0-eo - WCS extensions
- wps, wps-download, wps-jdbc - Web Processing Service
- ysld - YAML-based styling

### Community Modules (src/community/)
Experimental or specialized modules maintained by community members. May have different quality standards and support levels.

Notable community modules:
- backup-restore - Configuration backup/restore
- cog - Cloud Optimized GeoTIFF support
- elasticsearch - Elasticsearch data store
- features-templating - Advanced feature templating
- flatgeobuf, geoparquet - Modern vector formats
- gwc-azure-blob, gwc-gcs-blob, gwc-s3 - Cloud storage for tiles
- hz-cluster, jms-cluster - Clustering solutions
- jdbcconfig, jdbcstore - Database-backed configuration
- jwt-headers - JWT authentication
- mbtiles, pmtiles-store - Tile archive formats
- monitor-kafka, monitor-micrometer - Advanced monitoring
- ogcapi - Experimental OGC API features
- rest-openapi - OpenAPI documentation for REST
- saml - SAML authentication
- smart-data-loader - Intelligent data loading
- stac-datastore - SpatioTemporal Asset Catalog
- taskmanager - Task scheduling and management
- wps-openai - AI-powered WPS processes

## CITE Testing Structure (build/cite/)

OGC compliance testing infrastructure using TeamEngine and Docker.

```
build/cite/
├── wms11/, wms13/         # WMS 1.1 and 1.3 test suites
├── wfs10/, wfs11/, wfs20/ # WFS 1.0, 1.1, 2.0 test suites
├── wcs10/, wcs11/, wcs20/ # WCS test suites
├── wmts10/                # WMTS 1.0 test suite
├── ogcapi-features10/     # OGC API - Features test suite
├── ogcapi-tiles10/        # OGC API - Tiles test suite
├── geotiff11/             # GeoTIFF 1.1 test suite
├── gpkg12/                # GeoPackage 1.2 test suite
├── geoserver/             # GeoServer WAR and configuration
├── postgres/              # PostgreSQL/PostGIS for tests
├── logs/                  # Test execution logs
└── Makefile               # Test orchestration
```

Each test suite directory contains:
- Docker Compose configuration
- Test data and configuration
- Suite-specific GeoServer setup

## Source Code Conventions

### File Organization
- All source code under `src/` directory
- Each module has its own `pom.xml` for Maven configuration
- Test code follows same package structure as main code
- Configuration files use XML format (Spring, Maven)

### Module Dependencies
- Core modules cannot depend on extensions
- Extensions can depend on core modules
- Community modules have relaxed dependency rules
- Check parent POM for managed dependency versions

### Build Artifacts
- Compiled classes: `target/` in each module
- Final WAR: `src/web/app/target/geoserver.war`
- Release artifacts: `src/release/target/`
- Spotless formatting index: `.spotless-index` files

## Data Directories

Sample data directories provide different GeoServer configurations:
- `minimal/` - Bare minimum configuration for testing
- `release/` - Full-featured release configuration
- `app-schema-tutorial/` - Complex feature examples
- `citecsw-2.0.2/`, `citensg-1.0/` - CITE test configurations

## Development Guidelines

### Adding New Modules
- Extensions: Coordinate with core team, follow core standards
- Community: More flexible, document in community README
- Always add module to appropriate parent POM
- Include tests and documentation

### Module Naming
- Core services: `wms`, `wfs`, `wcs`, etc.
- Extensions: descriptive names (`importer`, `monitor`)
- Community: may include vendor/technology names

### Testing Locations
- Unit tests: `src/test/java` in each module
- Integration tests: May use Testcontainers
- CITE tests: `build/cite/` directory
- Acceptance tests: `build/acceptance/`
