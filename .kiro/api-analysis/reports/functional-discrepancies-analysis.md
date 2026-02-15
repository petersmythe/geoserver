# Functional Discrepancies Analysis

**Beyond Cosmetic Issues:** This document analyzes the actual functional differences between implementation and documentation, excluding cosmetic path variable naming.

---

## Summary of Functional Discrepancies

| Category | Count | Severity | Impact |
|----------|-------|----------|--------|
| **Missing Query Parameters** | ~15 unique params | Medium | Clients can't use documented features |
| **Missing Request Bodies** | ~31 endpoints | High | PUT operations undocumented |
| **Extra Query Parameters in Docs** | ~12 endpoints | Low | Docs show non-existent features |
| **GET with Request Body** | 1 endpoint | Medium | REST anti-pattern |

---

## 1. Missing Query Parameters (Medium Severity)

**Impact:** Implementation supports parameters that aren't documented. Clients won't know these features exist.

### 1.1 `expand` Parameter (6 endpoints)

**Endpoints:**
- `GET /rest/imports`
- `GET /rest/imports/{id}/tasks`
- `GET /rest/imports/{id}/tasks/{taskId}`
- `GET /rest/imports/{id}/tasks/{taskId}/layer`
- `GET /rest/imports/{id}/tasks/{taskId}/target`

**Implementation:**
```java
@GetMapping
public ImportWrapper getImports(@RequestParam(required = false) String expand) {
    // Controls level of detail in response
}
```

**What it does:** Controls whether related objects are expanded inline or returned as references.

**Severity:** Medium - This is a useful feature for reducing API calls, but clients can work without it.

**Example:**
```bash
# Without expand - returns references
GET /rest/imports/123
{"import": {"id": 123, "tasks": "/rest/imports/123/tasks"}}

# With expand - returns full objects
GET /rest/imports/123?expand=tasks
{"import": {"id": 123, "tasks": [{"id": 1, "state": "COMPLETE"}]}}
```

---

### 1.2 `async` and `exec` Parameters (2 endpoints)

**Endpoints:**
- `GET /rest/imports/{id}` 
- `PUT /rest/imports/{id}`

**Implementation:**
```java
@PostMapping(value = {"/{id}", ""})
public ResponseEntity<Object> postImports(
    @PathVariable(required = false) Long id,
    @RequestParam(name = "async", required = false, defaultValue = "false") boolean async,
    @RequestParam(name = "exec", required = false, defaultValue = "false") boolean exec,
    @RequestBody(required = false) ImportContext obj
) {
    // Controls execution mode
}
```

**What it does:**
- `async`: Run import asynchronously (return immediately, process in background)
- `exec`: Execute the import immediately after creation

**Severity:** Medium-High - These control critical behavior (sync vs async execution).

**Example:**
```bash
# Synchronous import (blocks until complete)
POST /rest/imports/123?exec=true

# Asynchronous import (returns immediately)
POST /rest/imports/123?async=true&exec=true
```

---

### 1.3 `from` and `to` Parameters (2 endpoints)

**Endpoints:**
- `GET /rest/about/manifest`
- `GET /rest/about/version`

**Implementation:**
```java
@GetMapping("/manifest")
public RestWrapper<AboutModel> manifestGet(
    @RequestParam(required = false) String manifest,
    @RequestParam(required = false) String from,
    @RequestParam(required = false) String to,
    @RequestParam(required = false) String key,
    @RequestParam(required = false) String value
) {
    // Filters manifests by version range
}
```

**What it does:** Filters JAR manifests by version range.

**Severity:** Low - Niche feature for version filtering.

**Example:**
```bash
# Get manifests for versions between 2.20 and 2.25
GET /rest/about/manifest?from=2.20&to=2.25
```

---

### 1.4 `offset` and `limit` Parameters (1 endpoint)

**Endpoint:** `GET /rest/oseo/collections`

**What it does:** Pagination for OpenSearch Earth Observation collections.

