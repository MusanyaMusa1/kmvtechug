#!/usr/bin/env python3
"""
KMVTECH Education - put ad spots on your pages.

Run from your kmvtechug folder:   python add-ads.py

Adds a small empty ad spot, plus the one-line ad script, to:
  - every course preview page   (spot "courses", above the FAQ)
  - the homepage                (spot "home", above the footer)
  - the student dashboard       (spot "dashboard", at the end of the main area)
Lessons and quizzes are never touched. An empty spot is invisible, so nothing changes until you
schedule an ad in the admin portal. Upload education/js/kmv-ads.js first.
Safe to run more than once.
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = next((p for p in (HERE, os.getcwd()) if os.path.isdir(os.path.join(p, 'education'))), None)
if ROOT is None:
    print('ERROR: I cannot find the "education" folder. Put this file in your kmvtechug folder and run it there.'); sys.exit(1)
EDU = os.path.join(ROOT, 'education')
TAG = '<script src="/education/js/kmv-ads.js" defer></script>'

def rd(p):
    with open(p, 'r', encoding='utf-8', errors='surrogateescape', newline='') as f: return f.read()
def wr(p, s):
    with open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='') as f: f.write(s)

def add(path, spot, anchors):
    """Insert the spot before the first anchor found, and the script before </body>."""
    h = rd(path)
    if 'data-kmv-ad=' in h: return 'SKIP  already has an ad spot'
    nl = '\r\n' if '\r\n' in h else '\n'
    box = '<div data-kmv-ad="%s"></div>' % spot
    pos = None
    for a in anchors:
        m = re.search(a, h, re.I)
        if m: pos = m.start(); break
    body = re.search(r'</body>', h, re.I)
    if pos is None: pos = body.start() if body else None
    if pos is None: return 'FAIL  no place to put it'
    h = h[:pos] + box + nl + h[pos:]
    if TAG not in h:
        body = re.search(r'</body>', h, re.I)
        h = (h[:body.start()] + TAG + nl + h[body.start():]) if body else h + nl + TAG + nl
    wr(path, h); return 'ADDED'

counts = {'ADDED': 0, 'SKIP': 0, 'FAIL': 0}
def run(label, path, spot, anchors):
    if not os.path.isfile(path): print('%-22s not found, skipped' % label); return
    r = add(path, spot, anchors); counts[r.split()[0]] += 1
    if label.startswith(('homepage', 'dashboard')) or r.startswith('FAIL'): print('%-22s %s' % (label, r))

run('homepage', os.path.join(EDU, 'index.html'), 'home', [r'<footer\b'])
run('dashboard', os.path.join(EDU, 'dashboard', 'index.html'), 'dashboard', [r'</main>', r'<footer\b'])
courses = os.path.join(EDU, 'courses')
for code in sorted(os.listdir(courses)) if os.path.isdir(courses) else []:
    p = os.path.join(courses, code, 'index.html')
    if os.path.isfile(p): run('course ' + code, p, 'courses', [r'<div class="section faq"', r'</main>', r'<footer\b'])
print('\nAd spots added: %d | already there: %d | problems: %d' % (counts['ADDED'], counts['SKIP'], counts['FAIL']))
if os.name == 'nt' and not os.environ.get('PROMPT'): input('Press Enter to close this window...')
