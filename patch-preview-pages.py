#!/usr/bin/env python3
"""
KMVTECH Education - course preview page button fix (version 2)

Run from the root of the kmvtechug repository:
    python patch-preview-pages.py

What it does for every education/courses/<code>/index.html:
  - Replaces the old Enroll Now / Start Learning buttons (and the earlier
    version of this fix) with the corrected enrollment check.
  - The check uses your real Supabase key and the same lookup your lesson
    pages use (courses.id -> enrollments.course_id).
  - Pages already on version 2 are skipped.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
COURSES = os.path.join(ROOT, 'education', 'courses')

NEW_BLOCK = '''<div class="btn-row" id="course-cta"><!-- cta-v2 -->
      <span style="color:var(--text-3);font-size:13px;">Checking your access...</span>
    </div>
    <script>
    (async function(){
      var cta=document.getElementById('course-cta'); if(!cta) return;
      var code=(document.documentElement.getAttribute('data-course')||'').toUpperCase();
      var first=document.querySelector('.side a[data-mod="1"]');
      var firstUrl=first?first.getAttribute('href'):'/education/';
      var t=document.querySelector('.ltitle');
      var title=t?t.textContent.trim():code;
      var enrollUrl='/education/enroll/?course='+code+'&name='+encodeURIComponent(title);
      function showEnroll(extra){cta.innerHTML='<a class="btn btn-primary" href="'+enrollUrl+'">Enroll Now</a>'+(extra||'');}
      try{
        if(typeof supabase==='undefined'){showEnroll();return;}
        var SB=supabase.createClient('https://nzjojrebyvxuawnkitth.supabase.co','sb_publishable_EKcJxtkPvorUeuLB9Q2xLA_SYIWzDDa');
        var s=await SB.auth.getSession(); var session=s&&s.data&&s.data.session;
        if(!session){showEnroll('<a class="btn btn-secondary" href="/education/login/?return='+encodeURIComponent(location.href)+'">Log In</a>');return;}
        var c=await SB.from('courses').select('id').eq('course_code',code).maybeSingle();
        if(!c.data){showEnroll();return;}
        var e=await SB.from('enrollments').select('id,expires_at').eq('student_id',session.user.id).eq('course_id',c.data.id).maybeSingle();
        var en=e.data;
        var active=en&&(!en.expires_at||new Date(en.expires_at)>new Date());
        if(active){cta.innerHTML='<a class="btn btn-primary" href="'+firstUrl+'">Start Learning</a>';}else{showEnroll();}
      }catch(err){showEnroll();}
    })();
    </script>'''

# earlier fix: div#course-cta followed by its own <script>...</script>
OLD_V1 = re.compile(r'<div class="btn-row" id="course-cta">[\s\S]*?</script>')
# original static buttons
STATIC = re.compile(r'<div class="btn-row">[\s\S]*?</div>')

def patch(path):
    with open(path, 'r', encoding='utf-8', errors='surrogateescape', newline='') as f:
        html = f.read()
    if 'cta-v2' in html:
        return 'SKIP   already version 2'
    if 'id="course-cta"' in html:
        new, n = OLD_V1.subn(lambda m: NEW_BLOCK, html, count=1)
        label = 'REPAIRED'
    elif 'class="btn-row"' in html:
        new, n = STATIC.subn(lambda m: NEW_BLOCK, html, count=1)
        label = 'FIXED'
    else:
        return 'SKIP   no button block found'
    if n == 0:
        return 'FAIL   pattern not matched'
    with open(path, 'w', encoding='utf-8', errors='surrogateescape', newline='') as f:
        f.write(new)
    return label

if not os.path.isdir(COURSES):
    print('ERROR: run this from the kmvtechug repository root.'); sys.exit(1)

counts = {}
for code in sorted(os.listdir(COURSES)):
    p = os.path.join(COURSES, code, 'index.html')
    if not os.path.isfile(p):
        continue
    r = patch(p)
    counts[r.split()[0]] = counts.get(r.split()[0], 0) + 1
    print('%-12s %s' % (code.upper(), r))
print('\nSummary:', counts)
