# Implementation Plan

## Phase 1: Bug Condition Exploration Tests

These tests MUST be written BEFORE implementing any fixes. They will FAIL on unfixed code, confirming the bugs exist.

- [x] 1. Write bug condition exploration test for navigation and title issues
  - **Property 1: Bug Condition** - Navigation and Title Rendering Bugs
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate navigation/title bugs exist
  - **Scoped PBT Approach**: Test concrete failing cases from Andrea's feedback
  - Test that pages with "path/index" titles render with proper human-readable titles (Requirement 1.2, 2.2)
  - Test that page titles in content match navigation tree entries (Requirement 1.1, 2.1)
  - Test that "Table of contents" is labeled as "Page contents" (Requirement 1.3, 2.3)
  - Test that "Installation" section has clear hierarchy with "Section contents" label (Requirement 1.4, 2.4)
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found (e.g., "services/index shows 'path/index' instead of 'Services'")
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4_

- [x] 2. Write bug condition exploration test for code formatting issues
  - **Property 1: Bug Condition** - Code Formatting and Syntax Highlighting Bugs
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **GOAL**: Surface counterexamples demonstrating code formatting bugs
  - **Scoped PBT Approach**: Test concrete failing cases from Andrea's feedback
  - Test that code blocks have consistent syntax highlighting (Requirement 1.5, 2.5)
  - Test that inline code in nested lists renders with backticks (Requirement 1.6, 2.6)
  - Test that YAML/JSON blocks have syntax highlighting (Requirement 1.7, 2.7)
  - Test that code sections maintain code block formatting (Requirement 1.8, 2.8)
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (confirms bugs exist)
  - Document counterexamples (e.g., "importer/rest_examples page has code without highlighting")
  - _Requirements: 1.5, 1.6, 1.7, 1.8, 2.5, 2.6, 2.7, 2.8_


- [x] 3. Write bug condition exploration test for list and nesting issues
  - **Property 1: Bug Condition** - List and Nesting Structure Bugs
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **GOAL**: Surface counterexamples demonstrating list/nesting bugs
  - **Scoped PBT Approach**: Test concrete failing cases from Andrea's feedback
  - Test that nested list items maintain proper indentation (Requirement 1.9, 2.9)
  - Test that images in list items render as images, not code blocks (Requirement 1.10, 2.10)
  - Test that indented content in lists doesn't render as blockquotes (Requirement 1.11, 2.11)
  - Test that numbered lists maintain structure (Requirement 1.12, 2.12)
  - Test that list items retain all content (Requirement 1.13, 2.13)
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (confirms bugs exist)
  - Document counterexamples (e.g., "imagemosaic/tutorial has nested images rendered as code")
  - _Requirements: 1.9, 1.10, 1.11, 1.12, 1.13, 2.9, 2.10, 2.11, 2.12, 2.13_

- [x] 4. Write bug condition exploration test for admonition and note issues
  - **Property 1: Bug Condition** - Admonition Block Rendering Bugs
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **GOAL**: Surface counterexamples demonstrating admonition bugs
  - **Scoped PBT Approach**: Test concrete failing cases from Andrea's feedback
  - Test that RST note/warning blocks render as styled admonitions, not blockquotes (Requirement 1.14, 2.14)
  - Test that admonition blocks don't show visible syntax markers like "!!! warning" (Requirement 1.15, 2.15)
  - Test that admonitions in tables don't break table structure (Requirement 1.16, 2.16)
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (confirms bugs exist)
  - Document counterexamples (e.g., "wfs/axis_order shows '!!! warning' as code")
  - _Requirements: 1.14, 1.15, 1.16, 2.14, 2.15, 2.16_

- [x] 5. Write bug condition exploration test for image and caption issues
  - **Property 1: Bug Condition** - Image and Caption Rendering Bugs
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **GOAL**: Surface counterexamples demonstrating image/caption bugs
  - **Scoped PBT Approach**: Test concrete failing cases from Andrea's feedback
  - Test that image captions appear below images, not beside them (Requirement 1.17, 2.17)
  - Test that images don't have blockquote wrapping (Requirement 1.18, 2.18)
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (confirms bugs exist)
  - Document counterexamples (e.g., "win_installer page has captions left-aligned beside images")
  - _Requirements: 1.17, 1.18, 2.17, 2.18_

- [x] 6. Write bug condition exploration test for table structure issues
  - **Property 1: Bug Condition** - Table Structure and Content Bugs
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **GOAL**: Surface counterexamples demonstrating table bugs
  - **Scoped PBT Approach**: Test concrete failing cases from Andrea's feedback
  - Test that lists in table cells don't split across multiple cells (Requirement 1.19, 2.19)
  - Test that notes/admonitions in cells don't break table structure (Requirement 1.20, 2.20)
  - Test that multi-line cell content stays in single cells (Requirement 1.21, 2.21)
  - Test that complex tables maintain structure and alignment (Requirement 1.22, 2.22)
  - Test that tables don't have empty rows/cells that had content (Requirement 1.23, 2.23)
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (confirms bugs exist)
  - Document counterexamples (e.g., "imagemosaic/configuration table has list items split across cells")
  - _Requirements: 1.19, 1.20, 1.21, 1.22, 1.23, 2.19, 2.20, 2.21, 2.22, 2.23_

