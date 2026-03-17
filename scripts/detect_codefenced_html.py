#!/usr/bin/env python3
"""Detect HTML content incorrectly wrapped in code fences inside markdown files.

Looks for patterns like:
  <a href="..." class="...">
  ```xml
  <div>...</div>
  ```
  </a>

Where HTML that should be rendered inline has been wrapped in code fences,
causing it to display as literal code blocks instead of rendered HTML.
"""

import re
import sys
from pathlib import Path


def find_codefenced_html(filepath: Path) -> list[dict]:
    """Find instances of HTML wrapped in code fences within a markdown file."""
    issues = []
    text = filepath.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")

    # Pattern: an HTML tag on a line, followed by a code fence opening,
    # then HTML content, then a code fence closing, then a closing HTML tag.
    # This catches the general case of HTML that was incorrectly fenced.
    
    # Strategy: find ```xml or ``` blocks that contain HTML tags,
    # where the lines immediately before/after the fences are also HTML tags.
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for opening code fence (``` or ```xml, ```html, etc.)
        fence_match = re.match(r'^```(\w*)$', line)
        if fence_match:
            fence_start = i
            lang = fence_match.group(1)
            
            # Find the closing fence
            j = i + 1
            fence_content_lines = []
            while j < len(lines):
                if lines[j].strip() == '```':
                    fence_end = j
                    break
                fence_content_lines.append(lines[j])
                j += 1
            else:
                # No closing fence found
                i += 1
                continue
            
            # Check if the fenced content contains HTML tags
            fence_content = "\n".join(fence_content_lines)
            has_html = bool(re.search(r'<\w+[\s>]', fence_content))
            
            if not has_html:
                i = j + 1
                continue
            
            # Check context: is there an HTML tag on the line(s) before the fence?
            html_context_before = False
            for k in range(max(0, fence_start - 3), fence_start):
                prev_line = lines[k].strip()
                if re.search(r'<\w+[\s>]', prev_line) and not prev_line.startswith('```'):
                    html_context_before = True
                    break
            
            # Check context: is there an HTML closing tag on the line(s) after the fence?
            html_context_after = False
            for k in range(fence_end + 1, min(len(lines), fence_end + 4)):
                next_line = lines[k].strip()
                if re.search(r'</\w+>', next_line) and not next_line.startswith('```'):
                    html_context_after = True
                    break
            
            if html_context_before and html_context_after:
                # Get a few lines of context
                ctx_start = max(0, fence_start - 2)
                ctx_end = min(len(lines), fence_end + 3)
                context = "\n".join(
                    f"  {n+1}: {lines[n]}" 
                    for n in range(ctx_start, ctx_end)
                )
                issues.append({
                    "line": fence_start + 1,  # 1-indexed
                    "fence_end": fence_end + 1,
                    "lang": lang or "(none)",
                    "context": context,
                })
            
            i = j + 1
        else:
            i += 1
    
    return issues


def main():
    doc_root = Path("doc")
    if not doc_root.exists():
        print("ERROR: 'doc/' directory not found.", file=sys.stderr)
        sys.exit(1)

    md_files = sorted(doc_root.rglob("*.md"))
    total_issues = 0
    files_with_issues = 0

    for md_file in md_files:
        issues = find_codefenced_html(md_file)
        if issues:
            files_with_issues += 1
            total_issues += len(issues)
            rel = md_file.as_posix()
            for issue in issues:
                print(f"\n{'='*70}")
                print(f"FILE: {rel}")
                print(f"  Code fence at line {issue['line']}-{issue['fence_end']} (lang: {issue['lang']})")
                print(f"  HTML content inside code fence with HTML context before/after")
                print(f"  Context:")
                print(issue["context"])

    print(f"\n{'='*70}")
    print(f"SUMMARY: Found {total_issues} issue(s) in {files_with_issues} file(s) out of {len(md_files)} markdown files scanned.")
    
    if total_issues > 0:
        sys.exit(1)
    else:
        print("No code-fenced HTML issues detected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
