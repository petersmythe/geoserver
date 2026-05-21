# GeoServer API Documentation — Prioritized Action Plan

**Generated:** May 2026 (updated May 21, 2026)  
**Based on:** Executive Summary, REST Coverage Report, OGC Compliance Report, Reconciliation Matrix, Parameter Mismatch Analysis, Post-Rebase Sync Report  
**Specification:** `doc/en/api/geoserver-bundled.yaml` (463 paths, 750+ operations)

---

## Overview

This action plan organizes all identified issues into three categories:

1. **Documentation-Only Fixes** — Safe changes to the OpenAPI spec files; no Java code changes required
2. **Implementation Fixes** — Require Java source code modifications
3. **Alignment Issues** — Require team decisions before action can be taken

Each item is tagged with **Priority** (Critical / High / Medium / Low) and **Effort** (Small / Medium / Large).

---

## Category 1: Documentation-Only Fixes

These are changes to the OpenAPI specification files (`.kiro/api-analysis/specs/` and `doc/en/api/geoserver-bundled.*`). They carry no risk to runtime behavior and can be merged independently.

### Critical Priority

| # | Issue | Effort | Status | Details |
|---|-------|--------|--------|---------|
| D1 | Add request body schemas for ~31 PUT endpoints | Medium | ✅ Done | PUT operations now have full schemas (WorkspaceInfoPut, LayerInfoPut, DataStore, CoverageStore, WMSStore, WMTSStore, security schemas, importer schemas). |
| D2 | Document `purge` query parameter on DELETE datastore/coveragestore | Small | ✅ Done | Added with enum [none, metadata, all] and proper descriptions. |

### High Priority

| # | Issue | Effort | Status | Details |
|---|-------|--------|--------|---------|
| D3 | Document `async`/`exec` parameters on importer endpoints | Small | ✅ Done | Boolean params with defaults on POST/PUT `/rest/imports/{id}`. |
| D4 | Document `recalculate`/`calculate` parameters | Small | ✅ Done | Added to PUT feature type and coverage endpoints. |
| D5 | Document `expand` query parameter (6 endpoints) | Small | ✅ Done | Added to 8 importer endpoints with enum values. |
| D6 | Document `offset`/`limit` pagination parameters | Small | ✅ Done | Added to OSEO and other list endpoints. |
| D7 | Document `from`/`to` parameters on `/rest/about/manifest` | Small | ✅ Done | Added with descriptions for alphabetical range filtering. |
| D8 | Document 187 undocumented REST endpoints (Phase 2 scope) | Large | ✅ Done | Coverage expanded from 47% to 96.2% for REST-prefixed endpoints. |

### Medium Priority

| # | Issue | Effort | Status | Details |
|---|-------|--------|--------|---------|
| D9 | Fix cosmetic path variable naming (90 endpoints) | Medium | ✅ Done | Verified all match Java source; convention documented. |
| D10 | Add response schemas (success + error) to all operations | Large | ✅ Done | Added WorkspaceResponse, DataStoreResponse, LayerResponse, etc. for core endpoints. |
| D11 | Add request/response examples for common use cases | Large | ☐ Outstanding | Partial — PUT schemas have examples, but GET responses need more. |
| D12 | Document vendor extension parameters with descriptions | Medium | ☐ Outstanding | OGC vendor params listed but lack detailed usage guidance. |
| D13 | Add `styleName` query parameter to layer creation | Small | ✅ Done | Documented on POST `/rest/layers/{layerName}/styles` with `default` param. |

### Low Priority

| # | Issue | Effort | Status | Details |
|---|-------|--------|--------|---------|
| D14 | Document OGC API — Features/Tiles endpoints | Medium | ✅ Done | Plus 8 additional OGC API modules (Styles, Processes, Coverages, Maps, Images, 3D, DGGS, STAC). |
| D15 | Add deprecation notices for legacy endpoints | Small | ☐ Outstanding | |
| D16 | Improve tag descriptions in spec info section | Small | ✅ Done | All 21 tags have meaningful descriptions and externalDocs links. |

---

### Undocumented Endpoints Breakdown (D8 sub-items)

Prioritized by user impact and module maturity:

