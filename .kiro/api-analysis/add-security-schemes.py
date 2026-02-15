#!/usr/bin/env python3
"""
Add security schemes to GeoServer OpenAPI specifications.

This script adds comprehensive security documentation based on GeoServer's
authentication methods:
- HTTP Basic Authentication (default)
- HTTP Digest Authentication
- API Key Authentication (authkey extension)
- OAuth2 (community module)

References:
- https://docs.geoserver.org/main/en/user/security/webadmin/auth.html
- https://docs.geoserver.org/2.22.x/en/user/security/tutorials/digest/index.html
- https://docs.geoserver.org/latest/en/user/extensions/authkey/
- https://docs.geoserver.org/2.20.x/en/user/community/oauth2/index.html
"""

import json
import yaml
import sys
from pathlib import Path

# Security schemes to add to OpenAPI specs
SECURITY_SCHEMES = {
    "basicAuth": {
        "type": "http",
        "scheme": "basic",
        "description": (
            "HTTP Basic Authentication is the default authentication method for GeoServer. "
            "Credentials are sent in the Authorization header as base64-encoded username:password. "
            "**Security Note**: Basic auth sends credentials in plain text (base64 is encoding, not encryption). "
            "Always use HTTPS in production to protect credentials."
        )
    },
    "digestAuth": {
        "type": "http",
        "scheme": "digest",
        "description": (
            "HTTP Digest Authentication provides a more secure alternative to Basic auth by applying "
            "a cryptographic hash function to passwords before sending them over the network. "
            "Must be explicitly configured in GeoServer's authentication filter chain. "
            "**Note**: Swagger UI does not support Digest authentication for interactive testing - "
            "use Basic or Bearer authentication for evaluation purposes. "
            "See: https://docs.geoserver.org/stable/en/user/security/tutorials/digest/"
        )
    },
    "apiKeyAuth": {
        "type": "apiKey",
        "in": "query",
        "name": "authkey",
        "description": (
            "API Key authentication using the authkey extension module. "
            "Designed for OGC clients that cannot handle other security protocols. "
            "The authentication key is a UUID appended to the URL as a query parameter. "
            "**Security Note**: This approach is vulnerable to token sniffing and must always be used with HTTPS. "
            "Requires the authkey extension to be installed and configured. "
            "See: https://docs.geoserver.org/stable/en/user/extensions/authkey/"
        )
    },
    "oauth2": {
        "type": "oauth2",
        "flows": {
            "authorizationCode": {
                "authorizationUrl": "https://accounts.google.com/o/oauth2/auth",
                "tokenUrl": "https://accounts.google.com/o/oauth2/token",
                "scopes": {
                    "openid": "OpenID Connect scope",
                    "profile": "Access user profile information",
                    "email": "Access user email address"
                }
            }
        },
        "description": (
            "OAuth2 authentication support (community module). "
            "GeoServer can authenticate against OAuth2 providers including Google, GitHub, and OpenID Connect. "
            "The authorization URLs and scopes shown are examples for Google OAuth2. "
            "Actual configuration depends on your OAuth2 provider. "
            "**Note**: This is a community module and must be installed separately. "
            "See: https://docs.geoserver.org/stable/en/user/community/oauth2/"
        )
    },
    "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": (
            "Bearer token authentication using JWT (JSON Web Tokens). "
            "Used with OAuth2/OpenID Connect authentication. "
            "The token is obtained from an OAuth2 provider and included in the Authorization header. "
            "Requires OAuth2 community module to be installed and configured."
        )
    }
}

# Default security requirements for different endpoint types
# Most endpoints require authentication, but some allow anonymous access
DEFAULT_SECURITY = [
    {"basicAuth": []},
    {"digestAuth": []},
    {"apiKeyAuth": []},
    {"oauth2": ["openid", "profile", "email"]},
    {"bearerAuth": []}
]

# Anonymous endpoints (no authentication required)
ANONYMOUS_ENDPOINTS = [
    # OGC service capabilities documents are typically public
    "/wms",  # WMS GetCapabilities
    "/wfs",  # WFS GetCapabilities
    "/wcs",  # WCS GetCapabilities
    "/wmts",  # WMTS GetCapabilities
    "/csw",  # CSW GetCapabilities
    "/wps",  # WPS GetCapabilities
]


