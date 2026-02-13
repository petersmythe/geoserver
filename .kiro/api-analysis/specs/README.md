# GeoServer OpenAPI Specifications

This directory contains the modular OpenAPI 3.0 specifications for GeoServer's REST API and OGC services.

## Structure

### Entry Points
- `geoserver.yaml` - Main YAML entry point with metadata and module references
- `geoserver.json` - Main JSON entry point with metadata and module references

### Modular Specifications

#### REST API Modules (`rest/`)
- `rest-core.yaml` - Core REST API endpoints (workspaces, layers, styles, stores)
- `rest-gwc.yaml` - GeoWebCache REST API endpoints (tile layers, gridsets)
- `rest-security.yaml` - Security REST API endpoints (users, roles, authentication)
- `rest-extensions.yaml` - Extension module REST API endpoints
- `rest-community.yaml` - Community module REST API endpoints

#### OGC Service Modules (`ogc/`)
- `wms.yaml` - Web Map Service (WMS) operations for all versions
- `wfs.yaml` - Web Feature Service (WFS) operations for all versions
- `wcs.yaml` - Web Coverage Service (WCS) operations for all versions
- `wmts.yaml` - Web Map Tile Service (WMTS) operations
- `csw.yaml` - Catalog Service for the Web (CSW) operations
- `wps.yaml` - Web Processing Service (WPS) operations

#### Common Components (`common/`)
- `schemas.yaml` - Reusable schema definitions
- `parameters.yaml` - Reusable parameter definitions
- `responses.yaml` - Reusable response definitions (error responses, etc.)

## Usage

### Option 1: Bundled Single-File Versions (Recommended)

The modular specifications need to be bundled into single files for use with most OpenAPI tools. Task 14.4 generates these bundled versions:

- `doc/en/api/geoserver-bundled.yaml` - Complete specification in YAML format
- `doc/en/api/geoserver-bundled.json` - Complete specification in JSON format

These bundled files are self-contained and can be used directly with:
- Swagger UI
- Redoc
- Postman
- OpenAPI Generator
- Any other OpenAPI 3.0 compatible tool

### Option 2: Manual Bundling

If you need to regenerate the bundled specifications manually, you can use bundling tools:

#### Using swagger-cli
```bash
npm install -g @apidevtools/swagger-cli
swagger-cli bundle geoserver.yaml -o geoserver-bundled.yaml -t yaml
swagger-cli bundle geoserver.yaml -o geoserver-bundled.json -t json
```

#### Using redocly
```bash
npm install -g @redocly/cli
redocly bundle geoserver.yaml -o geoserver-bundled.yaml
```

#### Using openapi-merge-cli
```bash
npm install -g openapi-merge-cli
openapi-merge-cli --config merge-config.json
```

### Option 3: Direct Use (Limited Support)

Some tools support modular specifications with `$ref` references, but this is not universally supported. The entry point files (`geoserver.yaml` and `geoserver.json`) contain metadata about the modular structure but include only a placeholder endpoint.

## Viewing the Documentation

### Swagger UI
1. Use the bundled version from task 14.4
2. Open Swagger UI: https://petstore.swagger.io/
3. Enter the URL or upload the bundled YAML/JSON file

### Redoc
1. Use the bundled version from task 14.4
2. Open Redoc: https://redocly.github.io/redoc/
3. Enter the URL or use redoc-cli locally

### Local Swagger UI
```bash
docker run -p 8080:8080 -e SWAGGER_JSON=/specs/geoserver-bundled.yaml \
  -v $(pwd):/specs swaggerapi/swagger-ui
```

## Maintenance

### Adding New Endpoints
1. Add endpoints to the appropriate modular file (rest/*.yaml or ogc/*.yaml)
2. Update common components if needed (common/*.yaml)
3. Regenerate bundled versions using task 14.4

### Updating Tags
All tags are defined in the main entry point files (`geoserver.yaml` and `geoserver.json`). Update these files to add or modify tag definitions.

### Updating Metadata
Update the `info` section in the main entry point files to change:
- API version
- Description
- Contact information
- License information

## Validation

To validate the specifications:

```bash
# Using swagger-cli
swagger-cli validate geoserver-bundled.yaml

# Using redocly
redocly lint geoserver-bundled.yaml

# Using openapi-generator
openapi-generator validate -i geoserver-bundled.yaml
```

## Notes

- The modular structure improves maintainability by separating concerns
- Each module can be developed and tested independently
- The bundled versions are required for most OpenAPI tools
- All specifications follow OpenAPI 3.0.0 standard
- Version-specific OGC operations use distinct operation IDs (e.g., WMS_1_1_GetMap, WMS_1_3_GetMap)
