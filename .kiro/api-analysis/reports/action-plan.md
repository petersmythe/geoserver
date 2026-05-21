# GeoServer API Documentation — Prioritized Action Plan

**Generated:** May 2026  
**Based on:** Executive Summary, REST Coverage Report, OGC Compliance Report, Reconciliation Matrix, Parameter Mismatch Analysis, Post-Rebase Sync Report  
**Specification:** `doc/en/api/geoserver-bundled.yaml` (312 paths, 515+ operations)

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

| # | Issue | Effort | Details |
|---|-------|--------|---------|
| D1 | Add request body schemas for ~31 PUT endpoints | Medium | PUT operations (layers, namespaces, datastores, security configs) accept JSON/XML bodies but the spec has no schema. Clients cannot construct valid requests. Extract from Java model classes (LayerInfo, StoreInfo, NamespaceInfo, etc.). |
| D2 | Document `purge` query parameter on DELETE datastore/coveragestore | Small | Missing parameter that controls whether data files are deleted or only configuration. Omission risks accidental data loss for API consumers. |

### High Priority

| # | Issue | Effort | Details |
|---|-------|--------|---------|
| D3 | Document `async`/`exec` parameters on importer endpoints | Small | Controls synchronous vs asynchronous import execution. 2 endpoints affected. |
| D4 | Document `recalculate`/`calculate` parameters | Small | Affects spatial metadata accuracy on coverage/featuretype creation. |
| D5 | Document `expand` query parameter (6 endpoints) | Small | Controls response detail level (e.g., inline sub-resources vs links). Affects `/rest/imports`, `/rest/workspaces/{ws}/datastores/{ds}`, etc. |
| D6 | Document `offset`/`limit` pagination parameters | Small | Pagination for large result sets on list endpoints. |
| D7 | Document `from`/`to` parameters on `/rest/about/manifest` | Small | Filtering manifest entries by version range. |
| D8 | Document 187 undocumented REST endpoints (Phase 2 scope) | Large | 187 implemented endpoints have no spec entry at all. Priority sub-groups below. |

### Medium Priority

| # | Issue | Effort | Details |
|---|-------|--------|---------|
| D9 | Fix cosmetic path variable naming (90 endpoints) | Medium | Spec uses `{importId}` where Java uses `{id}`, `{layergroupName}` vs `{layerGroupName}`, etc. Functionally correct but breaks code-generation tools. |
| D10 | Add response schemas (success + error) to all operations | Large | Most operations document only status codes, not response body structure. |
| D11 | Add request/response examples for common use cases | Large | Improves developer experience; required for "Try it out" in Swagger UI. |
| D12 | Document vendor extension parameters with descriptions | Medium | 102 OGC vendor parameters are listed but lack descriptions and usage guidance. |
| D13 | Add `styleName` query parameter to layer creation | Small | Convenience parameter for associating a default style during layer creation. |

### Low Priority

| # | Issue | Effort | Details |
|---|-------|--------|---------|
| D14 | Document OGC API — Features/Tiles endpoints | Medium | Modern OGC API standards implemented in `src/extension/ogcapi/` and `src/community/ogcapi/` but not yet in the spec. |
| D15 | Add deprecation notices for legacy endpoints | Small | Mark Swagger 2.0-era endpoints that have been superseded. |
| D16 | Improve tag descriptions in spec info section | Small | Some tags lack meaningful descriptions. |

---

### Undocumented Endpoints Breakdown (D8 sub-items)

Prioritized by user impact and module maturity:

| Sub-# | Module | Endpoints | Priority | Notes |
|--------|--------|-----------|----------|-------|
| D8.1 | restconfig (remaining 79) | 79 | High | Core configuration API — most commonly used |
| D8.2 | geofence | 11 | High | Advanced authorization — critical for enterprise users |
| D8.3 | features-templating | 18 | Medium | Output customization — growing adoption |
| D8.4 | gsr (ArcGIS compat) | 33 | Medium | ArcGIS REST compatibility layer |
| D8.5 | params-extractor | 10 | Medium | URL parameter extraction rules |
| D8.6 | backup-restore | 6 | Medium | Configuration backup/restore |
| D8.7 | sldService | 5 | Low | SLD generation utilities |
| D8.8 | monitor | 3 | Low | Request monitoring (community) |
| D8.9 | proxy-base-ext | 5 | Low | Proxy base URL rules |
| D8.10 | taskmanager | 1 | Low | Task scheduling |
| D8.11 | Other (jms-cluster, vector-mosaic, etc.) | 16 | Low | Specialized/niche modules |

---

## Category 2: Implementation Fixes

These require Java source code changes, a Maven build, and test verification. They should go through the normal PR review process.

### High Priority

| # | Issue | Effort | Details |
|---|-------|--------|---------|
| I1 | Investigate and fix `GET /rest/logging` request body | Small | GET with request body is a REST anti-pattern. Determine if the body is actually used; if not, remove `@RequestBody` annotation. If it is used, consider changing to POST or moving to query params. |
| I2 | Add Springdoc OpenAPI annotations to CRS endpoints | Small | 4 new CRS endpoints (added post-rebase) are good candidates for annotation-first documentation as a pilot. |
| I3 | Add `@Operation`/`@Parameter` annotations to core REST controllers (pilot) | Medium | Start with a small set of controllers (e.g., WorkspaceController, LayerController) to validate the annotation approach before full rollout. |

