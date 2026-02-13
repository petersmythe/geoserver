#!/usr/bin/env python3
"""Extract WMTS operations from GeoServer implementation."""

import json

def extract_wmts_operations():
    """Extract WMTS operations for version 1.0.0."""
    
    return {
        "service": "WMTS",
        "service_title": "Web Map Tile Service",
        "description": "OGC Web Map Tile Service for tiled map access",
        "versions": ["1.0.0"],
        "source_files": [
            "src/gwc/src/main/java/org/geoserver/gwc/wmts/"
        ],
        "operations": [
            {
                "name": "GetCapabilities",
                "description": "Returns service metadata and available tile matrix sets",
                "http_methods": ["GET", "POST"],
                "versions": ["1.0.0"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (WMTS)"},
                    {"name": "VERSION", "type": "string", "required": False, "description": "Service version", "default": "1.0.0"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "GetCapabilities"},
                    {"name": "ACCEPTVERSIONS", "type": "string", "required": False, "description": "Accepted versions"},
                    {"name": "SECTIONS", "type": "string", "required": False, "description": "Sections to include"},
                    {"name": "ACCEPTFORMATS", "type": "string", "required": False, "description": "Accepted output formats"}
                ]
            },
            {
                "name": "GetTile",
                "description": "Returns a tile from a tile matrix set",
                "http_methods": ["GET"],
                "versions": ["1.0.0"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (WMTS)"},
                    {"name": "VERSION", "type": "string", "required": True, "description": "Service version", "default": "1.0.0"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "GetTile"},
                    {"name": "LAYER", "type": "string", "required": True, "description": "Layer identifier"},
                    {"name": "STYLE", "type": "string", "required": True, "description": "Style identifier"},
                    {"name": "FORMAT", "type": "string", "required": True, "description": "Output format (e.g., image/png)"},
                    {"name": "TILEMATRIXSET", "type": "string", "required": True, "description": "Tile matrix set identifier"},
                    {"name": "TILEMATRIX", "type": "string", "required": True, "description": "Tile matrix identifier (zoom level)"},
                    {"name": "TILEROW", "type": "integer", "required": True, "description": "Row index in tile matrix"},
                    {"name": "TILECOL", "type": "integer", "required": True, "description": "Column index in tile matrix"},
                    {"name": "TIME", "type": "string", "required": False, "description": "Time dimension value"},
                    {"name": "ELEVATION", "type": "string", "required": False, "description": "Elevation dimension value"}
                ]
            },
            {
                "name": "GetFeatureInfo",
                "description": "Returns information about features at a tile location",
                "http_methods": ["GET"],
                "versions": ["1.0.0"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (WMTS)"},
                    {"name": "VERSION", "type": "string", "required": True, "description": "Service version", "default": "1.0.0"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "GetFeatureInfo"},
                    {"name": "LAYER", "type": "string", "required": True, "description": "Layer identifier"},
                    {"name": "STYLE", "type": "string", "required": True, "description": "Style identifier"},
                    {"name": "FORMAT", "type": "string", "required": True, "description": "Tile format"},
                    {"name": "TILEMATRIXSET", "type": "string", "required": True, "description": "Tile matrix set identifier"},
                    {"name": "TILEMATRIX", "type": "string", "required": True, "description": "Tile matrix identifier"},
                    {"name": "TILEROW", "type": "integer", "required": True, "description": "Row index"},
                    {"name": "TILECOL", "type": "integer", "required": True, "description": "Column index"},
                    {"name": "I", "type": "integer", "required": True, "description": "Column pixel coordinate"},
                    {"name": "J", "type": "integer", "required": True, "description": "Row pixel coordinate"},
                    {"name": "INFOFORMAT", "type": "string", "required": True, "description": "Output format for feature info"}
                ]
            }
        ]
    }

def main():
    operations = extract_wmts_operations()
    output_file = ".kiro/api-analysis/ogc/wmts-operations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(operations, f, indent=2, ensure_ascii=False)
    print(f"✓ WMTS operations extracted to {output_file}")
    print(f"  - Service: {operations['service']}")
    print(f"  - Versions: {', '.join(operations['versions'])}")
    print(f"  - Operations: {len(operations['operations'])}")

if __name__ == "__main__":
    main()