def add_security_to_yaml(yaml_file: Path):
    """Add security schemes to a YAML OpenAPI spec."""
    print(f"Processing YAML file: {yaml_file}")
    
    with open(yaml_file, 'r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)
    
    # Add security schemes to components
    if 'components' not in spec:
        spec['components'] = {}
    
    spec['components']['securitySchemes'] = SECURITY_SCHEMES
    
    # Add global security requirement (applies to all endpoints unless overridden)
    # This means all endpoints require one of the authentication methods
    spec['security'] = DEFAULT_SECURITY
    
    # Count endpoints that will have security applied
    endpoint_count = len(spec.get('paths', {}))
    
    # Write back to file
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"  ✓ Added {len(SECURITY_SCHEMES)} security schemes")
    print(f"  ✓ Applied global security to {endpoint_count} endpoints")
    return True


def add_security_to_json(json_file: Path):
    """Add security schemes to a JSON OpenAPI spec."""
    print(f"Processing JSON file: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    
    # Add security schemes to components
    if 'components' not in spec:
        spec['components'] = {}
    
    spec['components']['securitySchemes'] = SECURITY_SCHEMES
    
    # Add global security requirement
    spec['security'] = DEFAULT_SECURITY
    
    # Count endpoints
    endpoint_count = len(spec.get('paths', {}))
    
    # Write back to file with pretty printing
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Added {len(SECURITY_SCHEMES)} security schemes")
    print(f"  ✓ Applied global security to {endpoint_count} endpoints")
    return True


def main():
    """Main execution function."""
    print("=" * 70)
    print("Adding Security Schemes to GeoServer OpenAPI Specifications")
    print("=" * 70)
    print()
    
    # Files to process
    files_to_process = [
        # Modular specs
        (".kiro/api-analysis/specs/geoserver.yaml", "yaml"),
        (".kiro/api-analysis/specs/geoserver.json", "json"),
        # Bundled specs
        ("doc/en/api/geoserver-bundled.yaml", "yaml"),
        ("doc/en/api/geoserver-bundled.json", "json"),
    ]
    
    success_count = 0
    error_count = 0
    
    for file_path, file_type in files_to_process:
        path = Path(file_path)
        
        if not path.exists():
            print(f"⚠ File not found: {file_path}")
            error_count += 1
            continue
        
        try:
            if file_type == "yaml":
                if add_security_to_yaml(path):
                    success_count += 1
            elif file_type == "json":
                if add_security_to_json(path):
                    success_count += 1
            print()
        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")
            error_count += 1
            print()
    
    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Successfully processed: {success_count} files")
    print(f"Errors: {error_count} files")
    print()
    
    print("Security Schemes Added:")
    for scheme_name, scheme_def in SECURITY_SCHEMES.items():
        print(f"  • {scheme_name}: {scheme_def['type']} ({scheme_def.get('scheme', 'N/A')})")
    print()
    
    print("Authentication Methods Documented:")
    print("  1. HTTP Basic Authentication (default)")
    print("  2. HTTP Digest Authentication")
    print("  3. API Key Authentication (authkey extension)")
    print("  4. OAuth2/OpenID Connect (community module)")
    print("  5. Bearer Token/JWT (with OAuth2)")
    print()
    
    print("Global Security Applied:")
    print("  All endpoints now require one of the above authentication methods.")
    print("  Clients can choose any supported method based on their capabilities.")
    print()
    
    print("References:")
    print("  • Authentication: https://docs.geoserver.org/stable/en/user/security/webadmin/auth.html")
    print("  • Digest Auth: https://docs.geoserver.org/stable/en/user/security/tutorials/digest/")
    print("  • API Key: https://docs.geoserver.org/stable/en/user/extensions/authkey/")
    print("  • OAuth2: https://docs.geoserver.org/stable/en/user/community/oauth2/")
    print()
    
    if error_count > 0:
        print("⚠ Some files had errors. Please review the output above.")
        return 1
    
    print("✓ All files processed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
