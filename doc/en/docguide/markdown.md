# Markdown Syntax

This page contains syntax rules, tips, and tricks for writing GeoServer documentation in Markdown.

## Basic markup

The simplest Markdown elements are:

| **Format** | **Syntax** | **Output** |
|------------|------------|------------|
| Italics    | `*italics*` | *italics* |
| Bold       | `**bold**` | **bold** |
| Monospace  | `` `monospace` `` | `monospace` |

## Lists

Bulleted lists:

- An item
- Another item
- Yet another item

Source code:

```md
- An item
- Another item
- Yet another item
```

Numbered lists:

1. First item
2. Second item
3. Third item

Source code:

```md
1. First item
2. Second item
3. Third item
```

### Nested bullets and outdenting

- Top level
    - Nested level

To return to top level, use 0 indentation again. For example:

- Top level
    - Nested
- Back to top level

## List-packed table

Use a Markdown table instead of rst list-table:

| Shapes | Description |
|--------|-------------|
| Square | Four sides of equal length, 90 degree angles |
| Rectangle | Four sides, 90 degree angles |

## Page labels and anchors

In Markdown, you can use heading-based anchors or explicit named anchors (with HTML) if needed.

## Linking

Do not use "here" as link text. Instead:

- Bad: [here](#linking)
- Good: [Linking](#linking)

External link:

```md
[Text of the link](http://example.com)
```

## Sections

Use `#`, `##`, `###`, etc.: 

```md
# Main section
## Subsection
### Sub-subsection
```

## Notes and warnings (admonitions)

GeoServer documentation uses the `admonition` extension in Markdown for notes and warnings.

### Important user guidance

- `!!! note`, `!!! warning`, etc. must start at column 0 (no leading spaces).
- The content of the block should be indented by 4 spaces.
- Do not put `!!! note` at an indented list level; it will render as code text instead of an admonition.

Example:

```md
!!! note
    Do not wait for a release to fall out of support before upgrading.
```

This produces a note box.

If you need a note-like callout inside a list item, use inline emphasis instead:

```md
- Remember:
    - **Note:** Do not rely on this in production.
```

## Images

```md
![](pagelogo.png)
*The GeoServer logo as shown on the homepage.*
```

## External files

```md
[An external file](readme.txt)
```

## Code blocks and inline code

Inline code: `` `myCommand` ``

Fenced block:

```md
```bash
command args
```
```

## GUI element references

Use bold text:

- **Main Menu**
- **Start Menu -> Programs -> GeoServer**

## Show Source

All pages have a "Show Source" link in the right-hand table of contents.
