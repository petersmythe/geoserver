#!/usr/bin/env python3
"""Extract CSW operations from GeoServer implementation."""

import json

def extract_csw_operations():
    """Extract CSW operations for version 2.0.2."""
    
    return {
        "service": "CSW",
        "service_title": "Catalog Service for the Web",
        "description": "OGC Catalog Service for metadata discovery",
        "versions": ["2.0.2"],
        "source_files": [
            "src/extension/csw/"
        ],
        "operations": [
            {
                "name": "GetCapabilities",
                "description": "Returns service metadata",
                "http_methods": ["GET", "POST"],
                "versions": ["2.0.2"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (CSW)"},
                    {"name": "VERSION", "type": "string", "required": False, "description": "Service version", "default": "2.0.2"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "GetCapabilities"},
                    {"name": "ACCEPTVERSIONS", "type": "string", "required": False, "description": "Accepted versions"},
                    {"name": "SECTIONS", "type": "string", "required": False, "description": "Sections to include"},
                    {"name": "ACCEPTFORMATS", "type": "string", "required": False, "description": "Accepted output formats"}
                ]
            },
            {
                "name": "DescribeRecord",
                "description": "Returns schema information for record types",
                "http_methods": ["GET", "POST"],
                "versions": ["2.0.2"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (CSW)"},
                    {"name": "VERSION", "type": "string", "required": True, "description": "Service version", "default": "2.0.2"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "DescribeRecord"},
                    {"name": "TYPENAME", "type": "string", "required": False, "description": "Record type names"},
                    {"name": "OUTPUTFORMAT", "type": "string", "required": False, "description": "Output format", "default": "application/xml"},
                    {"name": "SCHEMALANGUAGE", "type": "string", "required": False, "description": "Schema language", "default": "http://www.w3.org/XML/Schema"}
                ]
            },
            {
                "name": "GetRecords",
                "description": "Searches and returns catalog records",
                "http_methods": ["GET", "POST"],
                "versions": ["2.0.2"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (CSW)"},
                    {"name": "VERSION", "type": "string", "required": True, "description": "Service version", "default": "2.0.2"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "GetRecords"},
                    {"name": "NAMESPACE", "type": "string", "required": False, "description": "Namespace declarations"},
                    {"name": "RESULTTYPE", "type": "string", "required": False, "description": "Results or hits", "default": "hits"},
                    {"name": "OUTPUTFORMAT", "type": "string", "required": False, "description": "Output format", "default": "application/xml"},
                    {"name": "OUTPUTSCHEMA", "type": "string", "required": False, "description": "Output schema"},
                    {"name": "STARTPOSITION", "type": "integer", "required": False, "description": "Start position", "default": "1"},
                    {"name": "MAXRECORDS", "type": "integer", "required": False, "description": "Maximum records", "default": "10"},
                    {"name": "TYPENAMES", "type": "string", "required": True, "description": "Record type names"},
                    {"name": "ELEMENTSETNAME", "type": "string", "required": False, "description": "Element set (brief, summary, full)", "default": "summary"},
                    {"name": "CONSTRAINTLANGUAGE", "type": "string", "required": False, "description": "Constraint language (FILTER or CQL_TEXT)"},
                    {"name": "CONSTRAINT", "type": "string", "required": False, "description": "Query constraint"},
                    {"name": "SORTBY", "type": "string", "required": False, "description": "Sort order"}
                ]
            },
            {
                "name": "GetRecordById",
                "description": "Returns a specific catalog record by ID",
                "http_methods": ["GET", "POST"],
                "versions": ["2.0.2"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (CSW)"},
                    {"name": "VERSION", "type": "string", "required": True, "description": "Service version", "default": "2.0.2"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "GetRecordById"},
                    {"name": "ID", "type": "string", "required": True, "description": "Record identifier(s)"},
                    {"name": "ELEMENTSETNAME", "type": "string", "required": False, "description": "Element set", "default": "summary"},
                    {"name": "OUTPUTFORMAT", "type": "string", "required": False, "description": "Output format", "default": "application/xml"},
                    {"name": "OUTPUTSCHEMA", "type": "string", "required": False, "description": "Output schema"}
                ]
            },
            {
                "name": "GetDomain",
                "description": "Returns domain values for a property",
                "http_methods": ["GET", "POST"],
                "versions": ["2.0.2"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (CSW)"},
                    {"name": "VERSION", "type": "string", "required": True, "description": "Service version", "default": "2.0.2"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "GetDomain"},
                    {"name": "PROPERTYNAME", "type": "string", "required": False, "description": "Property name"},
                    {"name": "PARAMETERNAME", "type": "string", "required": False, "description": "Parameter name"}
                ]
            },
            {
                "name": "Transaction",
                "description": "Inserts, updates, or deletes catalog records",
                "http_methods": ["POST"],
                "versions": ["2.0.2"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (CSW)"},
                    {"name": "VERSION", "type": "string", "required": True, "description": "Service version", "default": "2.0.2"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "Transaction"}
                ],
                "note": "Transaction operations (Insert, Update, Delete) specified in POST body"
            },
            {
                "name": "Harvest",
                "description": "Harvests metadata from external sources",
                "http_methods": ["POST"],
                "versions": ["2.0.2"],
                "parameters": [
                    {"name": "SERVICE", "type": "string", "required": True, "description": "Service name (CSW)"},
                    {"name": "VERSION", "type": "string", "required": True, "description": "Service version", "default": "2.0.2"},
                    {"name": "REQUEST", "type": "string", "required": True, "description": "Operation name", "default": "Harvest"},
                    {"name": "SOURCE", "type": "string", "required": True, "description": "Source URL"},
                    {"name": "RESOURCETYPE", "type": "string", "required": True, "description": "Resource type"},
                    {"name": "RESOURCEFORMAT", "type": "string", "required": False, "description": "Resource format"}
                ]
            }
        ]
    }

def main():
    operations = extract_csw_operations()
    output_file = ".kiro/api-analysis/ogc/csw-operations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(operations, f, indent=2, ensure_ascii=False)
    print(f"✓ CSW operations extracted to {output_file}")
    print(f"  - Service: {operations['service']}")
    print(f"  - Versions: {', '.join(operations['versions'])}")
    print(f"  - Operations: {len(operations['operations'])}")

if __name__ == "__main__":
    main()
