#!/bin/bash
# Bundle and serve the modular OpenAPI spec using swagger-cli

echo "Bundling modular spec with swagger-cli..."
npx --yes swagger-cli bundle geoserver.yaml -o geoserver-bundled-temp.yaml -t yaml

if [ $? -eq 0 ]; then
    echo "Bundle successful! Starting server..."
    echo ""
    echo "Swagger UI will be available at: http://localhost:8080"
    echo "Press Ctrl+C to stop the server"
    echo ""
    npx --yes swagger-ui-watcher geoserver-bundled-temp.yaml -p 8080
else
    echo "Bundle failed. Check the error messages above."
fi
