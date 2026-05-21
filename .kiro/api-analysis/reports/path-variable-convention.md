# Path Variable Naming Convention Decision

**Date:** 2026-05-19  
**Status:** Decided  
**Decision:** Match Java `@PathVariable` names exactly

## Context

The GeoServer OpenAPI specification has 170 path variable naming mismatches across 107 endpoints. The core question is: should the spec use generic names (e.g., `{id}`) or descriptive names (e.g., `{importId}`), and should it match the Java source or invent its own conventions?

## Decision

**Match Java `@PathVariable` names exactly.** The OpenAPI spec path variable names must correspond 1:1 with the names used in the Java controller `@PathVariable` annotations and `@RequestMapping` path templates.

## Rationale

1. **Code-generation tools** (openapi-generator, swagger-codegen) use path variable names as method parameter names in generated client code. Matching the Java source ensures generated clients have meaningful, consistent parameter names.

2. **Single source of truth** — the Java code IS the implementation. The spec should describe what exists, not invent alternative naming.

3. **Phase 3 alignment** — when Springdoc annotations are added to controllers, the generated spec will naturally use the Java path variable names. Adopting this convention now means zero rework later.

4. **Developer experience** — developers reading both the spec and the source code see the same names, reducing cognitive load.

## Observed Patterns in Java Source

### Pattern 1: Descriptive Names (majority of restconfig module)

Most catalog controllers use descriptive, camelCase names that indicate what the variable represents:

| Controller | Path Template | @PathVariable Name |
|-----------|--------------|-------------------|
| WorkspaceController | `/{workspaceName}` | `workspaceName` |
| LayerController | `/{layerName}` | `layerName` |
| StyleController | `/{styleName}` | `styleName` |
| LayerGroupController | `/{layerGroupName}` | `layerGroupName` |
| NamespaceController | `/{namespaceName}` | `namespaceName` |
| NamespaceController | `/{prefix}` | `prefix` |
| DataStoreController | `/{storeName}` | `storeName` |
| CoverageStoreController | `/{storeName}` | `storeName` |
| CoverageController | `/{coverageName}` | `coverageName` |
| FeatureTypeController | `/{featureTypeName}` | `featureTypeName` |
| TemplateController | `/{templateName}` | `templateName` |
| CRSController | `/{identifier:.+}` | `identifier` |
| AboutStatusController | `/{target}` | `target` |

### Pattern 2: Generic Names (importer module)

The importer module uses short generic names:

| Controller | Path Template | @PathVariable Name |
|-----------|--------------|-------------------|
| ImportController | `/{id}` | `id` (type: Long) |
| ImportTaskController | `/{taskId}` | `taskId` (type: Integer) |
| ImportDataController | `/{importId}` | `importId` |
| ImportTransformController | `/{transformId}` | `transformId` |

### Pattern 3: Explicit @PathVariable("name") Mapping (security module)

Some controllers use explicit name mapping where the path template name differs from the Java parameter name:

| Controller | Path Template | @PathVariable Annotation | Java Param |
|-----------|--------------|-------------------------|-----------|
| RolesRestController | `/{role}` | `@PathVariable("role")` | `roleName` |
| RolesRestController | `/{user}` | `@PathVariable("user")` | `userName` |
| RolesRestController | `/{group}` | `@PathVariable("group")` | `groupName` |
| RolesRestController | `/{serviceName}` | `@PathVariable("serviceName")` | `serviceName` |
| AuthenticationFilterController | `/{filterName}` | `@PathVariable("filterName")` | `filterName` |
| AuthenticationProviderRestController | `/{providerName}` | (implicit) | `providerName` |
| AuthenticationFilterChainRestController | `/{chainName}` | (implicit) | `chainName` |

### Pattern 4: OSEO Community Module (explicit name mapping)

| Controller | Path Template | @PathVariable Annotation | Java Param |
|-----------|--------------|-------------------------|-----------|
| CollectionsController | `/{collection}` | `@PathVariable(name="collection")` | `collection` |
| ProductsController | `/{product}` | `@PathVariable(name="product")` | `product` |

## Resolution Rule

When `@PathVariable("name")` specifies an explicit name, use that name. Otherwise, use the path template variable name from `@RequestMapping`/`@GetMapping`/etc. These are always the same in practice — Spring requires them to match.

**The spec path variable name = the name in the `@RequestMapping` path template.**

## Mapping Table: Current Spec → Correct Name

### Importer Module (needs changes)

| Current Spec Name | Correct Java Name | Path | Affected Endpoints |
|------------------|-------------------|------|-------------------|
| `{id}` | `{id}` | `/rest/imports/{id}` | ✅ Already correct |
| `{taskId}` | `{taskId}` | `/rest/imports/{id}/tasks/{taskId}` | ✅ Already correct |
| `{importId}` | `{importId}` | `/rest/imports/{importId}/data` | ✅ Already correct |
| `{importId}` | `{importId}` | `/rest/imports/{importId}/tasks/{taskId}/transforms` | ✅ Already correct |
| `{transformId}` | `{transformId}` | `/rest/imports/{importId}/tasks/{taskId}/transforms/{transformId}` | ✅ Already correct |

