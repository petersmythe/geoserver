# GeoServer Authentication Methods Documentation

## Overview

This document provides comprehensive documentation of all authentication methods supported by GeoServer, as implemented in the OpenAPI 3.0 specifications.

**Date**: 2026-02-15  
**Spec Version**: 3.0.x  
**Task**: 15.6 - Research and document authentication methods

## Supported Authentication Methods

GeoServer supports multiple authentication methods to accommodate different client capabilities and security requirements. All methods have been documented in the OpenAPI specifications under `components.securitySchemes`.

### 1. HTTP Basic Authentication (Default)

**Type**: `http`  
**Scheme**: `basic`  
**Status**: Built-in, enabled by default

#### Description
HTTP Basic Authentication is the default authentication method for GeoServer REST and OGC services. Credentials are sent in the `Authorization` header as base64-encoded `username:password`.

#### Usage
```http
GET /geoserver/rest/workspaces HTTP/1.1
Host: localhost:8080
Authorization: Basic YWRtaW46Z2Vvc2VydmVy
```

#### Security Considerations
- **⚠️ Security Warning**: Basic auth sends credentials in plain text (base64 is encoding, not encryption)
- **Always use HTTPS in production** to protect credentials from network sniffing
- Credentials are sent with every request (no session management)
- Simple to implement but less secure than digest or token-based methods

#### Configuration
No configuration required - enabled by default in GeoServer.

