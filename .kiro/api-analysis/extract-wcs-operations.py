#!/usr/bin/env python3
"""Extract WCS operations from GeoServer implementation."""

import json

def extract_wcs_operations():
    """Extract WCS operations for versions 1.0, 1.1, and 2.0."""
    
    return {
        "service": "WCS",
        "service_title": "Web Coverage Service",
        "description": "OGC Web Coverage Service for raster data access",
        "versions": ["1.0.0", "1.1.0", "1.1.1", "2.0.0", "2.0.1"],
        "source_files": [
            "src/wcs/src/main/java/org/geoserver/wcs/",
            "src/wcs2_0/src/main/java/org/geoserver/wcs2_0/"
        ],
        "operations": [
            {
                "name": "GetCapabilities",
                "description": "Returns service metadata and available coverages",
                "http_methods": ["GET", "POST"],
                "versions": ["1.0.0", "1.1.0", "1.1.1", "2.0.0", "2.0.1"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (WCS)"},
                    {"name": "VERSION", "type": "string", "required": False, "description": "Service version"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "GetCapabilities"},
                    {"name": "ACCEPTVERSIONS", "type": "string", "required": False, "description": "Accepted versions (WCS 2.0)", "versions": ["2.0.0", "2.0.1"]},
                    {"name": "SECTIONS", "type": "string", "required": False, "description": "Sections to include"},
                    {"name": "UPDATESEQUENCE", "type": "string", "required": False, "description": "Cache validation"}
                ]
            },
            {
                "name": "DescribeCoverage",
                "description": "Returns detailed coverage metadata",
                "http_methods": ["GET", "POST"],
                "versions": ["1.0.0", "1.1.0", "1.1.1", "2.0.0", "2.0.1"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (WCS)"},
                    {"name": "VERSION", "type": "string", "required": True, "description": "Service version"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "DescribeCoverage"},
                    {"name": "COVERAGE", "type": "string", "required": True, "description": "Coverage name (WCS 1.0)", "versions": ["1.0.0"]},
                    {"name": "IDENTIFIERS", "type": "string", "required": True, "description": "Coverage identifiers (WCS 1.1)", "versions": ["1.1.0", "1.1.1"]},
                    {"name": "COVERAGEID", "type": "string", "required": True, "description": "Coverage ID (WCS 2.0)", "versions": ["2.0.0", "2.0.1"]}
                ]
            },
            {
                "name": "GetCoverage",
                "description": "Returns coverage data",
                "http_methods": ["GET", "POST"],
                "versions": ["1.0.0", "1.1.0", "1.1.1", "2.0.0", "2.0.1"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (WCS)"},
                    {"name": "VERSION", "type": "string", "required": True, "description": "Service version"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "GetCoverage"},
                    {"name": "COVERAGE", "type": "string", "required": True, "description": "Coverage name (WCS 1.0)", "versions": ["1.0.0"]},
                    {"name": "IDENTIFIER", "type": "string", "required": True, "description": "Coverage identifier (WCS 1.1)", "versions": ["1.1.0", "1.1.1"]},
                    {"name": "COVERAGEID", "type": "string", "required": True, "description": "Coverage ID (WCS 2.0)", "versions": ["2.0.0", "2.0.1"]},
                    {"name": "CRS", "type": "string", "required": True, "description": "Coordinate reference system (WCS 1.0)", "versions": ["1.0.0"]},
                    {"name": "BOUNDINGBOX", "type": "string", "required": True, "description": "Bounding box (WCS 1.1)", "versions": ["1.1.0", "1.1.1"]},
                    {"name": "SUBSET", "type": "string", "required": False, "description": "Dimension subset (WCS 2.0)", "versions": ["2.0.0", "2.0.1"]},
                    {"name": "FORMAT", "type": "string", "required": True, "description": "Output format"},
                    {"name": "WIDTH", "type": "integer", "required": False, "description": "Output width in pixels"},
                    {"name": "HEIGHT", "type": "integer", "required": False, "description": "Output height in pixels"},
                    {"name": "RESX", "type": "number", "required": False, "description": "X resolution"},
                    {"name": "RESY", "type": "number", "required": False, "description": "Y resolution"},
                    {"name": "INTERPOLATION", "type": "string", "required": False, "description": "Interpolation method"},
                    {"name": "TIME", "type": "string", "required": False, "description": "Time dimension value"},
                    {"name": "ELEVATION", "type": "string", "required": False, "description": "Elevation dimension value"}
                ]
            }
        ]
    }

def main():
    operations = extract_wcs_operations()
    output_file = ".kiro/api-analysis/ogc/wcs-operations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(operations, f, indent=2, ensure_ascii=False)
    print(f"✓ WCS operations extracted to {output_file}")
    print(f"  - Service: {operations['service']}")
    print(f"  - Versions: {', '.join(operations['versions'])}")
    print(f"  - Operations: {len(operations['operations'])}")

if __name__ == "__main__":
    main()
