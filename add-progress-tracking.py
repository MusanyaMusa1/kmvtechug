"""
KMVTECH Education - Patch All Courses with Progress Tracking
============================================================
Place this file in: C:\Users\Matrix Computer Accs\Documents\GitHub\kmvtechug
Run: python patch-all-courses-progress.py
"""

import os, re

# Course code to folder name mapping
COURSES = {
    'EVL1':   'education/courses/evl1',
    'EVL2':   'education/courses/evl2',
    'ENVPSY': 'education/courses/envpsy',
    'HRM1':   'education/courses/hrm1',
    'COGPSY': 'education/courses/cogpsy',
    'SOCPSY': 'education/courses/socpsy',
    'EQT1':   'education/courses/eqt1',
}

SCRIPT_TAG = '<script src="/education/js/progress-tracking.js"></script>'
SUPABASE_TAG = '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>'

total_fixed = 0
total_skipped = 0
total_errors = 0

for course_code, folder in COURSES.items():
    if not os.path.exists(folder):
        print(f"  FOLDER NOT FOUND: {folder} - skipping {course_code}")
        continue

    course_fixed = 0
    course_skipped = 0

    for dirpath, dirs, files in os.walk(folder):
        for fname in files:
            if not fname.endswith('.html'):
                continue

            fpath = os.path.join(dirpath, fname)

            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    html = f.read()

                orig = html
                changed = False

                # 1. Add data-course to body tag
                if f'data-course="{course_code}"' not in html:
                    html = re.sub(
                        r'<body([^>]*)>',
                        f'<body\\1 data-course="{course_code}">',
                        html, count=1
                    )
                    changed = True

                # 2. Add progress-tracking.js script tag
                if 'progress-tracking.js' not in html:
                    if SUPABASE_TAG in html:
                        html = html.replace(
                            SUPABASE_TAG,
                            SUPABASE_TAG + '\n' + SCRIPT_TAG
                        )
                    else:
                        html = html.replace('</head>', SCRIPT_TAG + '\n</head>')
                    changed = True

                # 3. Add trackProgress() to show() function
                if 'trackProgress()' not in html:
                    # Pattern 1 - compact
                    if "if(lc)lc.style.display='block';}" in html:
                        html = html.replace(
                            "if(lc)lc.style.display='block';}",
                            "if(lc)lc.style.display='block';trackProgress();}"
                        )
                        changed = True
                    # Pattern 2 - with qs panel
                    elif "document.getElementById('qs').style.display='block';}" in html:
                        html = html.replace(
                            "document.getElementById('qs').style.display='block';}",
                            "document.getElementById('qs').style.display='block';trackProgress();}"
                        )
                        changed = True
                    # Pattern 3 - spaced
                    elif "if (lc) lc.style.display = 'block';" in html:
                        html = html.replace(
                            "if (lc) lc.style.display = 'block';",
                            "if (lc) lc.style.display = 'block';\n  trackProgress();"
                        )
                        changed = True
                    # Pattern 4 - lc display block with newline closing
                    elif "lc.style.display='block';\n}" in html:
                        html = html.replace(
                            "lc.style.display='block';\n}",
                            "lc.style.display='block';trackProgress();\n}"
                        )
                        changed = True

                if changed:
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(html)
                    course_fixed += 1
                    total_fixed += 1
                    print(f"    OK: {fpath.replace(folder,'')}")
                else:
                    course_skipped += 1
                    total_skipped += 1

            except Exception as e:
                total_errors += 1
                print(f"    ERROR: {fpath} - {e}")

    print(f"\n  {course_code}: {course_fixed} updated, {course_skipped} already done")

print(f"\n{'='*50}")
print(f"COMPLETE")
print(f"  Total updated:  {total_fixed}")
print(f"  Already done:   {total_skipped}")
print(f"  Errors:         {total_errors}")
print(f"{'='*50}")

if total_fixed > 0:
    print("\nGo to GitHub Desktop, commit all changes, and push.")
else:
    print("\nNothing changed. Check folder names if unexpected.")
