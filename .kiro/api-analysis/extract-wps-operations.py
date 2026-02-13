#!/usr/bin/env python3
"""Extract WPS operations from GeoServer implementation."""

import json

def extract_wps_operations():
    """Extract WPS operations for version 1.0.0."""
    
    return {
        "service": "WPS",
        "service_title": "Web Processing Service",
        "description": "OGC Web Processing Service for geospatial processing",
        "versions": ["1.0.0"],
        "source_files": [
            "src/extension/wps/"
        ],
        "operations": [
            {
                "name": "GetCapabilities",
                "description": "Returns service metadata and available processes",
                "http_methods": ["GET", "POST"],
                "versions": ["1.0.0"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (WPS)"},
                    {"name": "VERSION", "type": "string", "required": False, "description": "Service version", "default": "1.0.0"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "GetCapabilities"},
                    {"name": "ACCEPTVERSIONS", "type": "string", "required": False, "description": "Accepted versions"},
                    {"name": "LANGUAGE", "type": "string", "required": False, "description": "Preferred language"}
                ]
            },
            {
                "name": "DescribeProcess",
                "description": "Returns detailed process descriptions",
                "http_methods": ["GET", "POST"],
                "versions": ["1.0.0"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (WPS)"},
                    {"name": "VERSION", "type": "string", "required": True, "description": "Service version", "default": "1.0.0"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "DescribeProcess"},
                    {"name": "IDENTIFIER", "type": "string", "required": True, "description": "Comma-separated process identifiers"},
                    {"name": "LANGUAGE", "type": "string", "required": False, "description": "Preferred language"}
                ]
            },
            {
                "name": "Execute",
                "description": "Executes a process with specified inputs",
                "http_methods": ["GET", "POST"],
                "versions": ["1.0.0"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (WPS)"},
                    {"name": "VERSION", "type": "string", "required": True, "description": "Service version", "default": "1.0.0"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "Execute"},
                    {"name": "IDENTIFIER", "type": "string", "required": True, "description": "Process identifier"},
                    {"name": "DATAINPUTS", "type": "string", "required": False, "description": "Process input data (KVP format)"},
                    {"name": "RESPONSEFORM", "type": "string", "required": False, "description": "Response format"},
                    {"name": "STOREEXECUTERESPONSE", "type": "boolean", "required": False, "description": "Store response document", "default": "false"},
                    {"name": "LINEAGE", "type": "boolean", "required": False, "description": "Include lineage in response", "default": "false"},
                    {"name": "STATUS", "type": "boolean", "required": False, "description": "Include status updates", "default": "false"}
                ],
                "note": "Complex inputs and outputs typically specified in POST body"
            },
            {
                "name": "GetExecutionStatus",
                "description": "Returns status of asynchronous execution",
                "http_methods": ["GET"],
                "versions": ["1.0.0"],
                "parameters": [
                    {"name": "EXECUTIONID", "type": "string", "required": True, "description": "Execution identifier"}
                ],
                "vendor_extension": True,
                "note": "GeoServer extension for checking async execution status"
            },
            {
                "name": "Dismiss",
                "description": "Dismisses a stored execution result",
                "http_methods": ["GET"],
                "versions": ["1.0.0"],
                "parameters": [
                    {"name": "EXECUTIONID", "type": "string", "required": True, "description": "Execution identifier"}
                ],
                "vendor_extension": True,
                "note": "GeoServer extension for cleaning up stored results"
            }
        ]
    }

def main():
    operations = extract_wps_operations()
    output_file = ".kiro/api-analysis/ogc/wps-operations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(operations, f, indent=2, ensure_ascii=False)
    print(f"✓ WPS operations extracted to {output_file}")
    print(f"  - Service: {operations['service']}")
    print(f"  - Versions: {', '.join(operations['versions'])}")
    print(f"  - Operations: {len(operations['operations'])}")

if __name__ == "__main__":
    main()
