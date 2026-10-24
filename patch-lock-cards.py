#!/usr/bin/env python3
"""
KMVTECH Education - fix the locked-page message on every lesson, quiz and summary page.

Run from the root of the kmvtechug repository:
    python patch-lock-cards.py

What a visitor now sees when they land directly on a lesson page:
  - Not logged in      -> Log In / Register Free buttons (plus a link to the course page)
  - Logged in, no plan -> "Enroll in <course>" button that opens the enrollment form
  - Access expired     -> Renew button (opens the enrollment form)
  - Slow / failed check -> a clear message with Try Again (never a blank page)
Pages show "Checking your access..." while the check runs.

Safe to run more than once. Only touches education/courses/**/index.html.
"""
import os, re, sys, json

ROOT = os.path.dirname(os.path.abspath(__file__))
COURSES = os.path.join(ROOT, 'education', 'courses')
MARK = 'kmv-lock-v2'

FUNC = r'''/* kmv-lock-v2 */
function __FN__(r) {
  var CODE = __CODE__, NAME = __NAME__;
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); };
  var back = encodeURIComponent(location.href);
  var enrol = '/education/enroll/?course=' + CODE + '&name=' + encodeURIComponent(NAME);
  var info = '/education/courses/' + CODE.toLowerCase() + '/';
  var B = 'display:block;width:100%;max-width:340px;margin:10px auto 0;padding:13px 18px;border-radius:10px;font-weight:700;font-size:14.5px;text-align:center;text-decoration:none;box-sizing:border-box;font-family:inherit;';
  var P = B + 'background:#2B3FBF;color:#fff;border:1.5px solid #2B3FBF;';
  var S = B + 'background:transparent;color:#2B3FBF;border:1.5px solid #2B3FBF;';
  var L = 'display:inline-block;margin-top:16px;font-size:13px;color:#6B7280;text-decoration:underline;';
  var n = esc(NAME);
  var cards = {
    loading: { i: '&#8987;', h: 'Checking your access...', p: 'One moment please.', b: [] },
    guest: { i: '&#128274;', h: 'Log in to continue',
      p: 'This lesson is part of <strong>' + n + '</strong>. Log in with your student account, or register free to get your student number. After that, enroll in the course to start studying.',
      b: [['Log In', '/education/login/?return=' + back, P], ['Register Free', '/education/register/?return=' + back, S]] },
    no_plan: { i: '&#128218;', h: 'Enroll in ' + n + ' to continue',
      p: 'Your account is registered, but you are not enrolled in this course yet. Enroll to unlock all lessons, quizzes, notes and your certificate. UGX 5,000 for 30 days in this course, UGX 20,000 for all courses for 30 days, or UGX 50,000 for all courses for 5 months.',
      b: [['Enroll in this Course', enrol, P]] },
    expired: { i: '&#9200;', h: 'Your access has ended',
      p: 'Your plan for <strong>' + n + '</strong> has expired. Renew to continue from where you stopped. Your progress is saved.',
      b: [['Renew Access', enrol, P]] },
    error: { i: '&#9888;&#65039;', h: 'We could not check your access',
      p: 'This can happen on a slow connection. Please try again.',
      b: [['Try Again', 'javascript:location.reload()', P]] }
  };
  var x = cards[r] || cards.guest;
  var html = '<div style="max-width:520px;margin:48px auto;padding:32px 24px;text-align:center;border:1px solid rgba(128,128,128,.3);border-radius:16px;background:var(--surface,#fff);color:var(--text-1,#1C1C1C);">'
    + '<div style="font-size:40px;line-height:1;margin-bottom:12px;">' + x.i + '</div>'
    + '<h2 style="font-size:21px;margin:0 0 10px;font-weight:800;">' + x.h + '</h2>'
    + '<p style="font-size:14.5px;line-height:1.65;margin:0 0 18px;color:var(--text-2,#4B5563);">' + x.p + '</p>';
  for (var k = 0; k < x.b.length; k++) { html += '<a href="' + x.b[k][1] + '" style="' + x.b[k][2] + '">' + x.b[k][0] + '</a>'; }
  if (r !== 'loading') { html += '<a href="' + info + '" style="' + L + '">View course details</a>'; }
  html += '</div>';
  var box = document.getElementById('__BOX__');
  if (box) { box.innerHTML = html; box.style.display = 'block'; }
  var lc = document.getElementById('lc'); if (lc) lc.style.display = 'none';
}'''

WRAP = r'''/* kmv-lock-v2 */
(function () {
  __FN__('loading');
  var settled = false;
  var timer = setTimeout(function () { if (!settled) __FN__('error'); }, 12000);
  Promise.resolve().then(__CHK__).then(function () {
    settled = true; clearTimeout(timer);
    var lc = document.getElementById('lc'), bx = document.getElementById('__BOX__');
    if (lc && bx && lc.style.display === 'block') bx.style.display = 'none';
  }).catch(function () { settled = true; clearTimeout(timer); __FN__('error'); });
})();'''

def skip_template(s, j):
    j += 1
    while s[j] != '`':
        if s[j] == '\\': j += 2; continue
        if s[j] == '$' and s[j+1] == '{': j = match_brace(s, j+1) + 1; continue
        j += 1
    return j

