#!/usr/bin/env python3
"""
KMVTECH Education — Course Preview Page Patch Script
Run this from the root of the kmvtechug repository:
    python3 patch-preview-pages.py

What it does:
- Finds every education/courses/[code]/index.html file
- Replaces the static Enroll Now / Start Learning btn-row
  with a dynamic JavaScript enrollment check
- Already-patched files are skipped automatically
"""

import os, re, sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
COURSES_DIR = os.path.join(REPO_ROOT, 'education', 'courses')

NEW_BTN_SECTION = '''    <div class="btn-row" id="course-cta">
      <span style="color:var(--text-3);font-size:13px;">Checking your access...</span>
    </div>
    <script>
    (async function() {
      try {
        const SURL = 'https://nzjojrebyvxuawnkitth.supabase.co';
        const SKEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im56am9qcmVieXZ4dWF3bmtpdHRoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjE4MzI5NzcsImV4cCI6MjAzNzQwODk3N30.vK5lSBMigFMoKn-9Nf4onyFiVOehmhFIHzPrr7lL7Tg';
        const sb = (window.supabase && window.supabase.createClient)
          ? window.supabase.createClient(SURL, SKEY) : null;
        const cta = document.getElementById('course-cta');
        if (!cta) return;

        const COURSE_CODE = document.documentElement.getAttribute('data-course') || '';
        const firstLink = document.querySelector('.side a[data-mod="1"]');
        const firstUrl = firstLink ? firstLink.getAttribute('href') : '/education/';
        const title = document.querySelector('.ltitle');
        const titleText = title ? title.textContent.trim() : COURSE_CODE;
        const enrollUrl = '/education/enroll/?course=' + COURSE_CODE
          + '&name=' + encodeURIComponent(titleText);

        if (!sb) {
          cta.innerHTML = '<a class="btn btn-primary" href="' + enrollUrl + '">Enroll Now</a>';
          return;
        }

        const { data: { session } } = await sb.auth.getSession();

        if (!session) {
          cta.innerHTML =
            '<a class="btn btn-primary" href="' + enrollUrl + '">Enroll Now</a>'
            + '<a class="btn btn-secondary" href="/education/login/?return='
            + encodeURIComponent(window.location.href) + '">Log In</a>';
          return;
        }

        const now = new Date().toISOString();
        const { data: enr } = await sb
          .from('enrollments')
          .select('id, expires_at')
          .eq('student_id', session.user.id)
          .eq('course_code', COURSE_CODE)
          .single();

        const active = enr && (!enr.expires_at || enr.expires_at > now);

        if (active) {
          cta.innerHTML = '<a class="btn btn-primary" href="' + firstUrl + '">Start Learning</a>';
        } else {
          cta.innerHTML = '<a class="btn btn-primary" href="' + enrollUrl + '">Enroll Now</a>';
        }
      } catch(e) {
        const cta = document.getElementById('course-cta');
        const code = document.documentElement.getAttribute('data-course') || '';
        if (cta) cta.innerHTML =
          '<a class="btn btn-primary" href="/education/enroll/?course=' + code + '">Enroll Now</a>';
      }
    })();
    </script>'''

# Match the entire btn-row div including its contents
BTN_PATTERN = re.compile(
    r'<div class="btn-row">[\s\S]*?</div>(?=\s*(?:<script|<div class="section faq"|<div class="section"><h2>Frequently))',
    re.DOTALL
)

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    if 'id="course-cta"' in content:
        return 'SKIP  (already patched)'

    if 'class="btn-row"' not in content:
        return 'SKIP  (no btn-row found)'

    new_content, count = BTN_PATTERN.subn(NEW_BTN_SECTION, content)

    if count == 0:
        # Fallback: find btn-row and replace up to next section
        start = content.find('<div class="btn-row">')
        if start == -1:
            return 'SKIP  (btn-row not found)'
        # Find closing </div>
        depth = 0
        i = start
        end = -1
        while i < len(content):
            if content[i:i+4] == '<div':
                depth += 1
            elif content[i:i+6] == '</div>':
                depth -= 1
                if depth == 0:
                    end = i + 6
                    break
            i += 1
        if end == -1:
            return 'FAIL  (could not find closing div)'
        new_content = content[:start] + NEW_BTN_SECTION + content[end:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return 'FIXED'

patched = 0
skipped = 0
failed  = 0
results = []

if not os.path.isdir(COURSES_DIR):
    print(f'ERROR: courses directory not found at {COURSES_DIR}')
    print('Make sure you run this script from the kmvtechug repository root.')
    sys.exit(1)

for course in sorted(os.listdir(COURSES_DIR)):
    preview = os.path.join(COURSES_DIR, course, 'index.html')
    if not os.path.isfile(preview):
        continue
    result = patch_file(preview)
    results.append((course.upper(), result))
    if result == 'FIXED':
        patched += 1
    elif result.startswith('SKIP'):
        skipped += 1
    else:
        failed += 1

print('=' * 55)
print('  KMVTECH Education — Preview Page Patch Results')
print('=' * 55)
for code, res in results:
    icon = '✅' if res == 'FIXED' else ('⏭️' if res.startswith('SKIP') else '❌')
    print(f'  {icon}  {code:<12} {res}')
print('=' * 55)
print(f'  Fixed: {patched}   Skipped: {skipped}   Failed: {failed}')
print('=' * 55)

if failed == 0:
    print('\n✅ All done. Commit and push to GitHub to deploy.')
else:
    print(f'\n⚠️  {failed} file(s) need manual attention.')
