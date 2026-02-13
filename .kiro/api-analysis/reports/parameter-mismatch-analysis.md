# Parameter Mismatch Analysis

**Generated:** 2026-02-12  
**Total Mismatches:** 129 endpoints

## Executive Summary

After fixing the path prefix issue, 166 endpoints matched by path and HTTP method. However, 129 of these (77.7%) have parameter mismatches. This analysis identifies the root causes and provides actionable recommendations.

## Mismatch Categories

### 1. Path Variable Name Differences (170 issues across 107 endpoints)

**The Problem:** Implementation and documentation use different names for the same path variable.

**Most Common Pattern:**
- **Implementation:** Uses generic names like `{id}`, `{taskId}`, `{layerGroupName}`
- **Documentation:** Uses descriptive names like `{importId}`, `{task}`, `{layergroupName}` (note: different casing!)

**Examples:**

| Endpoint | Implementation | Documentation | Issue |
|----------|----------------|---------------|-------|
| `/rest/imports/{id}` | `{id}` | `{importId}` | Different name |
| `/rest/layergroups/{layerGroupName}` | `{layerGroupName}` | `{layergroupName}` | Different casing |
| `/rest/about/status` | `{target}` | (missing) | Not documented |

**Impact:** 107 endpoints (82.9% of mismatches)

**Root Cause:** 
- Java code uses `@PathVariable("id")` 
- OpenAPI docs use `{importId}` for clarity
- Our normalization converts both to `{var}` for matching, but parameter comparison still sees the difference

### 2. Request Body Mismatches (32 issues)

**The Problem:** One side expects a request body, the other doesn't.

**Breakdown:**
- **Implementation has body, docs don't:** 31 cases (96.9%)
- **Docs have body, implementation doesn't:** 1 case (3.1%)

**Examples:**

| Endpoint | Method | Issue |
|----------|--------|-------|
| `/rest/imports/{id}/tasks/{taskId}/layer` | PUT | Impl has body, docs missing |
| `/rest/imports/{id}/tasks/{taskId}/target` | PUT | Impl has body, docs missing |
| `/rest/logging` | GET | Impl has body (unusual!), docs missing |

**Impact:** 32 endpoints (24.8% of mismatches)

**Root Cause:**
- Documentation may be outdated
- GET with request body is unusual (REST anti-pattern)
- PUT endpoints often updated to accept bodies

### 3. Query Parameter Differences (27 issues)

**The Problem:** Implementation and documentation have different query parameters.

**Breakdown:**
- **Implementation has params, docs don't:** 15 cases (55.6%)
- **Docs have params, implementation doesn't:** 12 cases (44.4%)

**Most Common Missing Parameters (in implementation but not docs):**
1. `expand` - 6 endpoints (likely for resource expansion)
2. `from`, `to` - 2 endpoints each (filtering/versioning)
3. `exec`, `async` - 2 endpoints each (execution control)
4. `styleName`, `offset`, `limit`, `recalculate`, `calculate`, `purge` - 1 each

**Examples:**

| Endpoint | Method | Missing Params | Where |
|----------|--------|----------------|-------|
| `/rest/about/manifest` | GET | `from`, `to` | In impl, not docs |
| `/rest/imports` | GET | `expand` | In impl, not docs |
| `/rest/about/status` | GET | `manifest`, `key`, `value` | In docs, not impl |

**Impact:** 27 endpoints (20.9% of mismatches)

**Root Cause:**
- Features added without updating docs
- Documentation includes planned features not yet implemented
- Optional parameters not consistently documented

## Mismatches by Module

| Module | Mismatches | % of Total |
|--------|------------|------------|
| **restconfig** | 93 | 72.1% |
| **extension/importer** | 16 | 12.4% |
| **community/oseo** | 10 | 7.8% |
| **extension/mongodb** | 4 | 3.1% |
| **other** | 4 | 3.1% |
| **extension/rat** | 1 | 0.8% |
| **extension/wps-download** | 1 | 0.8% |

