# GeoWebCache REST API Analysis

## Overview

GeoWebCache provides its own REST API that is integrated into GeoServer at the `/gwc/rest` path. This API is provided by the GeoWebCache library itself, not by GeoServer's `gwc-rest` module. The `gwc-rest` module only provides configuration support for marshaling/unmarshaling GeoServer-specific tile layer objects.

## Key Findings

### 1. GeoWebCache REST API is External

The GeoWebCache REST API endpoints are implemented in the GeoWebCache library (org.geowebcache:gwc-rest), not in GeoServer's source code. GeoServer integrates this API through:

- **GeoServerGWCDispatcherController**: A Spring controller that extends `GeoWebCacheDispatcherController` from the GeoWebCache library
- **Path Configuration**: Uses `${gwc.context.suffix:}` property (defaults to empty string, making paths like `/gwc/rest/...`)
- **Integration Module**: `src/gwc-rest/` provides XStream configuration for REST serialization of GeoServer tile layers

### 2. Available GeoWebCache REST Endpoints

Based on official GeoWebCache documentation ([https://geowebcache.osgeo.org/docs/current/rest/](https://geowebcache.osgeo.org/docs/current/rest/)), the following endpoints are available:

#### Layer Management (`/gwc/rest/layers`)

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/gwc/rest/layers` | GET | List all cached layers |
| `/gwc/rest/layers/{layer}.xml` | GET, PUT, DELETE | Manage individual layer configuration |

**Formats**: XML only (JSON intentionally excluded due to marshaling issues with multi-valued properties)

#### Seeding and Truncation (`/gwc/rest/seed`)

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/gwc/rest/seed/{layer}.{format}` | GET, POST | Seed/truncate tiles for a layer, or get seeding status |
| `/gwc/rest/seed/{layer}` | POST | Terminate running/pending tasks for a layer |
| `/gwc/rest/seed.json` | GET | Get status of all seeding threads |
| `/gwc/rest/seed` | POST | Terminate all running/pending tasks |

**Formats**: XML, JSON

**Operations**:
- **seed**: Add tiles to cache
- **reseed**: Replace existing tiles
- **truncate**: Remove tiles from cache

#### GridSet Management (`/gwc/rest/gridsets`)

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/gwc/rest/gridsets` | GET | List all gridsets |
| `/gwc/rest/gridsets/{gridset}.xml` | GET, PUT, DELETE | Manage individual gridset configuration |

**Formats**: XML, JSON

#### BlobStore Management (`/gwc/rest/blobstores`)

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/gwc/rest/blobstores` | GET | List all blobstores |
| `/gwc/rest/blobstores/{blobstore}` | GET, PUT, DELETE | Manage individual blobstore configuration |

**Formats**: XML, JSON

#### Disk Quota Management (`/gwc/rest/diskquota`)

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/gwc/rest/diskquota` | GET, PUT | Get/set global disk quota configuration |
| `/gwc/rest/diskquota/{layer}` | GET, PUT, DELETE | Get/set/remove layer-specific disk quota |

**Formats**: XML, JSON

#### Global Configuration (`/gwc/rest/global`)

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/gwc/rest/global` | GET, PUT | Get/set global GeoWebCache configuration |

**Formats**: XML

#### Statistics (`/gwc/rest/statistics`)

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/gwc/rest/statistics` | GET | Get in-memory cache statistics |

**Formats**: JSON

#### Mass Truncation (`/gwc/rest/masstruncate`)

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/gwc/rest/masstruncate` | POST | Truncate tiles across multiple layers based on criteria |

**Formats**: XML, JSON

### 3. Authentication

All POST, PUT, and DELETE requests require HTTP Basic Authentication. GET requests may also require authentication depending on GeoServer security configuration.

### 4. Integration with GeoServer

When GeoWebCache is integrated with GeoServer:
- Base path is `/geoserver/gwc/rest` (instead of standalone `/geowebcache/rest`)
- Uses GeoServer's authentication system
- Layer names follow GeoServer naming conventions (workspace:layer)
- Configuration is stored in GeoServer's data directory

## Recommendations

### For OpenAPI Documentation

1. **Document all GeoWebCache REST endpoints** under the "REST GWC" tag
2. **Use `/gwc/rest` as the base path** (GeoServer integrated version)
3. **Mark as external API** - Note that these endpoints are provided by GeoWebCache library
4. **Document authentication requirements** - HTTP Basic Auth required for modifications
5. **Include format limitations** - Some endpoints only support XML, not JSON
6. **Add examples** - Include sample requests/responses from official documentation

### For Task 15.7 Completion

The "REST GWC" tag should be populated with comprehensive endpoint documentation based on the official GeoWebCache REST API specification, not by extracting from GeoServer source code (since the implementation is in the external GeoWebCache library).

## References

- [GeoWebCache REST API Documentation](https://geowebcache.osgeo.org/docs/current/rest/)
- [Managing Layers](https://geowebcache.osgeo.org/docs/current/rest/layers.html)
- [Seeding and Truncating](https://geowebcache.osgeo.org/docs/current/rest/seed.html)
- [GeoServer GeoWebCache Integration](https://docs.geoserver.org/stable/en/user/geowebcache/rest/)
