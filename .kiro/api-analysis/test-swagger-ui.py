#!/usr/bin/env python3
"""
Test script to verify GeoServer OpenAPI spec loads in Swagger UI format.
This simulates what Swagger UI does when loading a spec.
"""

import json
import yaml
import sys
from pathlib import Path

def test_swagger_ui_loading(spec_path):
    """
    Test if a spec can be loaded in Swagger UI format.
    Returns tuple of (success, issues_list)
    """
    issues = []
    
    try:
        # Read the spec file
        with open(spec_path, 'r', encoding='utf-8') as f:
            if spec_path.suffix == '.json':
                spec = json.load(f)
            elif spec_path.suffix in ['.yaml', '.yml']:
                spec = yaml.safe_load(f)
            else:
                return False, [f"Unknown file format: {spec_path.suffix}"]
        
        # Check OpenAPI version
        if 'openapi' not in spec:
            issues.append("Missing 'openapi' field - Swagger UI requires OpenAPI 3.x format")
            return False, issues
        
        openapi_version = spec['openapi']
        if not openapi_version.startswith('3.'):
            issues.append(f"OpenAPI version {openapi_version} may not be fully supported by Swagger UI (expects 3.x)")
        
        # Check required fields for Swagger UI
        required_fields = ['info', 'paths']
        for field in required_fields:
            if field not in spec:
                issues.append(f"Missing required field: '{field}'")
        
        # Check info object
        if 'info' in spec:
            info = spec['info']
            if 'title' not in info:
                issues.append("Missing 'info.title' - Swagger UI uses this for display")
            if 'version' not in info:
                issues.append("Missing 'info.version' - required by OpenAPI spec")
        
        # Check paths
        if 'paths' in spec:
            paths = spec['paths']
            if not paths:
                issues.append("Warning: 'paths' object is empty - no endpoints to display")
            else:
                # Check for common issues in paths
                path_count = len(paths)
                operation_count = 0
                
                for path, path_item in paths.items():
                    if not isinstance(path_item, dict):
                        issues.append(f"Invalid path item at '{path}' - must be an object")
                        continue
                    
                    # Count operations
                    http_methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']
                    for method in http_methods:
                        if method in path_item:
                            operation_count += 1
                            operation = path_item[method]
                            
                            # Check operation has required fields
                            if 'responses' not in operation:
                                issues.append(f"Operation {method.upper()} {path} missing 'responses' field")
                
                print(f"✓ Found {path_count} paths with {operation_count} operations")
        
        # Check for $ref references (should be resolved in bundled spec)
        def check_refs(obj, path=""):
            """Recursively check for unresolved $ref"""
            if isinstance(obj, dict):
                if '$ref' in obj:
                    ref = obj['ref']
                    # Check if it's an external reference
                    if ref.startswith('http://') or ref.startswith('https://') or '/' in ref:
                        issues.append(f"External $ref found at {path}: {ref} - may cause loading issues in Swagger UI")
                
                for key, value in obj.items():
                    check_refs(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_refs(item, f"{path}[{i}]")
        
        check_refs(spec)
        
        # Check servers
        if 'servers' not in spec:
            issues.append("Warning: No 'servers' defined - Swagger UI will use current host")
        
        # Check components/schemas if present
        if 'components' in spec and 'schemas' in spec['components']:
            schema_count = len(spec['components']['schemas'])
            print(f"✓ Found {schema_count} schema definitions in components")
        
        # Check tags
        if 'tags' in spec:
            tag_count = len(spec['tags'])
            print(f"✓ Found {tag_count} tag definitions")
        
        return len(issues) == 0, issues
        
    except json.JSONDecodeError as e:
        return False, [f"JSON parsing error: {e}"]
    except yaml.YAMLError as e:
        return False, [f"YAML parsing error: {e}"]
    except Exception as e:
        return False, [f"Unexpected error: {e}"]

def main():
    """Test both bundled spec formats"""
    
    # Paths to test
    yaml_spec = Path("doc/en/api/geoserver-bundled.yaml")
    json_spec = Path("doc/en/api/geoserver-bundled.json")
    
    results = []
    
    print("=" * 80)
    print("GeoServer OpenAPI Spec - Swagger UI Loading Test")
    print("=" * 80)
    print()
    
    # Test YAML spec
    if yaml_spec.exists():
        print(f"Testing: {yaml_spec}")
        print("-" * 80)
        success, issues = test_swagger_ui_loading(yaml_spec)
        results.append(("YAML", yaml_spec, success, issues))
        
        if success:
            print("✓ YAML spec should load successfully in Swagger UI")
        else:
            print("✗ YAML spec has issues that may prevent loading in Swagger UI")
        
        if issues:
            print("\nIssues found:")
            for issue in issues:
                print(f"  - {issue}")
        print()
    else:
        print(f"✗ YAML spec not found: {yaml_spec}")
        print()
    
    # Test JSON spec
    if json_spec.exists():
        print(f"Testing: {json_spec}")
        print("-" * 80)
        success, issues = test_swagger_ui_loading(json_spec)
        results.append(("JSON", json_spec, success, issues))
        
        if success:
            print("✓ JSON spec should load successfully in Swagger UI")
        else:
            print("✗ JSON spec has issues that may prevent loading in Swagger UI")
        
        if issues:
            print("\nIssues found:")
            for issue in issues:
                print(f"  - {issue}")
        print()
    else:
        print(f"✗ JSON spec not found: {json_spec}")
        print()
    
    # Generate report
    print("=" * 80)
    print("Generating report...")
    print("=" * 80)
    
    report_path = Path(".kiro/api-analysis/reports/swagger-ui-test.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Swagger UI Loading Test Report\n\n")
        f.write("This report documents the results of testing whether the generated OpenAPI specifications can be loaded in Swagger UI.\n\n")
        
        f.write("## Test Overview\n\n")
        f.write("Swagger UI is a popular tool for visualizing and interacting with OpenAPI specifications. ")
        f.write("This test validates that the generated GeoServer API specifications are compatible with Swagger UI.\n\n")
        
        f.write("## Test Results\n\n")
        
        for format_name, spec_path, success, issues in results:
            f.write(f"### {format_name} Format: `{spec_path}`\n\n")
            
            if success:
                f.write(f"**Status:** ✓ PASS - Spec should load successfully in Swagger UI\n\n")
            else:
                f.write(f"**Status:** ✗ FAIL - Spec has issues that may prevent loading\n\n")
            
            if issues:
                f.write("**Issues Found:**\n\n")
                for issue in issues:
                    f.write(f"- {issue}\n")
                f.write("\n")
            else:
                f.write("**Issues Found:** None\n\n")
        
        f.write("## How to View in Swagger UI\n\n")
        f.write("### Option 1: Local File Access\n\n")
        f.write("1. Open `doc/en/api/index.html` in a web browser\n")
        f.write("2. The URL should include the spec file as a fragment: `index.html#geoserver-bundled.yaml`\n")
        f.write("3. Swagger UI will load and display the API documentation\n\n")
        
        f.write("### Option 2: Online Swagger Editor\n\n")
        f.write("1. Go to https://editor.swagger.io/\n")
        f.write("2. Click File → Import file\n")
        f.write("3. Select `doc/en/api/geoserver-bundled.yaml` or `geoserver-bundled.json`\n")
        f.write("4. The spec will be loaded and validated\n\n")
        
        f.write("### Option 3: Swagger UI Docker\n\n")
        f.write("```bash\n")
        f.write("# Run Swagger UI in Docker\n")
        f.write("docker run -p 8080:8080 -e SWAGGER_JSON=/specs/geoserver-bundled.yaml \\\n")
        f.write("  -v $(pwd)/doc/en/api:/specs swaggerapi/swagger-ui\n")
        f.write("```\n\n")
        
        f.write("## Validation Checks Performed\n\n")
        f.write("The test validates the following aspects required for Swagger UI compatibility:\n\n")
        f.write("1. **OpenAPI Version**: Checks for OpenAPI 3.x format\n")
        f.write("2. **Required Fields**: Validates presence of `info`, `paths`, and other required fields\n")
        f.write("3. **Info Object**: Checks for `title` and `version` fields\n")
        f.write("4. **Paths**: Validates path structure and operation definitions\n")
        f.write("5. **References**: Checks for unresolved or external `$ref` references\n")
        f.write("6. **Servers**: Validates server definitions\n")
        f.write("7. **Components**: Checks schema definitions if present\n\n")
        
        f.write("## Recommendations\n\n")
        
        all_passed = all(success for _, _, success, _ in results)
        
        if all_passed:
            f.write("✓ All specs passed validation and should load successfully in Swagger UI.\n\n")
            f.write("**Next Steps:**\n")
            f.write("- Test the spec in a live Swagger UI instance using one of the methods above\n")
            f.write("- Verify that all endpoints are displayed correctly\n")
            f.write("- Test the 'Try it out' functionality for sample operations\n")
        else:
            f.write("⚠ Some issues were found that may affect Swagger UI loading.\n\n")
            f.write("**Next Steps:**\n")
            f.write("- Review and fix the issues listed above\n")
            f.write("- Re-run validation after fixes\n")
            f.write("- Test in Swagger UI to confirm issues are resolved\n")
        
        f.write("\n## Test Execution Details\n\n")
        f.write(f"- **Test Date**: {Path(__file__).stat().st_mtime}\n")
        f.write(f"- **Specs Tested**: {len(results)}\n")
        f.write(f"- **Passed**: {sum(1 for _, _, success, _ in results if success)}\n")
        f.write(f"- **Failed**: {sum(1 for _, _, success, _ in results if not success)}\n")
    
    print(f"\n✓ Report generated: {report_path}")
    
    # Return exit code
    all_passed = all(success for _, _, success, _ in results)
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
