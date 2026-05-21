#!/usr/bin/env python3
"""
Accurate REST API Coverage Calculation for GeoServer OpenAPI Spec.

This script:
1. Extracts all REST endpoints from Java source code (controllers)
2. Parses the bundled OpenAPI spec (geoserver-bundled.yaml)
3. Matches implemented endpoints against documented ones
4. Calculates coverage percentage
5. Outputs a detailed report
"""

import os
import re
import json
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Set

# Project root (script runs from .kiro/api-analysis/)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Directories to scan for REST controllers
CORE_SCAN_DIRS = [
    "src/rest/",
    "src/restconfig/",
    "src/restconfig-wcs/",
    "src/restconfig-wfs/",
    "src/restconfig-wms/",
    "src/restconfig-wmts/",
    "src/gwc-rest/",
]

EXTENSION_SCAN_DIRS = ["src/extension/"]
COMMUNITY_SCAN_DIRS = ["src/community/"]

# Known REST base path constant
REST_ROOT_PATH = "/rest"


def find_java_files(base_dir: Path, scan_dirs: List[str]) -> List[Path]:
    """Find all Java files in the given scan directories."""
    java_files = []
    for scan_dir in scan_dirs:
        dir_path = base_dir / scan_dir
        if dir_path.exists():
            for java_file in dir_path.rglob("*.java"):
                if "/main/java/" in str(java_file).replace("\\", "/"):
                    java_files.append(java_file)
    return java_files


def is_rest_controller(content: str) -> bool:
    """Check if file content contains REST controller annotations."""
    return bool(re.search(r'@(Rest)?Controller\b', content))


def extract_class_request_mapping(content: str) -> Optional[str]:
    """Extract the class-level @RequestMapping path."""
    # Match @RequestMapping with path or value attribute
    # Handle multi-line annotations
    patterns = [
        # @RequestMapping(path = ROOT_PATH + "/workspaces", ...)
        r'@RequestMapping\s*\([^)]*(?:path|value)\s*=\s*(?:RestBaseController\.ROOT_PATH|ROOT_PATH)\s*\+\s*"([^"]*)"',
        # @RequestMapping(path = "/rest/workspaces", ...)
        r'@RequestMapping\s*\([^)]*(?:path|value)\s*=\s*"(/[^"]*)"',
        # @RequestMapping("/rest/workspaces")
        r'@RequestMapping\s*\(\s*"(/[^"]*)"',
        # @RequestMapping(path = ROOT_PATH + "/gwc/rest/...", ...)
        r'@RequestMapping\s*\([^)]*(?:path|value)\s*=\s*"([^"]*)"',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            path = match.group(1)
            return path
    return None


def extract_request_mapping_path_full(content: str) -> Optional[str]:
    """Extract class-level @RequestMapping path, handling ROOT_PATH constant and multi-line."""
    # Remove comments first
    content_no_comments = re.sub(r'//.*?\n', '\n', content)
    content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)
    
    # Find class-level @RequestMapping (before class declaration)
    class_decl_match = re.search(r'public\s+(?:abstract\s+)?class\s+\w+', content_no_comments)
    if not class_decl_match:
        return None
    
    before_class = content_no_comments[:class_decl_match.start()]
    
    # Find @RequestMapping in the section before class
    # Use a robust approach to find the annotation body (handles nested braces in strings)
    rm_start = re.search(r'@RequestMapping\s*\(', before_class)
    if not rm_start:
        # Simple form: @RequestMapping("/path")
        rm_simple = re.search(r'@RequestMapping\s*\(\s*"([^"]+)"\s*\)', before_class)
        if rm_simple:
            return rm_simple.group(1)
        # Check for just ROOT_PATH without parentheses content
        rm_root = re.search(r'@RequestMapping\s*\(\s*(?:RestBaseController\.)?ROOT_PATH\s*\)', before_class)
        if rm_root:
            return "/rest"
        return None
    
    # Find matching closing paren, accounting for strings and nested parens
    paren_start = rm_start.end() - 1
    depth = 0
    in_string = False
    annotation_end = -1
    for i in range(paren_start, len(before_class)):
        c = before_class[i]
        if c == '"' and (i == 0 or before_class[i-1] != '\\'):
            in_string = not in_string
        elif not in_string:
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    annotation_end = i
                    break
    
    if annotation_end < 0:
        return None
    
    annotation_body = before_class[paren_start+1:annotation_end]
    
    # Handle: path = RestBaseController.ROOT_PATH (no concatenation)
    root_only_pattern = r'(?:path|value)\s*=\s*(?:RestBaseController\.)?ROOT_PATH\s*[,\)]'
    if re.search(root_only_pattern, annotation_body + ')'):
        return "/rest"
    
    # Handle: just ROOT_PATH as the only argument (no path= prefix)
    if re.match(r'\s*(?:RestBaseController\.)?ROOT_PATH\s*$', annotation_body.strip()):
        return "/rest"
    
    # Handle: path = RestBaseController.ROOT_PATH + "/workspaces"
    root_path_pattern = r'(?:path|value)\s*=\s*(?:RestBaseController\.)?ROOT_PATH\s*\+\s*"([^"]*)"'
    match = re.search(root_path_pattern, annotation_body)
    if match:
        return "/rest" + match.group(1)
    
    # Handle: just ROOT_PATH + "/something" as the only argument
    root_concat_only = r'^\s*(?:RestBaseController\.)?ROOT_PATH\s*\+\s*"([^"]*)"'
    match = re.search(root_concat_only, annotation_body.strip())
    if match:
        return "/rest" + match.group(1)
    
    # Handle: path = {ROOT_PATH + "/a", ROOT_PATH + "/b"} - take first
    # Use a more robust approach: find opening { after path/value =, then find matching }
    array_start = re.search(r'(?:path|value)\s*=\s*\{', annotation_body)
    if array_start:
        # Find the matching closing brace (accounting for nested braces in path vars)
        brace_start = array_start.end() - 1
        depth = 0
        array_end = -1
        in_string = False
        for i in range(brace_start, len(annotation_body)):
            c = annotation_body[i]
            if c == '"' and (i == 0 or annotation_body[i-1] != '\\'):
                in_string = not in_string
            elif not in_string:
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        array_end = i
                        break
        
        if array_end > 0:
            array_content = annotation_body[brace_start+1:array_end]
            # Check for ROOT_PATH concatenation in array
            root_concat = re.search(r'(?:RestBaseController\.)?ROOT_PATH\s*\+\s*"([^"]*)"', array_content)
            if root_concat:
                return "/rest" + root_concat.group(1)
            # Plain string in array
            first_str = re.search(r'"([^"]*)"', array_content)
            if first_str:
                return first_str.group(1)
    
    # Handle: path = "/rest/something"
    direct_path_pattern = r'(?:path|value)\s*=\s*"([^"]*)"'
    match = re.search(direct_path_pattern, annotation_body)
    if match:
        return match.group(1)
    
    # Handle: just a string as the only argument
    simple_str = re.search(r'^\s*"([^"]*)"', annotation_body.strip())
    if simple_str:
        return simple_str.group(1)
    
    return None