**Analysis:** 
- Core `restconfig` module has the most mismatches (93) but also the most documented endpoints
- This is actually a positive sign - the module IS documented, just needs parameter alignment

## Root Cause Analysis

### Why So Many Path Variable Mismatches?

The path variable mismatches are largely **cosmetic** and don't affect functionality:

1. **Normalization works correctly** - Both `{id}` and `{importId}` normalize to `{var}` for matching
2. **Runtime behavior identical** - Spring MVC binds the path segment regardless of parameter name
3. **Documentation clarity** - Docs use descriptive names for better UX

**Verdict:** These are **low-priority** issues. The endpoints work correctly; it's just a naming convention difference.

### Why Request Body Mismatches?

1. **Documentation lag** - Implementation evolved, docs didn't keep up
2. **Unusual patterns** - GET with request body (anti-pattern, should be fixed)
3. **Optional bodies** - Some endpoints accept optional bodies not documented

**Verdict:** These are **medium-priority** issues requiring manual review.

### Why Query Parameter Mismatches?

1. **Feature additions** - New optional parameters added without doc updates
2. **Incomplete extraction** - Our parser may miss some Spring `@RequestParam` annotations
3. **Documentation drift** - Planned features documented but not implemented

**Verdict:** These are **high-priority** issues affecting API usability.

## Recommendations

### Immediate Actions (High Priority)

1. **Document Missing Query Parameters**
   - Focus on `expand` parameter (6 endpoints)
   - Document `from`/`to` filtering parameters (2 endpoints)
   - Add `exec`/`async` execution control parameters (2 endpoints)
   - **Effort:** 2-3 hours
   - **Impact:** Improves API usability significantly

2. **Review Request Body Mismatches**
   - Investigate GET `/rest/logging` with request body (anti-pattern)
   - Verify PUT endpoints that should accept bodies
   - Update documentation for 31 endpoints
   - **Effort:** 4-6 hours
   - **Impact:** Prevents API misuse

### Medium-Term Actions

3. **Standardize Path Variable Names**
   - Decision needed: Use generic (`{id}`) or descriptive (`{importId}`) names?
   - Update either code or docs for consistency
   - **Effort:** 8-10 hours (107 endpoints)
   - **Impact:** Improves documentation clarity

4. **Improve Parameter Extraction**
   - Enhance parser to detect all `@RequestParam` annotations
   - Handle optional parameters correctly
   - **Effort:** 4-6 hours
   - **Impact:** More accurate analysis

### Long-Term Actions

5. **Automated Documentation Generation**
   - Use Springdoc/Swagger annotations in code
   - Generate OpenAPI specs from annotations
   - **Effort:** 20-30 hours (one-time setup)
   - **Impact:** Eliminates drift permanently

6. **CI/CD Validation**
   - Add checks for parameter mismatches
   - Fail builds if docs don't match implementation
   - **Effort:** 4-6 hours
   - **Impact:** Prevents future drift

## Priority Matrix

| Issue Type | Count | Priority | Effort | Impact |
|------------|-------|----------|--------|--------|
| Query param mismatches | 27 | HIGH | Low | High |
| Request body mismatches | 32 | MEDIUM | Medium | High |
| Path variable names | 170 | LOW | High | Low |

## Conclusion

The 129 parameter mismatches break down into three categories:

1. **Path variable naming (170 issues)** - Cosmetic, low priority
2. **Request body differences (32 issues)** - Functional, medium priority
3. **Query parameter gaps (27 issues)** - Usability, high priority

**Recommended Approach:**
1. Start with query parameters (high impact, low effort)
2. Review and fix request body mismatches (prevents API misuse)
3. Defer path variable standardization (low impact, high effort)

With focused effort on query parameters and request bodies, we can resolve the most impactful issues affecting ~60 endpoints in approximately 6-12 hours of work.

## Data Files

- **Detailed Analysis:** `.kiro/api-analysis/reports/mismatch-analysis.json`
- **All Matches:** `.kiro/api-analysis/rest/endpoint-matches.json`
- **Analysis Script:** `.kiro/api-analysis/analyze-mismatches.py`
