#!/usr/bin/env python3
"""
Fix remaining tag issues in OpenAPI specifications.

Sub-tasks:
- 15.5.2: Fix remaining "Gwc" tags in operations (should be "REST GWC")
- 15.5.10: Sort REST Extensions endpoints alphabetically
- 15.5.11: Apply alphabetical sorting to all endpoint groups
"""

import json
import yaml
from pathlib import Path
from collections import OrderedDict

def sort_paths_alphabetically(spec_data):
    """Sort all paths alphabetically."""
    if 'paths' not in spec_data:
        return
    
    # Sort paths dictionary
    sorted_paths = OrderedDict(sorted(spec_data['paths'].items()))
    spec_data['paths'] = sorted_paths
    
    return len(sorted_paths)

def fix_gwc_tags(spec_data):
    """Fix remaining 'Gwc' tags to 'REST GWC'."""
    fixed_count = 0
    
    if 'paths' not in spec_data:
        return fixed_count
    
    for path, path_item in spec_data['paths'].items():
        for method, operation in path_item.items():
            if method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                if 'tags' in operation:
                    new_tags = []
                    for tag in operation['tags']:
                        if tag == 'Gwc':
                            new_tags.append('REST GWC')
                            fixed_count += 1
                        else:
                            new_tags.append(tag)
                    operation['tags'] = new_tags
    
    return fixed_count

def analyze_endpoint_issues(spec_data):
    """Analyze endpoint classification issues."""
    issues = {
        'order_endpoints': [],
        'root_delete_endpoints': [],
        'gwc_endpoints': []
    }
    
    if 'paths' not in spec_data:
        return issues
    
    for path, path_item in spec_data['paths'].items():
        # Check for /order endpoints
        if path == '/order' or path.startswith('/order.'):
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    issues['order_endpoints'].append({
                        'path': path,
                        'method': method.upper(),
                        'operationId': operation.get('operationId', ''),
                        'tags': operation.get('tags', []),
                        'description': operation.get('description', '')
                    })
        
        # Check for DELETE / endpoints
        if path == '/':
            if 'delete' in path_item:
                operation = path_item['delete']
                issues['root_delete_endpoints'].append({
                    'path': path,
                    'method': 'DELETE',
                    'operationId': operation.get('operationId', ''),
                    'tags': operation.get('tags', []),
                    'description': operation.get('description', '')
                })
        
        # Check for REST GWC tagged endpoints
        for method, operation in path_item.items():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                if 'REST GWC' in operation.get('tags', []):
                    issues['gwc_endpoints'].append({
                        'path': path,
                        'method': method.upper(),
                        'operationId': operation.get('operationId', ''),
                        'tags': operation.get('tags', [])
                    })
    
    return issues

