# Markdown Conversion Cleanup Bugfix Design

## Overview

The RST to Markdown migration for GeoServer documentation used automated conversion tools (likely pandoc or similar) that introduced systematic formatting issues across 200+ pages. These issues stem from fundamental differences between RST and Markdown syntax, combined with conversion tool limitations in handling complex nested structures, admonitions, and tables.

This bugfix addresses 30 distinct bug conditions organized into 9 categories. The root causes are primarily:
1. Automated conversion tool misinterpretation of RST directives
2. Indentation-based syntax differences between RST and Markdown
3. Lack of direct Markdown equivalents for RST constructs (admonitions, definition lists)
4. Complex nested structure handling failures
5. Table cell content with newlines/lists breaking Markdown table syntax

The fix strategy combines automated pattern-based corrections for systematic issues with manual review for complex cases requiring human judgment.

## Glossary

- **Bug_Condition (C)**: The condition that triggers rendering issues - when specific RST constructs are converted to Markdown incorrectly
- **Property (P)**: The desired behavior - Markdown renders identically to original RST documentation
- **Preservation**: Correctly converted Markdown pages that must remain unchanged
- **Pandoc**: Likely conversion tool used for RST to Markdown migration
- **Admonition**: RST directive for notes/warnings (.. note::, .. warning::) that needs MkDocs admonition syntax (!!! note, !!! warning)
- **Definition List**: RST construct using indented ": text" that has no direct Markdown equivalent
- **Blockquote**: Markdown construct using ">" prefix, often incorrectly applied by converter to indented RST content
- **MkDocs**: Static site generator used for rendering Markdown documentation

## Bug Details

### Bug Condition

The bugs manifest when the automated RST to Markdown conversion tool encounters specific RST constructs and produces incorrect Markdown syntax. The conversion failures fall into systematic patterns based on RST construct types.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type MarkdownFile
  OUTPUT: boolean
  
  RETURN (hasNavigationTitleMismatch(input) OR
          hasCodeFormattingIssue(input) OR
          hasListNestingIssue(input) OR
          hasAdmonitionIssue(input) OR
          hasImageCaptionIssue(input) OR
          hasTableStructureIssue(input) OR
          hasLinkAnchorIssue(input) OR
          hasIndentationIssue(input) OR
          hasHeadingStructureIssue(input))
