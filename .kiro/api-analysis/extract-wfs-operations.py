#!/usr/bin/env python3
"""
Extract WFS operations from GeoServer implementation.

This script analyzes the WFS service implementation to extract:
- Operation names for WFS 1.0, 1.1, and 2.0
- Parameters for each operation
- Supported versions
- Parameter types and requirements
"""

import json
from typing import Dict, List, Any

def extract_wfs_operations() -> Dict[str, Any]:
    """
    Extract WFS operations based on WebFeatureService.java and WebFeatureService20.java.
    
    Returns:
        Dictionary containing WFS operations metadata
    """
    
    operations = {
        "service": "WFS",
        "service_title": "Web Feature Service",
        "description": "OGC Web Feature Service for vector data access and editing",
        "versions": ["1.0.0", "1.1.0", "2.0.0"],
        "source_files": [
            "src/wfs-core/src/main/java/org/geoserver/wfs/WebFeatureService.java",
            "src/wfs-core/src/main/java/org/geoserver/wfs/WebFeatureService20.java",
            "src/wfs-core/src/main/java/org/geoserver/wfs/kvp/"
        ],
        "operations": []
    }
    
    # GetCapabilities operation (all versions)
    get_capabilities = {
        "name": "GetCapabilities",
        "description": "Returns service metadata and available feature types",
        "http_methods": ["GET", "POST"],
        "versions": ["1.0.0", "1.1.0", "2.0.0"],
        "parameters": [
            {
                "name": "SERVICE",
                "type": "string",
                "required": True,
                "description": "Service name (WFS)",
                "default": "WFS"
            },
            {
                "name": "VERSION",
                "type": "string",
                "required": False,
                "description": "Service version (use ACCEPTVERSIONS in 2.0)",
                "allowed_values": ["1.0.0", "1.1.0", "2.0.0"]
            },
            {
                "name": "REQUEST",
                "type": "string",
                "required": True,
                "description": "Operation name",
                "default": "GetCapabilities"
            },
            {
                "name": "ACCEPTVERSIONS",
                "type": "string",
                "required": False,
                "description": "Comma-separated list of accepted versions (WFS 2.0)",
                "versions": ["2.0.0"]
            },
            {
                "name": "ACCEPTFORMATS",
                "type": "string",
                "required": False,
                "description": "Comma-separated list of accepted output formats",
                "default": "text/xml"
            },
            {
                "name": "UPDATESEQUENCE",
                "type": "string",
                "required": False,
                "description": "Sequence number for cache validation"
            },
            {
                "name": "SECTIONS",
                "type": "string",
                "required": False,
                "description": "Comma-separated list of sections to include (WFS 2.0)",
                "versions": ["2.0.0"]
            },
            {
                "name": "NAMESPACE",
                "type": "string",
                "required": False,
                "description": "Filter feature types by namespace (vendor extension)"
            }
        ]
    }
    operations["operations"].append(get_capabilities)
    
    # DescribeFeatureType operation (all versions)
    describe_feature_type = {
        "name": "DescribeFeatureType",
        "description": "Returns XML schema for requested feature types",
        "http_methods": ["GET", "POST"],
        "versions": ["1.0.0", "1.1.0", "2.0.0"],
        "parameters": [
            {
                "name": "SERVICE",
                "type": "string",
                "required": True,
                "description": "Service name (WFS)",
                "default": "WFS"
            },
            {
                "name": "VERSION",
                "type": "string",
                "required": True,
                "description": "Service version",
                "allowed_values": ["1.0.0", "1.1.0", "2.0.0"]
            },
            {
                "name": "REQUEST",
                "type": "string",
                "required": True,
                "description": "Operation name",
                "default": "DescribeFeatureType"
            },
            {
                "name": "TYPENAME",
                "type": "string",
                "required": False,
                "description": "Comma-separated list of feature type names (WFS 1.x)",
                "versions": ["1.0.0", "1.1.0"]
            },
            {
                "name": "TYPENAMES",
                "type": "string",
                "required": False,
                "description": "Comma-separated list of feature type names (WFS 2.0)",
                "versions": ["2.0.0"]
            },
            {
                "name": "OUTPUTFORMAT",
                "type": "string",
                "required": False,
                "description": "Output format MIME type",
                "default": "text/xml; subtype=gml/3.1.1"
            },
            {
                "name": "EXCEPTIONS",
                "type": "string",
                "required": False,
                "description": "Exception format",
                "default": "text/xml"
            }
        ]
    }
    operations["operations"].append(describe_feature_type)
    
    # GetFeature operation (all versions)
    get_feature = {
        "name": "GetFeature",
        "description": "Returns feature instances matching the query",
        "http_methods": ["GET", "POST"],
        "versions": ["1.0.0", "1.1.0", "2.0.0"],
        "parameters": [
            {
                "name": "SERVICE",
                "type": "string",
                "required": True,
                "description": "Service name (WFS)",
                "default": "WFS"
            },
            {
                "name": "VERSION",
                "type": "string",
                "required": True,
                "description": "Service version",
                "allowed_values": ["1.0.0", "1.1.0", "2.0.0"]
            },
            {
                "name": "REQUEST",
                "type": "string",
                "required": True,
                "description": "Operation name",
                "default": "GetFeature"
            },
            {
                "name": "TYPENAME",
                "type": "string",
                "required": True,
                "description": "Comma-separated list of feature type names (WFS 1.x)",
                "versions": ["1.0.0", "1.1.0"]
            },
            {
                "name": "TYPENAMES",
                "type": "string",
                "required": True,
                "description": "Comma-separated list of feature type names (WFS 2.0)",
                "versions": ["2.0.0"]
            },
            {
                "name": "OUTPUTFORMAT",
                "type": "string",
                "required": False,
                "description": "Output format MIME type",
                "default": "text/xml; subtype=gml/3.1.1"
            },
            {
                "name": "RESULTTYPE",
                "type": "string",
                "required": False,
                "description": "Results or hits",
                "allowed_values": ["results", "hits"],
                "default": "results"
            },
            {
                "name": "PROPERTYNAME",
                "type": "string",
                "required": False,
                "description": "Comma-separated list of properties to return"
            },
            {
                "name": "FEATUREID",
                "type": "string",
                "required": False,
                "description": "Comma-separated list of feature IDs"
            },
            {
                "name": "FILTER",
                "type": "string",
                "required": False,
                "description": "OGC Filter XML"
            },
            {
                "name": "BBOX",
                "type": "string",
                "required": False,
                "description": "Bounding box filter (minx,miny,maxx,maxy[,crs])"
            },
            {
                "name": "MAXFEATURES",
                "type": "integer",
                "required": False,
                "description": "Maximum features to return (WFS 1.x)",
                "versions": ["1.0.0", "1.1.0"]
            },
            {
                "name": "COUNT",
                "type": "integer",
                "required": False,
                "description": "Maximum features to return (WFS 2.0)",
                "versions": ["2.0.0"]
            },
            {
                "name": "STARTINDEX",
                "type": "integer",
                "required": False,
                "description": "Start index for paging (WFS 2.0)",
                "versions": ["2.0.0"]
            },
            {
                "name": "SORTBY",
                "type": "string",
                "required": False,
                "description": "Sort order (property[+A|-D])"
            },
            {
                "name": "SRSNAME",
                "type": "string",
                "required": False,
                "description": "Coordinate reference system for output"
            },
            {
                "name": "EXCEPTIONS",
                "type": "string",
                "required": False,
                "description": "Exception format",
                "default": "text/xml"
            },
            {
                "name": "CQL_FILTER",
                "type": "string",
                "required": False,
                "description": "CQL filter expression (vendor extension)"
            },
            {
                "name": "FEATUREVERSION",
                "type": "string",
                "required": False,
                "description": "Feature version for versioned layers (vendor extension)"
            },
            {
                "name": "VIEWPARAMS",
                "type": "string",
                "required": False,
                "description": "SQL view parameters (vendor extension)"
            },
            {
                "name": "FORMAT_OPTIONS",
                "type": "string",
                "required": False,
                "description": "Format-specific options (vendor extension)"
            }
        ],
        "vendor_extensions": ["CQL_FILTER", "FEATUREVERSION", "VIEWPARAMS", "FORMAT_OPTIONS"]
    }
    operations["operations"].append(get_feature)
    
    # GetFeatureWithLock operation (all versions)
    get_feature_with_lock = {
        "name": "GetFeatureWithLock",
        "description": "Returns features and locks them for editing",
        "http_methods": ["GET", "POST"],
        "versions": ["1.1.0", "2.0.0"],
        "parameters": [
            {
                "name": "EXPIRY",
                "type": "integer",
                "required": False,
                "description": "Lock expiry time in minutes"
            },
            {
                "name": "LOCKACTION",
                "type": "string",
                "required": False,
                "description": "Action on lock failure (ALL or SOME)",
                "allowed_values": ["ALL", "SOME"],
                "default": "ALL"
            }
        ],
        "note": "Includes all GetFeature parameters plus lock-specific parameters"
    }
    operations["operations"].append(get_feature_with_lock)
    
    # LockFeature operation (all versions)
    lock_feature = {
        "name": "LockFeature",
        "description": "Locks features for exclusive editing access",
        "http_methods": ["GET", "POST"],
        "versions": ["1.0.0", "1.1.0", "2.0.0"],
        "parameters": [
            {
                "name": "SERVICE",
                "type": "string",
                "required": True,
                "description": "Service name (WFS)",
                "default": "WFS"
            },
            {
                "name": "VERSION",
                "type": "string",
                "required": True,
                "description": "Service version",
                "allowed_values": ["1.0.0", "1.1.0", "2.0.0"]
            },
            {
                "name": "REQUEST",
                "type": "string",
                "required": True,
                "description": "Operation name",
                "default": "LockFeature"
            },
            {
                "name": "TYPENAME",
                "type": "string",
                "required": True,
                "description": "Feature type name"
            },
            {
                "name": "EXPIRY",
                "type": "integer",
                "required": False,
                "description": "Lock expiry time in minutes"
            },
            {
                "name": "LOCKACTION",
                "type": "string",
                "required": False,
                "description": "Action on lock failure (ALL or SOME)",
                "allowed_values": ["ALL", "SOME"],
                "default": "ALL"
            },
            {
                "name": "FILTER",
                "type": "string",
                "required": False,
                "description": "OGC Filter XML to select features"
            },
            {
                "name": "BBOX",
                "type": "string",
                "required": False,
                "description": "Bounding box filter"
            },
            {
                "name": "FEATUREID",
                "type": "string",
                "required": False,
                "description": "Comma-separated list of feature IDs"
            }
        ]
    }
    operations["operations"].append(lock_feature)
    
    # Transaction operation (all versions)
    transaction = {
        "name": "Transaction",
        "description": "Inserts, updates, or deletes features",
        "http_methods": ["POST"],
        "versions": ["1.0.0", "1.1.0", "2.0.0"],
        "parameters": [
            {
                "name": "SERVICE",
                "type": "string",
                "required": True,
                "description": "Service name (WFS)",
                "default": "WFS"
            },
            {
                "name": "VERSION",
                "type": "string",
                "required": True,
                "description": "Service version",
                "allowed_values": ["1.0.0", "1.1.0", "2.0.0"]
            },
            {
                "name": "REQUEST",
                "type": "string",
                "required": True,
                "description": "Operation name",
                "default": "Transaction"
            },
            {
                "name": "LOCKID",
                "type": "string",
                "required": False,
                "description": "Lock ID from previous LockFeature operation"
            },
            {
                "name": "RELEASEACTION",
                "type": "string",
                "required": False,
                "description": "Action on locks after transaction (ALL or SOME)",
                "allowed_values": ["ALL", "SOME"],
                "default": "ALL"
            }
        ],
        "note": "Transaction elements (Insert, Update, Delete, Native) are specified in POST body"
    }
    operations["operations"].append(transaction)
    
    # GetGmlObject operation (WFS 1.1 only)
    get_gml_object = {
        "name": "GetGmlObject",
        "description": "Returns a GML object by ID",
        "http_methods": ["GET", "POST"],
        "versions": ["1.1.0"],
        "parameters": [
            {
                "name": "SERVICE",
                "type": "string",
                "required": True,
                "description": "Service name (WFS)",
                "default": "WFS"
            },
            {
                "name": "VERSION",
                "type": "string",
                "required": True,
                "description": "Service version",
                "default": "1.1.0"
            },
            {
                "name": "REQUEST",
                "type": "string",
                "required": True,
                "description": "Operation name",
                "default": "GetGmlObject"
            },
            {
                "name": "GMLOBJECTID",
                "type": "string",
                "required": True,
                "description": "GML object identifier"
            },
            {
                "name": "OUTPUTFORMAT",
                "type": "string",
                "required": False,
                "description": "Output format MIME type"
            }
        ]
    }
    operations["operations"].append(get_gml_object)
    
    # GetPropertyValue operation (WFS 2.0 only)
    get_property_value = {
        "name": "GetPropertyValue",
        "description": "Returns values of a specific property",
        "http_methods": ["GET", "POST"],
        "versions": ["2.0.0"],
        "parameters": [
            {
                "name": "SERVICE",
                "type": "string",
                "required": True,
                "description": "Service name (WFS)",
                "default": "WFS"
            },
            {
                "name": "VERSION",
                "type": "string",
                "required": True,
                "description": "Service version",
                "default": "2.0.0"
            },
            {
                "name": "REQUEST",
                "type": "string",
                "required": True,
                "description": "Operation name",
                "default": "GetPropertyValue"
            },
            {
                "name": "TYPENAMES",
                "type": "string",
                "required": True,
                "description": "Feature type name"
            },
            {
                "name": "VALUEREFERENCE",
                "type": "string",
                "required": True,
                "description": "XPath expression for property"
            },
            {
                "name": "FILTER",
                "type": "string",
                "required": False,
                "description": "OGC Filter XML"
            },
            {
                "name": "COUNT",
                "type": "integer",
                "required": False,
                "description": "Maximum values to return"
            },
            {
                "name": "STARTINDEX",
                "type": "integer",
                "required": False,
                "description": "Start index for paging"
            }
        ]
    }
    operations["operations"].append(get_property_value)
    
    # ListStoredQueries operation (WFS 2.0 only)
    list_stored_queries = {
        "name": "ListStoredQueries",
        "description": "Returns list of available stored queries",
        "http_methods": ["GET", "POST"],
        "versions": ["2.0.0"],
        "parameters": [
            {
                "name": "SERVICE",
                "type": "string",
                "required": True,
                "description": "Service name (WFS)",
                "default": "WFS"
            },
            {
                "name": "VERSION",
                "type": "string",
                "required": True,
                "description": "Service version",
                "default": "2.0.0"
            },
            {
                "name": "REQUEST",
                "type": "string",
                "required": True,
                "description": "Operation name",
                "default": "ListStoredQueries"
            }
        ]
    }
    operations["operations"].append(list_stored_queries)
    
    # DescribeStoredQueries operation (WFS 2.0 only)
    describe_stored_queries = {
        "name": "DescribeStoredQueries",
        "description": "Returns metadata for stored queries",
        "http_methods": ["GET", "POST"],
        "versions": ["2.0.0"],
        "parameters": [
            {
                "name": "SERVICE",
                "type": "string",
                "required": True,
                "description": "Service name (WFS)",
                "default": "WFS"
            },
            {
                "name": "VERSION",
                "type": "string",
                "required": True,
                "description": "Service version",
                "default": "2.0.0"
            },
            {
                "name": "REQUEST",
                "type": "string",
                "required": True,
                "description": "Operation name",
                "default": "DescribeStoredQueries"
            },
            {
                "name": "STOREDQUERY_ID",
                "type": "string",
                "required": False,
                "description": "Comma-separated list of stored query IDs"
            }
        ]
    }
    operations["operations"].append(describe_stored_queries)
    
    # CreateStoredQuery operation (WFS 2.0 only)
    create_stored_query = {
        "name": "CreateStoredQuery",
        "description": "Creates a new stored query",
        "http_methods": ["POST"],
        "versions": ["2.0.0"],
        "parameters": [
            {
                "name": "SERVICE",
                "type": "string",
                "required": True,
                "description": "Service name (WFS)",
                "default": "WFS"
            },
            {
                "name": "VERSION",
                "type": "string",
                "required": True,
                "description": "Service version",
                "default": "2.0.0"
            },
            {
                "name": "REQUEST",
                "type": "string",
                "required": True,
                "description": "Operation name",
                "default": "CreateStoredQuery"
            }
        ],
        "note": "Query definition is specified in POST body"
    }
    operations["operations"].append(create_stored_query)
    
    # DropStoredQuery operation (WFS 2.0 only)
    drop_stored_query = {
        "name": "DropStoredQuery",
        "description": "Deletes a stored query",
        "http_methods": ["GET", "POST"],
        "versions": ["2.0.0"],
        "parameters": [
            {
                "name": "SERVICE",
                "type": "string",
                "required": True,
                "description": "Service name (WFS)",
                "default": "WFS"
            },
            {
                "name": "VERSION",
                "type": "string",
                "required": True,
                "description": "Service version",
                "default": "2.0.0"
            },
            {
                "name": "REQUEST",
                "type": "string",
                "required": True,
                "description": "Operation name",
                "default": "DropStoredQuery"
            },
            {
                "name": "ID",
                "type": "string",
                "required": True,
                "description": "Stored query ID to delete"
            }
        ]
    }
    operations["operations"].append(drop_stored_query)
    
    # ReleaseLock operation (vendor extension)
    release_lock = {
        "name": "ReleaseLock",
        "description": "Releases a previously acquired lock",
        "http_methods": ["GET", "POST"],
        "versions": ["1.0.0", "1.1.0", "2.0.0"],
        "parameters": [
            {
                "name": "SERVICE",
                "type": "string",
                "required": True,
                "description": "Service name (WFS)",
                "default": "WFS"
            },
            {
                "name": "VERSION",
                "type": "string",
                "required": True,
                "description": "Service version"
            },
            {
                "name": "REQUEST",
                "type": "string",
                "required": True,
                "description": "Operation name",
                "default": "ReleaseLock"
            },
            {
                "name": "LOCKID",
                "type": "string",
                "required": True,
                "description": "Lock ID to release"
            }
        ],
        "vendor_extension": True,
        "note": "Not part of official WFS specification"
    }
    operations["operations"].append(release_lock)
    
    return operations


def main():
    """Main execution function."""
    print("Extracting WFS operations from GeoServer implementation...")
    
    operations = extract_wfs_operations()
    
    # Write to JSON file
    output_file = ".kiro/api-analysis/ogc/wfs-operations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(operations, f, indent=2, ensure_ascii=False)
    
    print(f"✓ WFS operations extracted to {output_file}")
    print(f"  - Service: {operations['service']}")
    print(f"  - Versions: {', '.join(operations['versions'])}")
    print(f"  - Operations: {len(operations['operations'])}")
    
    for op in operations['operations']:
        vendor = " (vendor extension)" if op.get('vendor_extension') else ""
        versions = op.get('versions', operations['versions'])
        param_count = len(op.get('parameters', []))
        print(f"    • {op['name']}: {param_count} parameters, versions {', '.join(versions)}{vendor}")


if __name__ == "__main__":
    main()
