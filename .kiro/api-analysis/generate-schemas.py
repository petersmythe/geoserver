#!/usr/bin/env python3
"""
Generate OpenAPI 3.0 schemas from GeoServer Java interfaces.
This script creates schema definitions for common REST API data models.
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Any

# Schema definitions based on GeoServer catalog interfaces
SCHEMAS = {
    "Workspace": {
        "type": "object",
        "description": "A container for grouping store objects",
        "properties": {
            "name": {
                "type": "string",
                "description": "The unique name of the workspace"
            },
            "isolated": {
                "type": "boolean",
                "description": "Whether the workspace is isolated",
                "default": False
            }
        },
        "required": ["name"]
    },
    
    "DataStore": {
        "type": "object",
        "description": "A vector or feature based data store",
        "properties": {
            "name": {
                "type": "string",
                "description": "The unique name of the data store"
            },
            "description": {
                "type": "string",
                "description": "Description of the data store"
            },
            "type": {
                "type": "string",
                "description": "The store type (e.g., 'Shapefile', 'PostGIS', 'GeoPackage')",
                "example": "PostGIS"
            },
            "enabled": {
                "type": "boolean",
                "description": "Whether the store is enabled",
                "default": True
            },
            "workspace": {
                "$ref": "#/components/schemas/Workspace"
            },
            "connectionParameters": {
                "type": "object",
                "description": "Connection parameters specific to the store type",
                "additionalProperties": True
            },
            "disableOnConnFailure": {
                "type": "boolean",
                "description": "Auto-disable store on connection failure",
                "default": False
            }
        },
        "required": ["name", "type", "workspace"]
    },
