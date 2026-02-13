#!/usr/bin/env python3
"""
Consolidate all OGC service operations into a single file.

This script merges operation data from all OGC services:
- WMS, WFS, WCS, WMTS, CSW, WPS
"""

import json
import os
from typing import Dict, List, Any

def load_service_operations(service_name: str) -> Dict[str, Any]:
    """Load operations JSON for a specific service."""
    file_path = f".kiro/api-analysis/ogc/{service_name.lower()}-operations.json"
    
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def consolidate_operations() -> Dict[str, Any]:
    """Consolidate all OGC service operations."""
    
    services = ["WMS", "WFS", "WCS", "WMTS", "CSW", "WPS"]
    
    consolidated = {
        "title": "GeoServer OGC Service Operations",
        "description": "Consolidated operations from all OGC services implemented in GeoServer",
        "extraction_date": "2026-02-12",
        "services": []
    }
    
    total_operations = 0
    
    for service_name in services:
        service_data = load_service_operations(service_name)
        
        if service_data:
            consolidated["services"].append(service_data)
            total_operations += len(service_data.get("operations", []))
            print(f"  ✓ {service_name}: {len(service_data.get('operations', []))} operations")
        else:
            print(f"  ✗ {service_name}: Not found")
    
    # Add summary statistics
    consolidated["summary"] = {
        "total_services": len(consolidated["services"]),
        "total_operations": total_operations,
        "services_by_name": {
            service["service"]: {
                "title": service["service_title"],
                "versions": service["versions"],
                "operation_count": len(service["operations"])
            }
            for service in consolidated["services"]
        }
    }
    
    return consolidated


def generate_summary_report(consolidated: Dict[str, Any]) -> str:
    """Generate a markdown summary report."""
    
    report = []
    report.append("# OGC Service Operations Summary")
    report.append("")
    report.append(f"**Extraction Date:** {consolidated['extraction_date']}")
    report.append("")
    report.append("## Overview")
    report.append("")
    report.append(f"- **Total Services:** {consolidated['summary']['total_services']}")
    report.append(f"- **Total Operations:** {consolidated['summary']['total_operations']}")
    report.append("")
    report.append("## Services")
    report.append("")
    
    for service in consolidated["services"]:
        report.append(f"### {service['service']} - {service['service_title']}")
        report.append("")
        report.append(f"**Description:** {service['description']}")
        report.append("")
        report.append(f"**Versions:** {', '.join(service['versions'])}")
        report.append("")
        report.append(f"**Operations:** {len(service['operations'])}")
        report.append("")
        
        # List operations
        for op in service["operations"]:
            vendor = " *(vendor extension)*" if op.get("vendor_extension") else ""
            versions = op.get("versions", service["versions"])
            version_str = f" (versions: {', '.join(versions)})" if versions != service["versions"] else ""
            param_count = len(op.get("parameters", []))
            
            report.append(f"- **{op['name']}**{vendor}{version_str}")
            report.append(f"  - {op['description']}")
            report.append(f"  - HTTP Methods: {', '.join(op['http_methods'])}")
            report.append(f"  - Parameters: {param_count}")
            
            if op.get("note"):
                report.append(f"  - Note: {op['note']}")
            
            report.append("")
        
        report.append("")
    
    # Operation count by service
    report.append("## Operation Count by Service")
    report.append("")
    report.append("| Service | Title | Versions | Operations |")
    report.append("|---------|-------|----------|------------|")
    
    for service in consolidated["services"]:
        versions = ', '.join(service['versions'])
        op_count = len(service['operations'])
        report.append(f"| {service['service']} | {service['service_title']} | {versions} | {op_count} |")
    
    report.append("")
    
    # Total parameters
    report.append("## Parameter Statistics")
    report.append("")
    
    for service in consolidated["services"]:
        total_params = sum(len(op.get("parameters", [])) for op in service["operations"])
        avg_params = total_params / len(service["operations"]) if service["operations"] else 0
        
        report.append(f"- **{service['service']}**: {total_params} total parameters, "
                     f"{avg_params:.1f} average per operation")
    
    report.append("")
    
    return "\n".join(report)


def main():
    """Main execution function."""
    print("Consolidating OGC service operations...")
    print("")
    
    consolidated = consolidate_operations()
    
    # Write consolidated JSON
    output_file = ".kiro/api-analysis/ogc/all-operations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, indent=2, ensure_ascii=False)
    
    print("")
    print(f"✓ Consolidated operations written to {output_file}")
    print(f"  - Total services: {consolidated['summary']['total_services']}")
    print(f"  - Total operations: {consolidated['summary']['total_operations']}")
    
    # Generate summary report
    report = generate_summary_report(consolidated)
    report_file = ".kiro/api-analysis/reports/ogc-operations-summary.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ Summary report written to {report_file}")


if __name__ == "__main__":
    main()
