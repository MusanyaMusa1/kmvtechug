"""
KMVTECH Education - Master Patch Script
========================================
Fixes ALL courses in one run.

HOW TO USE:
1. Save this file to: C:\\Users\\ZAM\\Documents\\GitHub\\kmvtechug\\
2. Open Command Prompt
3. Type: cd C:\\Users\\ZAM\\Documents\\GitHub\\kmvtechug
4. Type: python patch-all-courses.py
5. Wait for it to finish
6. Open GitHub Desktop, commit all changes, push

WHAT THIS FIXES:
- Script load order (progress-tracking.js before inline script)
- True/False buttons missing type="button"
- saveQuizScore with raw score not percent
- checkAndIssueCertificate call on graded quizzes
- Em dashes replaced with hyphens
- trackProgress() in show() function
"""

import os, re

# ============================================================
# COURSE REGISTRY
# All 67 courses with code and total modules
# ============================================================
COURSES = {
    # LAW
    'evl1':     {'code': 'EVL1',     'modules': 8},
    'evl2':     {'code': 'EVL2',     'modules': 8},
    'eqt1':     {'code': 'EQT1',     'modules': 6},
    'crimproc': {'code': 'CRIMPROC', 'modules': 6},
    'medlaw':   {'code': 'MEDLAW',   'modules': 6},
    'fam1':     {'code': 'FAM1',     'modules': 6},
    'fam2':     {'code': 'FAM2',     'modules': 6},
    'lan1':     {'code': 'LAN1',     'modules': 6},
    'lan2':     {'code': 'LAN2',     'modules': 6},
    'crm1':     {'code': 'CRM1',     'modules': 6},
    'crm2':     {'code': 'CRM2',     'modules': 6},
    'jur1':     {'code': 'JUR1',     'modules': 6},
    'jur2':     {'code': 'JUR2',     'modules': 6},
    'cel1':     {'code': 'CEL1',     'modules': 6},
    'sog1':     {'code': 'SOG1',     'modules': 6},
    'inl1':     {'code': 'INL1',     'modules': 6},
    'ipl1':     {'code': 'IPL1',     'modules': 6},
    'cpl1':     {'code': 'CPL1',     'modules': 6},
    'tort1':    {'code': 'TORT1',    'modules': 6},
    'tort2':    {'code': 'TORT2',    'modules': 6},
    'conlaw1':  {'code': 'CONLAW1',  'modules': 6},
    'conlaw2':  {'code': 'CONLAW2',  'modules': 6},
    'adminlaw': {'code': 'ADMINLAW', 'modules': 6},
    'hrl1':     {'code': 'HRL1',     'modules': 6},
    # HEALTH SCIENCES
    'faec':     {'code': 'FAEC',     'modules': 6},
    'comh':     {'code': 'COMH',     'modules': 6},
    'ipc1':     {'code': 'IPC1',     'modules': 6},
    'mnch':     {'code': 'MNCH',     'modules': 6},
    'ncdpc':    {'code': 'NCDPC',    'modules': 6},
    'fammed':   {'code': 'FAMMED',   'modules': 6},
    'repuro':   {'code': 'REPURO',   'modules': 6},
    'foundhp':  {'code': 'FOUNDHP',  'modules': 6},
    'mhwp':     {'code': 'MHWP',     'modules': 6},
    'hcpe':     {'code': 'HCPE',     'modules': 6},
    'intepi':   {'code': 'INTEPI',   'modules': 6},
    'nuthw':    {'code': 'NUTHW',    'modules': 6},
    'meeth':    {'code': 'MEETH',    'modules': 6},
    # SOCIAL SCIENCES
    'envpsy':   {'code': 'ENVPSY',   'modules': 9},
    'cogpsy':   {'code': 'COGPSY',   'modules': 6},
    'socpsy':   {'code': 'SOCPSY',   'modules': 6},
    'compsy':   {'code': 'COMPSY',   'modules': 6},
    'comlife':  {'code': 'COMLIFE',  'modules': 6},
    'resmeth':  {'code': 'RESMETH',  'modules': 6},
    'bastat':   {'code': 'BASTAT',   'modules': 6},
    'newsrep':  {'code': 'NEWSREP',  'modules': 6},
    'genmedia': {'code': 'GENMEDIA', 'modules': 6},
    # BUSINESS
    'hrm1':     {'code': 'HRM1',     'modules': 9},
    'bmgt1':    {'code': 'BMGT1',    'modules': 6},
    'entrep':   {'code': 'ENTREP',   'modules': 6},
    'mktg1':    {'code': 'MKTG1',    'modules': 6},
    'acct1':    {'code': 'ACCT1',    'modules': 6},
    'econ1':    {'code': 'ECON1',    'modules': 6},
    'obehv':    {'code': 'OBEHV',    'modules': 6},
    'digmkt':   {'code': 'DIGMKT',   'modules': 6},
    'pmgt1':    {'code': 'PMGT1',    'modules': 6},
    'bcomm':    {'code': 'BCOMM',    'modules': 6},
    'procm':    {'code': 'PROCM',    'modules': 6},
    # IT
    'digsk':    {'code': 'DIGSK',    'modules': 6},
    'intrai':   {'code': 'INTRAI',   'modules': 6},
    'aiprompt': {'code': 'AIPROMPT', 'modules': 6},
    'cybersec': {'code': 'CYBERSEC', 'modules': 6},
    'ethhack':  {'code': 'ETHHACK',  'modules': 6},
    'hci':      {'code': 'HCI',      'modules': 6},
    'datapy1':  {'code': 'DATAPY1',  'modules': 6},
    'dbfund':   {'code': 'DBFUND',   'modules': 6},
    'webdev1':  {'code': 'WEBDEV1',  'modules': 6},
    'netfund':  {'code': 'NETFUND',  'modules': 6},
}

