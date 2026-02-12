---
inclusion: always
---

# Technology Stack & Development Guidelines

## Core Technologies

- Java 17+ (minimum required, use modern Java features appropriately)
- Apache Maven 3.8+ (all builds must use Maven, not Gradle)
- Spring Framework 7.0.2 with Spring Security 7.0.2
- Apache Wicket 10.7.0 (for web UI components)
- GeoTools [version synchronised with GeoServer] (core geospatial library)
- GeoWebCache [version synchronised with GeoServer] (tile caching)
- Jetty 12.1.3 (embedded server for development)
- Hibernate 7.1.4.Final (ORM)

## Code Style & Quality Requirements

### Mandatory Formatting
- ALL code MUST be formatted with Spotless (Palantir Java Format 2.74.0)
- Run `mvn spotless:apply` before committing any Java code
- Never commit code that fails `mvn spotless:check`
- Formatting is enforced in CI/CD pipeline

### Code Quality Standards
- Enable quality checks with `-Dqa=true` for production code
- Address Checkstyle, PMD, and Error Prone warnings
- Maintain or improve JaCoCo code coverage (0.8.14)
- Use Error Prone 2.31.0 annotations to catch common bugs

### Testing Requirements
- Use JUnit 5.13.4 (Jupiter) for all new tests
- Prefer Mockito 5.20.0 for mocking over manual stubs
- Use Testcontainers 2.0.1 for integration tests requiring external services
- Write tests in same package structure as source code
- Test heap: 512M default (adjust if needed for specific tests)

## Maven Build Conventions

### Standard Build Workflow
```bash
# Always build from src/ directory
cd src
mvn clean install

# For quick iteration (use sparingly)
mvn clean install -DskipTests=true

# Force dependency updates
mvn clean install -U

# Resume from specific module after failure
mvn clean install -rf :module-name

# Production-quality build with all checks
mvn clean install -Dqa=true
```

### Module-Specific Builds
- Each module has its own `pom.xml`
- Build individual modules from their directory: `cd src/module-name && mvn clean install`
- Parent POM is at `src/pom.xml`

## Development Server

### Running GeoServer Locally
```bash
# Start Jetty with hot reload
cd src/web/app
mvn jetty:run

# Access at http://localhost:8080/geoserver
# Default credentials: admin/geoserver
```

### Important Notes
- Jetty runs on port 8080 by default
- Configuration changes may require restart
- Use `Ctrl+C` to stop server

## Dependency Management

### Version Consistency
- All Spring dependencies must use version 7.0.2
- GeoTools and GeoWebCache versions must align
- Check parent POM for managed dependency versions
- Never override managed versions without justification

### Adding Dependencies
- Add to appropriate module's `pom.xml`
- Use `<dependencyManagement>` in parent POM for version control
- Verify license compatibility (GeoServer is GPL 2.0)
- Consider GeoTools LGPL licensing for integration

## Code Generation & Tooling

### Javac Configuration
- Max heap: 256M (configured in Maven)
- Use Java 17 language features
- Enable all compiler warnings

### IDE Setup
- Import Maven project structure
- Configure Spotless plugin for automatic formatting
- Enable Error Prone compiler plugin
- Set Java 17 as project SDK

## Common Issues & Solutions

### Build Failures
- Run `mvn spotless:apply` if formatting errors occur
- Use `-U` flag to force dependency updates
- Check Java version: `java -version` (must be 17+)
- Verify Maven version: `mvn -version` (must be 3.8+)

### Test Failures
- Increase heap if OutOfMemoryError: `-DargLine="-Xmx1024m"`
- Check Testcontainers Docker availability for integration tests
- Ensure no port conflicts (8080 for Jetty)

### Module Dependencies
- Respect module boundaries (see structure.md)
- Core modules cannot depend on extensions
- Extensions can depend on core modules
- Community modules have relaxed dependency rules

## Performance Considerations

- GeoWebCache integration for tile caching
- Spatial index usage for large datasets
- Connection pooling for database stores
- Memory management for raster operations
- Thread pool configuration for concurrent requests

## Security Guidelines

- Use Spring Security 7.0.2 for authentication/authorization
- Never hardcode credentials
- Follow OWASP guidelines for web services
- Validate all user inputs
- Use parameterized queries to prevent SQL injection
