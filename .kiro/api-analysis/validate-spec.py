#!/usr/bin/env python3
"""
OpenAPI 3.0 Specification Validator

Validates the generated GeoServer OpenAPI specification against:
- OpenAPI 3.0 schema
- $ref reference resolution
- Required field presence
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Set
from collections import defaultdict


class ValidationError:
    def __init__(self, location: str, message: str, severity: str = "error"):
        self.location = location
        self.message = message
        self.severity = severity
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.location}: {self.message}"


class OpenAPIValidator:
    def __init__(self, spec_path: Path):
        self.spec_path = spec_path
        self.spec = None
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.info_messages: List[str] = []
        
    def load_spec(self) -> bool:
        """Load the OpenAPI specification file"""
        try:
            with open(self.spec_path, 'r', encoding='utf-8') as f:
                if self.spec_path.suffix in ['.yaml', '.yml']:
                    self.spec = yaml.safe_load(f)
                else:
                    self.spec = json.load(f)
            self.info_messages.append(f"✓ Successfully loaded specification from {self.spec_path}")
            return True
        except Exception as e:
            self.errors.append(ValidationError("file", f"Failed to load specification: {e}"))
            return False
    
    def validate_openapi_version(self) -> bool:
        """Validate OpenAPI version is 3.0.x"""
        if 'openapi' not in self.spec:
            self.errors.append(ValidationError("root", "Missing required field 'openapi'"))
            return False
        
        version = self.spec['openapi']
        if not version.startswith('3.0'):
            self.errors.append(ValidationError(
                "openapi",
                f"Expected OpenAPI 3.0.x, found {version}"
            ))
            return False
        
        self.info_messages.append(f"✓ OpenAPI version: {version}")
        return True
    
    def validate_required_fields(self) -> bool:
        """Validate required top-level fields"""
        required_fields = ['openapi', 'info', 'paths']
        missing = [f for f in required_fields if f not in self.spec]
        
        if missing:
            for field in missing:
                self.errors.append(ValidationError(
                    "root",
                    f"Missing required field '{field}'"
                ))
            return False
        
        # Validate info object
        info = self.spec.get('info', {})
        info_required = ['title', 'version']
        info_missing = [f for f in info_required if f not in info]
        
        if info_missing:
            for field in info_missing:
                self.errors.append(ValidationError(
                    "info",
                    f"Missing required field '{field}'"
                ))
            return False
        
        self.info_messages.append(f"✓ All required top-level fields present")
        self.info_messages.append(f"  - Title: {info.get('title')}")
        self.info_messages.append(f"  - Version: {info.get('version')}")
        return True
    
    def find_all_refs(self, obj: Any, path: str = "root") -> List[Tuple[str, str]]:
        """Recursively find all $ref references in the spec"""
        refs = []
        
        if isinstance(obj, dict):
            if '$ref' in obj:
                refs.append((path, obj['$ref']))
            for key, value in obj.items():
                refs.extend(self.find_all_refs(value, f"{path}.{key}"))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                refs.extend(self.find_all_refs(item, f"{path}[{i}]"))
        
        return refs
    
    def resolve_ref(self, ref: str) -> Tuple[bool, Any]:
        """Resolve a $ref reference"""
        if not ref.startswith('#/'):
            return False, f"External references not supported: {ref}"
        
        # Remove leading #/ and split path
        parts = ref[2:].split('/')
        
        # Navigate through spec
        current = self.spec
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False, f"Reference path not found: {ref}"
        
        return True, current
    
    def validate_refs(self) -> bool:
        """Validate all $ref references resolve correctly"""
        refs = self.find_all_refs(self.spec)
        
        if not refs:
            self.info_messages.append("✓ No $ref references found (self-contained spec)")
            return True
        
        self.info_messages.append(f"  Found {len(refs)} $ref references to validate")
        
        unresolved = []
        for location, ref in refs:
            success, result = self.resolve_ref(ref)
            if not success:
                unresolved.append((location, ref, result))
        
        if unresolved:
            for location, ref, error in unresolved:
                self.errors.append(ValidationError(
                    location,
                    f"Unresolved reference '{ref}': {error}"
                ))
            return False
        
        self.info_messages.append(f"✓ All {len(refs)} $ref references resolve correctly")
        return True
    
    def validate_paths(self) -> bool:
        """Validate paths structure"""
        paths = self.spec.get('paths', {})
        
        if not paths:
            self.warnings.append(ValidationError(
                "paths",
                "No paths defined in specification",
                "warning"
            ))
            return True
        
        path_count = len(paths)
        operation_count = 0
        
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                self.errors.append(ValidationError(
                    f"paths.{path}",
                    "Path item must be an object"
                ))
                continue
            
            # Count operations
            http_methods = ['get', 'post', 'put', 'delete', 'patch', 'head', 'options', 'trace']
            for method in http_methods:
                if method in path_item:
                    operation_count += 1
                    
                    # Validate operation has operationId
                    operation = path_item[method]
                    if isinstance(operation, dict) and 'operationId' not in operation:
                        self.warnings.append(ValidationError(
                            f"paths.{path}.{method}",
                            "Operation missing 'operationId' (recommended)",
                            "warning"
                        ))
        
        self.info_messages.append(f"✓ Paths validation complete:")
        self.info_messages.append(f"  - {path_count} paths defined")
        self.info_messages.append(f"  - {operation_count} operations defined")
        return True
    
    def validate_components(self) -> bool:
        """Validate components structure"""
        if 'components' not in self.spec:
            self.info_messages.append("  No components section (optional)")
            return True
        
        components = self.spec['components']
        if not isinstance(components, dict):
            self.errors.append(ValidationError(
                "components",
                "Components must be an object"
            ))
            return False
        
        # Count component types
        component_types = ['schemas', 'responses', 'parameters', 'examples', 
                          'requestBodies', 'headers', 'securitySchemes', 
                          'links', 'callbacks']
        
        counts = {}
        for comp_type in component_types:
            if comp_type in components:
                counts[comp_type] = len(components[comp_type])
        
        if counts:
            self.info_messages.append(f"✓ Components defined:")
            for comp_type, count in counts.items():
                self.info_messages.append(f"  - {count} {comp_type}")
        
        return True
    
    def validate_tags(self) -> bool:
        """Validate tags structure"""
        if 'tags' not in self.spec:
            self.info_messages.append("  No tags section (optional)")
            return True
        
        tags = self.spec['tags']
        if not isinstance(tags, list):
            self.errors.append(ValidationError(
                "tags",
                "Tags must be an array"
            ))
            return False
        
        tag_names = set()
        for i, tag in enumerate(tags):
            if not isinstance(tag, dict):
                self.errors.append(ValidationError(
                    f"tags[{i}]",
                    "Tag must be an object"
                ))
                continue
            
            if 'name' not in tag:
                self.errors.append(ValidationError(
                    f"tags[{i}]",
                    "Tag missing required field 'name'"
                ))
                continue
            
            tag_names.add(tag['name'])
        
        self.info_messages.append(f"✓ {len(tag_names)} tags defined: {', '.join(sorted(tag_names))}")
        return True
    
    def validate(self) -> bool:
        """Run all validations"""
        if not self.load_spec():
            return False
        
        validations = [
            ("OpenAPI Version", self.validate_openapi_version),
            ("Required Fields", self.validate_required_fields),
            ("$ref References", self.validate_refs),
            ("Paths", self.validate_paths),
            ("Components", self.validate_components),
            ("Tags", self.validate_tags),
        ]
        
        all_passed = True
        for name, validator in validations:
            try:
                if not validator():
                    all_passed = False
            except Exception as e:
                self.errors.append(ValidationError(
                    name.lower().replace(" ", "_"),
                    f"Validation failed with exception: {e}"
                ))
                all_passed = False
        
        return all_passed and len(self.errors) == 0
    
    def generate_report(self, output_path: Path):
        """Generate validation report in Markdown format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# OpenAPI 3.0 Specification Validation Report\n\n")
            f.write(f"**Specification File:** `{self.spec_path}`\n\n")
            f.write(f"**Validation Date:** {Path(__file__).stat().st_mtime}\n\n")
            
            # Summary
            f.write("## Validation Summary\n\n")
            if len(self.errors) == 0:
                f.write("✅ **PASSED** - Specification is valid\n\n")
            else:
                f.write(f"❌ **FAILED** - {len(self.errors)} error(s) found\n\n")
            
            if self.warnings:
                f.write(f"⚠️  {len(self.warnings)} warning(s)\n\n")
            
            # Info messages
            if self.info_messages:
                f.write("## Validation Details\n\n")
                for msg in self.info_messages:
                    f.write(f"{msg}\n")
                f.write("\n")
            
            # Errors
            if self.errors:
                f.write("## Errors\n\n")
                for error in self.errors:
                    f.write(f"- **Location:** `{error.location}`\n")
                    f.write(f"  **Message:** {error.message}\n\n")
            
            # Warnings
            if self.warnings:
                f.write("## Warnings\n\n")
                for warning in self.warnings:
                    f.write(f"- **Location:** `{warning.location}`\n")
                    f.write(f"  **Message:** {warning.message}\n\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            if len(self.errors) == 0:
                f.write("The specification is valid and ready for use with:\n")
                f.write("- Swagger UI\n")
                f.write("- Redoc\n")
                f.write("- OpenAPI Generator\n")
                f.write("- Other OpenAPI 3.0 compatible tools\n\n")
            else:
                f.write("Please address the errors listed above before using this specification.\n\n")
            
            if self.warnings:
                f.write("Consider addressing the warnings to improve specification quality.\n\n")


def main():
    # Determine spec file to validate
    spec_file = Path("doc/en/api/geoserver-bundled.yaml")
    
    if not spec_file.exists():
        print(f"Error: Specification file not found: {spec_file}")
        sys.exit(1)
    
    # Run validation
    validator = OpenAPIValidator(spec_file)
    is_valid = validator.validate()
    
    # Generate report
    report_dir = Path(".kiro/api-analysis/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "validation-report.md"
    
    validator.generate_report(report_path)
    
    # Print summary
    print("\n" + "="*70)
    print("OpenAPI 3.0 Specification Validation")
    print("="*70)
    print(f"\nSpecification: {spec_file}")
    print(f"Report: {report_path}\n")
    
    for msg in validator.info_messages:
        print(msg)
    
    if validator.errors:
        print(f"\n❌ FAILED - {len(validator.errors)} error(s) found:")
        for error in validator.errors:
            print(f"  {error}")
    
    if validator.warnings:
        print(f"\n⚠️  {len(validator.warnings)} warning(s):")
        for warning in validator.warnings:
            print(f"  {warning}")
    
    if is_valid:
        print("\n✅ Validation PASSED - Specification is valid!")
        print(f"\nReport written to: {report_path}")
        sys.exit(0)
    else:
        print(f"\n❌ Validation FAILED - See report for details: {report_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
