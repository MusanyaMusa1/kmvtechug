#!/usr/bin/env python3
"""
KMVTECH Education - Google settings.

Run from your kmvtechug folder:   python patch-seo.py

1. Hides every lesson, quiz, summary, grades and completion page from Google (noindex).
   Course preview pages, the homepage, the terms page and the verify page stay searchable.
2. Hides private pages (dashboard, portal, enroll, certificates, auth pages) from Google too.
3. Fixes each course preview page so Google is told the correct web address
   (kmvtechug.app/education/...), and gives the sharing image a full address.
4. Writes education/sitemap.xml listing the pages you DO want people to find.
Safe to run more than once.
"""
import os, re, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = next((p for p in (HERE, os.getcwd()) if os.path.isdir(os.path.join(p, 'education'))), None)
if ROOT is None:
    print('ERROR: I cannot find the "education" folder. Put this file in your kmvtechug folder and run it there.'); sys.exit(1)
EDU = os.path.join(ROOT, 'education'); COURSES = os.path.join(EDU, 'courses')
SITE = 'https://kmvtechug.app'
NOINDEX = '<meta name="robots" content="noindex, nofollow"/>'
PRIVATE = ['dashboard', 'portal', 'enroll', 'certificates', 'auth-error', 'auth']

def rd(p):
    with open(p, 'r', encoding='utf-8', errors='surrogateescape', newline='') as f: return f.read()
def wr(p, s):
    with open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='') as f: f.write(s)

def set_noindex(h):
    if re.search(r'<meta[^>]+name=["\']robots["\'][^>]*noindex', h, re.I): return h, False
    if re.search(r'<meta[^>]+name=["\']robots["\']', h, re.I):
        return re.sub(r'<meta[^>]+name=["\']robots["\'][^>]*>', NOINDEX, h, count=1, flags=re.I), True
    m = re.search(r'</head>', h, re.I)
    if not m: return h, False
    nl = '\r\n' if '\r\n' in h else '\n'
    return h[:m.start()] + NOINDEX + nl + h[m.start():], True

stats = {'lesson': 0, 'private': 0, 'canon': 0, 'image': 0}
previews = []
# 1. lesson-level pages
for code in sorted(os.listdir(COURSES)):
    base = os.path.join(COURSES, code)
    if not os.path.isdir(base): continue
    for d, _, files in os.walk(base):
        if 'index.html' not in files: continue
        p = os.path.join(d, 'index.html'); is_root = os.path.abspath(d) == os.path.abspath(base)
        h = rd(p)
        if is_root:
            previews.append(code)
            c = SITE + '/education/courses/%s/' % code
            if re.search(r'<link[^>]+rel=["\']canonical["\']', h, re.I):
                n = re.sub(r'(<link[^>]+rel=["\']canonical["\'][^>]+href=["\'])[^"\']*(["\'])', lambda m: m.group(1) + c + m.group(2), h, count=1, flags=re.I)
            else:
                m = re.search(r'</head>', h, re.I); nl = '\r\n' if '\r\n' in h else '\n'
                n = h[:m.start()] + '<link rel="canonical" href="%s"/>' % c + nl + h[m.start():] if m else h
            if n != h: stats['canon'] += 1; h = n
            # share image: make it a full address, using whichever hero file really exists
            cand = ['/education/courses/%s/hero.jpg' % code, '/education/assets/course-images/%s-hero.jpg' % code]
            real = next((x for x in cand if os.path.isfile(os.path.join(ROOT, x.lstrip('/').replace('/', os.sep)))), None)
            if real:
                n = re.sub(r'(<meta[^>]+property=["\']og:image["\'][^>]+content=["\'])[^"\']*(["\'])', lambda m: m.group(1) + SITE + real + m.group(2), h, count=1, flags=re.I)
                if n != h: stats['image'] += 1; h = n
            wr(p, h)
        else:
            n, ch = set_noindex(h)
            if ch: wr(p, n); stats['lesson'] += 1
# 2. private pages
for name in PRIVATE:
    top = os.path.join(EDU, name)
    for d, _, files in os.walk(top):
        if 'index.html' in files:
            p = os.path.join(d, 'index.html'); n, ch = set_noindex(rd(p))
            if ch: wr(p, n); stats['private'] += 1
# 3. sitemap
today = datetime.date.today().isoformat()
urls = [(SITE + '/education/', '1.0'), (SITE + '/education/terms/', '0.3')]
urls += [(SITE + '/education/courses/%s/' % c, '0.8') for c in sorted(previews)]
xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
    '  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n' % (u, today, pr) for u, pr in urls) + '</urlset>\n'
wr(os.path.join(EDU, 'sitemap.xml'), xml)
print('Lesson-level pages hidden from Google : %d' % stats['lesson'])
print('Private pages hidden from Google      : %d' % stats['private'])
print('Preview pages with corrected address  : %d' % stats['canon'])
print('Preview pages with full sharing image : %d' % stats['image'])
print('Sitemap written: education/sitemap.xml with %d pages (%d course previews)' % (len(urls), len(previews)))
if os.name == 'nt' and not os.environ.get('PROMPT'): input('Press Enter to close this window...')
