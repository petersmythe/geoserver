"""
Iterate through each nav entry in mkdocs.yml IN ORDER,
including section headings as separate rows,
find all image references in each page, and output as CSV.

- Blank line before Developer Guide, Documentation Guide, API Reference
- Strip images/ prefix (assume images/ dir), keep ../ relative paths as-is
- Dedup: within a leaf directory, only show an image filename the first time;
  subsequent occurrences become '!'
"""

import csv
import os
import re
import yaml


# Top-level nav keys that should have a blank line before them
BLANK_BEFORE = {'Developer Guide:', 'Documentation Guide:', 'API Reference:'}


def extract_nav_entries(nav, entries=None):
    if entries is None:
        entries = []
    if isinstance(nav, list):
        for item in nav:
            extract_nav_entries(item, entries)
    elif isinstance(nav, dict):
        for key, value in nav.items():
            if isinstance(value, str):
                entries.append(('page', value, f'{key}: {value}'))
            elif isinstance(value, list):
                entries.append(('heading', None, f'{key}:'))
                extract_nav_entries(value, entries)
    elif isinstance(nav, str):
        entries.append(('page', nav, nav))
    return entries


def find_images_in_md(filepath):
    images = []
    if not os.path.isfile(filepath):
        return images
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    for m in re.finditer(r'!\[[^\]]*\]\(([^)]+)\)', content):
        img_path = m.group(1).strip()
        if img_path.startswith(('http://', 'https://', '$', '#')):
            continue
        img_path = img_path.split('"')[0].strip()
        img_path = img_path.split("'")[0].strip()
        if img_path:
            images.append(img_path)

    stripped = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    stripped = re.sub(r'`[^`]+`', '', stripped)
    for m in re.finditer(r'<img\s+[^>]*src=["\']([^"\']+)["\']', stripped):
        img_path = m.group(1).strip()
        if img_path.startswith(('http://', 'https://', '$', '#')):
            continue
        images.append(img_path)

    return images


def get_leaf_dir(page_path):
    """Get the immediate parent directory of a page for dedup grouping."""
    return os.path.dirname(page_path)


def shorten_image_path(page_path, img_ref, docs_dir):
    """
    Shorten image path:
    - If it's in the page's images/ subfolder, strip to just filename
    - If it's a relative path outside, keep the ../ addressing
    """
    page_dir = os.path.dirname(os.path.join(docs_dir, page_path))
    abs_img = os.path.normpath(os.path.join(page_dir, img_ref))
    page_dir_norm = os.path.normpath(page_dir)

    # Images in page's own images/ subfolder -> just filename
    images_dir = os.path.normpath(os.path.join(page_dir_norm, 'images'))
    if abs_img.startswith(images_dir + os.sep):
        return os.path.basename(abs_img)

    # Images in page's own img/ subfolder -> just filename
    img_dir = os.path.normpath(os.path.join(page_dir_norm, 'img'))
    if abs_img.startswith(img_dir + os.sep):
        return os.path.basename(abs_img)

    # Bare filename in same directory -> just filename
    if os.path.dirname(abs_img) == page_dir_norm:
        return os.path.basename(abs_img)

    # Otherwise relative from page dir
    return os.path.relpath(abs_img, page_dir_norm).replace(os.sep, '/')


def resolve_abs_image(page_path, img_ref, docs_dir):
    """Resolve to absolute normalized path for dedup comparison."""
    page_dir = os.path.dirname(os.path.join(docs_dir, page_path))
    return os.path.normpath(os.path.join(page_dir, img_ref))


def main():
    with open('mkdocs.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    docs_dir = config.get('docs_dir', 'docs')
    nav = config.get('nav', [])
    entries = extract_nav_entries(nav)

    # Track seen images per leaf directory (by absolute path)
    seen_per_dir = {}  # leaf_dir -> set of abs image paths

    all_rows = []  # list of (label, [image_strings])
    max_images = 0

    for kind, page_path, label in entries:
        # Insert blank row before certain top-level sections
        if kind == 'heading' and label in BLANK_BEFORE:
            all_rows.append(('', []))

        if kind == 'heading':
            all_rows.append((label, []))
            continue

        if not page_path or not page_path.endswith('.md'):
            all_rows.append((label, []))
            continue

        filepath = os.path.join(docs_dir, page_path)
        raw_images = find_images_in_md(filepath)

        leaf_dir = get_leaf_dir(page_path)
        if leaf_dir not in seen_per_dir:
            seen_per_dir[leaf_dir] = set()

        display_images = []
        for img in raw_images:
            short = shorten_image_path(page_path, img, docs_dir)
            abs_path = resolve_abs_image(page_path, img, docs_dir)

            if abs_path in seen_per_dir[leaf_dir]:
                display_images.append('!')
            else:
                seen_per_dir[leaf_dir].add(abs_path)
                display_images.append(short)

        all_rows.append((label, display_images))
        if len(display_images) > max_images:
            max_images = len(display_images)

    # Write CSV
    output_file = 'nav_images.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = ['page'] + [f'image_{i+1}' for i in range(max_images)]
        writer.writerow(header)
        for label, images in all_rows:
            row = [label] + images + [''] * (max_images - len(images))
            writer.writerow(row)

    total_rows = len(all_rows)
    headings = sum(1 for l, i in all_rows if not i and l.endswith(':'))
    pages_with_images = sum(1 for l, imgs in all_rows if imgs)
    total_unique = sum(1 for _, imgs in all_rows for img in imgs if img and img != '!')
    total_dupes = sum(1 for _, imgs in all_rows for img in imgs if img == '!')
    print(f"Rows: {total_rows} ({headings} headings)")
    print(f"Pages with images: {pages_with_images}")
    print(f"Unique image refs: {total_unique}, duplicates marked '!': {total_dupes}")
    print(f"Max images on a single page: {max_images}")
    print(f"Output: {output_file}")


if __name__ == '__main__':
    main()