END FUNCTION
```

### Examples

**Navigation Issues:**
- Page title "Data settings" in content but "webadmin" in navigation tree
- Page title displays as "path/index" instead of human-readable name
- "Table of contents" label used instead of "Page contents"

**Code Formatting:**
- YAML/JSON blocks render as plain text without syntax highlighting
- Inline code in nested lists renders as verbatim text without backticks
- Code sections lose fencing and render as plain paragraphs

**List Nesting:**
- Nested list items lose indentation and appear at wrong level
- Images within list items render as code blocks
- List items with indented content incorrectly render as blockquotes

**Admonitions:**
- RST ".. note::" converts to blockquote instead of "!!! note"
- Visible "!!! warning" syntax appears in rendered output
- Admonitions in table cells break table structure

**Tables:**
- Lists in table cells split across multiple cells
- Multi-line cell content splits into separate cells
- Empty rows appear where content existed in RST

**Edge Cases:**
- Definition list syntax ": - text" renders as malformed text
- Low-level subsection headings disappear from visual hierarchy
- Include statements fail and display as malformed syntax

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Pages without formatting issues must continue to render correctly
- Correctly formatted code blocks must maintain syntax highlighting
- Correctly formatted tables must preserve structure
- Correctly formatted lists must maintain nesting
- Correctly formatted images must display properly
- Correctly formatted links must resolve correctly
- MkDocs configuration must continue to work
- Navigation structure must function properly
- Page metadata must be preserved
- Build process must complete successfully

**Scope:**
All Markdown files that were correctly converted and render properly should be completely unaffected by this fix. This includes pages that don't use complex RST constructs like nested lists, admonitions, or complex tables.

## Hypothesized Root Cause

Based on Andrea's comprehensive review and the systematic nature of the issues, the root causes are:

### 1. Navigation and Title Issues (Bugs 1.1-1.4)

**Root Cause**: MkDocs navigation configuration (mkdocs.yml) not updated to match new Markdown file structure
- Conversion tool didn't update nav entries to use proper page titles
- Index files not properly configured with title metadata
- MkDocs theme configuration using wrong labels for TOC

**Evidence**: Systematic across all pages with index structure, not random

### 2. Code Formatting Issues (Bugs 1.5-1.8)

**Root Cause**: Pandoc's inconsistent handling of RST code blocks and literal blocks
- RST "::" literal block marker sometimes converted to fenced code blocks, sometimes not
- Language hints in RST not always preserved in Markdown fence info strings
- Inline code using RST backticks not consistently converted to Markdown backticks
- Indented code blocks in RST converted to plain indented text

**Evidence**: Spotty application suggests conditional logic in converter based on context

### 3. List and Nesting Issues (Bugs 1.9-1.13)

**Root Cause**: RST uses indentation for nesting, Markdown requires specific spacing (2-4 spaces)
- Converter used inconsistent indentation (sometimes tabs, sometimes wrong space count)
- Images in lists require specific indentation in Markdown that converter didn't apply
- Indented content within list items interpreted as blockquotes due to indentation rules
- Numbered lists with complex content flattened when converter couldn't determine structure
- Empty list items suggest content parsing failures

**Evidence**: All nesting issues relate to indentation handling

### 4. Admonition and Note Issues (Bugs 1.14-1.16)

**Root Cause**: RST admonitions (.. note::, .. warning::) have no standard Markdown equivalent
- Converter defaulted to blockquotes (>) as closest Markdown construct
- Some attempts to use MkDocs admonition syntax (!!! note) failed due to incorrect formatting
- Admonitions in tables break because Markdown tables can't contain block-level elements

**Evidence**: Systematic conversion of all RST directives to blockquotes or malformed admonitions

### 5. Image and Caption Issues (Bugs 1.17-1.18)

**Root Cause**: RST figure directive with captions has no direct Markdown equivalent
- Converter used HTML figure tags or Markdown image syntax without caption support
- Caption placement controlled by CSS not properly configured for MkDocs theme
- Images wrapped in blockquotes due to indentation in original RST

**Evidence**: All images with captions show same left-alignment issue

### 6. Table Issues (Bugs 1.19-1.23)

**Root Cause**: Markdown tables are fundamentally limited compared to RST tables
- Markdown table cells cannot contain newlines (must use <br> or HTML)
- Markdown table cells cannot contain block-level elements (lists, code blocks)
- Converter attempted to preserve RST table structure but Markdown syntax broke
- Complex tables with merged cells or nested content cannot be represented in Markdown

**Evidence**: All table issues involve multi-line or block-level content in cells

### 7. Link and Anchor Issues (Bugs 1.24-1.25)

**Root Cause**: RST reference syntax and include directives not properly converted
- RST `:ref:` role converted to plain text instead of Markdown links
- RST `.. include::` directive has no Markdown equivalent
- Anchor targets in RST not converted to Markdown anchor syntax

**Evidence**: Visible link syntax like "[Cache]" indicates incomplete conversion

### 8. Indentation and Whitespace Issues (Bugs 1.26-1.28)

**Root Cause**: RST definition lists and indented blocks misinterpreted by converter
- RST definition list syntax (term followed by indented ": definition") has no Markdown equivalent
- Converter interpreted indented paragraphs as code blocks (4+ spaces triggers code block in Markdown)
- Definition syntax ": - text" not recognized, rendered literally

**Evidence**: All issues involve RST constructs starting with ":" or indentation

### 9. Heading and Structure Issues (Bugs 1.29-1.30)

**Root Cause**: RST heading levels and block quote syntax not properly mapped
- RST supports more heading levels than Markdown (6 levels)
- RST block quotes (indented text) converted to code blocks instead of Markdown blockquotes (>)
- Low-level headings may have used RST-specific syntax not supported in Markdown

**Evidence**: Systematic issues with deep heading hierarchies and quoted specification text

## Correctness Properties

Property 1: Bug Condition - Markdown Renders Correctly

_For any_ Markdown file where the bug condition holds (isBugCondition returns true), the fixed Markdown SHALL render identically to the original RST documentation, with proper formatting for navigation, code blocks, lists, admonitions, images, tables, links, indentation, and headings.

**Validates: Requirements 2.1-2.30**

Property 2: Preservation - Unchanged Markdown Files

_For any_ Markdown file where the bug condition does NOT hold (isBugCondition returns false), the fixed documentation SHALL produce exactly the same rendered output as before the fix, preserving all correctly converted pages.

**Validates: Requirements 3.1-3.10**

## Fix Implementation

### Changes Required

The fix requires a multi-phase approach combining automated corrections with manual review:

### Phase 1: Automated Pattern-Based Fixes

**File**: Multiple Markdown files across `doc/en/` directory tree

**Automated Fix Categories**:

1. **Navigation Configuration** (Bugs 1.1-1.4)
   - Update `mkdocs.yml` nav entries to use proper page titles from front matter
   - Add title metadata to index.md files
   - Update MkDocs theme configuration to use "Page contents" instead of "Table of contents"
   - Add "Section contents" labels for major sections

2. **Code Block Fencing** (Bugs 1.5, 1.7, 1.8)
   - Pattern: Find indented code blocks without fencing
   - Replace with fenced code blocks using ``` with appropriate language hints
   - Add language identifiers (yaml, json, xml, bash, python) based on content analysis
   - Preserve existing correctly fenced blocks

