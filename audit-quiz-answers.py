#!/usr/bin/env python3
"""
KMVTECH Education - quiz answer audit.

Run from the repository root:   python audit-quiz-answers.py

Looks at EVERY quiz page and flags the ones where the correct answer is (almost) always the
first option, which lets a student pass by always clicking the first choice.
Reads the data-ans format only. Quiz pages in any other format are listed as "not readable",
so you know they were not checked.
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = next((p for p in (HERE, os.getcwd()) if os.path.isdir(os.path.join(p, 'education', 'courses'))), None)
if ROOT is None:
    print('ERROR: I cannot find the "education" folder.')
    print('  Folder this file is in :', HERE)
    print('  Folder you ran it from :', os.getcwd())
    print('FIX: put this file inside your kmvtechug folder (the one that contains the "education" folder),')
    print('     open Command Prompt in that folder, and run it again.')
    sys.exit(1)
COURSES = os.path.join(ROOT, 'education', 'courses')
tot_bad = 0; print('%-10s %6s %8s %12s' % ('COURSE', 'pages', 'flawed', 'not readable'))
for code in sorted(os.listdir(COURSES)):
    base = os.path.join(COURSES, code); pages = bad = unread = 0
    if not os.path.isdir(base): continue
    for d, _, files in os.walk(base):
        if os.path.basename(d) != 'quiz' or 'index.html' not in files: continue
        h = open(os.path.join(d, 'index.html'), encoding='utf-8', errors='ignore').read()
        a = re.findall(r'data-ans="(\d+)"', h)
        if not a: unread += 1; continue
        pages += 1
        if len(a) >= 4 and a.count('0') / len(a) >= 0.9: bad += 1
    if pages or unread:
        tot_bad += bad
        print('%-10s %6d %8d %12d   %s' % (code.upper(), pages, bad, unread, 'FIX NEEDED' if bad else ('ok' if pages else 'not checked')))
print('\n%d quiz page(s) can be passed by always choosing the first option.' % tot_bad)

if os.name == 'nt' and not os.environ.get('PROMPT'):
    input('Press Enter to close this window...')