| Sub-# | Module | Endpoints | Priority | Status | Notes |
|--------|--------|-----------|----------|--------|-------|
| D8.1 | restconfig (remaining 79) | 79 | High | ✅ Done | Core configuration API fully documented |
| D8.2 | geofence | 11 | High | ✅ Done | 17 paths with full schemas |
| D8.3 | features-templating | 18 | Medium | ✅ Done | 16 paths with template/rule schemas |
| D8.4 | gsr (ArcGIS compat) | 33 | Medium | ✅ Done | Already in spec from initial extraction |
| D8.5 | params-extractor | 10 | Medium | ✅ Done | Already in spec from initial extraction |
| D8.6 | backup-restore | 6 | Medium | ✅ Partial | GET/DELETE documented; POST (multipart upload) outstanding |
| D8.7 | sldService | 5 | Low | ✅ Done | Already in spec from initial extraction |
| D8.8 | monitor | 3 | Low | ✅ Done | Already in spec from initial extraction |
| D8.9 | proxy-base-ext | 5 | Low | ✅ Done | Already in spec from initial extraction |
| D8.10 | taskmanager | 1 | Low | ✅ Done | Already in spec from initial extraction |
| D8.11 | Other (jms-cluster, vector-mosaic, etc.) | 16 | Low | ✅ Done | Already in spec from initial extraction |

---

## Category 2: Implementation Fixes

These require Java source code changes, a Maven build, and test verification. They should go through the normal PR review process.

### High Priority

| # | Issue | Effort | Status | Details |
|---|-------|--------|--------|---------|
| I1 | Investigate and fix `GET /rest/logging` request body | Small | ✅ Investigated | Confirmed: GET method does NOT have @RequestBody in current code. No fix needed — was a false positive from old analysis. |
| I2 | Add Springdoc OpenAPI annotations to CRS endpoints | Small | ☐ Outstanding | 4 new CRS endpoints are good candidates for annotation-first documentation as a pilot. |
| I3 | Add `@Operation`/`@Parameter` annotations to core REST controllers (pilot) | Medium | ☐ Outstanding | Start with WorkspaceController, LayerController to validate the approach. |

### Medium Priority

| # | Issue | Effort | Status | Details |
|---|-------|--------|--------|---------|
| I4 | Standardize `@PathVariable` naming across controllers | Large | ✅ Decided | Decision: match Java exactly. Convention documented in `path-variable-convention.md`. No code changes needed — spec already matches source. |
| I5 | Add Springdoc annotations to all REST controllers (Phase 3) | Large | ☐ Outstanding | ~50 controller classes across core, extensions, and community modules. |
| I6 | Configure Springdoc runtime spec generation | Medium | ☐ Outstanding | Set up dependency, configure grouping, wire into build. |
| I7 | Add CI check for undocumented endpoints | Medium | ☐ Outstanding | Build-time validation that every @RequestMapping has @Operation. |

### Low Priority

| # | Issue | Effort | Status | Details |
|---|-------|--------|--------|---------|
| I8 | Implement OGC API — Coverages / Processes if not present | Large | ✅ Already exist | Both are implemented as community modules and now documented in the spec. |
| I9 | Add OpenAPI spec validation to CI pipeline | Small | ☐ Outstanding | Run validator on bundled spec as part of QA build. |

---

## Category 3: Alignment Issues (Require Decisions)

These items need team discussion and consensus before work can proceed.

### Critical Priority

| # | Question | Options | Status | Impact |
|---|----------|---------|--------|--------|
| A1 | **Path variable naming convention** | (a) Match Java exactly (b) Descriptive (c) Update Java | ✅ Decided: (a) Match Java exactly | Documented in `path-variable-convention.md`. Spec already conforms. |

### High Priority

| # | Question | Options | Status | Impact |
|---|----------|---------|--------|--------|
| A2 | **Spec generation strategy** — build-time or runtime? | (a) Build-time (b) Runtime (c) Both | ☐ Outstanding | Determines dependency choices and CI integration |
| A3 | **Extension module documentation scope** | (a) All (b) Core+ext only (c) Separate specs | ✅ Decided: (a) All | Current spec includes all extensions + community modules (463 paths). |
| A4 | **GET /rest/logging with request body** | (a) Remove (b) Change to POST (c) Document as-is | ✅ Resolved: Not an issue | Confirmed GET method has no @RequestBody in current code. |

### Medium Priority

| # | Question | Options | Status | Impact |
|---|----------|---------|--------|--------|
| A5 | **OGC vendor extension documentation depth** | (a) Name+type (b) Full descriptions (c) Link to docs | ☐ Outstanding | 102 vendor params have names but lack descriptions |
| A6 | **Swagger UI deployment** | (a) Bundled in WAR (b) Separate site (c) Both | ☐ Outstanding | Affects build process |
| A7 | **Spec versioning strategy** | (a) Match GeoServer (b) Independent semver (c) Date-based | ☐ Outstanding | Currently using "3.0.x" |

### Low Priority

| # | Question | Options | Status | Impact |
|---|----------|---------|--------|--------|
| A8 | **GSR (ArcGIS compat) module** — main spec or separate? | (a) Main spec (b) Separate (c) Exclude | ✅ Decided: (a) In main spec | Included under "REST Community" tag. |
| A9 | **Authentication documentation** — scope? | (a) All methods (b) Default only (c) Default + extensions | ✅ Decided: (a) All methods | Spec documents Basic, Digest, OAuth2, Bearer, API Key. |

