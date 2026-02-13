#!/usr/bin/env python3
"""
Consolidate all implemented REST endpoints from tasks 4.2-4.6
- Merge endpoint data from all source files
- Remove duplicates (same path + method)
- Count total endpoints by module and HTTP method
- Output consolidated JSON and summary report
"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Any

def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load a JSON file and return its contents."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
        return {"metadata": {}, "endpoints": []}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from {filepath}: {e}")
        return {"metadata": {}, "endpoints": []}

def create_endpoint_key(endpoint: Dict[str, Any]) -> str:
    """Create a unique key for an endpoint based on path and HTTP method."""
    path = endpoint.get('path', '')
    method = endpoint.get('http_method', '')
    return f"{method}:{path}"

def determine_module(endpoint: Dict[str, Any], source_file: str) -> str:
    """Determine the module name for an endpoint."""
    # Check if module is explicitly set
    if 'module' in endpoint:
        return endpoint['module']
    
    # Determine from source file path
    source = endpoint.get('source_file', source_file)
    
    if 'src/rest/' in source:
        return 'rest'
    elif 'src/restconfig/' in source:
        return 'restconfig'
    elif 'src/restconfig-wcs/' in source:
        return 'restconfig-wcs'
    elif 'src/restconfig-wfs/' in source:
        return 'restconfig-wfs'
    elif 'src/restconfig-wms/' in source:
        return 'restconfig-wms'
    elif 'src/restconfig-wmts/' in source:
        return 'restconfig-wmts'
    elif 'src/gwc-rest/' in source or 'src/gwc/' in source:
        return 'gwc'
    elif 'src/extension/' in source:
        # Extract extension module name
        parts = source.split('src/extension/')
        if len(parts) > 1:
            module_parts = parts[1].split('/')
            if module_parts:
                return f"extension-{module_parts[0]}"
        return 'extension'
    elif 'src/community/' in source:
        # Extract community module name
        parts = source.split('src/community/')
        if len(parts) > 1:
            module_parts = parts[1].split('/')
            if module_parts:
                return f"community-{module_parts[0]}"
        return 'community'
    else:
        return 'unknown'

def consolidate_endpoints():
    """Main consolidation function."""
    
    # Input files from tasks 4.2-4.6
    input_files = [
        '.kiro/api-analysis/rest/implemented-core-endpoints.json',
        '.kiro/api-analysis/rest/implemented-service-endpoints.json',
        '.kiro/api-analysis/rest/implemented-gwc-endpoints.json',
        '.kiro/api-analysis/rest/implemented-extension-endpoints.json',
        '.kiro/api-analysis/rest/implemented-community-endpoints.json'
    ]
    
    # Track all endpoints and detect duplicates
    all_endpoints = []
    endpoint_keys = set()
    duplicates = []
    
    # Counters
    total_endpoints = 0
    endpoints_by_method = defaultdict(int)
    endpoints_by_module = defaultdict(int)
    
    # Process each input file
    for input_file in input_files:
        print(f"Processing {input_file}...")
        data = load_json_file(input_file)
        
        endpoints = data.get('endpoints', [])
        print(f"  Found {len(endpoints)} endpoints")
        
        for endpoint in endpoints:
            # Create unique key
            key = create_endpoint_key(endpoint)
            
            # Check for duplicates
            if key in endpoint_keys:
                duplicates.append({
                    'key': key,
                    'endpoint': endpoint,
                    'source_file': input_file
                })
                print(f"  Duplicate found: {key}")
                continue
            
            # Add to collection
            endpoint_keys.add(key)
            all_endpoints.append(endpoint)
            
            # Update counters
            total_endpoints += 1
            method = endpoint.get('http_method', 'UNKNOWN')
            endpoints_by_method[method] += 1
            
            module = determine_module(endpoint, input_file)
            endpoints_by_module[module] += 1
    
    print(f"\nTotal unique endpoints: {total_endpoints}")
    print(f"Duplicates removed: {len(duplicates)}")
    
    # Sort endpoints by path and method for consistency
    all_endpoints.sort(key=lambda e: (e.get('path', ''), e.get('http_method', '')))
    
    # Create consolidated output
    consolidated = {
        "metadata": {
            "source_files": input_files,
            "total_endpoints": total_endpoints,
            "duplicates_removed": len(duplicates),
            "endpoints_by_method": dict(sorted(endpoints_by_method.items())),
            "endpoints_by_module": dict(sorted(endpoints_by_module.items()))
        },
        "endpoints": all_endpoints,
        "duplicates": duplicates
    }
    
    # Write consolidated JSON
    output_json = '.kiro/api-analysis/rest/implemented-all-endpoints.json'
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, indent=2, ensure_ascii=False)
    print(f"\nWrote consolidated endpoints to {output_json}")
    
    # Generate summary report
    generate_summary_report(consolidated)
    
    return consolidated

def generate_summary_report(data: Dict[str, Any]):
    """Generate a Markdown summary report."""
    
    metadata = data['metadata']
    endpoints = data['endpoints']
    
    report_lines = [
        "# Implemented REST Endpoints Summary",
        "",
        "## Overview",
        "",
        f"- **Total Unique Endpoints**: {metadata['total_endpoints']}",
        f"- **Duplicates Removed**: {metadata['duplicates_removed']}",
        f"- **Source Files**: {len(metadata['source_files'])}",
        "",
        "## Endpoints by HTTP Method",
        "",
        "| HTTP Method | Count |",
        "|-------------|-------|"
    ]
    
    for method, count in sorted(metadata['endpoints_by_method'].items()):
        report_lines.append(f"| {method} | {count} |")
    
    report_lines.extend([
        "",
        "## Endpoints by Module",
        "",
        "| Module | Count |",
        "|--------|-------|"
    ])
    
    for module, count in sorted(metadata['endpoints_by_module'].items()):
        report_lines.append(f"| {module} | {count} |")
    
    report_lines.extend([
        "",
        "## Module Categories",
        "",
        "### Core Modules",
        ""
    ])
    
    # Group modules by category
    core_modules = {k: v for k, v in metadata['endpoints_by_module'].items() 
                    if not k.startswith('extension-') and not k.startswith('community-')}
    extension_modules = {k: v for k, v in metadata['endpoints_by_module'].items() 
                         if k.startswith('extension-')}
    community_modules = {k: v for k, v in metadata['endpoints_by_module'].items() 
                         if k.startswith('community-')}
    
    core_total = sum(core_modules.values())
    extension_total = sum(extension_modules.values())
    community_total = sum(community_modules.values())
    
    report_lines.append(f"- **Total Core Endpoints**: {core_total}")
    for module, count in sorted(core_modules.items()):
        report_lines.append(f"  - {module}: {count}")
    
    report_lines.extend([
        "",
        "### Extension Modules",
        "",
        f"- **Total Extension Endpoints**: {extension_total}"
    ])
    for module, count in sorted(extension_modules.items()):
        module_name = module.replace('extension-', '')
        report_lines.append(f"  - {module_name}: {count}")
    
    report_lines.extend([
        "",
        "### Community Modules",
        "",
        f"- **Total Community Endpoints**: {community_total}"
    ])
    for module, count in sorted(community_modules.items()):
        module_name = module.replace('community-', '')
        report_lines.append(f"  - {module_name}: {count}")
    
    # Add sample endpoints
    report_lines.extend([
        "",
        "## Sample Endpoints",
        "",
        "### First 10 Endpoints",
        "",
        "| Method | Path | Module | Class |",
        "|--------|------|--------|-------|"
    ])
    
    for endpoint in endpoints[:10]:
        method = endpoint.get('http_method', 'N/A')
        path = endpoint.get('path', 'N/A')
        module = determine_module(endpoint, endpoint.get('source_file', ''))
        class_name = endpoint.get('class_name', 'N/A')
        report_lines.append(f"| {method} | {path} | {module} | {class_name} |")
    
    # Add duplicates section if any
    if data.get('duplicates'):
        report_lines.extend([
            "",
            "## Duplicates Removed",
            "",
            f"Found {len(data['duplicates'])} duplicate endpoints:",
            ""
        ])
        for dup in data['duplicates'][:10]:  # Show first 10
            report_lines.append(f"- {dup['key']} (from {dup['source_file']})")
    
    report_lines.extend([
        "",
        "## Source Files",
        ""
    ])
    
    for source_file in metadata['source_files']:
        report_lines.append(f"- {source_file}")
    
    report_lines.extend([
        "",
        "---",
        "",
        f"*Generated from {len(metadata['source_files'])} source files*"
    ])
    
    # Write report
    output_report = '.kiro/api-analysis/reports/implemented-summary.md'
    os.makedirs(os.path.dirname(output_report), exist_ok=True)
    with open(output_report, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    print(f"Wrote summary report to {output_report}")

if __name__ == '__main__':
    print("Consolidating REST endpoints from tasks 4.2-4.6...")
    print("=" * 60)
    consolidate_endpoints()
    print("=" * 60)
    print("Consolidation complete!")
