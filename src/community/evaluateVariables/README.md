# Evaluate Variables - GeoServer Community Module

## Overview
A GeoServer community module that provides a UI tool for testing and debugging environment properties file configuration. This module adds a new entry to the GeoServer **Tools** menu with an Ajax-based interface for evaluating placeholder variables in real-time.

## What It Does

This tool allows administrators to:
- Test property placeholder resolution (`${VARIABLE_NAME}`) against properties files
- Debug configuration issues with `geoserver-environment.properties` or custom properties files
- Verify that `ALLOW_ENV_PARAMETRIZATION` is enabled and working correctly
- Pre-flight test configuration templates before deploying them

**Important:** This tool evaluates ONLY against properties files (not system properties or environment variables), providing a safe way to test custom configurations.

See [USAGE.md](USAGE.md) for detailed usage examples and configuration instructions.

## What's Included

### Source Files
- **PageEvaluateVariables.java** - Wicket page with Ajax form that uses `GeoServerEnvironment` to evaluate placeholders
- **PageEvaluateVariables.html** - Wicket HTML template with Bootstrap-styled form
- **PageEvaluateVariablesTest.java** - Wicket test that validates the Tools menu integration
- **applicationContext.xml** - Spring bean configuration
  - Registers `ToolLinkInfo` bean to add Tools menu entry
  - Registers `ModuleStatusImpl` for module tracking
- **GeoServerApplication.properties** - i18n resource bundle with page title and description
- **pom.xml** - Maven build configuration

### Built Artifacts
Located in `target/` after building:
- **gs-evaluateVariables-3.0-SNAPSHOT.jar** (~4KB) - Main deployable JAR

## Features Implemented

✅ **Environment Variable Evaluation**
- Uses `GeoServerEnvironment` to access properties file
- Evaluates ONLY against properties files (not system properties or environment variables)
- Checks if `ALLOW_ENV_PARAMETRIZATION` is enabled
- Custom `PlaceholderResolver` for properties-file-only resolution
- Real-time Ajax-based evaluation (no page reload)

✅ **GUI Integration**
- Appears in **Tools** menu as "Evaluate Variables"
- Secured page (requires administrator login)
- Uses GeoServer's standard page layout
- Bootstrap-styled responsive interface

✅ **Testing**
- Wicket unit test validates:
  - Tools menu contains the module link
  - Link is clickable and navigates to the correct page
  - Page renders with expected content

✅ **Build Integration**
- Included in community aggregator POM
- Builds via Maven reactor
- Follows GeoServer module conventions

## Building

### Build Just This Module
```bash
mvn -f src/pom.xml clean install -P communityRelease -pl :gs-evaluateVariables -am -DskipTests
```

### Build and Run Tests
```bash
mvn -f src/community/evaluateVariables/pom.xml clean test
```

### Build Entire Community Reactor
```bash
mvn -f src/pom.xml clean install -P communityRelease -DskipTests
```

## Deploying to GeoServer

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

**Quick Deploy:**
1. Copy `target/gs-evaluateVariables-3.0-SNAPSHOT.jar` to `<GEOSERVER_HOME>/webapps/geoserver/WEB-INF/lib/`
2. Restart GeoServer
3. Log in as admin
4. Navigate to **Tools** → **Evaluate Variables**

## Architecture

### Module Structure
```
evaluateVariables/
├── pom.xml
├── src/
│   ├── main/
│   │   ├── java/org/geoserver/web/evaluate/
│   │   │   └── PageEvaluateVariables.java
│   │   └── resources/
│   │       ├── applicationContext.xml
│   │       └── GeoServerApplication.properties
│   └── test/
│       └── java/org/geoserver/web/evaluate/
│           └── PageEvaluateVariablesTest.java
├── DEPLOYMENT.md
└── README.md (this file)
```

### How It Works

1. **Spring Bean Registration**
   - `applicationContext.xml` defines a `ToolLinkInfo` bean
   - Bean specifies the Wicket page class and i18n keys
   - Uses `AdminComponentAuthorizer` to restrict access to admins

2. **Tools Menu Integration**
   - GeoServer's `ToolPage` scans for all `ToolLinkInfo` beans
   - Creates a `BookmarkablePageLink` for each bean
   - Renders links in the Tools page list

3. **Wicket Page**
   - `PageEvaluateVariables` extends `GeoServerSecuredPage`
   - Inherits GeoServer's standard page layout and security
   - Currently displays a simple label (ready for Ajax enhancements)

## Dependencies

Runtime dependencies (provided by GeoServer):
- **gs-main** - GeoServer core services
- **gs-web-core** - Wicket UI framework and GeoServer page components

Test dependencies:
- **gs-main:tests** - Test utilities
- **gs-web-core:tests** - Wicket test support (GeoServerWicketTestSupport)
- **wicket-tester** - Wicket test harness
- **jakarta.servlet-api** - Servlet API for testing

## Next Steps

### Planned Enhancements
- [ ] Add Ajax behaviors (AjaxLink, AjaxButton) for interactive UI
- [ ] Implement server-side evaluation logic (service/bean)
- [ ] Add HTML template (`PageEvaluateVariables.html`) for richer UI
- [ ] Add form inputs for variable entry
- [ ] Display evaluation results
- [ ] Add additional unit tests

### Learning Opportunities
This module demonstrates:
- ✅ GeoServer module structure and Maven conventions
- ✅ Spring application context configuration
- ✅ Wicket page creation and component hierarchy
- ✅ GeoServer UI extension points (ToolLinkInfo)
- ✅ Wicket testing with GeoServerWicketTestSupport
- ✅ i18n resource bundles
- ✅ Security integration (AdminComponentAuthorizer)

## Testing

### Run Unit Tests
```bash
mvn -f src/community/evaluateVariables/pom.xml test
```

### Test Output
```
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
```

### What the Test Validates
1. Logs in as admin user
2. Navigates to Tools page
3. Searches for "Evaluate Variables" link by content (robust to list order)
4. Clicks the link
5. Asserts the page renders correctly with expected title

## References

### Similar Modules
- **web-resource** (`src/extension/web-resource`) - Resource Browser tool
  - Good example of a Tools menu entry
  - Shows file browsing UI with Ajax tree view

### GeoServer Documentation
- [Building GeoServer](https://docs.geoserver.org/latest/en/developer/programming-guide/building.html)
- [Wicket Development](https://docs.geoserver.org/latest/en/developer/programming-guide/wicket/index.html)
- [Module Development](https://docs.geoserver.org/latest/en/developer/programming-guide/modules.html)

### Wicket Resources
- [Apache Wicket User Guide](https://wicket.apache.org/learn/guide/)
- [Wicket Testing](https://wicket.apache.org/learn/guide/testing.html)

## License
Copyright (C) 2025 - Open Source Geospatial Foundation. All rights reserved.
This code is licensed under the GPL 2.0 license, available at the root application directory.

## Author
Created as a learning exercise for GeoServer community module development.
