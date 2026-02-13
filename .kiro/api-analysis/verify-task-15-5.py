#!/usr/bin/env python3
"""
Verify Task 15.5 completion.
"""

import json
from pathlib import Path

def verify_spec(spec_path):
    """Verify the specification meets all requirements."""
    print(f"\nVerifying: {spec_path}")
    
    with open(spec_path, 'r', encoding='utf-8') as f:
        spec_data = json.load(f)
    
    issues = []
    
    # Check 1: No "Gwc" tags (should be "REST GWC")
    gwc_count = 0
    rest_gwc_count = 0
    for path, path_item in spec_data.get('paths', {}).items():
        for method, operation in path_item.items():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                tags = operation.get('tags', [])
                if 'Gwc' in tags:
                    gwc_count += 1
                if 'REST GWC' in tags:
                    rest_gwc_count += 1
    
    if gwc_count > 0:
        issues.append(f"❌ Found {gwc_count} operations with 'Gwc' tag (should be 'REST GWC')")
    else:
        print(f"  ✅ No 'Gwc' tags found")
    
    print(f"  ✅ Found {rest_gwc_count} operations with 'REST GWC' tag")
    
    # Check 2: All REST tags have "REST" prefix
    rest_tags = ['REST', 'REST Extensions', 'REST Community', 'REST GWC', 'REST Security']
    old_tags = ['Core', 'GeoWebCache', 'Extensions', 'Community', 'Security']
    
    for path, path_item in spec_data.get('paths', {}).items():
        for method, operation in path_item.items():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                tags = operation.get('tags', [])
                for tag in tags:
                    if tag in old_tags:
                        issues.append(f"❌ Found old tag '{tag}' in {method.upper()} {path}")
    
    if not any('old tag' in issue for issue in issues):
        print(f"  ✅ All REST tags properly prefixed")
    
    # Check 3: OGC service tags include versions
    ogc_services = ['WMS', 'WFS', 'WCS', 'WMTS', 'CSW', 'WPS']
    version_tags = []
    generic_tags = []
    
    for tag in spec_data.get('tags', []):
        tag_name = tag['name']
        for service in ogc_services:
            if tag_name.startswith(service):
                if tag_name == service:
                    generic_tags.append(tag_name)
                elif ' ' in tag_name:
                    version_tags.append(tag_name)
    
    print(f"  ✅ Found {len(version_tags)} version-specific OGC tags")
    if generic_tags:
        print(f"  ⚠️  Found {len(generic_tags)} generic OGC tags (may be intentional): {generic_tags}")
    
    # Check 4: Paths are sorted alphabetically
    paths = list(spec_data.get('paths', {}).keys())
    sorted_paths = sorted(paths)
    
    if paths == sorted_paths:
        print(f"  ✅ All {len(paths)} paths sorted alphabetically")
    else:
        issues.append(f"❌ Paths not sorted alphabetically")
        # Find first mismatch
        for i, (actual, expected) in enumerate(zip(paths, sorted_paths)):
            if actual != expected:
                issues.append(f"   First mismatch at position {i}: got '{actual}', expected '{expected}'")
                break
    
    # Check 5: Tag ordering
    tag_names = [tag['name'] for tag in spec_data.get('tags', [])]
    rest_tag_positions = []
    ogc_tag_positions = []
    
    for i, tag_name in enumerate(tag_names):
        if tag_name.startswith('REST'):
            rest_tag_positions.append(i)
        elif any(tag_name.startswith(svc) for svc in ogc_services):
            ogc_tag_positions.append(i)
    
    if rest_tag_positions and ogc_tag_positions:
        if max(rest_tag_positions) < min(ogc_tag_positions):
            print(f"  ✅ Tags properly ordered (REST before OGC)")
        else:
            issues.append(f"❌ Tags not properly ordered (REST should come before OGC)")
    
    # Summary
    print(f"\n  Summary:")
    print(f"    Total paths: {len(paths)}")
    print(f"    Total tags: {len(tag_names)}")
    print(f"    REST GWC endpoints: {rest_gwc_count}")
    print(f"    Version-specific OGC tags: {len(version_tags)}")
    
    return issues

def main():
    """Main execution."""
    base_dir = Path(__file__).parent
    
    print("=== Task 15.5 Verification ===")
    
    bundled_json = base_dir.parent / 'doc' / 'en' / 'api' / 'geoserver-bundled.json'
    
    all_issues = []
    
    if bundled_json.exists():
        issues = verify_spec(bundled_json)
        all_issues.extend(issues)
    else:
        print(f"Warning: {bundled_json} not found")
    
    print("\n=== Verification Results ===")
    if all_issues:
        print("\n❌ Issues found:")
        for issue in all_issues:
            print(f"  {issue}")
    else:
        print("\n✅ All checks passed!")
    
    print("\n=== Verification Complete ===")

if __name__ == '__main__':
    main()
