"""
KMVTECH Education - Add Progress Tracking to All EVL1 Pages v3
Place this file in: C:\Users\Matrix Computer Accs\Documents\GitHub\kmvtechug
Then run: python add-progress-tracking-v3.py
"""

import os
import re

COURSE_ROOT = os.path.join("education", "courses", "evl1")
COURSE_CODE = "EVL1"
fixed = 0
skipped = 0
errors = []

print(f"Looking for: {os.path.abspath(COURSE_ROOT)}")

if not os.path.exists(COURSE_ROOT):
    print(f"ERROR: Folder not found.")
    print(f"Current directory: {os.getcwd()}")
    print(f"Contents: {os.listdir('.')}")
    exit()

print(f"Found. Scanning HTML files...")
print()

for root, dirs, files in os.walk(COURSE_ROOT):
    for fname in files:
        if not fname.endswith('.html'):
            continue

        fpath = os.path.join(root, fname)

        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                html = f.read()

            changed = False

            # 1. Add data-course to <body> tag
            if f'data-course="{COURSE_CODE}"' not in html:
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
            # This handles the compact version used in all EVL1 pages
            if 'trackProgress()' not in html:
                before = html
                html = html.replace(
                    "if(lc)lc.style.display='block';}",
                    "if(lc)lc.style.display='block';trackProgress();}"
                )
                if html != before:
                    changed = True
                else:
                    # Try alternate spacing
                    html = html.replace(
                        "if(lc)lc.style.display='block'; }",
                        "if(lc)lc.style.display='block';trackProgress();}"
                    )
                    if html != before:
                        changed = True

            if changed:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(html)
                fixed += 1
                print(f"  UPDATED: {fpath}")
            else:
                skipped += 1
                print(f"  SKIPPED: {fpath}")

        except Exception as e:
            errors.append(f"{fpath}: {e}")
            print(f"  ERROR:   {fpath} - {e}")

print()
print(f"===========================")
print(f"DONE.")
print(f"  Updated:      {fixed} files")
print(f"  Skipped:      {skipped} files")
print(f"  Errors:       {len(errors)}")
print(f"===========================")
if fixed > 0:
    print()
    print("Go to GitHub Desktop, commit all changes, and push.")