3. **Inline Code in Lists** (Bug 1.6)
   - Pattern: Find verbatim text in nested list items matching code patterns
   - Wrap with backticks for inline code formatting
   - Preserve list indentation

4. **Admonition Conversion** (Bugs 1.14-1.15)
   - Pattern: Find blockquotes that were RST admonitions (look for "Note:", "Warning:" at start)
   - Convert to MkDocs admonition syntax: `!!! note` or `!!! warning`
   - Indent content properly (4 spaces after admonition marker)
   - Pattern: Find visible `!!! warning` in code blocks, convert to proper admonitions

5. **Image Caption Alignment** (Bug 1.17)
   - Pattern: Find image + caption combinations
   - Wrap in HTML figure tags with proper CSS classes
   - Or use MkDocs-specific caption syntax if available

6. **Blockquote Removal from Images** (Bug 1.18)
   - Pattern: Find images wrapped in blockquote syntax (> ![...])
   - Remove blockquote prefix, preserve image syntax

7. **Link Anchor Fixes** (Bug 1.24)
   - Pattern: Find dangling anchor references like "[Cache]"
   - Convert to proper Markdown link syntax [Cache](#anchor-target)
   - Generate anchor targets from heading text

8. **Definition List Conversion** (Bugs 1.27-1.28)
   - Pattern: Find ": - text" or indented ": text" patterns
   - Convert to Markdown lists or HTML definition lists
   - Remove leading colons and fix indentation

9. **Heading Level Fixes** (Bug 1.29)
   - Pattern: Find low-level headings (##### or deeper)
   - Ensure proper heading hierarchy (no skipped levels)
   - Convert to #### maximum depth if needed

10. **Blockquote Conversion** (Bug 1.30)
    - Pattern: Find code blocks containing quoted specification text
    - Convert to Markdown blockquotes using > prefix
    - Preserve formatting within blockquote

### Phase 2: Semi-Automated Fixes Requiring Review

**List Nesting Fixes** (Bugs 1.9-1.13)
- Script to detect and fix indentation issues
- Manual review required for complex nested structures
- Fix images in lists by adjusting indentation
- Fix blockquoted list content by removing > prefix and adjusting indentation
- Restore lost list item content from original RST files

**Table Fixes** (Bugs 1.19-1.23)
- Script to detect tables with complex content
- Options:
  a) Convert to HTML tables for complex cases
  b) Simplify content (convert lists to comma-separated text)
  c) Use <br> tags for multi-line content
  d) Split complex tables into multiple simpler tables
- Manual review required for each table to choose best approach

**Admonitions in Tables** (Bug 1.16)
- Script to detect admonitions within table cells
- Convert to simplified text or move admonition outside table
- Manual review required

**Include Statement Fixes** (Bug 1.25)
- Script to find failed include statements
- Options:
  a) Replace with actual content from included file
  b) Convert to MkDocs snippets extension if available
  c) Remove if content is redundant
- Manual review required

### Phase 3: Manual Review and Validation

**Complex Cases Requiring Human Judgment**:
- Pages with multiple overlapping issues
- Tables with very complex structure
- Nested lists with images and code blocks
- Custom RST directives not covered by automated fixes

**Validation Process**:
1. Build documentation with MkDocs
2. Visual comparison with original RST-rendered pages
3. Check all 200+ affected pages identified by Andrea
4. Verify navigation, search, and cross-references work
5. Test on multiple browsers and screen sizes

### Implementation Tools

**Automated Fix Script** (`fix_markdown_conversion.py`):
```python
# Python script using regex patterns and AST parsing
# - Scan all .md files in doc/en/
# - Apply pattern-based fixes
# - Generate report of changes
# - Create backup before modifications
```

**Manual Review Checklist** (`manual_review_checklist.md`):
- List of pages requiring manual review
- Specific issues to check on each page
- Sign-off tracking

**Validation Script** (`validate_markdown_fixes.py`):
- Compare rendered output before/after
- Check for broken links
- Verify all images load
- Validate table structure
- Check code block syntax highlighting

## Testing Strategy

### Validation Approach

The testing strategy follows a three-phase approach:
1. **Exploratory**: Surface counterexamples on unfixed Markdown to confirm root causes
2. **Fix Checking**: Verify fixed Markdown renders correctly
3. **Preservation Checking**: Verify unchanged Markdown still renders correctly

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bugs BEFORE implementing the fix. Confirm or refute the root cause analysis.

**Test Plan**: Build the current Markdown documentation and systematically compare rendered output against original RST documentation for all 200+ affected pages identified by Andrea.