- [x] 7. Write bug condition exploration test for link and anchor issues
  - **Property 1: Bug Condition** - Link and Anchor Resolution Bugs
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **GOAL**: Surface counterexamples demonstrating link/anchor bugs
  - **Scoped PBT Approach**: Test concrete failing cases from Andrea's feedback
  - Test that internal links resolve correctly without visible syntax (Requirement 1.24, 2.24)
  - Test that include statements work or are replaced with content (Requirement 1.25, 2.25)
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (confirms bugs exist)
  - Document counterexamples (e.g., "app-schema/app-schema-resolution shows dangling '[Cache]' anchor")
  - _Requirements: 1.24, 1.25, 2.24, 2.25_

- [x] 8. Write bug condition exploration test for indentation and whitespace issues
  - **Property 1: Bug Condition** - Indentation and Whitespace Rendering Bugs
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **GOAL**: Surface counterexamples demonstrating indentation bugs
  - **Scoped PBT Approach**: Test concrete failing cases from Andrea's feedback
  - Test that indented paragraphs don't render as code blocks or blockquotes (Requirement 1.26, 2.26)
  - Test that definition list-style content renders properly (Requirement 1.27, 2.27)
  - Test that text starting with ": " converts to proper Markdown (Requirement 1.28, 2.28)
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (confirms bugs exist)
  - Document counterexamples (e.g., "app-schema/cql-functions has ': -' rendering as malformed text")
  - _Requirements: 1.26, 1.27, 1.28, 2.26, 2.27, 2.28_

- [x] 9. Write bug condition exploration test for heading and structure issues
  - **Property 1: Bug Condition** - Heading and Structure Rendering Bugs
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **GOAL**: Surface counterexamples demonstrating heading/structure bugs
  - **Scoped PBT Approach**: Test concrete failing cases from Andrea's feedback
  - Test that low-level subsection headings render with correct hierarchy (Requirement 1.29, 2.29)
  - Test that quoted specification text formats as blockquotes, not code (Requirement 1.30, 2.30)
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (confirms bugs exist)
  - Document counterexamples (e.g., "wms/vendor page has low-level titles rendering incorrectly")
  - _Requirements: 1.29, 1.30, 2.29, 2.30_

## Phase 2: Preservation Property Tests

These tests MUST be written BEFORE implementing fixes. They will PASS on unfixed code, establishing baseline behavior to preserve.

- [x] 10. Write preservation property tests for correctly formatted pages
  - **Property 2: Preservation** - Correctly Formatted Content Preservation
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for pages without formatting issues
  - Identify pages that render correctly (no issues reported by Andrea)
  - Write property-based tests capturing correct rendering patterns:
    - Pages with proper titles render correctly (Requirement 3.1)
    - Code blocks with proper highlighting continue to work (Requirement 3.2)
    - Correctly formatted tables maintain structure (Requirement 3.3)
    - Properly nested lists maintain indentation (Requirement 3.4)
    - Correctly formatted images display properly (Requirement 3.5)
    - Working links continue to resolve (Requirement 3.6)
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 11. Write preservation property tests for MkDocs configuration
  - **Property 2: Preservation** - MkDocs Configuration Preservation
  - **IMPORTANT**: Follow observation-first methodology
  - Observe current MkDocs configuration on UNFIXED code
  - Write property-based tests capturing configuration behavior:
    - MkDocs builds successfully without errors (Requirement 3.10)
    - Navigation structure functions properly (Requirement 3.8)
    - Page metadata is preserved (Requirement 3.9)
    - Theme and styling work correctly (Requirement 3.7)
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (confirms baseline to preserve)
  - _Requirements: 3.7, 3.8, 3.9, 3.10_


## Phase 3: Implementation - Automated Pattern-Based Fixes

### 3.1 Navigation and Title Fixes

