# GeoServer Bundled OpenAPI Specifications

This directory contains bundled, self-contained OpenAPI 3.0 specifications for the complete GeoServer API.

## Files

### Bundled Specifications (Single-File, Self-Contained)

- **geoserver-bundled.yaml** - Complete OpenAPI 3.0 specification in YAML format (892KB)
- **geoserver-bundled.json** - Complete OpenAPI 3.0 specification in JSON format (1.3MB)

These files are **self-contained** - all `$ref` references have been resolved and inlined. They are ready for:
- Swagger UI
- Redoc
- Postman import
- OpenAPI code generators
- Distribution to API consumers

### Modular Specifications (Development)

The modular source specifications are located in `.kiro/api-analysis/specs/`:
- `geoserver.yaml` - Main entry point with `$ref` to modular files
- `rest/` - REST API modules (core, gwc, security, extensions, community)
- `ogc/` - OGC service modules (WMS, WFS, WCS, WMTS, CSW, WPS)
- `common/` - Shared components (schemas, parameters, responses)

## Usage

### Swagger UI

```bash
# Serve with Swagger UI
docker run -p 8080:8080 -e SWAGGER_JSON=/api/geoserver-bundled.yaml \
  -v $(pwd)/doc/en/api:/api swaggerapi/swagger-ui
```

Then open http://localhost:8080

### Redoc

```bash
# Serve with Redoc
docker run -p 8080:80 -e SPEC_URL=/api/geoserver-bundled.yaml \
  -v $(pwd)/doc/en/api:/usr/share/nginx/html/api redocly/redoc
```

Then open http://localhost:8080

### Postman

1. Open Postman
2. Click "Import"
3. Select `geoserver-bundled.json`
4. Postman will create a collection with all endpoints

### Code Generation

```bash
# Generate Java client
openapi-generator-cli generate \
  -i doc/en/api/geoserver-bundled.yaml \
  -g java \
  -o generated/java-client

# Generate Python client
openapi-generator-cli generate \
  -i doc/en/api/geoserver-bundled.yaml \
  -g python \
  -o generated/python-client
```

## API Coverage

The bundled specifications include:

### REST API (300+ endpoints)
- Core configuration (workspaces, layers, styles, stores)
- GeoWebCache tile caching
- Security and authentication
- Extension modules
- Community modules

### OGC Services
- WMS (Web Map Service) - versions 1.1.1, 1.3.0
- WFS (Web Feature Service) - versions 1.0, 1.1, 2.0
- WCS (Web Coverage Service) - versions 1.0, 1.1, 2.0
- WMTS (Web Map Tile Service) - version 1.0
- CSW (Catalog Service for the Web) - version 2.0
- WPS (Web Processing Service) - version 1.0

## Validation

Both bundled files have been validated to ensure:
- ✓ Valid OpenAPI 3.0 format
- ✓ No external `$ref` references (fully self-contained)
- ✓ All paths, parameters, and responses included
- ✓ JSON uses 2-space indentation (per requirements)

## Regenerating Bundled Specs

To regenerate the bundled specifications from the modular sources:

```bash
python .kiro/api-analysis/bundle-spec.py
```

This will:
1. Load the modular specification from `.kiro/api-analysis/specs/geoserver.yaml`
2. Merge all referenced module files
3. Resolve all `$ref` references
4. Generate self-contained `geoserver-bundled.yaml` and `geoserver-bundled.json`

## License

GeoServer is licensed under GPL 2.0. See https://www.gnu.org/licenses/gpl-2.0.html

## More Information

- GeoServer Website: https://geoserver.org
- Documentation: https://docs.geoserver.org/
- Source Code: https://github.com/geoserver/geoserver
