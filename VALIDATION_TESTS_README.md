# MkDocs Validation Tests

This directory contains three validation scripts for the consolidated MkDocs configuration. These scripts validate different aspects of the unified documentation build.

## Scripts

### 1. validate_mkdocs_config.py

**Purpose**: Validates the mkdocs.yml configuration file structure and content.

**What it checks**:
- YAML file can be parsed successfully
- Required fields are present (site_name, docs_dir, theme, nav)
- Theme is set to 'material'
- Navigation tabs features are enabled
- Custom theme directory exists
- All navigation paths exist in the filesystem
- All paths have the correct 'en/' prefix
- Expected navigation tabs are present (User Manual, Developer Guide, Documentation Guide, API Reference)

**Requirements validated**: 1.1, 3.4

**Usage**:
```bash
# Activate virtual environment
source .venv/Scripts/activate

# Run validation
python validate_mkdocs_config.py
```

**Exit codes**:
- 0: All checks passed
- 1: Validation failed

### 2. validate_path_resolution.py

**Purpose**: Validates source-to-output path mapping and URL structure.

**What it checks**:
- docs_dir configuration is correct
- Source paths map correctly to output paths
- /en/ is preserved in all output paths
- Expected output directory structure exists (en/user/, en/developer/, en/docguide/, en/api/)
- Sample output files exist in correct locations

**Requirements validated**: 2.1, 4.1, 4.2

**Usage**:
```bash
# Activate virtual environment
source .venv/Scripts/activate

# Run validation
python validate_path_resolution.py
```

**Exit codes**:
- 0: All checks passed
- 1: Validation failed

**Note**: This script will show warnings if the build output doesn't exist yet. Run `mkdocs build` first to generate the output.

### 3. validate_build_output.sh

**Purpose**: Validates the generated build output structure.

**What it checks**:
- mkdocs_output/ directory exists
- Expected directory structure (en/user/, en/developer/, en/docguide/, en/api/)
- Index files exist for all manuals
- HTML files are under the en/ directory
- No unexpected directories at root level
- File counts for each manual
- Navigation tabs feature is present in generated HTML
- All four expected tabs are present in the HTML

**Requirements validated**: 1.2, 1.3

**Usage**:
```bash
# Make script executable (first time only)
chmod +x validate_build_output.sh

# Run validation
./validate_build_output.sh
```

**Exit codes**:
- 0: All checks passed
- 1: Validation failed

**Note**: This script requires the build output to exist. Run `mkdocs build` first.

## Running All Validations

To run all three validation scripts in sequence:

```bash
# Activate virtual environment
source .venv/Scripts/activate

# Run all validations
echo "=== Running YAML Configuration Validation ==="
python validate_mkdocs_config.py
echo ""
echo "=== Running Path Resolution Validation ==="
python validate_path_resolution.py
echo ""
echo "=== Running Build Output Validation ==="
./validate_build_output.sh
```

## Integration with CI/CD

These scripts can be integrated into GitHub Actions workflows:

```yaml
- name: Validate MkDocs Configuration
  run: |
    source .venv/Scripts/activate
    python validate_mkdocs_config.py

- name: Build Documentation
  run: mkdocs build

- name: Validate Path Resolution
  run: |
    source .venv/Scripts/activate
    python validate_path_resolution.py

- name: Validate Build Output
  run: ./validate_build_output.sh
```

## Expected Output

When all validations pass, you should see:

```
✓ All validation checks passed!
```

If there are errors, the scripts will display detailed error messages indicating what failed and where.

## Troubleshooting

### "Output directory not found"
- Run `mkdocs build` to generate the output before running path resolution or build output validation

### "Missing files referenced in nav"
- Check that all files referenced in mkdocs.yml exist in the doc/ directory
- Verify file paths are correct and use forward slashes

### "Navigation tabs feature not detected"
- Ensure theme.features includes 'navigation.tabs' and 'navigation.tabs.sticky'
- Check that the Material theme is properly installed

### "Path mapping mismatch"
- Verify docs_dir is set to 'doc' in mkdocs.yml
- Check that source files are in the correct location under doc/en/