- [ ] 12. Fix navigation and title issues

  - [x] 12.1 Create detection script for navigation/title issues
    - Scan all Markdown files for "path/index" in titles
    - Identify pages where title doesn't match navigation entry
    - Detect "Table of contents" vs "Page contents" labeling
    - Detect "Installation" section hierarchy issues
    - Generate report of affected files
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 12.2 Implement automated fix for "path/index" titles
    - Replace "path/index" patterns with human-readable titles
    - Extract proper title from navigation structure or file metadata
    - Update Markdown frontmatter if needed
    - _Bug_Condition: Page title displays as "path/index"_
    - _Expected_Behavior: Page titles display human-readable names_
    - _Preservation: Correctly formatted titles remain unchanged_
    - _Requirements: 1.2, 2.2, 3.1_

  - [x] 12.3 Implement automated fix for title/navigation mismatches
    - Synchronize page titles with navigation tree entries
    - Update either title or navigation to match (prefer navigation as source of truth)
    - Preserve existing correct matches
    - _Bug_Condition: Page title in content doesn't match navigation tree_
    - _Expected_Behavior: Page title matches navigation entry_
    - _Preservation: Matching titles remain unchanged_
    - _Requirements: 1.1, 2.1, 3.1_

  - [x] 12.4 Implement automated fix for "Table of contents" labeling
    - Replace "Table of contents" with "Page contents" for page-level TOC
    - Update MkDocs configuration or theme templates
    - _Bug_Condition: Page TOC labeled as "Table of contents"_
    - _Expected_Behavior: Page TOC labeled as "Page contents"_
    - _Preservation: Correct labels remain unchanged_
    - _Requirements: 1.3, 2.3, 3.8_

  - [x] 12.5 Implement automated fix for Installation section hierarchy
    - Add "Section contents" label to Installation section
    - Fix indentation and bolding for clear hierarchy
    - _Bug_Condition: Installation section has unclear hierarchy_
    - _Expected_Behavior: Clear hierarchy with "Section contents" label_
    - _Preservation: Other sections remain unchanged_
    - _Requirements: 1.4, 2.4, 3.8_

  - [x] 12.6 Verify navigation/title exploration test now passes
    - **Property 1: Expected Behavior** - Navigation and Title Rendering Fixed
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - Run navigation/title exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bugs are fixed)
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 12.7 Verify preservation tests still pass
    - **Property 2: Preservation** - No Regressions in Navigation/Titles
    - **IMPORTANT**: Re-run the SAME tests from tasks 10-11
    - Run preservation tests for correctly formatted pages
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - _Requirements: 3.1, 3.8_

### 3.2 Code Formatting Fixes

- [ ] 13. Fix code formatting and syntax highlighting issues

  - [x] 13.1 Create detection script for code formatting issues
    - Scan for code blocks without syntax highlighting
    - Identify inline code in nested lists without backticks
    - Detect YAML/JSON blocks without highlighting
    - Find code sections rendered as plain text
    - Generate report with file locations and line numbers
    - _Requirements: 1.5, 1.6, 1.7, 1.8_

  - [x] 13.2 Implement automated fix for missing syntax highlighting
    - Add language identifiers to code fence blocks (```python, ```yaml, etc.)
    - Detect language from context or file extension references
    - Apply consistent highlighting across similar code blocks
    - _Bug_Condition: Code blocks lack syntax highlighting_
    - _Expected_Behavior: Code blocks have consistent syntax highlighting_
    - _Preservation: Correctly highlighted code remains unchanged_
    - _Requirements: 1.5, 2.5, 3.2_

  - [x] 13.3 Implement automated fix for inline code in nested lists
    - Wrap inline code references with backticks in list items
    - Preserve list indentation and structure
    - Handle multiple inline code references per list item
    - _Bug_Condition: Inline code in nested lists renders as verbatim text_
    - _Expected_Behavior: Inline code renders with backtick formatting_
    - _Preservation: Correctly formatted inline code remains unchanged_
    - _Requirements: 1.6, 2.6, 3.4_

  - [x] 13.4 Implement automated fix for YAML/JSON highlighting
    - Add ```yaml or ```json language identifiers
    - Detect YAML vs JSON from content structure
    - Ensure proper code fence formatting
    - _Bug_Condition: YAML/JSON blocks lack syntax highlighting_
    - _Expected_Behavior: YAML/JSON blocks have appropriate highlighting_
    - _Preservation: Correctly highlighted YAML/JSON remains unchanged_
    - _Requirements: 1.7, 2.7, 3.2_

  - [x] 13.5 Implement automated fix for code sections as plain text
    - Convert plain text paragraphs back to code blocks where appropriate
    - Detect code patterns (indentation, syntax markers, etc.)
    - Add proper code fence markers
    - _Bug_Condition: Code sections render as plain text paragraphs_
    - _Expected_Behavior: Code sections maintain code block formatting_
    - _Preservation: Non-code text remains as paragraphs_
    - _Requirements: 1.8, 2.8, 3.2_

  - [x] 13.6 Verify code formatting exploration test now passes
    - **Property 1: Expected Behavior** - Code Formatting Fixed
    - **IMPORTANT**: Re-run the SAME test from task 2
    - Run code formatting exploration test from step 2
    - **EXPECTED OUTCOME**: Test PASSES (confirms bugs are fixed)
    - _Requirements: 2.5, 2.6, 2.7, 2.8_

  - [x] 13.7 Verify preservation tests still pass
    - **Property 2: Preservation** - No Regressions in Code Formatting
    - **IMPORTANT**: Re-run preservation tests from tasks 10-11
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - _Requirements: 3.2, 3.4_