**Note:** The importer module has an inconsistency in its own source code — `ImportController` uses `{id}` (type Long) while `ImportDataController` uses `{importId}` for the same concept. This is a source code inconsistency, not a spec issue. The spec should match each controller's actual path template.

### Core REST Module (needs changes)

| Current Spec Name | Correct Java Name | Path | Affected Endpoints |
|------------------|-------------------|------|-------------------|
| `{workspaceName}` | `{workspaceName}` | `/rest/workspaces/{workspaceName}` | ✅ Already correct |
| `{layerName}` | `{layerName}` | `/rest/layers/{layerName}` | ✅ Already correct |
| `{styleName}` | `{styleName}` | `/rest/styles/{styleName}` | ✅ Already correct |
| `{layerGroupName}` | `{layerGroupName}` | `/rest/layergroups/{layerGroupName}` | ✅ Already correct |
| `{storeName}` | `{storeName}` | `/rest/workspaces/{workspaceName}/datastores/{storeName}` | ✅ Already correct |
| `{coverageName}` | `{coverageName}` | `/rest/workspaces/{workspaceName}/coveragestores/{storeName}/coverages/{coverageName}` | ✅ Already correct |
| `{featureTypeName}` | `{featureTypeName}` | `/rest/workspaces/{workspaceName}/datastores/{storeName}/featuretypes/{featureTypeName}` | ✅ Already correct |
| `{namespaceName}` | `{namespaceName}` | `/rest/namespaces/{namespaceName}` | ✅ Already correct |
| `{prefix}` | `{prefix}` | `/rest/namespaces/{prefix}` | ✅ Already correct |
| `{templateName}` | `{templateName}` | `/rest/templates/{templateName}` | ✅ Already correct |
| `{identifier}` | `{identifier}` | `/rest/crs/{identifier}.wkt` | ✅ Already correct |
| `{target}` | `{target}` | `/rest/about/status/{target}` | ✅ Already correct |
| `{format}` | `{format}` | `/rest/workspaces/{workspaceName}/datastores/{storeName}/{method}.{format}` | ✅ Already correct |
| `{method}` | `{method}` | (UploadMethod enum path variable) | ✅ Already correct |

### Security Module (needs changes)

| Current Spec Name | Correct Java Name | Path | Affected Endpoints |
|------------------|-------------------|------|-------------------|
| `{role}` | `{role}` | `/rest/security/roles/role/{role}` | ✅ Already correct |
| `{user}` | `{user}` | `/rest/security/roles/user/{user}` | ✅ Already correct |
| `{group}` | `{group}` | `/rest/security/roles/group/{group}` | ✅ Already correct |
| `{serviceName}` | `{serviceName}` | `/rest/security/roles/service/{serviceName}` | ✅ Already correct |
| `{filterName}` | `{filterName}` | `/rest/security/authfilters/{filterName}` | ✅ Already correct |
| `{providerName}` | `{providerName}` | `/rest/security/authproviders/{providerName}` | ✅ Already correct |
| `{chainName}` | `{chainName}` | `/rest/security/filterchains/{chainName}` | ✅ Already correct |

### OSEO Community Module

| Current Spec Name | Correct Java Name | Path | Affected Endpoints |
|------------------|-------------------|------|-------------------|
| `{collection}` | `{collection}` | `/rest/oseo/collections/{collection}` | ✅ Already correct |
| `{product}` | `{product}` | `/rest/oseo/collections/{collection}/products/{product}` | ✅ Already correct |

## Summary of Required Changes

After reviewing the current spec against the Java source, the path variable names in the spec **already match the Java source** in most cases. The original mismatch analysis (170 issues across 107 endpoints) was comparing against the *old Swagger 2.0 documentation* which used different conventions.

The remaining issues to address in tasks 32-33 are:

1. **Malformed paths** — Some paths have missing closing braces (e.g., `/rest/workspaces/{workspaceName/{featureTypeName}`) which is a path extraction bug, not a naming issue.

2. **Namespace controller inconsistency** — The Java source itself uses both `{namespaceName}` (for GET) and `{prefix}` (for DELETE/PUT) for the same resource. The spec should document both paths as they exist in code.

3. **Importer module inconsistency** — `ImportController` uses `{id}` while `ImportDataController` uses `{importId}` for the same import ID concept. The spec correctly reflects this source-level inconsistency.

## Implications for Tasks 32-33

When fixing path variable mismatches in the spec:

1. **DO** use the exact name from the Java `@RequestMapping` path template
2. **DO NOT** rename variables for "clarity" — if Java says `{id}`, the spec says `{id}`
3. **DO** fix malformed paths (missing braces) — these are extraction bugs
4. **DO** document the parameter with a clear `description` field to compensate for generic names (e.g., `{id}` → description: "The import context identifier")
5. **DO** use the `name` attribute from `@PathVariable("name")` when it differs from the Java parameter name

## Validation Checklist

For each endpoint in the spec, verify:
- [ ] Path variable name matches the `@RequestMapping`/`@GetMapping`/etc. path template
- [ ] All path template variables have corresponding parameter definitions
- [ ] Parameter descriptions are clear even when names are generic
- [ ] No malformed path templates (all braces properly opened and closed)
