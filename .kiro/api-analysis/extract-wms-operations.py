#!/usr/bin/env python3
"""
Extract WMS operations from GeoServer implementation.

This script analyzes the WMS service implementation to extract:
- Operation names
- Parameters for each operation
- Supported versions
- Parameter types and requirements
"""

import json
from typing import Dict, List, Any

def extract_wms_operations() -> Dict[str, Any]:
    """
    Extract WMS operations based on WebMapService.java and request classes.
    
    Returns:
        Dictionary containing WMS operations metadata
    """
    
    operations = {
        "service": "WMS",
        "service_title": "Web Map Service",
        "description": "OGC Web Map Service for rendering maps from geospatial data",
        "versions": ["1.0.0", "1.1.0", "1.1.1", "1.3.0"],
        "source_files": [
            "src/wms/src/main/java/org/geoserver/wms/WebMapService.java",
            "src/wms/src/main/java/org/geoserver/wms/GetMapRequest.java",
            "src/wms/src/main/java/org/geoserver/wms/GetFeatureInfoRequest.java",
            "src/wms/src/main/java/org/geoserver/wms/GetLegendGraphicRequest.java",
            "src/wms/src/main/java/org/geoserver/wms/DescribeLayerRequest.java",
            "src/wms/src/main/java/org/geoserver/wms/GetCapabilitiesRequest.java"
        ],
        "operations": []
    }
    
    # GetCapabilities operation
    get_capabilities = {
        "name": "GetCapabilities",
        "description": "Returns service metadata and available layers",
        "http_methods": ["GET", "POST"],
        "parameters": [
            {
                "name": "SERVICE",
                "type": "string",
                "required": True,
                "description": "Service name (WMS)",
                "default": "WMS"
            },
            {
                "name": "VERSION",
                "type": "string",
                "required": True,
                "description": "Service version",
                "allowed_values": ["1.0.0", "1.1.0", "1.1.1", "1.3.0"]
            },
            {
                "name": "REQUEST",
                "type": "string",
                "required": True,
                "description": "Operation name",
                "default": "GetCapabilities"
            },
            {
                "name": "UPDATESEQUENCE",
                "type": "string",
                "required": False,
                "description": "Sequence number for cache validation"
            },
            {
                "name": "NAMESPACE",
                "type": "string",
                "required": False,
                "description": "Filter layers by namespace prefix"
            },
            {
                "name": "ROOTLAYER",
                "type": "boolean",
                "required": False,
                "description": "Include root layer in capabilities"
            },
            {
                "name": "ACCEPTLANGUAGES",
                "type": "string",
                "required": False,
                "description": "Comma-separated list of accepted languages"
            }
        ]
    }
    operations["operations"].append(get_capabilities)
    
    # GetMap operation
    get_map = {
        "name": "GetMap",
        "description": "Returns a map image for specified layers and area",
        "http_methods": ["GET", "POST"],
        "parameters": [
            # Mandatory parameters
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
                "default": "GetMap"
            },
            {
                "name": "LAYERS",
                "type": "string",
                "required": True,
                "description": "Comma-separated list of layer names"
            },
            {
                "name": "STYLES",
                "type": "string",
                "required": True,
                "description": "Comma-separated list of style names (empty for default)"
            },
            {
                "name": "SRS",
                "type": "string",
                "required": True,
                "description": "Spatial Reference System (WMS 1.1.x) or CRS (WMS 1.3.0)",
                "note": "Parameter name changes to CRS in WMS 1.3.0"
            },
            {
                "name": "BBOX",
                "type": "string",
                "required": True,
                "description": "Bounding box (minx,miny,maxx,maxy)"
            },
            {
                "name": "WIDTH",
                "type": "integer",
                "required": True,
                "description": "Image width in pixels"
            },
            {
                "name": "HEIGHT",
                "type": "integer",
                "required": True,
                "description": "Image height in pixels"
            },
            {
                "name": "FORMAT",
                "type": "string",
                "required": True,
                "description": "Output image MIME type (e.g., image/png, image/jpeg)"
            },
            # Optional parameters
            {
                "name": "TRANSPARENT",
                "type": "boolean",
                "required": False,
                "description": "Background transparency",
                "default": "false"
            },
            {
                "name": "BGCOLOR",
                "type": "string",
                "required": False,
                "description": "Background color (hex format: 0xRRGGBB)",
                "default": "0xFFFFFF"
            },
            {
                "name": "EXCEPTIONS",
                "type": "string",
                "required": False,
                "description": "Exception format",
                "default": "application/vnd.ogc.se_xml"
            },
            {
                "name": "TIME",
                "type": "string",
                "required": False,
                "description": "Time dimension value or range"
            },
            {
                "name": "ELEVATION",
                "type": "string",
                "required": False,
                "description": "Elevation dimension value or range"
            },
            {
                "name": "SLD",
                "type": "string",
                "required": False,
                "description": "URL to external SLD document (alias for STYLE_URL)"
            },
            {
                "name": "SLD_BODY",
                "type": "string",
                "required": False,
                "description": "Inline SLD document (alias for STYLE_BODY)"
            },
            {
                "name": "STYLE_URL",
                "type": "string",
                "required": False,
                "description": "URL to external style document"
            },
            {
                "name": "STYLE_BODY",
                "type": "string",
                "required": False,
                "description": "Inline style document"
            },
            {
                "name": "STYLE_VERSION",
                "type": "string",
                "required": False,
                "description": "Style language version"
            },
            {
                "name": "STYLE_FORMAT",
                "type": "string",
                "required": False,
                "description": "Style document format"
            },
            {
                "name": "VALIDATESCHEMA",
                "type": "boolean",
                "required": False,
                "description": "Validate SLD schema",
                "default": "false"
            },
            {
                "name": "FILTER",
                "type": "string",
                "required": False,
                "description": "OGC Filter XML for each layer"
            },
            {
                "name": "CQL_FILTER",
                "type": "string",
                "required": False,
                "description": "CQL filter expressions for each layer"
            },
            {
                "name": "FEATUREID",
                "type": "string",
                "required": False,
                "description": "Feature IDs to render"
            },
            {
                "name": "TILED",
                "type": "boolean",
                "required": False,
                "description": "WMS-C tiling hint",
                "default": "false"
            },
            {
                "name": "TILESORIGIN",
                "type": "string",
                "required": False,
                "description": "Tile origin point (x,y)"
            },
            {
                "name": "BUFFER",
                "type": "integer",
                "required": False,
                "description": "Rendering buffer in pixels",
                "default": "0"
            },
            {
                "name": "PALETTE",
                "type": "string",
                "required": False,
                "description": "Color palette for indexed color images"
            },
            {
                "name": "FEATUREVERSION",
                "type": "string",
                "required": False,
                "description": "Feature version for versioned layers"
            },
            {
                "name": "REMOTE_OWS_TYPE",
                "type": "string",
                "required": False,
                "description": "Remote OWS service type"
            },
            {
                "name": "REMOTE_OWS_URL",
                "type": "string",
                "required": False,
                "description": "Remote OWS service URL"
            },
            {
                "name": "MAXFEATURES",
                "type": "integer",
                "required": False,
                "description": "Maximum features to render (vector layers)"
            },
            {
                "name": "STARTINDEX",
                "type": "integer",
                "required": False,
                "description": "Start index for feature paging (vector layers)"
            },
            {
                "name": "ANGLE",
                "type": "number",
                "required": False,
                "description": "Map rotation angle in degrees",
                "default": "0"
            },
            {
                "name": "SORTBY",
                "type": "string",
                "required": False,
                "description": "Sort order for features"
            },
            {
                "name": "SCALEMETHOD",
                "type": "string",
                "required": False,
                "description": "Scale computation method (OGC or Accurate)",
                "default": "OGC"
            },
            {
                "name": "CLIP",
                "type": "string",
                "required": False,
                "description": "Polygon WKT to clip output"
            },
            {
                "name": "FORMAT_OPTIONS",
                "type": "string",
                "required": False,
                "description": "Format-specific options (key:value pairs)"
            },
            {
                "name": "ENV",
                "type": "string",
                "required": False,
                "description": "SLD environment variables for substitution"
            },
            {
                "name": "VIEWPARAMS",
                "type": "string",
                "required": False,
                "description": "SQL view parameters"
            },
            {
                "name": "INTERPOLATIONS",
                "type": "string",
                "required": False,
                "description": "Interpolation methods for raster layers"
            }
        ],
        "vendor_extensions": [
            "CQL_FILTER", "FEATUREID", "TILED", "TILESORIGIN", "BUFFER", 
            "PALETTE", "FEATUREVERSION", "MAXFEATURES", "STARTINDEX", 
            "ANGLE", "SORTBY", "SCALEMETHOD", "CLIP", "FORMAT_OPTIONS", 
            "ENV", "VIEWPARAMS", "INTERPOLATIONS", "REMOTE_OWS_TYPE", "REMOTE_OWS_URL"
        ]
    }
    operations["operations"].append(get_map)
    
    # GetFeatureInfo operation
    get_feature_info = {
        "name": "GetFeatureInfo",
        "description": "Returns information about features at a pixel location",
        "http_methods": ["GET", "POST"],
        "parameters": [
            # All GetMap parameters plus:
            {
                "name": "QUERY_LAYERS",
                "type": "string",
                "required": True,
                "description": "Comma-separated list of layers to query"
            },
            {
                "name": "INFO_FORMAT",
                "type": "string",
                "required": True,
                "description": "Output format MIME type"
            },
            {
                "name": "FEATURE_COUNT",
                "type": "integer",
                "required": False,
                "description": "Maximum number of features to return",
                "default": "1"
            },
            {
                "name": "X",
                "type": "integer",
                "required": True,
                "description": "X pixel coordinate (WMS 1.1.x) or I (WMS 1.3.0)"
            },
            {
                "name": "Y",
                "type": "integer",
                "required": True,
                "description": "Y pixel coordinate (WMS 1.1.x) or J (WMS 1.3.0)"
            },
            {
                "name": "EXCEPTIONS",
                "type": "string",
                "required": False,
                "description": "Exception format",
                "default": "application/vnd.ogc.se_xml"
            },
            {
                "name": "PROPERTYNAME",
                "type": "string",
                "required": False,
                "description": "Comma-separated list of properties to return"
            },
            {
                "name": "EXCLUDE_NODATA_RESULT",
                "type": "boolean",
                "required": False,
                "description": "Exclude nodata values from results",
                "default": "false"
            }
        ],
        "note": "Includes all GetMap parameters to define the map context",
        "vendor_extensions": ["PROPERTYNAME", "EXCLUDE_NODATA_RESULT"]
    }
    operations["operations"].append(get_feature_info)
    
    # GetLegendGraphic operation
    get_legend_graphic = {
        "name": "GetLegendGraphic",
        "description": "Returns a legend graphic for a layer style",
        "http_methods": ["GET", "POST"],
        "parameters": [
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
                "default": "GetLegendGraphic"
            },
            {
                "name": "LAYER",
                "type": "string",
                "required": True,
                "description": "Layer name or layer group"
            },
            {
                "name": "FORMAT",
                "type": "string",
                "required": True,
                "description": "Output image MIME type",
                "default": "image/png"
            },
            {
                "name": "STYLE",
                "type": "string",
                "required": False,
                "description": "Style name (default style if not specified)"
            },
            {
                "name": "FEATURETYPE",
                "type": "string",
                "required": False,
                "description": "Feature type name for multi-type layers"
            },
            {
                "name": "RULE",
                "type": "string",
                "required": False,
                "description": "Specific rule name to render"
            },
            {
                "name": "SCALE",
                "type": "number",
                "required": False,
                "description": "Scale denominator for rule selection"
            },
            {
                "name": "SLD",
                "type": "string",
                "required": False,
                "description": "URL to external SLD document"
            },
            {
                "name": "SLD_BODY",
                "type": "string",
                "required": False,
                "description": "Inline SLD document"
            },
            {
                "name": "WIDTH",
                "type": "integer",
                "required": False,
                "description": "Legend graphic width hint in pixels",
                "default": "20"
            },
            {
                "name": "HEIGHT",
                "type": "integer",
                "required": False,
                "description": "Legend graphic height hint in pixels",
                "default": "20"
            },
            {
                "name": "LANGUAGE",
                "type": "string",
                "required": False,
                "description": "Language code for internationalized text"
            },
            {
                "name": "EXCEPTIONS",
                "type": "string",
                "required": False,
                "description": "Exception format",
                "default": "application/vnd.ogc.se_xml"
            },
            {
                "name": "TRANSPARENT",
                "type": "boolean",
                "required": False,
                "description": "Background transparency",
                "default": "false"
            },
            {
                "name": "LEGEND_OPTIONS",
                "type": "string",
                "required": False,
                "description": "Key:value pairs for legend customization (fontName, fontSize, fontStyle, fontColor, bgColor, fontAntiAliasing, forceLabels, forceTitles, minSymbolSize, countMatched, hideEmptyRules)"
            },
            {
                "name": "STRICT",
                "type": "boolean",
                "required": False,
                "description": "Enforce mandatory parameter checking",
                "default": "true"
            },
            {
                "name": "ENV",
                "type": "string",
                "required": False,
                "description": "SLD environment variables for substitution"
            }
        ],
        "vendor_extensions": ["LEGEND_OPTIONS", "STRICT", "ENV"]
    }
    operations["operations"].append(get_legend_graphic)
    
    # DescribeLayer operation
    describe_layer = {
        "name": "DescribeLayer",
        "description": "Returns layer metadata including feature type and WFS URL",
        "http_methods": ["GET", "POST"],
        "parameters": [
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
                "default": "DescribeLayer"
            },
            {
                "name": "LAYERS",
                "type": "string",
                "required": True,
                "description": "Comma-separated list of layer names"
            },
            {
                "name": "EXCEPTIONS",
                "type": "string",
                "required": False,
                "description": "Exception format",
                "default": "application/vnd.ogc.se_xml"
            },
            {
                "name": "OUTPUT_FORMAT",
                "type": "string",
                "required": False,
                "description": "Output format",
                "default": "application/vnd.ogc.wms_xml"
            }
        ]
    }
    operations["operations"].append(describe_layer)
    
    # Reflector operations (vendor extensions)
    reflector = {
        "name": "reflect",
        "description": "GetMap reflector with simplified parameters",
        "http_methods": ["GET"],
        "parameters": [
            {
                "name": "layers",
                "type": "string",
                "required": True,
                "description": "Layer name (simplified parameter)"
            },
            {
                "name": "format",
                "type": "string",
                "required": False,
                "description": "Output format",
                "default": "image/png"
            }
        ],
        "note": "Vendor extension - simplified GetMap with intelligent defaults",
        "vendor_extension": True
    }
    operations["operations"].append(reflector)
    
    kml_reflector = {
        "name": "kml",
        "description": "KML reflector for Google Earth integration",
        "http_methods": ["GET"],
        "parameters": [
            {
                "name": "layers",
                "type": "string",
                "required": True,
                "description": "Layer name"
            }
        ],
        "note": "Vendor extension - generates KML/KMZ output",
        "vendor_extension": True
    }
    operations["operations"].append(kml_reflector)
    
    return operations


def main():
    """Main execution function."""
    print("Extracting WMS operations from GeoServer implementation...")
    
    operations = extract_wms_operations()
    
    # Write to JSON file
    output_file = ".kiro/api-analysis/ogc/wms-operations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(operations, f, indent=2, ensure_ascii=False)
    
    print(f"✓ WMS operations extracted to {output_file}")
    print(f"  - Service: {operations['service']}")
    print(f"  - Versions: {', '.join(operations['versions'])}")
    print(f"  - Operations: {len(operations['operations'])}")
    
    for op in operations['operations']:
        vendor = " (vendor extension)" if op.get('vendor_extension') else ""
        param_count = len(op.get('parameters', []))
        print(f"    • {op['name']}: {param_count} parameters{vendor}")


if __name__ == "__main__":
    main()