### 3.3 List and Nesting Fixes

- [ ] 14. Fix list and nesting structure issues

  - [x] 14.1 Create detection script for list/nesting issues
    - Scan for nested lists with incorrect indentation
    - Identify images in lists rendered as code blocks
    - Detect indented content incorrectly rendered as blockquotes
    - Find numbered lists flattened to text blocks
    - Identify list items with lost content
    - Generate detailed report with examples
    - _Requirements: 1.9, 1.10, 1.11, 1.12, 1.13_

  - [x] 14.2 Implement automated fix for nested list indentation
    - Correct indentation levels for nested list items
    - Ensure proper spacing (2 or 4 spaces per level)
    - Maintain list marker consistency (-, *, 1., etc.)
    - _Bug_Condition: Nested list items lose proper indentation_
    - _Expected_Behavior: Nested lists maintain correct indentation levels_
    - _Preservation: Correctly indented lists remain unchanged_
    - _Requirements: 1.9, 2.9, 3.4_

  - [x] 14.3 Implement automated fix for images in list items
    - Convert code block image references back to proper image syntax
    - Maintain list indentation for images
    - Ensure images render inline with list content
    - _Bug_Condition: Images in list items render as code blocks_
    - _Expected_Behavior: Images render as images with proper indentation_
    - _Preservation: Correctly formatted list images remain unchanged_
    - _Requirements: 1.10, 2.10, 3.4, 3.5_

  - [x] 14.4 Implement automated fix for indented content as blockquotes
    - Remove incorrect blockquote markers (>) from indented list content
    - Preserve proper indentation without blockquote formatting
    - Maintain list structure and hierarchy
    - _Bug_Condition: Indented list content renders as blockquotes_
    - _Expected_Behavior: Indented content renders as normal indented text_
    - _Preservation: Intentional blockquotes remain unchanged_
    - _Requirements: 1.11, 2.11, 3.4_

  - [x] 14.5 Implement automated fix for flattened numbered lists
    - Restore list structure from text blocks
    - Detect numbered patterns (1., 2., etc.) in text
    - Add proper list formatting with line breaks
    - _Bug_Condition: Numbered lists flatten into solid text blocks_
    - _Expected_Behavior: Numbered lists maintain structure with proper numbering_
    - _Preservation: Correctly formatted numbered lists remain unchanged_
    - _Requirements: 1.12, 2.12, 3.4_

  - [x] 14.6 Implement automated fix for lost list content
    - Identify empty list items and restore content from RST source
    - Cross-reference with original RST files
    - Ensure all list items have their content
    - _Bug_Condition: List items lose content, appearing as empty bullets_
    - _Expected_Behavior: List items retain all content_
    - _Preservation: Non-empty list items remain unchanged_
    - _Requirements: 1.13, 2.13, 3.4_

  - [x] 14.7 Verify list/nesting exploration test now passes
    - **Property 1: Expected Behavior** - List and Nesting Fixed
    - **IMPORTANT**: Re-run the SAME test from task 3
    - Run list/nesting exploration test from step 3
    - **EXPECTED OUTCOME**: Test PASSES (confirms bugs are fixed)
    - _Requirements: 2.9, 2.10, 2.11, 2.12, 2.13_

  - [x] 14.8 Verify preservation tests still pass
    - **Property 2: Preservation** - No Regressions in Lists
    - **IMPORTANT**: Re-run preservation tests from tasks 10-11
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - _Requirements: 3.4, 3.5_


### 3.4 Admonition and Note Fixes