SUPABASE = '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>'
PROGRESS = '<script src="/education/js/progress-tracking.js"></script>'
SAVE_QUIZ = '<script src="/education/js/save-quiz-score.js"></script>'
CHECK_CERT = '<script src="/education/js/check-certificate.js"></script>'

COURSES_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'education', 'courses')

total_fixed = 0
total_skipped = 0
total_errors = 0
courses_found = 0
courses_missing = 0

print("=" * 60)
print("KMVTECH Education - Master Patch Script")
print("=" * 60)
print(f"Courses root: {COURSES_ROOT}")
print()

for folder, info in COURSES.items():
    course_path = os.path.join(COURSES_ROOT, folder)
    code = info['code']
    total_modules = info['modules']

    if not os.path.exists(course_path):
        print(f"  SKIP: {folder}/ not found on disk")
        courses_missing += 1
        continue

    courses_found += 1
    course_fixed = 0
    course_errors = 0

    for dirpath, dirs, files in os.walk(course_path):
        for fname in files:
            if not fname.endswith('.html'):
                continue

            fpath = os.path.join(dirpath, fname)
            rel = fpath.replace(COURSES_ROOT, '').replace('\\', '/')

            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    html = f.read()

                orig = html

                # Determine page type
                is_graded = bool(re.search(r'/\d+/quiz/index\.html$', rel))
                is_practice = bool(re.search(r'/\d+/\d+/quiz/index\.html$', rel))
                is_lesson = bool(re.search(r'/\d+/\d+/\d+/index\.html$', rel))
                is_summary = 'summary' in rel
                is_complete = 'complete' in rel
                is_grades = 'grades' in rel

                # Skip grades page - different structure
                if is_grades:
                    continue

                # ---- FIX 1: data-course attribute ----
                if f'data-course="{code}"' not in html:
                    html = re.sub(
                        r'<body([^>]*)>',
                        f'<body\\1 data-course="{code}">',
                        html, count=1
                    )

                # ---- FIX 2: Script order ----
                # Remove existing progress/save/cert tags wherever they are
                html = html.replace('\n' + PROGRESS, '')
                html = html.replace(PROGRESS + '\n', '')
                html = html.replace(PROGRESS, '')
                html = html.replace('\n' + SAVE_QUIZ, '')
                html = html.replace(SAVE_QUIZ + '\n', '')
                html = html.replace(SAVE_QUIZ, '')
                html = html.replace('\n' + CHECK_CERT, '')
                html = html.replace(CHECK_CERT + '\n', '')
                html = html.replace(CHECK_CERT, '')

                # Re-insert in correct order after Supabase
                if SUPABASE in html:
                    if is_graded:
                        # Graded quiz: all 4 scripts
                        html = html.replace(
                            SUPABASE,
                            SUPABASE + '\n' + PROGRESS + '\n' + SAVE_QUIZ + '\n' + CHECK_CERT
                        )
                    else:
                        # All other pages: only progress tracking
                        html = html.replace(
                            SUPABASE,
                            SUPABASE + '\n' + PROGRESS
                        )
                else:
                    # No supabase - add before </head>
                    if is_graded:
                        html = html.replace('</head>', SUPABASE + '\n' + PROGRESS + '\n' + SAVE_QUIZ + '\n' + CHECK_CERT + '\n</head>', 1)
                    else:
                        html = html.replace('</head>', SUPABASE + '\n' + PROGRESS + '\n</head>', 1)

                # ---- FIX 3: trackProgress() in show() ----
                if 'trackProgress()' not in html:
                    patterns = [
                        ("if(lc)lc.style.display='block';}", "if(lc)lc.style.display='block';trackProgress();}"),
                        ("if (lc) lc.style.display = 'block'; }", "if (lc) lc.style.display = 'block'; trackProgress(); }"),
                        ("if (lc) lc.style.display = 'block';\n  }", "if (lc) lc.style.display = 'block';\n  trackProgress();\n  }"),
                        ("lc.style.display='block';}", "lc.style.display='block';trackProgress();}"),
                        ("lc.style.display = 'block';\n}", "lc.style.display = 'block';\ntrackProgress();\n}"),
                    ]
                    for old_p, new_p in patterns:
                        if old_p in html:
                            html = html.replace(old_p, new_p)
                            break

                # ---- FIX 4: True/False type="button" ----
                def fix_tf(m):
                    tag = m.group(0)
                    if 'type=' not in tag:
                        tag = tag.replace('<button', '<button type="button"', 1)
                    return tag
                html = re.sub(r'<button[^>]*class="[^"]*tf-btn[^"]*"[^>]*>', fix_tf, html)
                html = re.sub(r'<button[^>]*>(True|False|TRUE|FALSE)</button>', 
                    lambda m: m.group(0).replace('<button', '<button type="button"', 1) 
                    if 'type=' not in m.group(0) else m.group(0), html)

                # ---- FIX 5: Graded quiz score saving ----
                if is_graded:
                    # Get module number from path
                    m = re.search(r'/(\d+)/quiz/index\.html$', rel)
                    mod_num = int(m.group(1)) if m else 1

                    # Fix saveQuizScore - ensure raw score not percent
                    if 'saveQuizScore(' not in html:
                        score_patterns = [
                            (f"const pct=Math.round(100*score/total);",
                             f"const pct=Math.round(100*score/total);saveQuizScore('{code}',{mod_num},score,total);checkAndIssueCertificate('{code}',{total_modules});"),
                            (f"const pct=Math.round((score/total)*100);",
                             f"const pct=Math.round((score/total)*100);saveQuizScore('{code}',{mod_num},score,total);checkAndIssueCertificate('{code}',{total_modules});"),
                            (f"const pct=Math.round((score/tot)*100);",
                             f"const pct=Math.round((score/tot)*100);saveQuizScore('{code}',{mod_num},score,tot);checkAndIssueCertificate('{code}',{total_modules});"),
                            (f"const pct = Math.round((score/total)*100);",
                             f"const pct = Math.round((score/total)*100);saveQuizScore('{code}',{mod_num},score,total);checkAndIssueCertificate('{code}',{total_modules});"),
                            (f"const pct = Math.round(100*score/total);",
                             f"const pct = Math.round(100*score/total);saveQuizScore('{code}',{mod_num},score,total);checkAndIssueCertificate('{code}',{total_modules});"),
                        ]
                        for old_p, new_p in score_patterns:
                            if old_p in html:
                                html = html.replace(old_p, new_p)
                                break
                    else:
                        # Fix if using percent*100 pattern (old wrong way)
                        html = re.sub(
                            rf"saveQuizScore\('{code}',\s*{mod_num},\s*pct,\s*100\)",
                            f"saveQuizScore('{code}',{mod_num},score,total)",
                            html
                        )
                        # Add checkAndIssueCertificate if missing
                        if 'checkAndIssueCertificate(' not in html and 'saveQuizScore(' in html:
                            html = re.sub(
                                rf"saveQuizScore\('{code}',{mod_num},([^)]+)\);",
                                f"saveQuizScore('{code}',{mod_num},\\1);checkAndIssueCertificate('{code}',{total_modules});",
                                html
                            )

                    # ---- FIX 6: Disable retry after answers shown ----
                    if 'bret' in html and 'style.display' not in html.split('bret')[1][:200]:
                        html = html.replace(
                            "document.getElementById('bret').style.display='block';",
                            "// retry disabled on graded quiz"
                        )
                        html = html.replace(
                            "document.getElementById('bret').style.display = 'block';",
                            "// retry disabled on graded quiz"
                        )

                # ---- FIX 7: Em dashes ----
                html = html.replace('\u2014', '-')

                # Save if changed
                if html != orig:
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(html)
                    total_fixed += 1
                    course_fixed += 1
                else:
                    total_skipped += 1

            except Exception as e:
                total_errors += 1
                course_errors += 1
                print(f"    ERROR: {rel}: {e}")

    status = "OK" if course_errors == 0 else "ERRORS"
    print(f"  [{status}] {folder}/ - Fixed: {course_fixed} files")

print()
print("=" * 60)
print("COMPLETE")
print(f"  Courses found on disk: {courses_found}")
print(f"  Courses not yet uploaded: {courses_missing}")
print(f"  Files fixed: {total_fixed}")
print(f"  Files already correct: {total_skipped}")
print(f"  Errors: {total_errors}")
print("=" * 60)

if total_fixed > 0:
    print()
    print("Next step: Open GitHub Desktop, commit all changes, and push.")
else:
    print()
    print("Nothing changed. All files already correct or no courses found.")