#### References
- [GeoServer Authentication Documentation](https://docs.geoserver.org/stable/en/user/security/webadmin/auth.html)
- [RFC 7617 - HTTP Basic Authentication](https://tools.ietf.org/html/rfc7617)

---

### 2. HTTP Digest Authentication

**Type**: `http`  
**Scheme**: `digest`  
**Status**: Optional, requires configuration

#### Description
HTTP Digest Authentication provides a more secure alternative to Basic auth by applying a cryptographic hash function (MD5) to passwords before sending them over the network. This prevents password sniffing even on unencrypted connections.

#### Usage
```http
GET /geoserver/wfs?request=getcapabilities HTTP/1.1
Host: localhost:8080
Authorization: Digest username="admin", realm="GeoServer Realm", 
  nonce="MTMzMzQzMDkxMTU3MjphZGIwMWE4MTc1NmRiMzI3YmFiODhmY2NmZGQ2MzEwZg==",
  uri="/geoserver/wfs?request=getcapabilities", qop=auth, nc=00000001,
  cnonce="0a4f113b", response="6629fae49393a05397450978507c4ef1"
```

#### Security Considerations
- More secure than Basic auth - passwords are hashed before transmission
- Protects against replay attacks using nonces
- Still vulnerable to man-in-the-middle attacks without HTTPS
- Requires more complex client implementation

#### Configuration
Must be explicitly configured in GeoServer's authentication filter chain:

1. Navigate to **Security > Authentication**
2. Add new **Digest** authentication filter
3. Configure user/group service
4. Add filter to appropriate filter chains (web, rest, gwc, default)
5. Position before anonymous filter

#### References
- [Configuring Digest Authentication Tutorial](https://docs.geoserver.org/stable/en/user/security/tutorials/digest/)
- [RFC 7616 - HTTP Digest Authentication](https://tools.ietf.org/html/rfc7616)

---

### 3. API Key Authentication (authkey extension)

**Type**: `apiKey`  
**Location**: `query`  
**Parameter Name**: `authkey`  
**Status**: Extension module, requires installation

#### Description
API Key authentication using the authkey extension module. Designed for OGC clients that cannot handle other security protocols (not even HTTP Basic). The authentication key is a UUID appended to the URL as a query parameter.

#### Usage
```http
GET /geoserver/topp/wms?service=WMS&version=1.3.0&request=GetCapabilities&authkey=ef18d7e7-963b-470f-9230-c7f9de166888 HTTP/1.1
Host: localhost:8080
```

#### Key Providers

GeoServer supports three key provider implementations:

1. **User Properties Provider**: Stores UUID in user properties (property name: `UUID`)
2. **Property File Provider**: Uses `authkeys.properties` file mapping keys to usernames
3. **External Web Service Provider**: Calls external URL to validate keys

#### Security Considerations
- **⚠️ Security Warning**: Vulnerable to token sniffing in URLs (logs, browser history, referrer headers)
- **Must always be used with HTTPS** to protect authentication keys
- Keys appear in server logs and browser history
- Suitable only for clients that cannot support other authentication methods
- Not recommended for web browsers or REST API access

#### Configuration

1. **Install Extension**:
   - Download `geoserver-{version}-authkey-plugin.zip`
   - Extract to `WEB-INF/lib`
   - Restart GeoServer

2. **Configure Filter**:
   - Navigate to **Security > Authentication > Authentication Filters**
   - Add new **authkey** filter
   - Select key provider (user properties, property file, or web service)
   - Configure user/group service
   - Add to filter chains

3. **Synchronize Keys**:
   - Click "Synchronize" button to generate keys for existing users
   - Keys are UUIDs (e.g., `b52d2068-0a9b-45d7-aacc-144d16322018`)

#### Limitations
- Meant for OGC services only (WMS, WFS, WCS, etc.)
- Won't work properly with administration GUI or RESTConfig
- Cannot disable users via "Enabled" checkbox (authkey bypasses this)

#### References
- [Key Authentication Module Documentation](https://docs.geoserver.org/stable/en/user/extensions/authkey/)

---

### 4. OAuth2 / OpenID Connect

**Type**: `oauth2`  
**Flow**: `authorizationCode`  
**Status**: Community module, requires installation

#### Description
OAuth2 authentication support allows GeoServer to authenticate against OAuth2 providers including Google, GitHub, and OpenID Connect. This enables integration with existing identity management systems and single sign-on (SSO) solutions.

#### Supported Providers
- Google OAuth2
- GitHub OAuth2
- OpenID Connect (generic)
- Custom OAuth2 providers

#### OAuth2 Flow Example (Google)

```
1. User requests protected resource
   → GET /geoserver/rest/workspaces

2. GeoServer redirects to OAuth2 provider
   → https://accounts.google.com/o/oauth2/auth?
     scope=openid+profile+email&
     response_type=code&
     redirect_uri=http://localhost:8080/geoserver&
     client_id={CLIENT_ID}

3. User authenticates with provider and grants permissions

4. Provider redirects back with authorization code
   → http://localhost:8080/geoserver?code={AUTH_CODE}

5. GeoServer exchanges code for access token
   → POST https://accounts.google.com/o/oauth2/token
     code={AUTH_CODE}&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}

6. GeoServer validates token and creates session

7. User accesses protected resource with session
```

#### Configuration

1. **Install Extension**:
   - Download `geoserver-{version}-sec-oauth2.zip`
   - Extract both `oauth2` and `oauth2-{provider}` JARs to `WEB-INF/lib`
   - Restart GeoServer

2. **Configure OAuth2 Provider** (e.g., Google):
   - Visit [Google API Console](https://console.developers.google.com/)
   - Create OAuth 2.0 credentials (Client ID and Client Secret)
   - Add authorized redirect URIs:
     - `http://localhost:8080/geoserver`
     - `http://localhost:8080/geoserver/`

3. **Configure GeoServer Filter**:
   - Navigate to **Security > Authentication > Authentication Filters**
   - Add new **OAuth2** filter
   - Configure endpoints:
     - **Access Token URI**: `https://accounts.google.com/o/oauth2/token`
     - **User Authorization URI**: `https://accounts.google.com/o/oauth2/auth`
     - **Redirect URI**: `http://localhost:8080/geoserver`
     - **Check Token Endpoint**: `https://www.googleapis.com/oauth2/v1/tokeninfo`
     - **Scopes**: `https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/userinfo.profile`
   - Enter Client ID and Client Secret
   - Select Role Service
   - Add to filter chains

#### OpenID Connect Configuration

For OpenID Connect providers, the configuration supports auto-discovery:

- Provide the OpenID Discovery document URL (e.g., `https://provider.com/.well-known/openid-configuration`)
- GeoServer will auto-fill endpoint URLs from the discovery document
- Configure role extraction from ID token or Access token

#### Security Considerations
- More secure than Basic or Digest auth
- Supports modern authentication flows (MFA, SSO)
- Tokens have expiration times
- Requires HTTPS for production use
- Client Secret must be kept secure

#### References
- [OAuth2 Authentication Documentation](https://docs.geoserver.org/stable/en/user/community/oauth2/)
- [OpenID Connect Specification](https://openid.net/connect/)

---

### 5. Bearer Token / JWT

**Type**: `http`  
**Scheme**: `bearer`  
**Bearer Format**: `JWT`  
**Status**: Used with OAuth2/OpenID Connect

#### Description
Bearer token authentication using JWT (JSON Web Tokens). This is used in conjunction with OAuth2/OpenID Connect authentication. The token is obtained from an OAuth2 provider and included in the `Authorization` header for subsequent requests.

#### Usage
```http
GET /geoserver/rest/workspaces HTTP/1.1
Host: localhost:8080
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.NHVaYe26MbtOYhSKkoKYdFVomg4i8ZJd8_-RU8VNbftc4TSMb4bXP3l3YlNWACwyXPGffz5aXHc6lty1Y2t4SWRqGteragsVdZufDn5BlnJl9pdR_kdVFUsra2rWKEofkZeIC4yWytE58sMIihvo9H1ScmmVwBcQP6XETqYd0aSHp1gOa9RdUPDvoXQ5oqygTqVtxaDr6wUFKrKItgBMzWIdNZ6y7O9E0DhEPTbE9rfBo6KTFsHAZnMg4k68CDp2woYIaXbmYTWcvbzIuHO7_37GT79XdIwkm95QJ7hYC9RiwrV7mesbY4PAahERJawntho0my942XheVLmGwLMBkQ
```

#### JWT Token Structure
```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user@example.com",
    "name": "John Doe",
    "email": "user@example.com",
    "roles": ["ROLE_USER", "ROLE_ADMIN"],
    "iat": 1516239022,
    "exp": 1516242622
  },
  "signature": "..."
}
```

#### Security Considerations
- Tokens are cryptographically signed (cannot be tampered with)
- Tokens have expiration times (typically 1 hour)
- Tokens can be revoked by the OAuth2 provider
- Should be transmitted over HTTPS only
- Tokens should not be stored in browser localStorage (XSS vulnerability)

#### Configuration
Automatically supported when OAuth2/OpenID Connect module is installed and configured. No additional configuration required.

#### References
- [JWT.io - JSON Web Tokens](https://jwt.io/)
- [RFC 7519 - JSON Web Token](https://tools.ietf.org/html/rfc7519)

---

## OpenAPI Specification Implementation

### Security Schemes Definition

All authentication methods are defined in the OpenAPI specification under `components.securitySchemes`:

```yaml
components:
  securitySchemes:
    basicAuth:
      type: http
      scheme: basic
      description: "HTTP Basic Authentication (default)..."
    
    digestAuth:
      type: http
      scheme: digest
      description: "HTTP Digest Authentication..."
    
    apiKeyAuth:
      type: apiKey
      in: query
      name: authkey
      description: "API Key authentication (authkey extension)..."
    
    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://accounts.google.com/o/oauth2/auth
          tokenUrl: https://accounts.google.com/o/oauth2/token
          scopes:
            openid: "OpenID Connect scope"
            profile: "Access user profile information"
            email: "Access user email address"
      description: "OAuth2 authentication (community module)..."
    
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: "Bearer token authentication (JWT)..."
```

### Global Security Requirement

A global security requirement is applied to all endpoints, allowing clients to choose any supported authentication method:

```yaml
security:
  - basicAuth: []
  - digestAuth: []
  - apiKeyAuth: []
  - oauth2: [openid, profile, email]
  - bearerAuth: []
```

This means:
- All endpoints require authentication (one of the methods above)
- Clients can choose the most appropriate method for their capabilities
- Multiple methods can be attempted (e.g., try Bearer token, fall back to Basic auth)

### Per-Endpoint Security Overrides

Individual endpoints can override the global security requirement if needed. For example, public endpoints like OGC GetCapabilities could be marked as not requiring authentication:

```yaml
paths:
  /wms:
    get:
      summary: WMS GetCapabilities
      security: []  # Override global security - no authentication required
```

## Authentication Method Comparison

| Method | Security Level | Ease of Use | Client Support | Installation | Use Case |
|--------|---------------|-------------|----------------|--------------|----------|
| **Basic Auth** | Low (without HTTPS) | Very Easy | Universal | Built-in | Development, simple clients |
| **Digest Auth** | Medium | Easy | Good | Configuration | Better security without HTTPS |
| **API Key** | Low (without HTTPS) | Very Easy | Universal | Extension | Legacy OGC clients |
| **OAuth2** | High | Complex | Modern clients | Community module | Enterprise SSO, modern apps |
| **Bearer/JWT** | High | Medium | Modern clients | With OAuth2 | Stateless API access |

## Recommendations

### Development Environment
- Use **HTTP Basic Authentication** for simplicity
- No additional configuration required
- Easy to test with curl, Postman, or browser

### Production Environment
- **Always use HTTPS** regardless of authentication method
- Prefer **OAuth2/OpenID Connect** for enterprise deployments
- Use **Digest Authentication** if OAuth2 is not available
- Avoid **API Key** authentication unless required for legacy clients

### OGC Service Clients
- Use **HTTP Basic** or **Digest** for desktop GIS clients (QGIS, ArcGIS)
- Use **API Key** only for clients that cannot support other methods
- Use **Bearer tokens** for modern web applications

### REST API Clients
- Use **Bearer tokens** (OAuth2) for web applications
- Use **HTTP Basic** for server-to-server communication (with HTTPS)
- Use **Digest** for enhanced security without OAuth2 complexity

## Testing Authentication

### Testing with curl

**Basic Authentication**:
```bash
curl -u admin:geoserver http://localhost:8080/geoserver/rest/workspaces
```

**Digest Authentication**:
```bash
curl --digest -u admin:geoserver http://localhost:8080/geoserver/wfs?request=getcapabilities
```

**API Key Authentication**:
```bash
curl "http://localhost:8080/geoserver/wms?service=WMS&request=GetCapabilities&authkey=ef18d7e7-963b-470f-9230-c7f9de166888"
```

**Bearer Token Authentication**:
```bash
curl -H "Authorization: Bearer eyJhbGc..." http://localhost:8080/geoserver/rest/workspaces
```

### Testing with Python

```python
import requests

# Basic Auth
response = requests.get(
    'http://localhost:8080/geoserver/rest/workspaces',
    auth=('admin', 'geoserver')
)

# Digest Auth
from requests.auth import HTTPDigestAuth
response = requests.get(
    'http://localhost:8080/geoserver/wfs?request=getcapabilities',
    auth=HTTPDigestAuth('admin', 'geoserver')
)

# API Key
response = requests.get(
    'http://localhost:8080/geoserver/wms',
    params={
        'service': 'WMS',
        'request': 'GetCapabilities',
        'authkey': 'ef18d7e7-963b-470f-9230-c7f9de166888'
    }
)

# Bearer Token
response = requests.get(
    'http://localhost:8080/geoserver/rest/workspaces',
    headers={'Authorization': 'Bearer eyJhbGc...'}
)
```

## Files Modified

The following OpenAPI specification files have been updated with security schemes:

1. **Modular Specifications**:
   - `.kiro/api-analysis/specs/geoserver.yaml`
   - `.kiro/api-analysis/specs/geoserver.json`

2. **Bundled Specifications**:
   - `doc/en/api/geoserver-bundled.yaml`
   - `doc/en/api/geoserver-bundled.json`

All files now include:
- Complete `securitySchemes` definitions in `components`
- Global `security` requirement applying to all endpoints
- Comprehensive descriptions with security warnings and configuration links

## References

### Official GeoServer Documentation
- [Authentication Overview](https://docs.geoserver.org/stable/en/user/security/webadmin/auth.html)
- [Authentication Chain](https://docs.geoserver.org/stable/en/user/security/auth/chain.html)
- [Digest Authentication Tutorial](https://docs.geoserver.org/stable/en/user/security/tutorials/digest/)
- [Key Authentication Extension](https://docs.geoserver.org/stable/en/user/extensions/authkey/)
- [OAuth2 Community Module](https://docs.geoserver.org/stable/en/user/community/oauth2/)

### Standards and Specifications
- [RFC 7617 - HTTP Basic Authentication](https://tools.ietf.org/html/rfc7617)
- [RFC 7616 - HTTP Digest Authentication](https://tools.ietf.org/html/rfc7616)
- [RFC 6749 - OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749)
- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [OpenAPI 3.0 Security Scheme Object](https://swagger.io/specification/#security-scheme-object)

## Conclusion

GeoServer's OpenAPI specifications now include comprehensive documentation for all supported authentication methods. This enables:

1. **Better API Documentation**: Clients can see all available authentication options
2. **Swagger UI Integration**: Interactive API testing with authentication
3. **Code Generation**: Tools can generate client code with proper authentication
4. **Security Awareness**: Clear warnings about security considerations
5. **Configuration Guidance**: Links to official documentation for setup

All authentication methods are properly documented according to OpenAPI 3.0 standards and include detailed descriptions, security warnings, and configuration references.