- [x] 15. Fix admonition and note rendering issues

  - [x] 15.1 Create detection script for admonition issues
    - Scan for RST note/warning blocks rendered as blockquotes
    - Identify visible admonition syntax markers ("!!! warning", etc.)
    - Detect admonitions in tables that break structure
    - Generate report with affected files and patterns
    - _Requirements: 1.14, 1.15, 1.16_

  - [x] 15.2 Implement automated fix for admonitions as blockquotes
    - Convert blockquote-rendered notes to MkDocs admonition syntax
    - Detect note/warning/caution patterns in blockquotes
    - Apply proper admonition formatting: !!! note, !!! warning, etc.
    - _Bug_Condition: RST note/warning blocks render as blockquotes_
    - _Expected_Behavior: Admonitions render as styled admonition boxes_
    - _Preservation: Intentional blockquotes remain unchanged_
    - _Requirements: 1.14, 2.14, 3.1_

  - [x] 15.3 Implement automated fix for visible admonition syntax
    - Remove or fix malformed admonition syntax markers
    - Ensure proper MkDocs admonition format (correct indentation, spacing)
    - Convert code-rendered admonitions to proper admonition blocks
    - _Bug_Condition: Admonition syntax visible as "!!! warning" in code blocks_
    - _Expected_Behavior: Admonitions render with proper formatting, no visible syntax_
    - _Preservation: Correctly formatted admonitions remain unchanged_
    - _Requirements: 1.15, 2.15, 3.1_

  - [x] 15.4 Implement automated fix for admonitions in tables
    - Simplify admonitions in table cells to plain text or simple formatting
    - OR extract admonitions outside of tables with references
    - Ensure table structure remains intact
    - _Bug_Condition: Admonitions in tables break table structure_
    - _Expected_Behavior: Table content simplified to maintain structure_
    - _Preservation: Tables without admonitions remain unchanged_
    - _Requirements: 1.16, 2.16, 3.3_

  - [x] 15.5 Verify admonition exploration test now passes
    - **Property 1: Expected Behavior** - Admonitions Fixed
    - **IMPORTANT**: Re-run the SAME test from task 4
    - Run admonition exploration test from step 4
    - **EXPECTED OUTCOME**: Test PASSES (confirms bugs are fixed)
    - _Requirements: 2.14, 2.15, 2.16_

  - [x] 15.6 Verify preservation tests still pass
    - **Property 2: Preservation** - No Regressions in Admonitions
    - **IMPORTANT**: Re-run preservation tests from tasks 10-11
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - _Requirements: 3.1, 3.3_

### 3.5 Image and Caption Fixes

- [-] 16. Fix image and caption rendering issues

  - [x] 16.1 Create detection script for image/caption issues
    - Scan for images with captions aligned beside (not below)
    - Identify images wrapped in blockquote syntax
    - Generate report with affected image references
    - _Requirements: 1.17, 1.18_

  - [x] 16.2 Implement automated fix for caption positioning
    - Convert caption syntax to place captions below images
    - Use proper Markdown figure syntax or HTML figure tags
    - Ensure captions are visually separated from images
    - _Bug_Condition: Image captions appear left-aligned beside images_
    - _Expected_Behavior: Captions appear below images_
    - _Preservation: Correctly positioned captions remain unchanged_
    - _Requirements: 1.17, 2.17, 3.5_

  - [x] 16.3 Implement automated fix for blockquote-wrapped images
    - Remove blockquote markers (>) from image references
    - Ensure images render without quote styling
    - Maintain image alignment and sizing
    - _Bug_Condition: Images incorrectly wrapped in blockquote syntax_
    - _Expected_Behavior: Images render without blockquote wrapping_
    - _Preservation: Correctly formatted images remain unchanged_
    - _Requirements: 1.18, 2.18, 3.5_

  - [x] 16.4 Verify image/caption exploration test now passes
    - **Property 1: Expected Behavior** - Images and Captions Fixed
    - **IMPORTANT**: Re-run the SAME test from task 5
    - Run image/caption exploration test from step 5
    - **EXPECTED OUTCOME**: Test PASSES (confirms bugs are fixed)
    - _Requirements: 2.17, 2.18_

  - [x] 16.5 Verify preservation tests still pass
    - **Property 2: Preservation** - No Regressions in Images
    - **IMPORTANT**: Re-run preservation tests from tasks 10-11
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - _Requirements: 3.5_

### 3.6 Table Structure Fixes

