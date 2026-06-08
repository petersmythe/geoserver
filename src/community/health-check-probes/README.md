# Health Check Probes Community Module

A GeoServer community module providing Kubernetes-style liveness and readiness probe endpoints.

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/management/health/liveness` | GET | Always returns 200 while GeoServer is running |
| `/management/health/readiness` | GET | Returns 200 when catalog is loaded, 503 during reload |

### Response Format

```json
{"status":"UP"}
```
or
```json
{"status":"DOWN"}
```

Content-Type: `application/json;charset=UTF-8`

## Building

### Build the module JAR only

```bash
cd src/community
mvn clean install -Phealth-check-probes -DskipTests
```

The JAR will be at:
```
src/community/health-check-probes/target/gs-health-check-probes-3.0-SNAPSHOT.jar
```

### Build with tests

```bash
cd src/community
mvn clean install -Phealth-check-probes
```

### Build from workspace root

```bash
mvn clean install -f src/community/pom.xml -Phealth-check-probes -DskipTests
```

## Deploying to GeoServer

### Option 1: Copy JAR to existing GeoServer installation

1. Build the module JAR (see above)
2. Copy the JAR into GeoServer's `WEB-INF/lib/` directory:

```bash
cp src/community/health-check-probes/target/gs-health-check-probes-3.0-SNAPSHOT.jar \
   /path/to/geoserver/webapps/geoserver/WEB-INF/lib/
```

3. Restart GeoServer

### Option 2: Build GeoServer with the module included

Build the full GeoServer web application with this module activated:

```bash
mvn clean install -DskipTests -Phealth-check-probes
```

Then run with the embedded Jetty:

```bash
cd src/web/app
mvn jetty:run -Phealth-check-probes
```

### Option 3: Run tests with embedded GeoServer (development)

```bash
cd src/community/health-check-probes
mvn test
```

## Verifying the Endpoints

Once GeoServer is running with the module installed:

```bash
# Liveness probe (always 200 while running)
curl -i http://localhost:8080/geoserver/management/health/liveness

# Readiness probe (200 after catalog loaded, 503 during reload)
curl -i http://localhost:8080/geoserver/management/health/readiness

# No authentication required - credentials are ignored
curl -i http://localhost:8080/geoserver/management/health/liveness -u invalid:credentials

# Non-GET methods return 405
curl -i -X POST http://localhost:8080/geoserver/management/health/liveness
```

## Kubernetes Configuration Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: geoserver
spec:
  template:
    spec:
      containers:
        - name: geoserver
          image: geoserver:latest
          livenessProbe:
            httpGet:
              path: /geoserver/management/health/liveness
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /geoserver/management/health/readiness
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 3
```

## How It Works

- **Liveness**: Simply returns 200/UP if the JVM and servlet container are responding. No dependencies.
- **Readiness**: Tracks GeoServer's lifecycle via `GeoServerReinitializer` and Spring's `ContextRefreshedEvent`:
  - Starts as DOWN (not ready)
  - Becomes UP when Spring context finishes refreshing (catalog loaded)
  - Goes DOWN during catalog reload (`beforeReinitialize`)
  - Returns to UP after reload completes (`reinitialize`)

The filter runs inside GeoServer's `SpringDelegatingFilter` and short-circuits health requests before they reach the dispatcher, ensuring fast responses with no authentication overhead.

## Module Status

After installation, the module registers itself in GeoServer's module status system. You can verify it's loaded via the REST API:

```bash
curl http://localhost:8080/geoserver/rest/about/status.json -u admin:geoserver | \
  jq '.about.status[] | select(.name == "gs-health-check-probes")'
```
