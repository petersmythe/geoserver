# Swagger UI Digest Authentication Note

**Date**: 2026-02-15  
**Issue**: Swagger UI does not support HTTP Digest authentication for interactive testing

## Background

The GeoServer OpenAPI specifications correctly document HTTP Digest Authentication as a supported authentication method. However, Swagger UI (the interactive API documentation tool) has a limitation where it only supports the following HTTP authentication schemes for interactive testing:

- `basic` (HTTP Basic Authentication)
- `bearer` (Bearer Token Authentication)

## The Limitation

When viewing the OpenAPI specification in Swagger UI, you may see a warning:

```
digestAuth HTTP authentication: unsupported scheme 'digest' for available authorisations.
```

This is **not an error in the OpenAPI specification** - it's a limitation of Swagger UI itself.

## Why We Keep It

We've chosen to keep the `digestAuth` security scheme in the specification for the following reasons:

1. **Accuracy**: The OpenAPI spec should accurately document what GeoServer actually supports, not just what Swagger UI can test
2. **Other Tools**: Many other API tools support Digest authentication:
   - Postman
   - Insomnia
   - curl
   - HTTPie
   - Generated client libraries
3. **Documentation Value**: Developers need to know that Digest auth is available as an option
4. **Standards Compliance**: HTTP Digest is a valid authentication scheme per RFC 7616 and OpenAPI 3.0 specification

## Solution Added

We've added a note to the `digestAuth` description in the OpenAPI specification:

```yaml
digestAuth:
  type: http
  scheme: digest
  description: |
    HTTP Digest Authentication provides a more secure alternative to Basic auth 
    by applying a cryptographic hash function to passwords before sending them 
    over the network. Must be explicitly configured in GeoServer's authentication 
    filter chain. 
    
    **Note**: Swagger UI does not support Digest authentication for interactive 
    testing - use Basic or Bearer authentication for evaluation purposes.
    
    See: https://docs.geoserver.org/stable/en/user/security/tutorials/digest/
```

## For Interactive Testing

When using Swagger UI to test the GeoServer API, use one of these alternatives:

1. **HTTP Basic Authentication** - Simplest option, works in Swagger UI
2. **Bearer Token Authentication** - If OAuth2 is configured

## For Production Use

In production environments, you can still use HTTP Digest Authentication:

- Configure it in GeoServer's authentication filter chain
- Use it with curl, Postman, or other API clients
- It provides better security than Basic auth (without HTTPS)
- Always use HTTPS in production regardless of authentication method

## Testing Digest Auth

To test Digest authentication outside of Swagger UI:

**Using curl**:
```bash
curl --digest -u admin:geoserver \
  http://localhost:8080/geoserver/wfs?request=getcapabilities
```

**Using Python requests**:
```python
from requests.auth import HTTPDigestAuth
import requests

response = requests.get(
    'http://localhost:8080/geoserver/wfs?request=getcapabilities',
    auth=HTTPDigestAuth('admin', 'geoserver')
)
```

**Using Postman**:
1. Open Postman
2. Create a new request
3. Go to Authorization tab
4. Select "Digest Auth" from the Type dropdown
5. Enter username and password
6. Send request

## References

- [RFC 7616 - HTTP Digest Access Authentication](https://tools.ietf.org/html/rfc7616)
- [OpenAPI 3.0 Security Scheme Object](https://swagger.io/specification/#security-scheme-object)
- [GeoServer Digest Authentication Tutorial](https://docs.geoserver.org/stable/en/user/security/tutorials/digest/)
- [Swagger UI Issue #3054 - Digest Auth Support](https://github.com/swagger-api/swagger-ui/issues/3054)

## Conclusion

The OpenAPI specification is correct and complete. The Swagger UI warning is expected and does not indicate a problem with the specification. Users who need to test Digest authentication should use alternative tools like curl, Postman, or Insomnia.