- [ ] 17. Fix table structure and content issues

  - [x] 17.1 Create detection script for table issues
    - Scan for tables with lists in cells that split across cells
    - Identify tables with notes/admonitions breaking structure
    - Detect multi-line cell content splitting into multiple cells
    - Find complex tables with misaligned cells
    - Identify tables with empty rows/cells that had content
    - Generate comprehensive report with table locations
    - _Requirements: 1.19, 1.20, 1.21, 1.22, 1.23_

  - [x] 17.2 Implement automated fix for lists in table cells
    - Convert multi-item lists to single-cell format (semicolon-separated or HTML)
    - Use <br> tags for line breaks within cells
    - Ensure list content stays within single cells
    - _Bug_Condition: Lists in table cells split across multiple cells_
    - _Expected_Behavior: Lists render within single cells_
    - _Preservation: Correctly formatted table lists remain unchanged_
    - _Requirements: 1.19, 2.19, 3.3_

  - [x] 17.3 Implement automated fix for notes/admonitions in tables
    - Simplify note/admonition content to plain text in cells
    - OR move notes outside tables with cell references
    - Maintain table structure integrity
    - _Bug_Condition: Notes/admonitions in cells break table structure_
    - _Expected_Behavior: Content simplified to maintain table structure_
    - _Preservation: Tables without notes remain unchanged_
    - _Requirements: 1.20, 2.20, 3.3_

  - [x] 17.4 Implement automated fix for multi-line cell content
    - Use HTML <br> tags or proper Markdown table syntax for line breaks
    - Ensure newlines don't split content into multiple cells
    - Maintain cell content integrity
    - _Bug_Condition: Multi-line cell content splits into multiple cells_
    - _Expected_Behavior: Content remains in single cells with proper line breaks_
    - _Preservation: Correctly formatted multi-line cells remain unchanged_
    - _Requirements: 1.21, 2.21, 3.3_

  - [x] 17.5 Implement automated fix for complex table alignment
    - Repair table structure with correct column alignment
    - Ensure header and data rows align properly
    - Fix cell spanning issues
    - _Bug_Condition: Complex tables have misaligned cells and lost content_
    - _Expected_Behavior: Table structure preserved with correct alignment_
    - _Preservation: Correctly aligned tables remain unchanged_
    - _Requirements: 1.22, 2.22, 3.3_

  - [x] 17.6 Implement automated fix for empty table cells
    - Restore content to empty cells from RST source
    - Cross-reference with original RST files
    - Ensure all cells have their original content
    - _Bug_Condition: Tables show empty rows/cells that had content_
    - _Expected_Behavior: All cells contain original content_
    - _Preservation: Non-empty cells remain unchanged_
    - _Requirements: 1.23, 2.23, 3.3_

  - [x] 17.7 Verify table exploration test now passes
    - **Property 1: Expected Behavior** - Tables Fixed
    - **IMPORTANT**: Re-run the SAME test from task 6
    - Run table exploration test from step 6
    - **EXPECTED OUTCOME**: Test PASSES (confirms bugs are fixed)
    - _Requirements: 2.19, 2.20, 2.21, 2.22, 2.23_

  - [x] 17.8 Verify preservation tests still pass
    - **Property 2: Preservation** - No Regressions in Tables
    - **IMPORTANT**: Re-run preservation tests from tasks 10-11
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - _Requirements: 3.3_

### 3.7 Link and Anchor Fixes

- [ ] 18. Fix link and anchor resolution issues

  - [x] 18.1 Create detection script for link/anchor issues
    - Scan for dangling anchors with visible link syntax
    - Identify failed include statements
    - Detect broken internal links
    - Generate report with link locations and targets
    - _Requirements: 1.24, 1.25_

  - [x] 18.2 Implement automated fix for dangling anchors
    - Convert visible link syntax to proper Markdown links
    - Resolve anchor targets to correct page references
    - Update link paths for MkDocs structure
    - _Bug_Condition: Internal links show visible syntax like "[Cache]"_
    - _Expected_Behavior: Anchors resolve correctly with proper Markdown syntax_
    - _Preservation: Working links remain unchanged_
    - _Requirements: 1.24, 2.24, 3.6_

  - [x] 18.3 Implement automated fix for include statements
    - Replace failed include statements with actual content
    - OR convert to proper MkDocs snippet syntax
    - Ensure referenced content is accessible
    - _Bug_Condition: Include statements fail and display malformed syntax_
    - _Expected_Behavior: Includes work or are replaced with content_
    - _Preservation: Working includes remain unchanged_
    - _Requirements: 1.25, 2.25, 3.6_

  - [x] 18.4 Verify link/anchor exploration test now passes
    - **Property 1: Expected Behavior** - Links and Anchors Fixed
    - **IMPORTANT**: Re-run the SAME test from task 7
    - Run link/anchor exploration test from step 7
    - **EXPECTED OUTCOME**: Test PASSES (confirms bugs are fixed)
    - _Requirements: 2.24, 2.25_

  - [x] 18.5 Verify preservation tests still pass
    - **Property 2: Preservation** - No Regressions in Links
    - **IMPORTANT**: Re-run preservation tests from tasks 10-11
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - _Requirements: 3.6_


### 3.8 Indentation and Whitespace Fixes

