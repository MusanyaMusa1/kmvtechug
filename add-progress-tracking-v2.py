"""
KMVTECH Education - Add Progress Tracking to All EVL1 Pages v2
Run from inside your kmvtechug folder:
  python add-progress-tracking-v2.py
"""

import os
import re

# Try multiple possible paths
possible_roots = [
    "education/courses/evl1",
    "education\\courses\\evl1",
]

COURSE_CODE = "EVL1"
fixed = 0
skipped = 0
errors = []

# Find the correct root
COURSE_ROOT = None
for p in possible_roots:
    if os.path.exists(p):
        COURSE_ROOT = p
        break

if not COURSE_ROOT:
    print("ERROR: Could not find education/courses/evl1 folder.")
    print("Current directory:", os.getcwd())
    print("Folders here:", os.listdir("."))
    exit()

print(f"Found course folder: {COURSE_ROOT}")
print(f"Scanning for HTML files...")
print()

for root, dirs, files in os.walk(COURSE_ROOT):
    for fname in files:
        if not fname.endswith('.html'):
            continue

        fpath = os.path.join(root, fname)

        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                html = f.read()

            original = html
            changed = False

            # 1. Add data-course to <body> tag
            if f'data-course="{COURSE_CODE}"' not in html:
                # Handle <body> with or without other attributes
                html = re.sub(
                    r'<body([^>]*)>',
                    f'<body\\1 data-course="{COURSE_CODE}">',
                    html, count=1
                )
                changed = True

            # 2. Add progress-tracking.js script tag
            if 'progress-tracking.js' not in html:
                html = html.replace(
                    '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>',
                    '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>\n<script src="/education/js/progress-tracking.js"></script>'
                )
                changed = True

            # 3. Add trackProgress() inside show() function
            if 'trackProgress()' not in html:
                # Compact version used in lesson pages
                html = html.replace(
                    "if(lc)lc.style.display='block';}",
                    "if(lc)lc.style.display='block';trackProgress();}"
                )
                # Spaced version
                html = html.replace(
                    "if(lc)lc.style.display='block'; }",
                    "if(lc)lc.style.display='block';trackProgress();}"
                )
                if 'trackProgress()' not in html:
                    changed = False  # could not inject - skip safely

            if changed:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(html)
                fixed += 1
                print(f"  OK: {fpath}")
            else:
                skipped += 1

        except Exception as e:
            errors.append(f"{fpath}: {e}")
            print(f"  ERROR: {fpath} - {e}")

print()
print(f"DONE.")
print(f"  Updated:      {fixed} files")
print(f"  Already done: {skipped} files")
print(f"  Errors:       {len(errors)}")
if errors:
    for e in errors:
        print(f"    {e}")
print()
if fixed > 0:
    print("Now go to GitHub Desktop, commit all changes, and push.")
