# GeoServer OGC Service Compliance Report

**Generated:** 2026-02-13 09:09:28

## Executive Summary

- **Total Services Analyzed:** 6
- **Total Service Versions:** 11
- **Compliant Versions:** 11
- **Non-Compliant Versions:** 0
- **Total Vendor Extension Parameters:** 102
- **Total Vendor Operations:** 9

### Compliance Status by Service

| Service | Versions Analyzed | Compliant | Non-Compliant | Status |
|---------|-------------------|-----------|---------------|--------|
| WMS | 2 | 2 | 0 | ✅ |
| WFS | 3 | 3 | 0 | ✅ |
| WCS | 3 | 3 | 0 | ✅ |
| WMTS | 1 | 1 | 0 | ✅ |
| CSW | 1 | 1 | 0 | ✅ |
| WPS | 1 | 1 | 0 | ✅ |

---

## WMS - Web Map Service

### Version 1.1.1

**Specification:** [OpenGIS Web Map Service (WMS) Implementation Specification, Version 1.1.1](https://portal.ogc.org/files/?artifact_id=1081&version=1&format=pdf)

**Compliance Status:** ✅ Compliant

**Summary:**

- Required Operations: 3/3
- Optional Operations: 2/2
- Vendor Operations: reflect, kml

#### Operations

| Operation | Status | Issues |
|-----------|--------|--------|
| GetCapabilities | ✅ compliant | - |
| GetMap | ✅ compliant | 19 vendor param(s) |
| GetFeatureInfo | ✅ compliant | 2 vendor param(s) |
| DescribeLayer | ✅ compliant | - |
| GetLegendGraphic | ✅ compliant | 3 vendor param(s) |

#### Vendor Extension Parameters

| Operation | Parameter | Type | Description |
|-----------|-----------|------|-------------|
| GetMap | `ANGLE` | - | - |
| GetMap | `BUFFER` | - | - |
| GetMap | `CLIP` | - | - |
| GetMap | `CQL_FILTER` | - | - |
| GetMap | `ENV` | - | - |
| GetMap | `FEATUREID` | - | - |
| GetMap | `FEATUREVERSION` | - | - |
| GetMap | `FORMAT_OPTIONS` | - | - |
| GetMap | `INTERPOLATIONS` | - | - |
| GetMap | `MAXFEATURES` | - | - |
| GetMap | `PALETTE` | - | - |
| GetMap | `REMOTE_OWS_TYPE` | - | - |
| GetMap | `REMOTE_OWS_URL` | - | - |
| GetMap | `SCALEMETHOD` | - | - |
| GetMap | `SORTBY` | - | - |
| GetMap | `STARTINDEX` | - | - |
| GetMap | `TILED` | - | - |
| GetMap | `TILESORIGIN` | - | - |
| GetMap | `VIEWPARAMS` | - | - |
| GetFeatureInfo | `EXCLUDE_NODATA_RESULT` | - | - |
| GetFeatureInfo | `PROPERTYNAME` | - | - |
| GetLegendGraphic | `ENV` | - | - |
| GetLegendGraphic | `LEGEND_OPTIONS` | - | - |
| GetLegendGraphic | `STRICT` | - | - |

---

### Version 1.3.0

**Specification:** [OpenGIS Web Map Service (WMS) Implementation Specification, Version 1.3.0](https://portal.ogc.org/files/?artifact_id=14416)

**Compliance Status:** ✅ Compliant

**Summary:**

- Required Operations: 3/3
- Optional Operations: 2/2
- Vendor Operations: reflect, kml

#### Operations

| Operation | Status | Issues |
|-----------|--------|--------|
| GetCapabilities | ✅ compliant | - |
| GetMap | ✅ compliant | 19 vendor param(s) |
| GetFeatureInfo | ✅ compliant | 2 vendor param(s) |

#### Vendor Extension Parameters

| Operation | Parameter | Type | Description |
|-----------|-----------|------|-------------|
| GetMap | `ANGLE` | - | - |
| GetMap | `BUFFER` | - | - |
| GetMap | `CLIP` | - | - |
| GetMap | `CQL_FILTER` | - | - |
| GetMap | `ENV` | - | - |
| GetMap | `FEATUREID` | - | - |
| GetMap | `FEATUREVERSION` | - | - |
| GetMap | `FORMAT_OPTIONS` | - | - |
| GetMap | `INTERPOLATIONS` | - | - |
| GetMap | `MAXFEATURES` | - | - |
| GetMap | `PALETTE` | - | - |
| GetMap | `REMOTE_OWS_TYPE` | - | - |
| GetMap | `REMOTE_OWS_URL` | - | - |
| GetMap | `SCALEMETHOD` | - | - |
| GetMap | `SORTBY` | - | - |
| GetMap | `STARTINDEX` | - | - |
| GetMap | `TILED` | - | - |
| GetMap | `TILESORIGIN` | - | - |
| GetMap | `VIEWPARAMS` | - | - |
| GetFeatureInfo | `EXCLUDE_NODATA_RESULT` | - | - |
| GetFeatureInfo | `PROPERTYNAME` | - | - |

---

## WFS - Web Feature Service

### Version 1.0.0

**Specification:** [Web Feature Service Implementation Specification, Version 1.0.0](https://portal.ogc.org/files/?artifact_id=7176)

**Compliance Status:** ✅ Compliant

**Summary:**

- Required Operations: 3/3
- Optional Operations: 2/3
- Vendor Operations: ReleaseLock

#### Operations

| Operation | Status | Issues |
|-----------|--------|--------|
| GetCapabilities | ✅ compliant | - |
| DescribeFeatureType | ✅ compliant | - |
| GetFeature | ✅ compliant | 4 vendor param(s) |
| Transaction | ✅ compliant | - |
| LockFeature | ✅ compliant | - |

#### Vendor Extension Parameters

| Operation | Parameter | Type | Description |
|-----------|-----------|------|-------------|
| GetFeature | `CQL_FILTER` | - | - |
| GetFeature | `FEATUREVERSION` | - | - |
| GetFeature | `VIEWPARAMS` | - | - |
| GetFeature | `FORMAT_OPTIONS` | - | - |

---

### Version 1.1.0

**Specification:** [Web Feature Service Implementation Specification, Version 1.1.0](https://portal.ogc.org/files/?artifact_id=8339)

**Compliance Status:** ✅ Compliant

**Summary:**

- Required Operations: 3/3
- Optional Operations: 4/4
- Vendor Operations: ReleaseLock

#### Operations

| Operation | Status | Issues |
|-----------|--------|--------|
| GetCapabilities | ✅ compliant | - |
| DescribeFeatureType | ✅ compliant | - |
| GetFeature | ✅ compliant | 4 vendor param(s) |
| Transaction | ✅ compliant | - |
| LockFeature | ✅ compliant | - |
| GetFeatureWithLock | ✅ compliant | - |
| GetGmlObject | ✅ compliant | - |

#### Vendor Extension Parameters

| Operation | Parameter | Type | Description |
|-----------|-----------|------|-------------|
| GetFeature | `CQL_FILTER` | - | - |
| GetFeature | `FEATUREVERSION` | - | - |
| GetFeature | `VIEWPARAMS` | - | - |
| GetFeature | `FORMAT_OPTIONS` | - | - |

---

### Version 2.0.0

**Specification:** [OpenGIS Web Feature Service 2.0 Interface Standard](https://portal.ogc.org/files/?artifact_id=39967)

**Compliance Status:** ✅ Compliant

**Summary:**

- Required Operations: 6/6
- Optional Operations: 5/5
- Vendor Operations: ReleaseLock

#### Operations

| Operation | Status | Issues |
|-----------|--------|--------|
| GetCapabilities | ✅ compliant | - |
| DescribeFeatureType | ✅ compliant | - |
| GetFeature | ✅ compliant | 4 vendor param(s) |
| ListStoredQueries | ✅ compliant | - |
| DescribeStoredQueries | ✅ compliant | - |
| GetPropertyValue | ✅ compliant | - |
| Transaction | ✅ compliant | - |
| LockFeature | ✅ compliant | - |
| GetFeatureWithLock | ✅ compliant | - |
| CreateStoredQuery | ✅ compliant | - |
| DropStoredQuery | ✅ compliant | - |

#### Vendor Extension Parameters

| Operation | Parameter | Type | Description |
|-----------|-----------|------|-------------|
| GetFeature | `CQL_FILTER` | - | - |
| GetFeature | `FEATUREVERSION` | - | - |
| GetFeature | `VIEWPARAMS` | - | - |
| GetFeature | `FORMAT_OPTIONS` | - | - |

---

## WCS - Web Coverage Service

### Version 1.0.0

**Specification:** [Web Coverage Service (WCS) Implementation Specification, Version 1.0.0](https://portal.ogc.org/files/?artifact_id=3837)

**Compliance Status:** ✅ Compliant

**Summary:**

- Required Operations: 3/3
- Optional Operations: 0/0

#### Operations

| Operation | Status | Issues |
|-----------|--------|--------|
| GetCapabilities | ✅ compliant | 3 vendor param(s) |
| DescribeCoverage | ✅ compliant | - |
| GetCoverage | ✅ compliant | 1 vendor param(s) |

#### Vendor Extension Parameters

| Operation | Parameter | Type | Description |
|-----------|-----------|------|-------------|
| GetCapabilities | `VERSION` | - | - |
| GetCapabilities | `SECTIONS` | - | - |
| GetCapabilities | `UPDATESEQUENCE` | - | - |
| GetCoverage | `ELEVATION` | - | - |

---

### Version 1.1.0

**Specification:** [OGC WCS 1.1 Implementation Specification](https://portal.ogc.org/files/?artifact_id=25355)

**Compliance Status:** ✅ Compliant

**Summary:**

- Required Operations: 3/3
- Optional Operations: 0/0

#### Operations

| Operation | Status | Issues |
|-----------|--------|--------|
| GetCapabilities | ✅ compliant | 5 vendor param(s) |
| DescribeCoverage | ✅ compliant | 4 vendor param(s) |
| GetCoverage | ✅ compliant | 10 vendor param(s) |

#### Vendor Extension Parameters

| Operation | Parameter | Type | Description |
|-----------|-----------|------|-------------|
| GetCapabilities | `SERVICE` | - | - |
| GetCapabilities | `VERSION` | - | - |
| GetCapabilities | `REQUEST` | - | - |
| GetCapabilities | `SECTIONS` | - | - |
| GetCapabilities | `UPDATESEQUENCE` | - | - |
| DescribeCoverage | `SERVICE` | - | - |
| DescribeCoverage | `VERSION` | - | - |
| DescribeCoverage | `REQUEST` | - | - |
| DescribeCoverage | `IDENTIFIERS` | - | - |
| GetCoverage | `SERVICE` | - | - |
| GetCoverage | `VERSION` | - | - |
| GetCoverage | `REQUEST` | - | - |
| GetCoverage | `WIDTH` | - | - |
| GetCoverage | `HEIGHT` | - | - |
| GetCoverage | `RESX` | - | - |
| GetCoverage | `RESY` | - | - |
| GetCoverage | `INTERPOLATION` | - | - |
| GetCoverage | `TIME` | - | - |
| GetCoverage | `ELEVATION` | - | - |

---

### Version 2.0.0

**Specification:** [OGC WCS 2.0 Interface Standard - Core](https://portal.ogc.org/files/?artifact_id=41437)

**Compliance Status:** ✅ Compliant

**Summary:**

- Required Operations: 3/3
- Optional Operations: 0/0

#### Operations

| Operation | Status | Issues |
|-----------|--------|--------|
| GetCapabilities | ✅ compliant | 6 vendor param(s) |
| DescribeCoverage | ✅ compliant | 3 vendor param(s) |
| GetCoverage | ✅ compliant | 9 vendor param(s) |

#### Vendor Extension Parameters

| Operation | Parameter | Type | Description |
|-----------|-----------|------|-------------|
| GetCapabilities | `SERVICE` | - | - |
| GetCapabilities | `VERSION` | - | - |
| GetCapabilities | `REQUEST` | - | - |
| GetCapabilities | `ACCEPTVERSIONS` | - | - |
| GetCapabilities | `SECTIONS` | - | - |
| GetCapabilities | `UPDATESEQUENCE` | - | - |
| DescribeCoverage | `SERVICE` | - | - |
| DescribeCoverage | `VERSION` | - | - |
| DescribeCoverage | `REQUEST` | - | - |
| GetCoverage | `SERVICE` | - | - |
| GetCoverage | `VERSION` | - | - |
| GetCoverage | `REQUEST` | - | - |
| GetCoverage | `WIDTH` | - | - |
| GetCoverage | `HEIGHT` | - | - |
| GetCoverage | `RESX` | - | - |
| GetCoverage | `RESY` | - | - |
| GetCoverage | `TIME` | - | - |
| GetCoverage | `ELEVATION` | - | - |

---

## WMTS - WMTS

### Version 1.0.0

**Specification:** [N/A](https://portal.ogc.org/files/?artifact_id=35326)

**Compliance Status:** ✅ Compliant (with extensions)

#### Operations

| Operation | Status | Issues |
|-----------|--------|--------|
| GetCapabilities | ✅* COMPLIANT_WITH_EXTENSIONS | HTTP method extension |
| GetTile | ✅* COMPLIANT_WITH_EXTENSIONS | 2 vendor param(s) |
| GetFeatureInfo | ✅ FULLY_COMPLIANT | Optional operation fully implemented per specifica |

#### Vendor Extension Parameters

| Operation | Parameter | Type | Description |
|-----------|-----------|------|-------------|
| GetTile | `TIME` | string | Time dimension value |
| GetTile | `ELEVATION` | string | Elevation dimension value |

**Analysis:** GeoServer WMTS 1.0.0 is compliant with OGC specification with useful extensions for dimensional data (time, elevation) and enhanced protocol support (POST for GetCapabilities)

---

## CSW - CSW

### Version 2.0.2

**Specification:** [N/A](https://portal.ogc.org/files/?artifact_id=20555)

**Compliance Status:** ✅ Compliant (with extensions)

#### Operations

| Operation | Status | Issues |
|-----------|--------|--------|
| GetCapabilities | ✅* COMPLIANT_WITH_EXTENSIONS | Fully compliant with specification |
| DescribeRecord | ✅ FULLY_COMPLIANT | - |
| GetRecords | ✅* COMPLIANT_WITH_EXTENSIONS | 1 vendor param(s) |
| GetRecordById | ✅ FULLY_COMPLIANT | - |
| GetDomain | ✅ FULLY_COMPLIANT | Optional operation implemented |
| Transaction | ✅ FULLY_COMPLIANT | Optional operation implemented |
| Harvest | ✅* COMPLIANT_WITH_EXTENSIONS | 1 vendor param(s) |

#### Vendor Extension Parameters

| Operation | Parameter | Type | Description |
|-----------|-----------|------|-------------|
| GetRecords | `SORTBY` | string | Sort order |
| Harvest | `RESOURCEFORMAT` | string | Resource format |

**Analysis:** GeoServer CSW 2.0.2 is fully compliant with OGC specification, implementing all required operations and most optional operations with minor extensions for enhanced functionality

---

## WPS - WPS

### Version 1.0.0

**Specification:** [N/A](https://portal.ogc.org/files/?artifact_id=24151)

**Compliance Status:** ✅ Compliant (with extensions)

#### Operations

| Operation | Status | Issues |
|-----------|--------|--------|
| GetCapabilities | ✅* COMPLIANT_WITH_EXTENSIONS | Fully compliant with specification |
| DescribeProcess | ✅ FULLY_COMPLIANT | - |
| Execute | ✅ FULLY_COMPLIANT | - |
| GetExecutionStatus | 🔧 VENDOR_EXTENSION | GeoServer-specific operation for asynchronous exec |
| Dismiss | 🔧 VENDOR_EXTENSION | GeoServer-specific operation for resource cleanup  |

**Analysis:** GeoServer WPS 1.0.0 is fully compliant with OGC specification for all required operations. Includes two vendor extensions (GetExecutionStatus, Dismiss) that provide functionality similar to WPS 2.0 for better asynchronous execution management

---

## Vendor Extensions Summary

GeoServer implements various vendor-specific extensions to enhance OGC service functionality.

### WMS

**Vendor Extension Parameters:**
- `ANGLE`
- `BUFFER`
- `CLIP`
- `CQL_FILTER`
- `ENV`
- `EXCLUDE_NODATA_RESULT`
- `FEATUREID`
- `FEATUREVERSION`
- `FORMAT_OPTIONS`
- `INTERPOLATIONS`
- `LEGEND_OPTIONS`
- `MAXFEATURES`
- `PALETTE`
- `PROPERTYNAME`
- `REMOTE_OWS_TYPE`
- `REMOTE_OWS_URL`
- `SCALEMETHOD`
- `SORTBY`
- `STARTINDEX`
- `STRICT`
- `TILED`
- `TILESORIGIN`
- `VIEWPARAMS`

**Vendor Operations:**
- `kml`
- `reflect`

### WFS

**Vendor Extension Parameters:**
- `CQL_FILTER`
- `FEATUREVERSION`
- `FORMAT_OPTIONS`
- `VIEWPARAMS`

**Vendor Operations:**
- `ReleaseLock`

### WCS

**Vendor Extension Parameters:**
- `ACCEPTVERSIONS`
- `ELEVATION`
- `HEIGHT`
- `IDENTIFIERS`
- `INTERPOLATION`
- `REQUEST`
- `RESX`
- `RESY`
- `SECTIONS`
- `SERVICE`
- `TIME`
- `UPDATESEQUENCE`
- `VERSION`
- `WIDTH`

### WMTS

**Vendor Extension Parameters:**
- `ELEVATION`
- `TIME`

### CSW

**Vendor Extension Parameters:**
- `RESOURCEFORMAT`
- `SORTBY`

### WPS

**Vendor Operations:**
- `Dismiss`
- `GetExecutionStatus`

---

## Recommendations

1. **Documentation**: Ensure all vendor extensions are clearly documented in user-facing documentation
2. **Standards Compliance**: Continue maintaining strict compliance with OGC specifications
3. **Extension Justification**: Each vendor extension should have a clear use case and benefit
4. **Version Support**: Consider implementing newer OGC standard versions (e.g., WPS 2.0)
5. **Testing**: Maintain CITE test suite compliance for all certified services