def extract_method_endpoints(content: str, class_path: str, file_path: str) -> List[Dict]:
    """Extract all HTTP method endpoints from a controller file."""
    endpoints = []
    
    # Remove block comments
    content_clean = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Method-level mapping annotations
    method_annotations = {
        'GetMapping': 'GET',
        'PostMapping': 'POST',
        'PutMapping': 'PUT',
        'DeleteMapping': 'DELETE',
        'PatchMapping': 'PATCH',
    }
    
    for annotation, http_method in method_annotations.items():
        # Find all occurrences of @GetMapping, @PostMapping, etc.
        # Pattern handles: @GetMapping, @GetMapping("/path"), @GetMapping(value="/path"), @GetMapping(path="/path")
        pattern = rf'@{annotation}\s*(?:\(([^)]*(?:\([^)]*\)[^)]*)*)\))?'
        
        for match in re.finditer(pattern, content_clean):
            annotation_body = match.group(1) or ""
            
            # Extract sub-path from annotation
            sub_path = ""
            if annotation_body.strip():
                # Check for value= or path= or just a string
                path_match = re.search(r'(?:value|path)\s*=\s*"([^"]*)"', annotation_body)
                if path_match:
                    sub_path = path_match.group(1)
                else:
                    # Check for array: value = {"/a", "/b"}
                    array_match = re.search(r'(?:value|path)\s*=\s*\{([^}]+)\}', annotation_body)
                    if array_match:
                        first_str = re.search(r'"([^"]*)"', array_match.group(1))
                        if first_str:
                            sub_path = first_str.group(1)
                    else:
                        # Simple string: @GetMapping("/path")
                        simple_match = re.search(r'"([^"]*)"', annotation_body)
                        if simple_match:
                            sub_path = simple_match.group(1)
            
            # Build full path
            full_path = class_path
            if sub_path:
                if not sub_path.startswith("/"):
                    sub_path = "/" + sub_path
                full_path = class_path + sub_path
            
            # Normalize path
            full_path = full_path.replace("//", "/")
            
            endpoints.append({
                "path": full_path,
                "http_method": http_method,
                "source_file": str(file_path).replace("\\", "/"),
            })
    
    # Also handle @RequestMapping at method level with method= attribute
    rm_pattern = r'@RequestMapping\s*\(([^)]*(?:\([^)]*\)[^)]*)*)\)'
    class_decl = re.search(r'public\s+(?:abstract\s+)?class\s+\w+', content_clean)
    if class_decl:
        after_class = content_clean[class_decl.end():]
        for match in re.finditer(rm_pattern, after_class):
            annotation_body = match.group(1)
            
            # Extract method
            method_match = re.search(r'method\s*=\s*(?:RequestMethod\.)?(\w+)', annotation_body)
            if not method_match:
                # Check for array of methods
                method_array = re.search(r'method\s*=\s*\{([^}]+)\}', annotation_body)
                if method_array:
                    methods_str = method_array.group(1)
                    methods = re.findall(r'(?:RequestMethod\.)?(\w+)', methods_str)
                else:
                    continue
            else:
                methods = [method_match.group(1)]
            
            # Extract path
            sub_path = ""
            path_match = re.search(r'(?:value|path)\s*=\s*"([^"]*)"', annotation_body)
            if path_match:
                sub_path = path_match.group(1)
            else:
                simple_match = re.search(r'"([^"]*)"', annotation_body)
                if simple_match:
                    sub_path = simple_match.group(1)
            
            for method in methods:
                full_path = class_path
                if sub_path:
                    if not sub_path.startswith("/"):
                        sub_path = "/" + sub_path
                    full_path = class_path + sub_path
                full_path = full_path.replace("//", "/")
                
                endpoints.append({
                    "path": full_path,
                    "http_method": method.upper(),
                    "source_file": str(file_path).replace("\\", "/"),
                })
    
    return endpoints