**Severity:** Medium - Pagination is important for large datasets.

---

### 1.5 `recalculate` and `calculate` Parameters (2 endpoints)

**Endpoints:**
- Feature type operations
- Layer operations

**What it does:** Controls whether bounding boxes are recalculated from data.

**Severity:** Medium - Affects performance and accuracy of spatial metadata.

---

### 1.6 `purge` Parameter (1 endpoint)

**Endpoint:** `DELETE /rest/workspaces/{workspace}/datastores/{datastore}`

**What it does:** Controls whether to delete the underlying data files or just the configuration.

**Severity:** High - This is a destructive operation flag that prevents data loss.

**Example:**
```bash
# Delete configuration only (data files remain)
DELETE /rest/workspaces/myws/datastores/mystore

# Delete configuration AND data files
DELETE /rest/workspaces/myws/datastores/mystore?purge=true
```

---

### 1.7 `styleName` Parameter (1 endpoint)

**Endpoint:** `POST /rest/layers`

**What it does:** Specifies default style when creating a layer.

**Severity:** Medium - Useful for layer creation workflow.

---

## 2. Missing Request Bodies (High Severity)

**Impact:** PUT operations that accept request bodies aren't documented. Clients won't know how to update resources.

### Count: ~31 PUT endpoints

**Pattern:** Many PUT endpoints accept request bodies for updates but documentation doesn't show the schema.

**Examples:**

#### 2.1 Importer Module (2 endpoints)
```java
// PUT /rest/imports/{id}/tasks/{taskId}/layer
@PutMapping("/{id}/tasks/{taskId}/layer")
public void updateLayer(
    @PathVariable Long id,
    @PathVariable Long taskId,
    @RequestBody LayerInfo layer  // ← Not documented
) {
    // Updates layer configuration
}

// PUT /rest/imports/{id}/tasks/{taskId}/target
@PutMapping("/{id}/tasks/{taskId}/target")
public void updateTarget(
    @PathVariable Long id,
    @PathVariable Long taskId,
    @RequestBody StoreInfo target  // ← Not documented
) {
    // Updates target store
}
```

**Severity:** High - These are core update operations. Without documentation, clients don't know what JSON to send.

---

#### 2.2 Namespace Operations (1 endpoint)
```java
// PUT /rest/namespaces/{prefix}
@PutMapping("/{prefix}")
public void updateNamespace(
    @PathVariable String prefix,
    @RequestBody NamespaceInfo namespace  // ← Not documented
) {
    // Updates namespace configuration
}
```

---

#### 2.3 User/Group Operations (6 endpoints)

Security-related PUT operations for updating users and groups:
- `PUT /rest/security/usergroup/user/{userName}/group/{groupName}`
- `PUT /rest/security/usergroup/service/{serviceName}/user/{userName}/group/{groupName}`
- And 4 more similar endpoints

**Severity:** High - Security configuration without documentation is risky.

---

#### 2.4 Datastore Operations (Multiple endpoints)

Many datastore PUT operations accept configuration bodies:
- `PUT /rest/workspaces/{workspace}/datastores/{datastore}`
- `PUT /rest/workspaces/{workspace}/coveragestores/{coveragestore}`
- `PUT /rest/workspaces/{workspace}/wmsstores/{wmsstore}`
- `PUT /rest/workspaces/{workspace}/wmtsstores/{wmtsstore}`

**Severity:** High - Core configuration operations.

---

## 3. Extra Query Parameters in Documentation (Low Severity)

**Impact:** Documentation shows parameters that don't exist in implementation. Clients will try to use them and get confused.

### 3.1 Status Endpoint Mismatch

**Endpoint:** `GET /rest/about/status`

**Documentation shows:**
- `manifest` (query parameter)
- `key` (query parameter)
- `value` (query parameter)

**Implementation has:**
- `target` (path variable)
- No query parameters

**Severity:** Low - Documentation is wrong, but clients will just get ignored parameters.

---

