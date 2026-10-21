#!/usr/bin/env python3
"""
KMVTECH Education - add the logo icon to every page's browser tab.

1. Put the icon files in  education/assets/logos/
2. Run from the kmvtechug repository root:   python add-favicon.py
3. Commit and push.

Safe to run more than once. Only touches files inside education/.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(ROOT, 'education')
MARK = '<!-- kmv-favicon -->'
TAGS = (MARK + '\n'
 '<link rel="icon" type="image/png" sizes="32x32" href="/education/assets/logos/kmvtech-education-favicon-32.png"/>\n'
 '<link rel="icon" type="image/png" sizes="16x16" href="/education/assets/logos/kmvtech-education-favicon-16.png"/>\n'
 '<link rel="shortcut icon" href="/education/assets/logos/favicon.ico"/>\n'
 '<link rel="apple-touch-icon" href="/education/assets/logos/apple-touch-icon.png"/>\n')

if not os.path.isdir(BASE):
    print('ERROR: run this from the kmvtechug repository root.'); sys.exit(1)
if not os.path.isfile(os.path.join(BASE, 'assets', 'logos', 'favicon.ico')):
    print('ERROR: upload the icon files to education/assets/logos/ first.'); sys.exit(1)

done = skipped = problems = 0
for folder, _, files in os.walk(BASE):
    for name in files:
        if not name.lower().endswith('.html'):
            continue
        path = os.path.join(folder, name)
        with open(path, 'r', encoding='utf-8', errors='surrogateescape', newline='') as f:
            html = f.read()
        if MARK in html or re.search(r'rel=["\'](shortcut )?icon["\']', html, re.I):
            skipped += 1; continue
        m = re.search(r'</head>', html, re.I)
        if not m:
            problems += 1; print('NO </head>:', os.path.relpath(path, ROOT)); continue
        nl = '\r\n' if '\r\n' in html else '\n'
        new = html[:m.start()] + TAGS.replace('\n', nl) + html[m.start():]
        with open(path, 'w', encoding='utf-8', errors='surrogateescape', newline='') as f:
            f.write(new)
        done += 1
print('Icon added to %d pages, %d already had one, %d need attention.' % (done, skipped, problems))