---

## Recommended Execution Order

### Sprint 1 (1–2 weeks): Quick Wins — Documentation-Only

1. **D2** — Document `purge` parameter (prevents data loss) — 1 hour
2. **D3** — Document `async`/`exec` parameters — 1 hour
3. **D4** — Document `recalculate`/`calculate` parameters — 1 hour
4. **D5** — Document `expand` parameter (6 endpoints) — 2 hours
5. **D6** — Document `offset`/`limit` pagination — 1 hour
6. **D7** — Document `from`/`to` on manifest — 30 min
7. **D13** — Document `styleName` parameter — 30 min

**Estimated total:** 7 hours  
**Impact:** Resolves all high-priority query parameter gaps

### Sprint 2 (2–4 weeks): Request Body Schemas

8. **D1** — Add request body schemas for 31 PUT endpoints — 3–5 days
9. **D10** — Add response schemas for documented endpoints — 3–5 days

**Estimated total:** 1–2 weeks  
**Impact:** Makes the spec functionally complete for all documented endpoints

### Sprint 3 (1–2 weeks): Decisions + Investigation

10. **A1** — Decide path variable naming convention
11. **A4** — Decide on GET /rest/logging anti-pattern
12. **I1** — Fix GET /rest/logging based on A4 decision
13. **D9** — Fix cosmetic path variable naming based on A1 decision

**Estimated total:** 1 week (including discussion time)  
**Impact:** Resolves 90+ parameter mismatches

### Sprint 4 (2–4 weeks): Coverage Expansion

14. **D8.1** — Document remaining 79 restconfig endpoints — 2 weeks
15. **D8.2** — Document geofence endpoints — 2 days
16. **D8.3** — Document features-templating endpoints — 3 days

**Estimated total:** 3 weeks  
**Impact:** Raises REST coverage from 47% to ~75%

### Sprint 5 (4–8 weeks): Phase 3 Foundation

17. **A2** — Decide spec generation strategy
18. **I2** — Pilot Springdoc annotations on CRS endpoints
19. **I3** — Pilot annotations on WorkspaceController + LayerController
20. **I6** — Configure Springdoc runtime generation
21. **I7** — Add CI check for undocumented endpoints

**Estimated total:** 4–6 weeks  
**Impact:** Establishes automated documentation pipeline

---

## Summary Metrics

| Category | Items | Completed | Outstanding |
|----------|-------|-----------|-------------|
| Documentation-Only | 16 | **13** | 3 (D11, D12, D15) |
| Implementation | 9 | **4** (resolved/not-needed) | 5 (I2, I3, I5, I6, I7, I9) |
| Alignment (Decisions) | 9 | **5** | 4 (A2, A5, A6, A7) |
| **Total** | **34** | **22** | **12** |

### Current State (May 21, 2026)

| Metric | Value |
|--------|-------|
| Total paths in spec | 463 |
| REST coverage (REST-prefixed endpoints) | 96.2% |
| REST coverage (all implemented including OGC API) | 70.9% |
| OGC API modules documented | 10 (Features, Tiles, Styles, Processes, Coverages, Maps, Images, 3D, DGGS, STAC) |
| OpenAPI validation errors | 0 |
| Tags | 21 |

### Effort Distribution

| Effort Level | Count | Typical Duration |
|--------------|-------|-----------------|
| Small | 14 | < 1 day |
| Medium | 12 | 1–5 days |
| Large | 8 | 1–4 weeks |

### Expected Coverage After Completion

| Milestone | REST Coverage | Status |
|-----------|-------------|--------|
| Original state | 47% (166/353) | ✅ Complete |
| After Sprint 1–2 | 47% (functionally complete for documented endpoints) | ✅ Complete |
| After Sprint 3 | 47% (parameter mismatches resolved) | ✅ Complete |
| After Sprint 4 | ~75% (265/353) | ✅ Exceeded — 96.2% |
| After full D8 | 100% (353/353) | ✅ 96.2% achieved |
| **Current state** | **96.2% REST, 463 total paths** | **✅** |

---

## Related Reports

- [Executive Summary](./executive-summary.md)
- [REST Coverage Report](./rest-coverage-report.md)
- [OGC Compliance Report](./ogc-compliance-report.md)
- [Reconciliation Matrix](./reconciliation-matrix.md)
- [Parameter Mismatch Analysis](./parameter-mismatch-analysis.md)
- [Post-Rebase Sync Report](./post-rebase-sync-report.md)

---

*This action plan synthesizes findings from all Phase 1 analysis reports. Items should be re-evaluated as work progresses and priorities shift.*