**Test Cases**:
1. **Navigation Test**: Check 10 sample pages for title mismatches (will fail on unfixed Markdown)
2. **Code Formatting Test**: Check 20 sample pages for missing syntax highlighting (will fail on unfixed Markdown)
3. **List Nesting Test**: Check 15 sample pages for incorrect indentation (will fail on unfixed Markdown)
4. **Admonition Test**: Check 10 sample pages for blockquote vs admonition (will fail on unfixed Markdown)
5. **Table Test**: Check 15 sample pages for broken table structure (will fail on unfixed Markdown)
6. **Image Caption Test**: Check 10 sample pages for caption alignment (will fail on unfixed Markdown)

**Expected Counterexamples**:
- Navigation titles don't match between tree and page content
- Code blocks render as plain text without highlighting
- Nested lists lose indentation levels
- Notes render as blockquotes instead of styled admonitions
- Tables with lists in cells show broken structure
- Image captions appear beside images instead of below

**Root Cause Validation**:
- If counterexamples match predictions, proceed with automated fixes
- If counterexamples differ, re-analyze root causes and adjust fix strategy

### Fix Checking

**Goal**: Verify that for all Markdown files where the bug condition holds, the fixed Markdown produces the expected rendering.

**Pseudocode:**
```
FOR ALL markdownFile WHERE isBugCondition(markdownFile) DO
  fixedFile := applyFixes(markdownFile)
  renderedOutput := buildWithMkDocs(fixedFile)
  originalRSTOutput := getRSTRenderedVersion(markdownFile)
  ASSERT visuallyEquivalent(renderedOutput, originalRSTOutput)
END FOR
```

**Test Plan**: 
1. Apply automated fixes to all affected files
2. Build documentation with MkDocs
3. Use visual regression testing tool (e.g., Percy, BackstopJS) to compare before/after
4. Manual review of sample pages from each bug category

**Test Cases**:
1. **Navigation Fixes**: Verify all page titles match navigation tree entries
2. **Code Formatting Fixes**: Verify all code blocks have proper syntax highlighting
3. **List Nesting Fixes**: Verify all nested lists maintain proper indentation
4. **Admonition Fixes**: Verify all notes/warnings render as styled admonitions
5. **Table Fixes**: Verify all tables maintain structure with complex content
6. **Image Caption Fixes**: Verify all captions appear below images
7. **Link Fixes**: Verify all internal links resolve correctly
8. **Indentation Fixes**: Verify definition lists and indented content render correctly
9. **Heading Fixes**: Verify all headings appear in proper hierarchy

### Preservation Checking

**Goal**: Verify that for all Markdown files where the bug condition does NOT hold, the fixed documentation produces the same result as before the fix.

**Pseudocode:**
```
FOR ALL markdownFile WHERE NOT isBugCondition(markdownFile) DO
  originalOutput := buildWithMkDocs(markdownFile)
  fixedOutput := buildWithMkDocs(applyFixes(markdownFile))
  ASSERT originalOutput = fixedOutput
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates test cases across the entire documentation set
- It catches edge cases where fixes might inadvertently affect correct files
- It provides strong guarantees that correctly converted pages remain unchanged

**Test Plan**: 
1. Identify all Markdown files NOT in Andrea's affected page list
2. Build documentation before applying fixes
3. Build documentation after applying fixes
4. Compare rendered output using diff tools
5. Verify no changes in correctly formatted pages

**Test Cases**:
1. **Unaffected Pages**: Verify pages without issues render identically before/after
2. **Simple Pages**: Verify pages with only basic Markdown render identically
3. **Correct Code Blocks**: Verify properly formatted code blocks unchanged
4. **Correct Tables**: Verify simple tables without complex content unchanged
5. **Correct Lists**: Verify simple lists without nesting unchanged
6. **Correct Images**: Verify images without captions unchanged
7. **MkDocs Config**: Verify build process completes without errors
8. **Navigation**: Verify navigation structure functions properly
9. **Search**: Verify search index builds correctly
10. **Cross-References**: Verify internal links continue to work

### Unit Tests

- Test pattern matching for each bug category
- Test fix application for each bug type
- Test edge cases (empty files, malformed Markdown, mixed issues)
- Test backup and rollback functionality
- Test report generation

### Property-Based Tests

- Generate random Markdown files with various formatting
- Verify fixes only apply to files matching bug conditions
- Verify fixes don't corrupt valid Markdown syntax
- Test across many file variations to catch edge cases

### Integration Tests

- Build full documentation site before fixes
- Build full documentation site after fixes
- Compare rendered output for all pages
- Test navigation, search, and cross-references
- Test on multiple browsers (Chrome, Firefox, Safari)
- Test responsive design on mobile devices
- Performance testing (build time, page load time)
