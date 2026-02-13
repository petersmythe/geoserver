def extract_annotation_value(annotation_text: str, key: str) -> Optional[str]:
    """Extract a value from an annotation by key (e.g., 'path', 'value')."""
    # Handle both path= and value=
    # Pattern 1: Simple string value
    simple_pattern = rf'{key}\s*=\s*"([^"]*)"'
    match = re.search(simple_pattern, annotation_text)
    if match:
        return match.group(1).strip()
    
    # Pattern 2: Array of strings - need to handle nested braces carefully
    # Match: key = {"string1", "string2", ...}
    array_pattern = rf'{key}\s*=\s*\{{([^}}]+)\}}'
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
    bare_pattern = rf'{key}\s*=\s*([^,\)\s]+)'
    match = re.search(bare_pattern, annotation_text)
    if match:
        value = match.group(1).strip()
        # Remove quotes if present
        value = value.strip('"').strip("'")
        return value
    
    return None
