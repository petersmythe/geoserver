#!/usr/bin/env python3
"""
Generate documented endpoints summary from documented-endpoints.json
Counts endpoints by HTTP method and groups by module/tag
"""

import json
from collections import defaultdict
from pathlib import Path

def load_endpoints():
    """Load the documented endpoints JSON file"""
    input_file = Path('.kiro/api-analysis/rest/documented-endpoints.json')
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_endpoints(data):
    """Analyze endpoints and generate statistics"""
    # Count by HTTP method
    method_counts = defaultdict(int)
    
    # Group by module/tag
    module_endpoints = defaultdict(list)
    
    # Track all endpoints
    all_endpoints = []
    
    for file_info in data['files']:
        for endpoint in file_info['endpoints']:
            method = endpoint['method']
            path = endpoint['path']
            operation_id = endpoint.get('operation_id', 'N/A')
            tags = endpoint.get('tags', [])
            
            # Count by method
            method_counts[method] += 1
            
            # Determine module from tags or path
            module = 'Untagged'
            if tags:
                module = tags[0]  # Use first tag as primary module
            elif path:
                # Try to infer module from path
                parts = path.strip('/').split('/')
                if len(parts) > 0:
                    module = parts[0].capitalize()
            
            # Add to module group
            module_endpoints[module].append({
                'method': method,
                'path': path,
                'operation_id': operation_id,
                'file': file_info['file']
            })
            
            all_endpoints.append({
                'method': method,
                'path': path,
                'operation_id': operation_id,
                'module': module,
                'file': file_info['file']
            })
    
    return {
        'method_counts': dict(method_counts),
        'module_endpoints': dict(module_endpoints),
        'all_endpoints': all_endpoints,
        'total_endpoints': len(all_endpoints)
    }

def generate_markdown_report(data, analysis):
    """Generate Markdown summary report"""
    output = []
    
    # Header
    output.append("# Documented REST API Endpoints Summary")
    output.append("")
    output.append(f"**Generated:** {data['metadata']['parse_date']}")
    output.append(f"**Total Spec Files:** {data['metadata']['total_files']}")
    output.append(f"**Total Endpoints:** {analysis['total_endpoints']}")
    output.append("")
    
    # Overview by HTTP Method
    output.append("## Endpoints by HTTP Method")
    output.append("")
    output.append("| HTTP Method | Count |")
    output.append("|-------------|-------|")
    
    # Sort methods in standard order
    method_order = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']
    for method in method_order:
        if method in analysis['method_counts']:
            count = analysis['method_counts'][method]
            output.append(f"| {method} | {count} |")
    
    # Add any other methods not in standard order
    for method, count in sorted(analysis['method_counts'].items()):
        if method not in method_order:
            output.append(f"| {method} | {count} |")
    
    output.append("")
    
    # Endpoints by Module/Tag
    output.append("## Endpoints by Module/Tag")
    output.append("")
    output.append("| Module | Endpoint Count |")
    output.append("|--------|----------------|")
    
    # Sort modules by endpoint count (descending)
    sorted_modules = sorted(
        analysis['module_endpoints'].items(),
        key=lambda x: len(x[1]),
        reverse=True
    )
    
    for module, endpoints in sorted_modules:
        output.append(f"| {module} | {len(endpoints)} |")
    
    output.append("")
    
    # Detailed breakdown by module
    output.append("## Detailed Breakdown by Module")
    output.append("")
    
    for module, endpoints in sorted_modules:
        output.append(f"### {module} ({len(endpoints)} endpoints)")
        output.append("")
        output.append("| Method | Path | Operation ID |")
        output.append("|--------|------|--------------|")
        
        # Sort endpoints by method then path
        sorted_endpoints = sorted(endpoints, key=lambda x: (x['method'], x['path']))
        
        for ep in sorted_endpoints:
            op_id = ep['operation_id'] if ep['operation_id'] else 'N/A'
            output.append(f"| {ep['method']} | `{ep['path']}` | {op_id} |")
        
        output.append("")
    
    # Summary statistics
    output.append("## Summary Statistics")
    output.append("")
    output.append(f"- **Total Modules:** {len(analysis['module_endpoints'])}")
    output.append(f"- **Total Endpoints:** {analysis['total_endpoints']}")
    output.append(f"- **Spec Files Parsed:** {data['metadata']['successful_parses']}/{data['metadata']['total_files']}")
    output.append(f"- **Parse Failures:** {data['metadata']['failed_parses']}")
    output.append("")
    
    # Method distribution
    output.append("### HTTP Method Distribution")
    output.append("")
    for method in method_order:
        if method in analysis['method_counts']:
            count = analysis['method_counts'][method]
            percentage = (count / analysis['total_endpoints']) * 100
            output.append(f"- **{method}:** {count} ({percentage:.1f}%)")
    output.append("")
    
    return '\n'.join(output)

def main():
    """Main execution"""
    print("Loading documented endpoints...")
    data = load_endpoints()
    
    print("Analyzing endpoints...")
    analysis = analyze_endpoints(data)
    
    print(f"Found {analysis['total_endpoints']} endpoints across {len(analysis['module_endpoints'])} modules")
    
    print("Generating Markdown report...")
    report = generate_markdown_report(data, analysis)
    
    # Write output
    output_file = Path('.kiro/api-analysis/reports/documented-summary.md')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Report written to: {output_file}")
    print("\nSummary:")
    print(f"  Total endpoints: {analysis['total_endpoints']}")
    print(f"  Total modules: {len(analysis['module_endpoints'])}")
    print(f"  HTTP methods: {', '.join(sorted(analysis['method_counts'].keys()))}")

if __name__ == '__main__':
    main()
