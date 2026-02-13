#!/bin/bash
# Serve the modular OpenAPI spec using Redocly CLI
# Redocly has better support for multi-file specs with $ref

echo "Starting Redocly preview server for modular GeoServer OpenAPI spec..."
echo ""
echo "The spec will be available at: http://localhost:8080"
echo "Press Ctrl+C to stop the server"
echo ""

npx --yes @redocly/cli preview-docs geoserver.yaml -p 8080
