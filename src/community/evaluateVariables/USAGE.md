# Evaluate Variables Tool - Usage Guide

## Overview

The Evaluate Variables tool allows you to test and debug variables defined in GeoServer's environment properties files. You can enter strings with placeholders and see how they are resolved against your properties file configuration.

**Important:** This tool ONLY evaluates against properties files, NOT system properties or environment variables. This provides a safe way to test your custom configuration without exposing system-level information.

## Prerequisites

Environment parametrization must be enabled by setting the system property:
```
ALLOW_ENV_PARAMETRIZATION=true
```

This can be set in one of the following ways:

1. **JVM argument**: `-DALLOW_ENV_PARAMETRIZATION=true`
2. **Environment variable**: `export ALLOW_ENV_PARAMETRIZATION=true` (Linux/Mac) or `set ALLOW_ENV_PARAMETRIZATION=true` (Windows)
3. **Docker**: Add to docker-compose.yml environment section

## How It Works

The tool reads the `geoserver-environment.properties` file (or custom file) and resolves placeholders in the format `${VARIABLE_NAME}` using ONLY the properties defined in that file.

### Properties File Location

The tool looks for properties in this order:

1. **Custom file** - If `ENV_PROPERTIES` system property is set, uses that file path
2. **Default file** - `geoserver-environment.properties` in the GeoServer data directory

### What's NOT Evaluated

Unlike GeoServer's standard resolution (which checks system properties and environment variables first), this tool:
- ❌ Does NOT resolve system properties (e.g., `${java.version}`)
- ❌ Does NOT resolve environment variables (e.g., `${PATH}`)
- ✅ ONLY resolves properties defined in your properties file

This ensures you're testing exactly what's in your configuration file.

## Usage Examples

### Example 1: Database Configuration
Create `geoserver-environment.properties` in your GeoServer data directory:
```properties
DB_HOST=localhost
DB_PORT=5432
DB_NAME=geoserver
DB_USER=postgres
```

**Input:** `jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}`
**Output:** `Evaluated: jdbc:postgresql://localhost:5432/geoserver`

### Example 2: Multiple Placeholders
Properties file:
```properties
PROXY_HOST=proxy.example.com
PROXY_PORT=8080
APP_PATH=geoserver
```

**Input:** `http://${PROXY_HOST}:${PROXY_PORT}/${APP_PATH}`
**Output:** `Evaluated: http://proxy.example.com:8080/geoserver`

### Example 3: File Paths
Properties file:
```properties
DATA_DIR=/opt/geoserver_data
STYLES_DIR=styles
CUSTOM_STYLE=custom.sld
```

**Input:** `${DATA_DIR}/${STYLES_DIR}/${CUSTOM_STYLE}`
**Output:** `Evaluated: /opt/geoserver_data/styles/custom.sld`

### Example 4: Using Custom Properties File
Set the `ENV_PROPERTIES` system property:
```
-DENV_PROPERTIES=/path/to/my-custom.properties
```

Content of `/path/to/my-custom.properties`:
```properties
API_KEY=abc123
API_ENDPOINT=https://api.example.com/v1
```

**Input:** `${API_ENDPOINT}?key=${API_KEY}`
**Output:** `Evaluated: https://api.example.com/v1?key=abc123`

### Example 5: Undefined Variables
If a variable is not defined in the properties file, it remains unchanged.

Properties file:
```properties
DEFINED_VAR=value123
```

**Input:** `${DEFINED_VAR} and ${UNDEFINED_VAR}`
**Output:** `Evaluated: value123 and ${UNDEFINED_VAR}`

## Common Use Cases

### 1. Database Connection Strings
Test database connection templates before using them in data stores:
```
jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}?user=${DB_USER}&password=${DB_PASSWORD}
```

### 2. External Service URLs
Verify URL templates for WMS/WFS cascading or external services:
```
${WMS_BASE_URL}/service?request=GetCapabilities&version=${WMS_VERSION}
```

### 3. File Path Templates
Test file path configurations for styles, templates, or data:
```
${GEOSERVER_DATA_DIR}/workspaces/${WORKSPACE}/styles/${STYLE}.sld
```

### 4. API Configuration
Verify API endpoint and credential placeholders:
```
${API_ENDPOINT}/authenticate?key=${API_KEY}&secret=${API_SECRET}
```

## Troubleshooting

### "Environment parametrization is disabled"
**Solution:** Set `ALLOW_ENV_PARAMETRIZATION=true` and restart GeoServer.

### "No properties file loaded"
**Possible causes:**
1. `geoserver-environment.properties` doesn't exist in the GeoServer data directory
2. `ENV_PROPERTIES` points to a non-existent file
3. Properties file has a syntax error and failed to load

**Solution:** Create the properties file or check the file path and syntax.

### Variable not resolved (shows as `${VAR}`)
**Possible causes:**
1. Variable is not defined in the properties file
2. Variable name is misspelled (case-sensitive)
3. Properties file was not reloaded after changes

**Solution:** 
- Verify the variable exists in your properties file
- Check spelling and case
- Restart GeoServer to reload the properties file

### Testing System Properties or Environment Variables
This tool intentionally does NOT evaluate system properties or environment variables. If you need to test those:
- Use a properties file with the values you want to test
- Or use GeoServer's standard configuration directly (this tool is for pre-flight testing)

## Tips

1. **Case Sensitive:** Variable names are case-sensitive
2. **No Default Values:** Unlike GeoServer's standard resolution, this tool doesn't support default values syntax `${VAR:default}`
3. **Reload Required:** Changes to the properties file require a GeoServer restart to take effect
4. **Safe Testing:** Since this only uses your properties file, it's safe to test sensitive configurations without exposing system information

## Accessing the Tool

1. Log in to GeoServer as an administrator
2. Navigate to **Tools** → **Evaluate Variables**
3. Enter your text with placeholders
4. Click **Evaluate** to see the resolved result