def process_yaml_spec(input_path, output_path):
    """Process YAML specification."""
    print(f"\nProcessing YAML: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        spec_data = yaml.safe_load(f)
    
    # Fix Gwc tags
    gwc_fixed = fix_gwc_tags(spec_data)
    print(f"  Fixed {gwc_fixed} 'Gwc' tags to 'REST GWC'")
    
    # Sort paths alphabetically
    path_count = sort_paths_alphabetically(spec_data)
    print(f"  Sorted {path_count} paths alphabetically")
    
    # Analyze issues
    issues = analyze_endpoint_issues(spec_data)
    print(f"  Found {len(issues['order_endpoints'])} /order endpoints")
    print(f"  Found {len(issues['root_delete_endpoints'])} DELETE / endpoints")
    print(f"  Found {len(issues['gwc_endpoints'])} REST GWC endpoints")
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(spec_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"  Written to: {output_path}")
    
    return issues

def process_json_spec(input_path, output_path):
    """Process JSON specification."""
    print(f"\nProcessing JSON: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        spec_data = json.load(f)
    
    # Fix Gwc tags
    gwc_fixed = fix_gwc_tags(spec_data)
    print(f"  Fixed {gwc_fixed} 'Gwc' tags to 'REST GWC'")
    
    # Sort paths alphabetically
    path_count = sort_paths_alphabetically(spec_data)
    print(f"  Sorted {path_count} paths alphabetically")
    
    # Analyze issues
    issues = analyze_endpoint_issues(spec_data)
    print(f"  Found {len(issues['order_endpoints'])} /order endpoints")
    print(f"  Found {len(issues['root_delete_endpoints'])} DELETE / endpoints")
    print(f"  Found {len(issues['gwc_endpoints'])} REST GWC endpoints")
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(spec_data, f, indent=2)
    
    print(f"  Written to: {output_path}")
    
    return issues

def generate_issues_report(all_issues, output_path):
    """Generate report of endpoint classification issues."""
    report = []
    report.append("# Endpoint Classification Issues Report\n")
    report.append("Generated by fix-tag-issues.py\n\n")
    
    # /order endpoints
    report.append("## /order Endpoints\n\n")
    report.append("These endpoints are currently tagged as 'REST Security' but come from the rest module.\n")
    report.append("Source files:\n")
    report.append("- AuthenticationFilterChainRestController.java\n")
    report.append("- AuthenticationProviderRestController.java\n\n")
    
    if all_issues.get('order_endpoints'):
        report.append("| Path | Method | Operation ID | Current Tags |\n")
        report.append("|------|--------|--------------|-------------|\n")
        for endpoint in all_issues['order_endpoints']:
            tags_str = ', '.join(endpoint['tags'])
            report.append(f"| {endpoint['path']} | {endpoint['method']} | {endpoint['operationId']} | {tags_str} |\n")
    else:
        report.append("No /order endpoints found.\n")
    
    report.append("\n**Recommendation**: These are security-related endpoints (authentication filter chain ordering),\n")
    report.append("so 'REST Security' tag is appropriate despite being in the rest module.\n\n")
    
    # DELETE / endpoints
    report.append("## DELETE / Endpoints\n\n")
    report.append("These endpoints have path '/' which seems incorrect.\n")
    report.append("Source: MetaDataRestService.java in metadata extension module\n")
    report.append("Expected path: /rest/metadata (not just /)\n\n")
    
    if all_issues.get('root_delete_endpoints'):
        report.append("| Path | Method | Operation ID | Current Tags |\n")
        report.append("|------|--------|--------------|-------------|\n")
        for endpoint in all_issues['root_delete_endpoints']:
            tags_str = ', '.join(endpoint['tags'])
            report.append(f"| {endpoint['path']} | {endpoint['method']} | {endpoint['operationId']} | {tags_str} |\n")
    else:
        report.append("No DELETE / endpoints found.\n")
    
    report.append("\n**Recommendation**: Verify path extraction. The @RequestMapping(\"/rest/metadata\") should\n")
    report.append("result in /rest/metadata path, not /. This may be a path extraction bug.\n\n")
    
    # REST GWC endpoints
    report.append("## REST GWC Endpoints\n\n")
    report.append("Endpoints tagged with 'REST GWC'.\n\n")
    
    if all_issues.get('gwc_endpoints'):
        report.append("| Path | Method | Operation ID | Tags |\n")
        report.append("|------|--------|--------------|------|\n")
        for endpoint in all_issues['gwc_endpoints']:
            tags_str = ', '.join(endpoint['tags'])
            report.append(f"| {endpoint['path']} | {endpoint['method']} | {endpoint['operationId']} | {tags_str} |\n")
    else:
        report.append("No REST GWC endpoints found in the spec.\n\n")
        report.append("**Note**: GWC endpoints were extracted but use dynamic paths (${gwc.context.suffix:})\n")
        report.append("which may not have been included in the final spec. GeoWebCache has its own REST API\n")
        report.append("that may be documented separately.\n")
    
    report.append("\n## Summary\n\n")
    report.append(f"- /order endpoints: {len(all_issues.get('order_endpoints', []))}\n")
    report.append(f"- DELETE / endpoints: {len(all_issues.get('root_delete_endpoints', []))}\n")
    report.append(f"- REST GWC endpoints: {len(all_issues.get('gwc_endpoints', []))}\n")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(report)
    
    print(f"\nIssues report written to: {output_path}")

def main():
    """Main execution."""
    base_dir = Path(__file__).parent
    
    print("=== Fixing Tag Issues ===")
    
    # Process bundled specs
    bundled_yaml = base_dir.parent.parent / 'doc' / 'en' / 'api' / 'geoserver-bundled.yaml'
    bundled_json = base_dir.parent.parent / 'doc' / 'en' / 'api' / 'geoserver-bundled.json'
    
    all_issues = {}
    
    if bundled_yaml.exists():
        issues_yaml = process_yaml_spec(bundled_yaml, bundled_yaml)
        all_issues.update(issues_yaml)
    else:
        print(f"Warning: {bundled_yaml} not found")
    
    if bundled_json.exists():
        issues_json = process_json_spec(bundled_json, bundled_json)
    else:
        print(f"Warning: {bundled_json} not found")
    
    # Generate issues report
    report_path = base_dir / 'reports' / 'endpoint-classification-issues.md'
    generate_issues_report(all_issues, report_path)
    
    print("\n=== Tag Issues Fix Complete ===")

if __name__ == '__main__':
    main()