## 4. GET with Request Body (Medium Severity - Anti-pattern)

**Endpoint:** `GET /rest/logging`

**Implementation:**
```java
@GetMapping
public RestWrapper<LoggingInfo> loggingGet(
    @RequestBody(required = false) LoggingInfo logging  // ← Anti-pattern!
) {
    // GET with body is non-standard
}
```

**Issue:** HTTP GET requests shouldn't have request bodies per REST conventions. This violates HTTP semantics.

**Severity:** Medium - Works but violates REST principles. Some HTTP clients/proxies may strip the body.

**Recommendation:** This should probably be:
- `GET /rest/logging` - No body, just retrieves current logging config
- `PUT /rest/logging` - With body, updates logging config

---

## Severity Classification

### High Severity (Fix Soon)
1. **Missing `purge` parameter** - Prevents accidental data deletion
2. **Missing request body schemas for PUT operations** - ~31 endpoints can't be used properly
3. **Missing `async`/`exec` parameters** - Controls critical execution behavior

### Medium Severity (Fix When Convenient)
1. **Missing `expand` parameter** - Useful optimization feature
2. **Missing `recalculate`/`calculate` parameters** - Affects spatial metadata accuracy
3. **Missing `offset`/`limit` parameters** - Pagination for large datasets
4. **GET with request body anti-pattern** - Violates REST principles

### Low Severity (Cosmetic/Nice-to-have)
1. **Missing `from`/`to` parameters** - Niche version filtering
2. **Missing `styleName` parameter** - Convenience feature
3. **Extra parameters in documentation** - Confusing but harmless

---

## Recommendations

### Immediate Actions (High Priority)

1. **Document request body schemas for PUT operations**
   - Extract Java classes (LayerInfo, StoreInfo, NamespaceInfo, etc.)
   - Generate JSON schemas
   - Add to OpenAPI spec with examples
   - **Estimated effort:** 1-2 days

2. **Document critical query parameters**
   - `purge` - Prevents data loss
   - `async`/`exec` - Controls execution mode
   - `recalculate`/`calculate` - Affects metadata
   - **Estimated effort:** 2-3 hours

3. **Fix GET /rest/logging anti-pattern**
   - Investigate if body is actually used
   - If not used, remove from implementation
   - If used, consider changing to POST or PUT
   - **Estimated effort:** 1-2 hours investigation + fix

### Medium-Term Actions

4. **Document convenience parameters**
   - `expand` - Response detail control
   - `offset`/`limit` - Pagination
   - `styleName` - Layer creation
   - **Estimated effort:** 1-2 hours

5. **Remove incorrect documentation**
   - Fix `/rest/about/status` parameters
   - Remove non-existent parameters from other endpoints
   - **Estimated effort:** 1 hour

---

## Impact on Coverage Calculation

### Current Calculation
- **166 matched endpoints** (47.0% coverage)
- **37 exact matches** (10.5%)
- **129 with parameter mismatches** (36.5%)

### Proposed Recalculation

If we exclude cosmetic path variable naming (~90 mismatches):

- **Functional mismatches:** ~39 endpoints
  - Missing query parameters: ~15 endpoints
  - Missing request bodies: ~31 endpoints (some overlap)
  - Other issues: ~5 endpoints

**Adjusted coverage:**
- **Exact + Cosmetic matches:** 127 endpoints (36.0%)
- **Functional mismatches:** 39 endpoints (11.0%)
- **Undocumented:** 187 endpoints (53.0%)

This gives a more accurate picture: **36% are fully correct**, **11% have functional gaps**, **53% are completely undocumented**.

---

## Conclusion

The most serious functional discrepancies are:

1. **31 PUT endpoints missing request body documentation** - Clients can't use these operations
2. **`purge` parameter undocumented** - Risk of accidental data deletion
3. **`async`/`exec` parameters undocumented** - Can't control execution mode
4. **GET with request body anti-pattern** - Violates HTTP semantics

These should be prioritized over cosmetic path variable naming issues.
