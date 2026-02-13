#!/usr/bin/env python3
"""
Generate reconciliation matrix reports in Markdown and CSV formats.

This script reads the reconciliation-matrix.json file and generates:
- Markdown report with sortable tables
- CSV version for spreadsheet analysis
- Summary statistics
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


def load_json(filepath: str) -> Dict:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_markdown_report(matrix: Dict, output_file: str):
    """Generate Markdown report with sortable tables."""
    
    metadata = matrix.get('metadata', {})
    summary = matrix.get('summary', {})
    status_counts = matrix.get('status_counts', {})
    entries = matrix.get('entries', [])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write("# GeoServer API Reconciliation Matrix\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Description:** {metadata.get('description', 'N/A')}\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write(f"- **Total Endpoints/Operations:** {summary.get('total_endpoints', 0)}\n")
        f.write(f"- **REST Endpoints:** {summary.get('rest_endpoints', 0)}\n")
        f.write(f"- **OGC Operations:** {summary.get('ogc_operations', 0)}\n")
        f.write(f"- **Complete (Implemented & Documented):** {summary.get('implemented_and_documented', 0)}\n")
        f.write(f"- **Needs Documentation:** {summary.get('needs_documentation', 0)}\n")
        f.write(f"- **Needs Investigation:** {summary.get('needs_investigation', 0)}\n")
        f.write(f"- **Missing Both:** {summary.get('missing_both', 0)}\n\n")
        
        # Coverage Percentage
        total = summary.get('total_endpoints', 0)
        complete = summary.get('implemented_and_documented', 0)
        if total > 0:
            coverage_pct = (complete / total) * 100
            f.write(f"**Overall Coverage:** {coverage_pct:.1f}%\n\n")
        
        # Status Breakdown
        f.write("## Status Breakdown\n\n")
        f.write("| Category | Count |\n")
        f.write("|----------|-------|\n")
        
        # Sort status counts for consistent display
        major_categories = [
            ('Complete (impl+doc)', 'Complete (Implemented & Documented)'),
            ('Needs Documentation (impl only)', 'Needs Documentation'),
            ('Needs Investigation (doc only)', 'Needs Investigation'),
            ('Missing (neither impl nor doc)', 'Missing Both')
        ]
        
        for key, label in major_categories:
            count = status_counts.get(key, 0)
            f.write(f"| {label} | {count} |\n")
        
        f.write("\n")
        
        # Service Breakdown
        f.write("## Breakdown by Service\n\n")
        f.write("| Service | Count |\n")
        f.write("|---------|-------|\n")
        
        services = ['REST API', 'WMS', 'WFS', 'WCS', 'WMTS', 'CSW', 'WPS']
        for service in services:
            key = f"Service: {service}"
            count = status_counts.get(key, 0)
            if count > 0:
                f.write(f"| {service} | {count} |\n")
        
        f.write("\n")
        
        # REST Endpoints Table
        f.write("## REST API Endpoints\n\n")
        f.write("### Summary\n\n")
        rest_entries = [e for e in entries if e.get('endpoint_type') == 'REST']
        rest_complete = len([e for e in rest_entries if e.get('status', '').startswith('Complete')])
        rest_needs_doc = len([e for e in rest_entries if e.get('status') == 'Needs Documentation'])
        rest_needs_inv = len([e for e in rest_entries if e.get('status') == 'Needs Investigation'])
        
        f.write(f"- Total REST Endpoints: {len(rest_entries)}\n")
        f.write(f"- Complete: {rest_complete}\n")
        f.write(f"- Needs Documentation: {rest_needs_doc}\n")
        f.write(f"- Needs Investigation: {rest_needs_inv}\n\n")
        
        # REST Endpoints Detail Table
        f.write("### REST Endpoints Detail\n\n")
        f.write("| Operation | Implemented | Documented | Status | Module | Issues |\n")
        f.write("|-----------|-------------|------------|--------|--------|--------|\n")
        
        for entry in rest_entries:
            operation = entry.get('operation', '')
            implemented = '✓' if entry.get('implemented') else '✗'
            documented = '✓' if entry.get('documented') else '✗'
            status = entry.get('status', '')
            module = entry.get('module', '')
            issues = entry.get('issues', [])
            issue_summary = f"{len(issues)} issue(s)" if issues else "None"
            
            f.write(f"| {operation} | {implemented} | {documented} | {status} | {module} | {issue_summary} |\n")
        
        f.write("\n")
        
        # OGC Operations Table
        f.write("## OGC Service Operations\n\n")
        f.write("### Summary\n\n")
        ogc_entries = [e for e in entries if e.get('endpoint_type') == 'OGC']
        ogc_complete = len([e for e in ogc_entries if e.get('status', '').startswith('Complete')])
        ogc_needs_impl = len([e for e in ogc_entries if 'Needs Implementation' in e.get('status', '')])
        ogc_optional = len([e for e in ogc_entries if 'Optional' in e.get('status', '')])
        
        f.write(f"- Total OGC Operations: {len(ogc_entries)}\n")
        f.write(f"- Complete: {ogc_complete}\n")
        f.write(f"- Needs Implementation: {ogc_needs_impl}\n")
        f.write(f"- Optional (Not Implemented): {ogc_optional}\n\n")
        
        # OGC Operations Detail Table
        f.write("### OGC Operations Detail\n\n")
        f.write("| Service | Version | Operation | Implemented | Documented | OGC Required | Status | Issues |\n")
        f.write("|---------|---------|-----------|-------------|------------|--------------|--------|--------|\n")
        
        for entry in ogc_entries:
            service = entry.get('service', '')
            version = entry.get('version', '')
            operation = entry.get('operation', '')
            implemented = '✓' if entry.get('implemented') else '✗'
            documented = '✓' if entry.get('documented') else '✗'
            ogc_required = entry.get('ogc_required', '')
            status = entry.get('status', '')
            issues = entry.get('issues', [])
            issue_summary = f"{len(issues)} issue(s)" if issues else "None"
            
            f.write(f"| {service} | {version} | {operation} | {implemented} | {documented} | {ogc_required} | {status} | {issue_summary} |\n")
        
        f.write("\n")
        
        # Priority Actions
        f.write("## Priority Actions\n\n")
        
        # Critical: Missing required OGC operations
        critical_missing = [e for e in ogc_entries if 'Critical' in e.get('status', '')]
        if critical_missing:
            f.write("### Critical: Missing Required OGC Operations\n\n")
            for entry in critical_missing:
                f.write(f"- **{entry.get('service')} {entry.get('version')}**: {entry.get('operation')}\n")
            f.write("\n")
        
        # High Priority: REST endpoints needing documentation
        if rest_needs_doc > 0:
            f.write("### High Priority: REST Endpoints Needing Documentation\n\n")
            needs_doc_entries = [e for e in rest_entries if e.get('status') == 'Needs Documentation']
            for entry in needs_doc_entries:
                f.write(f"- {entry.get('operation')} (Module: {entry.get('module')})\n")
            f.write("\n")
        
        # Medium Priority: Endpoints needing investigation
        if rest_needs_inv > 0:
            f.write("### Medium Priority: Endpoints Needing Investigation\n\n")
            needs_inv_entries = [e for e in rest_entries if e.get('status') == 'Needs Investigation']
            for entry in needs_inv_entries:
                f.write(f"- {entry.get('operation')}\n")
            f.write("\n")
        
        # Footer
        f.write("---\n\n")
        f.write(f"*Report generated from: {metadata.get('created_date', 'N/A')}*\n")
    
    print(f"Markdown report written to: {output_file}")


def generate_csv_report(matrix: Dict, output_file: str):
    """Generate CSV report for spreadsheet analysis."""
    
    entries = matrix.get('entries', [])
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'Endpoint Type',
            'Service',
            'Version',
            'Operation',
            'HTTP Method',
            'Path',
            'Implemented',
            'Documented',
            'OGC Required',
            'Status',
            'Module',
            'Source File',
            'Documented File',
            'Issue Count',
            'Issues',
            'Notes'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for entry in entries:
            issues = entry.get('issues', [])
            issue_text = '; '.join(issues) if issues else ''
            
            writer.writerow({
                'Endpoint Type': entry.get('endpoint_type', ''),
                'Service': entry.get('service', ''),
                'Version': entry.get('version', ''),
                'Operation': entry.get('operation', ''),
                'HTTP Method': entry.get('http_method', ''),
                'Path': entry.get('path', ''),
                'Implemented': 'Yes' if entry.get('implemented') else 'No',
                'Documented': 'Yes' if entry.get('documented') else 'No',
                'OGC Required': entry.get('ogc_required', ''),
                'Status': entry.get('status', ''),
                'Module': entry.get('module', ''),
                'Source File': entry.get('source_file', ''),
                'Documented File': entry.get('documented_file', ''),
                'Issue Count': len(issues),
                'Issues': issue_text,
                'Notes': entry.get('notes', '')
            })
    
    print(f"CSV report written to: {output_file}")


def main():
    """Main execution function."""
    print("Generating reconciliation matrix reports...")
    
    # Load reconciliation matrix
    matrix_file = '.kiro/api-analysis/reconciliation-matrix.json'
    print(f"Loading reconciliation matrix from {matrix_file}...")
    matrix = load_json(matrix_file)
    
    # Generate Markdown report
    md_output = '.kiro/api-analysis/reports/reconciliation-matrix.md'
    print(f"Generating Markdown report...")
    generate_markdown_report(matrix, md_output)
    
    # Generate CSV report
    csv_output = '.kiro/api-analysis/reports/reconciliation-matrix.csv'
    print(f"Generating CSV report...")
    generate_csv_report(matrix, csv_output)
    
    print("\nReconciliation matrix reports generated successfully!")
    print(f"  Markdown: {md_output}")
    print(f"  CSV: {csv_output}")


if __name__ == '__main__':
    main()