- [ ] 19. Fix indentation and whitespace rendering issues

  - [x] 19.1 Create detection script for indentation/whitespace issues
    - Scan for indented paragraphs rendered as code blocks or blockquotes
    - Identify definition list-style content (": - text") rendered incorrectly
    - Detect text starting with ": " that renders malformed
    - Generate report with affected content patterns
    - _Requirements: 1.26, 1.27, 1.28_

  - [ ] 19.2 Implement automated fix for indented paragraphs
    - Remove incorrect code block or blockquote formatting from indented text
    - Preserve intentional indentation using proper Markdown syntax
    - Distinguish between code blocks and indented prose
    - _Bug_Condition: Indented paragraphs render as code blocks or blockquotes_
    - _Expected_Behavior: Indented paragraphs render as normal indented text_
    - _Preservation: Intentional code blocks and blockquotes remain unchanged_
    - _Requirements: 1.26, 2.26, 3.1_

  - [ ] 19.3 Implement automated fix for definition list-style content
    - Convert ": - text" patterns to proper Markdown definition lists
    - OR convert to regular lists if definition list semantics don't apply
    - Remove malformed colon/dash syntax
    - _Bug_Condition: Definition list-style content renders as malformed text_
    - _Expected_Behavior: Content renders as proper definition lists or regular lists_
    - _Preservation: Correctly formatted lists remain unchanged_
    - _Requirements: 1.27, 2.27, 3.4_

  - [ ] 19.4 Implement automated fix for ": " prefix text
    - Convert text starting with ": " to proper Markdown syntax
    - Remove leading colons where inappropriate
    - Apply proper formatting based on context
    - _Bug_Condition: Text starting with ": " renders incorrectly_
    - _Expected_Behavior: Text converts to proper Markdown syntax_
    - _Preservation: Correctly formatted text remains unchanged_
    - _Requirements: 1.28, 2.28, 3.1_

  - [ ] 19.5 Verify indentation/whitespace exploration test now passes
    - **Property 1: Expected Behavior** - Indentation and Whitespace Fixed
    - **IMPORTANT**: Re-run the SAME test from task 8
    - Run indentation/whitespace exploration test from step 8
    - **EXPECTED OUTCOME**: Test PASSES (confirms bugs are fixed)
    - _Requirements: 2.26, 2.27, 2.28_

  - [ ] 19.6 Verify preservation tests still pass
    - **Property 2: Preservation** - No Regressions in Indentation
    - **IMPORTANT**: Re-run preservation tests from tasks 10-11
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - _Requirements: 3.1, 3.4_

### 3.9 Heading and Structure Fixes

