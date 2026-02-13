#!/usr/bin/env python3
"""
Fix path extraction bug in all REST endpoint extraction scripts.

The bug: regex pattern for extracting path arrays doesn't handle nested braces correctly.
This causes paths like {"/styles/{styleName}"} to be extracted as "/styles/{styleName" (missing closing brace).

Fix: Use a more robust regex that properly handles nested braces.
"""

import re
from pathlib import Path

def fix_extract_annotation_value_function(content: str) -> str:
    """Fix the extract_annotation_value function in extraction scripts."""
    
    # Find the function
    pattern = r'(def extract_annotation_value\(annotation_text: str, key: str\) -> Optional\[str\]:.*?""".*?""")(.*?)((?=\ndef )|(?=\nclass )|$)'
    
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print("  Could not find extract_annotation_value function")
        return content
    
    function_header = match.group(1)
    function_body = match.group(2)
    after_function = match.group(3)
    
    # New improved function body
    new_function_body = '''
    # Handle both path= and value=
    # Pattern 1: Simple string value
    simple_pattern = rf'{key}\\s*=\\s*"([^"]*)"'
    match = re.search(simple_pattern, annotation_text)
    if match:
        return match.group(1).strip()
    
    # Pattern 2: Array of strings - need to handle nested braces carefully
    # Match: key = {"string1", "string2", ...}
    array_pattern = rf'{key}\\s*=\\s*\\{{([^}}]+)\\}}'
    match = re.search(array_pattern, annotation_text)
    if match:
        array_content = match.group(1)
        # Extract all quoted strings from the array
        string_pattern = r'"([^"]*)"'
        strings = re.findall(string_pattern, array_content)
        if strings:
            # Return first non-empty string
            return next((s for s in strings if s), '')
    
    # Pattern 3: Single value without quotes
    bare_pattern = rf'{key}\\s*=\\s*([^,\\)\\s]+)'
    match = re.search(bare_pattern, annotation_text)
    if match:
        value = match.group(1).strip()
        # Remove quotes if present
        value = value.strip('"').strip("'")
        return value
    
    return None
'''
    
    return function_header + new_function_body + after_function


def fix_script(script_path: Path) -> bool:
    """Fix a single extraction script."""
    print(f"Fixing {script_path.name}...")
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already fixed
        if 'Extract all quoted strings from the array' in content:
            print(f"  Already fixed, skipping")
            return False
        
        # Apply fix
        fixed_content = fix_extract_annotation_value_function(content)
        
        if fixed_content == content:
            print(f"  No changes made")
            return False
        
        # Write back
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"  ✓ Fixed successfully")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Fix all extraction scripts."""
    print("=" * 60)
    print("Fixing Path Extraction Bug in REST Endpoint Scripts")
    print("=" * 60)
    print()
    
    scripts = [
        '.kiro/api-analysis/extract-core-rest-endpoints.py',
        '.kiro/api-analysis/extract-service-rest-endpoints.py',
        '.kiro/api-analysis/extract-gwc-rest-endpoints.py',
        '.kiro/api-analysis/extract-extension-rest-endpoints.py',
        '.kiro/api-analysis/extract-community-rest-endpoints.py',
    ]
    
    fixed_count = 0
    for script_path in scripts:
        path = Path(script_path)
        if path.exists():
            if fix_script(path):
                fixed_count += 1
        else:
            print(f"Script not found: {script_path}")
    
    print()
    print("=" * 60)
    print(f"✓ Fixed {fixed_count} scripts")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Re-run tasks 4.2-4.6 to extract endpoints with fixed paths")
    print("2. Re-run task 4.7 to consolidate endpoints")
    print("3. Re-run task 14 to regenerate OpenAPI specs")
    print("4. Re-run task 15.1 to validate specs")


if __name__ == '__main__':
    main()
