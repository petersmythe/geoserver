#!/bin/bash
# Serve the merged OpenAPI spec using Redocly CLI

echo "Starting Redocly preview server for merged GeoServer OpenAPI spec..."
echo ""
echo "The spec will be available at: http://localhost:8080"
echo "Press Ctrl+C to stop the server"
echo ""

npx --yes @redocly/cli preview-docs geoserver-merged.yaml -p 8080