- [ ] 20. Fix heading and structure rendering issues

  - [ ] 20.1 Create detection script for heading/structure issues
    - Scan for low-level subsection headings that render incorrectly
    - Identify quoted specification text formatted as code blocks
    - Detect heading hierarchy problems
    - Generate report with affected headings and locations
    - _Requirements: 1.29, 1.30_

  - [ ] 20.2 Implement automated fix for low-level heading hierarchy
    - Correct heading levels (##, ###, ####, etc.) for proper hierarchy
    - Ensure headings render in visual hierarchy
    - Maintain document structure and navigation
    - _Bug_Condition: Low-level subsection headings render incorrectly_
    - _Expected_Behavior: Headings render with correct levels in hierarchy_
    - _Preservation: Correctly leveled headings remain unchanged_
    - _Requirements: 1.29, 2.29, 3.8_

  - [ ] 20.3 Implement automated fix for quoted specification text
    - Convert code block-formatted quotes to proper blockquotes
    - Use > syntax for quoted text from specifications
    - Maintain quote formatting and attribution
    - _Bug_Condition: Quoted specification text formats as code blocks_
    - _Expected_Behavior: Quoted text formats as styled blockquotes_
    - _Preservation: Intentional code blocks remain unchanged_
    - _Requirements: 1.30, 2.30, 3.1_

  - [ ] 20.4 Verify heading/structure exploration test now passes
    - **Property 1: Expected Behavior** - Headings and Structure Fixed
    - **IMPORTANT**: Re-run the SAME test from task 9
    - Run heading/structure exploration test from step 9
    - **EXPECTED OUTCOME**: Test PASSES (confirms bugs are fixed)
    - _Requirements: 2.29, 2.30_

  - [ ] 20.5 Verify preservation tests still pass
    - **Property 2: Preservation** - No Regressions in Structure
    - **IMPORTANT**: Re-run preservation tests from tasks 10-11
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - _Requirements: 3.1, 3.8_

## Phase 4: Semi-Automated Fixes with Review

### 4.1 Complex Table Repairs

- [ ] 21. Review and repair complex tables requiring manual intervention

  - [ ] 21.1 Identify complex tables that automated fixes couldn't resolve
    - Review detection script output for remaining table issues
    - Prioritize tables with most severe structural problems
    - Document specific issues per table
    - _Requirements: 1.22, 2.22_

  - [ ] 21.2 Manually repair complex table structures
    - Fix tables with nested structures beyond automation capability
    - Ensure proper alignment and cell content
    - Consider converting extremely complex tables to alternative formats
    - _Bug_Condition: Complex tables remain broken after automated fixes_
    - _Expected_Behavior: All tables render with correct structure_
    - _Preservation: Correctly formatted tables remain unchanged_
    - _Requirements: 1.22, 2.22, 3.3_

  - [ ] 21.3 Document complex table repair patterns
    - Record patterns found in manual repairs
    - Create guidelines for future table conversions
    - Update automated scripts if patterns are generalizable
    - _Requirements: 2.22_

### 4.2 Content Validation

- [ ] 22. Validate content accuracy and completeness

  - [ ] 22.1 Cross-reference Markdown with original RST sources
    - Sample pages across all documentation sections
    - Compare content completeness (no lost paragraphs, sections, etc.)
    - Verify technical accuracy of converted content
    - _Requirements: 1.13, 1.23, 2.13, 2.23_

  - [ ] 22.2 Validate code examples and snippets
    - Ensure all code examples are present and correctly formatted
    - Verify syntax highlighting is appropriate for language
    - Test code examples where feasible
    - _Requirements: 1.5, 1.6, 1.7, 1.8, 2.5, 2.6, 2.7, 2.8_

  - [ ] 22.3 Validate links and references
    - Test internal links across documentation
    - Verify external links are accessible
    - Ensure anchor references resolve correctly
    - _Requirements: 1.24, 1.25, 2.24, 2.25_

  - [ ] 22.4 Validate images and media
    - Ensure all images load correctly
    - Verify image paths are correct
    - Check that captions are properly associated
    - _Requirements: 1.17, 1.18, 2.17, 2.18_

### 4.3 Edge Case Handling

- [ ] 23. Handle edge cases and special formatting

  - [ ] 23.1 Review pages with multiple overlapping issues
    - Identify pages with 5+ different issue types
    - Prioritize fixes to avoid conflicts
    - Test fixes incrementally
    - _Requirements: All requirements_

  - [ ] 23.2 Handle special RST directives not covered by automation
    - Identify RST directives without Markdown equivalents
    - Convert to appropriate Markdown or HTML
    - Document conversion decisions
    - _Requirements: 1.25, 2.25_

  - [ ] 23.3 Fix remaining miscellaneous issues from Andrea's feedback
    - Address "Other assorted issues" section items
    - Fix malformed include statements
    - Repair pipe characters in lists ("| For raster layers")
    - Fix mixed code/quote formatting
    - Handle lost table content (e.g., empty example locations)
    - _Requirements: 1.25, 2.25, 3.1_

## Phase 5: Manual Validation and Quality Assurance

### 5.1 Comprehensive Testing

- [ ] 24. Perform comprehensive testing across all documentation

  - [ ] 24.1 Build documentation and verify no errors
    - Run MkDocs build process
    - Ensure no build errors or warnings
    - Verify all pages generate successfully
    - _Requirements: 3.10_

  - [ ] 24.2 Test navigation and structure
    - Verify navigation tree is complete and correct
    - Test all navigation links
    - Ensure page hierarchy is logical
    - _Requirements: 2.1, 2.3, 2.4, 3.8_

  - [ ] 24.3 Test search functionality
    - Verify search index builds correctly
    - Test search with common queries
    - Ensure search results are relevant
    - _Requirements: 3.7_

  - [ ] 24.4 Test responsive design and mobile rendering
    - View documentation on different screen sizes
    - Verify tables, images, and code blocks are responsive
    - Ensure navigation works on mobile
    - _Requirements: 3.7_

### 5.2 Visual Inspection

- [ ] 25. Perform visual inspection of documentation

  - [ ] 25.1 Review sample pages from each documentation section
    - Installation guides
    - Getting started tutorials
    - Data management
    - Styling documentation
    - Services documentation
    - Security documentation
    - Extensions documentation
    - Community documentation
    - _Requirements: All requirements_

  - [ ] 25.2 Compare rendered output with original RST documentation
    - Verify visual parity where possible
    - Document intentional differences
    - Ensure readability is maintained or improved
    - _Requirements: All requirements_

  - [ ] 25.3 Review pages specifically mentioned in Andrea's feedback
    - Systematically check each page URL from Andrea's report
    - Verify all reported issues are resolved
    - Document any remaining issues
    - _Requirements: All requirements_

### 5.3 Regression Testing

- [ ] 26. Perform regression testing

  - [ ] 26.1 Re-run all exploration tests
    - **Property 1: Expected Behavior** - All Bugs Fixed
    - Run all exploration tests from Phase 1 (tasks 1-9)
    - **EXPECTED OUTCOME**: All tests PASS
    - Document any failures for immediate attention
    - _Requirements: All Expected Behavior requirements (2.x)_

  - [ ] 26.2 Re-run all preservation tests
    - **Property 2: Preservation** - No Regressions
    - Run all preservation tests from Phase 2 (tasks 10-11)
    - **EXPECTED OUTCOME**: All tests PASS
    - Document any failures indicating regressions
    - _Requirements: All Preservation requirements (3.x)_

  - [ ] 26.3 Verify MkDocs configuration integrity
    - Ensure mkdocs.yml is valid
    - Verify theme configuration is correct
    - Test plugin functionality
    - _Requirements: 3.7, 3.8, 3.9, 3.10_

## Phase 6: Final Checkpoint

- [ ] 27. Final checkpoint - Ensure all tests pass and documentation is production-ready
  - Confirm all exploration tests pass (bugs fixed)
  - Confirm all preservation tests pass (no regressions)
  - Verify documentation builds without errors
  - Ensure all pages from Andrea's feedback are resolved
  - Ask user if any questions or issues arise before marking complete
  - _Requirements: All requirements_

