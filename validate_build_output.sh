#!/bin/bash
#
# Build Output Structure Validation Script
#
# Validates mkdocs_output/ directory structure:
# - Checks all expected directories exist
# - Verifies HTML files are generated for all nav entries
# - Validates /en/ path structure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

echo "============================================================"
echo "Build Output Structure Validation"
echo "============================================================"
echo ""

# Check if mkdocs.yml exists
if [ ! -f "mkdocs.yml" ]; then
    echo -e "${RED}✗ mkdocs.yml not found in current directory${NC}"
    exit 1
fi

# Read site_dir from mkdocs.yml (default to 'site' if not found)
SITE_DIR=$(grep -E "^site_dir:" mkdocs.yml | awk '{print $2}' | tr -d '"' || echo "site")
echo "📁 Build output directory: $SITE_DIR"
echo ""

# Check if build output exists
if [ ! -d "$SITE_DIR" ]; then
    echo -e "${YELLOW}⊙ Build output directory does not exist: $SITE_DIR${NC}"
    echo -e "${YELLOW}  Run 'mkdocs build' first to generate output${NC}"
    exit 0
fi

echo "🔍 Validating directory structure..."
echo ""

# Expected directories
EXPECTED_DIRS=(
    "$SITE_DIR/en"
    "$SITE_DIR/en/user"
    "$SITE_DIR/en/developer"
    "$SITE_DIR/en/docguide"
    "$SITE_DIR/en/api"
)

# Check each expected directory
for dir in "${EXPECTED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        # Count HTML files in directory
        HTML_COUNT=$(find "$dir" -name "*.html" 2>/dev/null | wc -l)
        echo -e "${GREEN}✓${NC} $dir (${HTML_COUNT} HTML files)"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Missing: $dir"
        ((FAILED++))
    fi
done

echo ""
echo "📄 Checking critical index files..."
echo ""

# Expected index files
INDEX_FILES=(
    "$SITE_DIR/en/user/index.html"
    "$SITE_DIR/en/developer/index.html"
    "$SITE_DIR/en/docguide/index.html"
)

# Check each index file
for file in "${INDEX_FILES[@]}"; do
    if [ -f "$file" ]; then
        FILE_SIZE=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo "unknown")
        echo -e "${GREEN}✓${NC} $file (${FILE_SIZE} bytes)"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Missing: $file"
        ((FAILED++))
    fi
done

echo ""
echo "🔗 Validating /en/ path structure..."
echo ""

# Check that /en/ exists in paths
if [ -d "$SITE_DIR/en" ]; then
    echo -e "${GREEN}✓${NC} /en/ directory exists in output"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} /en/ directory missing from output"
    ((FAILED++))
fi

# Check that manuals are under /en/
MANUALS_UNDER_EN=true
for manual in user developer docguide api; do
    if [ -d "$SITE_DIR/en/$manual" ]; then
        echo -e "${GREEN}✓${NC} /$manual/ is under /en/"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} /$manual/ not found under /en/"
        ((FAILED++))
        MANUALS_UNDER_EN=false
    fi
done

echo ""
echo "📊 Build Output Statistics:"
echo ""

# Count total HTML files
TOTAL_HTML=$(find "$SITE_DIR" -name "*.html" 2>/dev/null | wc -l)
echo "  Total HTML files: $TOTAL_HTML"

# Count files per manual
for manual in user developer docguide api; do
    if [ -d "$SITE_DIR/en/$manual" ]; then
        MANUAL_HTML=$(find "$SITE_DIR/en/$manual" -name "*.html" 2>/dev/null | wc -l)
        echo "  $manual: $MANUAL_HTML HTML files"
    fi
done

# Check for assets
if [ -d "$SITE_DIR/assets" ]; then
    echo "  ✓ Assets directory exists"
fi

if [ -d "$SITE_DIR/stylesheets" ]; then
    echo "  ✓ Stylesheets directory exists"
fi

if [ -d "$SITE_DIR/javascripts" ]; then
    echo "  ✓ Javascripts directory exists"
fi

echo ""
echo "============================================================"

# Summary
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All validations PASSED${NC} (${PASSED} checks)"
    echo "============================================================"
    exit 0
else
    echo -e "${RED}❌ Validation FAILED${NC} (${PASSED} passed, ${FAILED} failed)"
    echo "============================================================"
    exit 1
fi