def match_brace(s, i):
    depth, j, n = 0, i, len(s)
    while j < n:
        c = s[j]
        if c in '\'"':
            q = c; j += 1
            while j < n and s[j] != q:
                if s[j] == '\\': j += 1
                j += 1
        elif c == '`': j = skip_template(s, j)
        elif c == '/' and s[j+1:j+2] == '/':
            k = s.find('\n', j); j = n if k < 0 else k
        elif c == '/' and s[j+1:j+2] == '*': j = s.index('*/', j) + 1
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return j
        j += 1
    raise ValueError('unbalanced')

def course_name(folder, cache):
    if folder in cache: return cache[folder]
    name = None
    p = os.path.join(COURSES, folder, 'index.html')
    if os.path.isfile(p):
        h = open(p, encoding='utf-8', errors='replace').read()
        m = re.search(r'<h1 class="ltitle">([^<]+)', h) or re.search(r'<title>([^<(|]+)', h)
        if m: name = m.group(1).strip()
    cache[folder] = name or folder.upper()
    return cache[folder]

def patch(path, folder, cache):
    with open(path, 'r', encoding='utf-8', errors='surrogateescape', newline='') as f:
        h = f.read()
    if MARK in h: return 'SKIP  already patched'
    fm = re.search(r'function (showLk|showLocked)\s*\(', h)
    if not fm: return 'SKIP  no lock code'
    fn = fm.group(1); box = 'lk' if fn == 'showLk' else 'locked'
    if ('id="%s"' % box) not in h: return 'SKIP  older layout (links updated separately)'
    cm = re.search(r"eq\('course_code',\s*'([A-Z0-9]+)'\)", h)
    code = cm.group(1) if cm else folder.upper()
    name = course_name(folder, cache)
    try:
        end = match_brace(h, h.index('{', fm.start())) + 1
    except Exception:
        return 'FAIL  could not read function'
    func = (FUNC.replace('__FN__', fn).replace('__BOX__', box)
            .replace('__CODE__', json.dumps(code)).replace('__NAME__', json.dumps(name)))
    h2 = h[:fm.start()] + func + h[end:]
    calls = list(re.finditer(r'\b(chkAccess|checkAccess)\(\);', h2))
    if not calls: return 'FAIL  access call not found'
    im = calls[-1]
    wrap = WRAP.replace('__FN__', fn).replace('__BOX__', box).replace('__CHK__', im.group(1))
    h2 = h2[:im.start()] + wrap + h2[im.end():]
    if '\r\n' in h: h2 = h2.replace('\r\n', '\n').replace('\n', '\r\n')
    with open(path, 'w', encoding='utf-8', errors='surrogateescape', newline='') as f:
        f.write(h2)
    return 'FIXED'

if not os.path.isdir(COURSES):
    print('ERROR: run this from the kmvtechug repository root.'); sys.exit(1)

cache, total, bad = {}, {}, []
for folder in sorted(os.listdir(COURSES)):
    base = os.path.join(COURSES, folder)
    if not os.path.isdir(base): continue
    c = {'FIXED': 0, 'SKIP': 0, 'FAIL': 0}
    for d, _, files in os.walk(base):
        for fn_ in files:
            if fn_ != 'index.html': continue
            p = os.path.join(d, fn_)
            r = patch(p, folder, cache)
            c[r.split()[0]] += 1
            if r.startswith('FAIL'): bad.append((os.path.relpath(p, ROOT), r))
    total[folder] = c
    print('%-10s fixed=%-3d skipped=%-3d failed=%d' % (folder.upper(), c['FIXED'], c['SKIP'], c['FAIL']))

# Sweep: any page still linking to the broken sign-in address (e.g. the grades pages)
swept = 0
for d, _, files in os.walk(COURSES):
    for fn_ in files:
        if not fn_.endswith('.html'): continue
        p = os.path.join(d, fn_)
        with open(p, 'r', encoding='utf-8', errors='surrogateescape', newline='') as f:
            h = f.read()
        if 'href="/education/auth/"' in h:
            with open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='') as f:
                f.write(h.replace('href="/education/auth/"', 'href="/education/login/"'))
            swept += 1
print('Sign-in links corrected on %d more pages.' % swept)

# Older quiz layout (locked-state box): point the plan buttons at the enrollment form
old_layout = 0
for folder in sorted(os.listdir(COURSES)):
    base = os.path.join(COURSES, folder)
    if not os.path.isdir(base): continue
    for d, _, files in os.walk(base):
        for fn_ in files:
            if fn_ != 'index.html': continue
            p = os.path.join(d, fn_)
            with open(p, 'r', encoding='utf-8', errors='surrogateescape', newline='') as f:
                h = f.read()
            if 'id="locked-state"' not in h or 'href="/education/#pricing"' not in h: continue
            cm = re.search(r"eq\('course_code',\s*'([A-Z0-9]+)'\)", h)
            code = cm.group(1) if cm else folder.upper()
            url = '/education/enroll/?course=%s&name=%s' % (code, __import__('urllib.parse').parse.quote(course_name(folder, cache)))
            h = h.replace('href="/education/#pricing" class="btn-unlock">View Plans &#8594;', 'href="%s" class="btn-unlock">Enroll in this Course &#8594;' % url)
            h = h.replace('href="/education/#pricing"', 'href="%s"' % url)
            with open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='') as f:
                f.write(h)
            old_layout += 1
print('Older-layout quiz pages updated: %d' % old_layout)
print('\nTotal fixed:', sum(v['FIXED'] for v in total.values()))
for p, r in bad: print('NEEDS ATTENTION:', p, '-', r)