### Medium Priority

| # | Issue | Effort | Details |
|---|-------|--------|---------|
| I4 | Standardize `@PathVariable` naming across controllers | Large | Some controllers use `@PathVariable("id")` while others use `@PathVariable("importId")`. Standardize to descriptive names for consistency with generated specs. Requires careful backward-compat analysis. |
| I5 | Add Springdoc annotations to all REST controllers (Phase 3) | Large | Full annotation coverage for auto-generated spec. ~50 controller classes across core, extensions, and community modules. |
| I6 | Configure Springdoc runtime spec generation | Medium | Set up `springdoc-openapi` dependency, configure grouping by tag, and wire into the build so the spec is generated at build time or available at `/v3/api-docs`. |
| I7 | Add CI check for undocumented endpoints | Medium | Build-time validation that every `@RequestMapping` method has a corresponding `@Operation` annotation. Fail the build if coverage drops. |

### Low Priority

| # | Issue | Effort | Details |
|---|-------|--------|---------|
| I8 | Implement OGC API — Coverages / Processes if not present | Large | Newer OGC API standards that may be expected by users. Requires new module development. |
| I9 | Add OpenAPI spec validation to CI pipeline | Small | Run `swagger-cli validate` or equivalent on the bundled spec as part of the QA build. |

---

## Category 3: Alignment Issues (Require Decisions)

These items need team discussion and consensus before work can proceed.

### Critical Priority

| # | Question | Options | Impact |
|---|----------|---------|--------|
| A1 | **Path variable naming convention** — Should the spec use generic names (`{id}`) matching Java code, or descriptive names (`{importId}`) for clarity? | (a) Match Java exactly — best for code-gen tools<br>(b) Use descriptive names — best for human readers<br>(c) Update Java to use descriptive names — best long-term but high effort | Affects 90+ endpoints and all future development |

### High Priority

| # | Question | Options | Impact |
|---|----------|---------|--------|
| A2 | **Spec generation strategy** — Should Phase 3 use build-time generation (Maven plugin) or runtime generation (Springdoc endpoint)? | (a) Build-time — spec is a build artifact, no runtime overhead<br>(b) Runtime — always current, supports "Try it out"<br>(c) Both — build-time for distribution, runtime for dev | Determines dependency choices and CI integration |
| A3 | **Extension module documentation scope** — Which extension/community modules should be included in the official spec? | (a) All extensions + graduated community modules<br>(b) Only core + extensions (exclude community)<br>(c) Separate specs per module group | Affects spec size (currently 312 paths; could grow to 500+) |
| A4 | **GET /rest/logging with request body** — Is this intentional or a bug? | (a) Remove request body (fix the anti-pattern)<br>(b) Change to POST (breaking change)<br>(c) Document as-is with a warning | Affects API contract and backward compatibility |

### Medium Priority

| # | Question | Options | Impact |
|---|----------|---------|--------|
| A5 | **OGC vendor extension documentation depth** — How much detail should vendor parameters get? | (a) Name + type only (current state)<br>(b) Full descriptions + examples + use cases<br>(c) Link to external docs page | Affects spec size and maintenance burden |
| A6 | **Swagger UI deployment** — Where should interactive docs be hosted? | (a) Bundled with GeoServer WAR (available at `/api-docs`)<br>(b) Separate static site (docs.geoserver.org)<br>(c) Both | Affects build process and deployment |
| A7 | **Spec versioning strategy** — How to version the OpenAPI spec relative to GeoServer releases? | (a) Match GeoServer version (e.g., 2.26.0)<br>(b) Independent semver (e.g., 1.0.0, 1.1.0)<br>(c) Date-based (e.g., 2026.05) | Affects release process and consumer expectations |

### Low Priority

| # | Question | Options | Impact |
|---|----------|---------|--------|
| A8 | **GSR (ArcGIS compat) module** — Should these 33 endpoints be in the main spec or a separate document? | (a) Include in main spec under "ArcGIS Compatibility" tag<br>(b) Separate spec file<br>(c) Exclude entirely (community module) | Affects spec organization |
| A9 | **Authentication documentation** — Should the spec document all auth methods or only the defaults? | (a) All methods (Basic, Digest, OAuth2, SAML, JWT, API Key)<br>(b) Only default (Basic + Digest)<br>(c) Default + extension auth methods | Affects security section complexity |

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

| Category | Items | Critical | High | Medium | Low |
|----------|-------|----------|------|--------|-----|
| Documentation-Only | 16 | 2 | 5 | 5 | 4 |
| Implementation | 9 | 0 | 3 | 4 | 2 |
| Alignment (Decisions) | 9 | 1 | 3 | 3 | 2 |
| **Total** | **34** | **3** | **11** | **12** | **8** |

### Effort Distribution

| Effort Level | Count | Typical Duration |
|--------------|-------|-----------------|
| Small | 14 | < 1 day |
| Medium | 12 | 1–5 days |
| Large | 8 | 1–4 weeks |

### Expected Coverage After Completion

| Milestone | REST Coverage | Timeline |
|-----------|-------------|----------|
| Current state | 47% (166/353) | — |
| After Sprint 1–2 | 47% (functionally complete for documented endpoints) | 4 weeks |
| After Sprint 3 | 47% (parameter mismatches resolved) | 6 weeks |
| After Sprint 4 | ~75% (265/353) | 10 weeks |
| After full D8 | 100% (353/353) | 6 months |

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