def extract_endpoints_from_file(file_path: Path) -> List[Dict]:
    """Extract all REST endpoints from a single Java file."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        print(f"  Error reading {file_path}: {e}")
        return []
    
    if not is_rest_controller(content):
        # Check if it has method-level mappings without class-level @Controller
        if not re.search(r'@(Get|Post|Put|Delete|Patch)Mapping', content):
            return []
    
    # Get class-level path
    class_path = extract_request_mapping_path_full(content)
    if not class_path:
        # Some controllers don't have class-level mapping
        # Check if methods have full paths
        class_path = ""
    
    # Ensure path starts with /rest or /gwc/rest
    if class_path and not class_path.startswith("/"):
        class_path = "/" + class_path
    
    # Extract method endpoints
    endpoints = extract_method_endpoints(content, class_path, file_path)
    
    return endpoints


def extract_all_implemented_endpoints() -> List[Dict]:
    """Extract all implemented REST endpoints from Java source code."""
    all_endpoints = []
    seen_keys = set()
    
    # Scan core directories
    print("Scanning core REST modules...")
    core_files = find_java_files(PROJECT_ROOT, CORE_SCAN_DIRS)
    print(f"  Found {len(core_files)} Java files in core modules")
    
    for f in core_files:
        endpoints = extract_endpoints_from_file(f)
        for ep in endpoints:
            key = f"{ep['http_method']}:{ep['path']}"
            if key not in seen_keys:
                seen_keys.add(key)
                ep['category'] = 'core'
                all_endpoints.append(ep)
    
    print(f"  Extracted {len(all_endpoints)} unique core endpoints")
    
    # Scan extension directories
    print("Scanning extension modules...")
    ext_files = find_java_files(PROJECT_ROOT, EXTENSION_SCAN_DIRS)
    print(f"  Found {len(ext_files)} Java files in extension modules")
    
    ext_count = 0
    for f in ext_files:
        endpoints = extract_endpoints_from_file(f)
        for ep in endpoints:
            key = f"{ep['http_method']}:{ep['path']}"
            if key not in seen_keys:
                seen_keys.add(key)
                ep['category'] = 'extension'
                all_endpoints.append(ep)
                ext_count += 1
    
    print(f"  Extracted {ext_count} unique extension endpoints")
    
    # Scan community directories
    print("Scanning community modules...")
    comm_files = find_java_files(PROJECT_ROOT, COMMUNITY_SCAN_DIRS)
    print(f"  Found {len(comm_files)} Java files in community modules")
    
    comm_count = 0
    for f in comm_files:
        endpoints = extract_endpoints_from_file(f)
        for ep in endpoints:
            key = f"{ep['http_method']}:{ep['path']}"
            if key not in seen_keys:
                seen_keys.add(key)
                ep['category'] = 'community'
                all_endpoints.append(ep)
                comm_count += 1
    
    print(f"  Extracted {comm_count} unique community endpoints")
    
    return all_endpoints


def extract_documented_endpoints(yaml_path: Path) -> List[Dict]:
    """Extract all REST endpoints from the bundled OpenAPI YAML spec."""
    print(f"Loading bundled spec from {yaml_path}...")
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)
    
    documented = []
    paths = spec.get('paths', {})
    
    http_methods = {'get', 'post', 'put', 'delete', 'patch', 'head', 'options'}
    
    for path, path_item in paths.items():
        # Only count REST endpoints (not OGC service endpoints)
        if not (path.startswith('/rest/') or path.startswith('/gwc/rest/') or path.startswith('/gsr/')):
            continue
        
        if not isinstance(path_item, dict):
            continue
        
        for method in http_methods:
            if method in path_item:
                documented.append({
                    "path": path,
                    "http_method": method.upper(),
                })
    
    print(f"  Found {len(documented)} documented REST operations")
    return documented


def normalize_path_for_matching(path: str) -> str:
    """Normalize a path for fuzzy matching by replacing variable names with {var}."""
    # Replace {anyVariableName} with {var}
    normalized = re.sub(r'\{[^}]+\}', '{var}', path)
    # Remove trailing slashes
    normalized = normalized.rstrip('/')
    # Lowercase
    normalized = normalized.lower()
    return normalized


def normalize_path_segments(path: str) -> str:
    """Normalize path by replacing variables and format extensions."""
    # Remove format extensions like .json, .xml, .html
    path = re.sub(r'\.\{[^}]+\}$', '', path)
    path = re.sub(r'\.(json|xml|html|sld|zip|css|yaml|yml)$', '', path)
    # Replace all path variables with generic placeholder
    path = re.sub(r'\{[^}]+\}', '{var}', path)
    path = path.rstrip('/')
    return path.lower()


def match_endpoints(implemented: List[Dict], documented: List[Dict]) -> Dict:
    """Match implemented endpoints against documented ones."""
    
    # Build lookup structures for documented endpoints
    # Exact match: method + path
    doc_exact = set()
    for ep in documented:
        doc_exact.add(f"{ep['http_method']}:{ep['path']}")
    
    # Normalized match: method + normalized path
    doc_normalized = set()
    doc_normalized_map = {}
    for ep in documented:
        norm_path = normalize_path_for_matching(ep['path'])
        key = f"{ep['http_method']}:{norm_path}"
        doc_normalized.add(key)
        doc_normalized_map[key] = ep['path']
    
    # Segment-normalized match
    doc_segments = set()
    doc_segments_map = {}
    for ep in documented:
        seg_path = normalize_path_segments(ep['path'])
        key = f"{ep['http_method']}:{seg_path}"
        doc_segments.add(key)
        doc_segments_map[key] = ep['path']
    
    exact_matches = []
    fuzzy_matches = []
    unmatched = []
    
    for ep in implemented:
        path = ep['path']
        method = ep['http_method']
        
        # Skip endpoints without valid REST paths
        if not path or not path.startswith('/'):
            continue
        
        # Exact match
        exact_key = f"{method}:{path}"
        if exact_key in doc_exact:
            exact_matches.append(ep)
            continue
        
        # Normalized match (variable names differ)
        norm_path = normalize_path_for_matching(path)
        norm_key = f"{method}:{norm_path}"
        if norm_key in doc_normalized:
            ep['matched_doc_path'] = doc_normalized_map[norm_key]
            fuzzy_matches.append(ep)
            continue
        
        # Segment-normalized match (format extensions, etc.)
        seg_path = normalize_path_segments(path)
        seg_key = f"{method}:{seg_path}"
        if seg_key in doc_segments:
            ep['matched_doc_path'] = doc_segments_map[seg_key]
            fuzzy_matches.append(ep)
            continue
        
        unmatched.append(ep)
    
    return {
        "exact_matches": exact_matches,
        "fuzzy_matches": fuzzy_matches,
        "unmatched": unmatched,
    }


def generate_report(implemented: List[Dict], documented: List[Dict], 
                    match_results: Dict, output_path: Path):
    """Generate the coverage report."""
    
    total_implemented = len(implemented)
    total_documented = len(documented)
    exact_count = len(match_results['exact_matches'])
    fuzzy_count = len(match_results['fuzzy_matches'])
    unmatched_count = len(match_results['unmatched'])
    total_matched = exact_count + fuzzy_count
    
    # Filter to only REST endpoints (those with /rest/ or /gwc/rest/ paths)
    rest_implemented = [ep for ep in implemented 
                        if ep['path'].startswith('/rest/') or ep['path'].startswith('/gwc/rest/')]
    
    coverage_pct = (total_matched / total_implemented * 100) if total_implemented > 0 else 0
    rest_coverage_pct = (total_matched / len(rest_implemented) * 100) if rest_implemented else 0
    
    # Count by category
    by_category = defaultdict(int)
    for ep in implemented:
        by_category[ep.get('category', 'unknown')] += 1
    
    unmatched_by_category = defaultdict(list)
    for ep in match_results['unmatched']:
        unmatched_by_category[ep.get('category', 'unknown')].append(ep)
    
    # Count by HTTP method
    by_method = defaultdict(int)
    for ep in implemented:
        by_method[ep['http_method']] += 1
    
    doc_by_method = defaultdict(int)
    for ep in documented:
        doc_by_method[ep['http_method']] += 1
    
    lines = [
        "# Accurate REST API Coverage Calculation",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total implemented REST endpoints (from Java source) | {total_implemented} |",
        f"| Implemented endpoints with /rest/ or /gwc/rest/ prefix | {len(rest_implemented)} |",
        f"| Total documented REST operations (from bundled YAML) | {total_documented} |",
        f"| Exact matches (path + method identical) | {exact_count} |",
        f"| Fuzzy matches (path pattern similar, variable names differ) | {fuzzy_count} |",
        f"| Total matched | {total_matched} |",
        f"| Unmatched implemented endpoints | {unmatched_count} |",
        f"| **Coverage (matched / all implemented)** | **{coverage_pct:.1f}%** |",
        f"| **Coverage (matched / REST-prefixed only)** | **{rest_coverage_pct:.1f}%** |",
        "",
        "## Implemented Endpoints by Category",
        "",
        "| Category | Count |",
        "|----------|-------|",
    ]
    
    for cat in sorted(by_category.keys()):
        lines.append(f"| {cat} | {by_category[cat]} |")
    
    lines.extend([
        "",
        "## Implemented Endpoints by HTTP Method",
        "",
        "| Method | Implemented | Documented |",
        "|--------|-------------|------------|",
    ])
    
    all_methods = sorted(set(list(by_method.keys()) + list(doc_by_method.keys())))
    for method in all_methods:
        lines.append(f"| {method} | {by_method.get(method, 0)} | {doc_by_method.get(method, 0)} |")
    
    lines.extend([
        "",
        "## Fuzzy Matches (variable name differences)",
        "",
        "These endpoints matched after normalizing path variable names:",
        "",
        "| Method | Implemented Path | Documented Path |",
        "|--------|-----------------|-----------------|",
    ])
    
    for ep in sorted(match_results['fuzzy_matches'], key=lambda x: x['path'])[:50]:
        doc_path = ep.get('matched_doc_path', 'N/A')
        lines.append(f"| {ep['http_method']} | `{ep['path']}` | `{doc_path}` |")
    
    if len(match_results['fuzzy_matches']) > 50:
        lines.append(f"| ... | *({len(match_results['fuzzy_matches']) - 50} more)* | |")
    
    lines.extend([
        "",
        "## Unmatched Implemented Endpoints (NOT in spec)",
        "",
        "These endpoints exist in Java source but are not documented in the bundled spec:",
        "",
    ])
    
    for cat in sorted(unmatched_by_category.keys()):
        cat_endpoints = unmatched_by_category[cat]
        lines.append(f"### {cat.title()} ({len(cat_endpoints)} endpoints)")
        lines.append("")
        lines.append("| Method | Path | Source File |")
        lines.append("|--------|------|-------------|")
        
        for ep in sorted(cat_endpoints, key=lambda x: x['path']):
            src = ep.get('source_file', 'N/A')
            # Shorten source file path
            if 'src/' in src:
                src = src[src.index('src/'):]
            lines.append(f"| {ep['http_method']} | `{ep['path']}` | {src} |")
        
        lines.append("")
    
    lines.extend([
        "## Methodology",
        "",
        "1. **Source extraction**: Scanned all Java files in core REST modules, extensions,",
        "   and community modules for `@RestController`/`@Controller` annotations and",
        "   `@GetMapping`/`@PostMapping`/`@PutMapping`/`@DeleteMapping`/`@PatchMapping` methods.",
        "2. **Spec parsing**: Loaded `doc/en/api/geoserver-bundled.yaml` and extracted all",
        "   paths starting with `/rest/`, `/gwc/rest/`, or `/gsr/` with their HTTP methods.",
        "3. **Matching**: Three-tier matching:",
        "   - Exact: path + method identical",
        "   - Normalized: path variables replaced with `{var}` (e.g., `{id}` matches `{importId}`)",
        "   - Segment-normalized: also strips format extensions (`.json`, `.xml`)",
        "4. **Coverage**: (exact + fuzzy matches) / total implemented × 100",
        "",
        "---",
        "*Generated by accurate-coverage-calculation.py*",
    ])
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"\nReport written to: {output_path}")


def main():
    """Main execution."""
    print("=" * 70)
    print("ACCURATE REST API COVERAGE CALCULATION")
    print("=" * 70)
    print()
    
    # Step 1: Extract implemented endpoints from Java source
    print("STEP 1: Extracting implemented endpoints from Java source code...")
    print("-" * 70)
    implemented = extract_all_implemented_endpoints()
    
    # Filter to only REST-relevant endpoints (have a path starting with /)
    implemented = [ep for ep in implemented if ep['path'] and ep['path'].startswith('/')]
    
    print(f"\nTotal implemented endpoints with valid paths: {len(implemented)}")
    
    # Save implemented endpoints to JSON for future use
    output_json = PROJECT_ROOT / ".kiro" / "api-analysis" / "rest" / "implemented-all-endpoints.json"
    output_json.parent.mkdir(parents=True, exist_ok=True)
    
    json_data = {
        "metadata": {
            "total_endpoints": len(implemented),
            "endpoints_by_method": {},
            "endpoints_by_category": {},
        },
        "endpoints": implemented
    }
    
    # Count by method and category
    for ep in implemented:
        method = ep['http_method']
        json_data["metadata"]["endpoints_by_method"][method] = \
            json_data["metadata"]["endpoints_by_method"].get(method, 0) + 1
        cat = ep.get('category', 'unknown')
        json_data["metadata"]["endpoints_by_category"][cat] = \
            json_data["metadata"]["endpoints_by_category"].get(cat, 0) + 1
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"Saved implemented endpoints to: {output_json}")
    
    # Step 2: Extract documented endpoints from bundled YAML
    print()
    print("STEP 2: Extracting documented endpoints from bundled YAML spec...")
    print("-" * 70)
    yaml_path = PROJECT_ROOT / "doc" / "en" / "api" / "geoserver-bundled.yaml"
    documented = extract_documented_endpoints(yaml_path)
    
    # Step 3: Match endpoints
    print()
    print("STEP 3: Matching implemented vs documented endpoints...")
    print("-" * 70)
    match_results = match_endpoints(implemented, documented)
    
    exact_count = len(match_results['exact_matches'])
    fuzzy_count = len(match_results['fuzzy_matches'])
    unmatched_count = len(match_results['unmatched'])
    total_matched = exact_count + fuzzy_count
    coverage = (total_matched / len(implemented) * 100) if implemented else 0
    
    print(f"  Exact matches: {exact_count}")
    print(f"  Fuzzy matches: {fuzzy_count}")
    print(f"  Total matched: {total_matched}")
    print(f"  Unmatched: {unmatched_count}")
    print(f"  Coverage: {coverage:.1f}%")
    
    # Step 4: Generate report
    print()
    print("STEP 4: Generating coverage report...")
    print("-" * 70)
    report_path = PROJECT_ROOT / ".kiro" / "api-analysis" / "reports" / "accurate-coverage-calculation.md"
    generate_report(implemented, documented, match_results, report_path)
    
    print()
    print("=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
