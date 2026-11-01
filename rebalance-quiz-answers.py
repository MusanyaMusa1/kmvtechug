#!/usr/bin/env python3
"""
KMVTECH Education - spread the correct answers in quizzes where it is always the first option.

Run from the repository root:   python rebalance-quiz-answers.py

Only touches quiz pages (data-ans format) where 90% or more of the answers are option 1.
It moves the existing correct option to a different position and updates the page to match.
The wording of every question and option stays exactly the same. Safe to run more than once.
This closes the "always click the first option" loophole. It does NOT improve weak wrong
options, so the quiz content itself still needs rewriting course by course.
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
BLOCK = re.compile(r'(<div class="qblock" data-ans=")(\d+)(">)([\s\S]*?)(</div>)(?=\s*(?:<div class="qblock"|<button|</form))')
LABEL = re.compile(r'<label class="opt">[\s\S]*?</label>')
SEQ = [1, 3, 0, 2, 3, 1, 2, 0]
fixed = skipped = 0
for d, _, files in os.walk(COURSES):
    if os.path.basename(d) != 'quiz' or 'index.html' not in files: continue
    p = os.path.join(d, 'index.html')
    with open(p, 'r', encoding='utf-8', errors='surrogateescape', newline='') as f: h = f.read()
    a = re.findall(r'data-ans="(\d+)"', h)
    if len(a) < 4 or a.count('0') / len(a) < 0.9: skipped += 1; continue
    shift = sum(map(ord, os.path.relpath(p, COURSES))) % len(SEQ); k = [0]
    def fix(m):
        body = m.group(4); labels = LABEL.findall(body)
        c = int(m.group(2))
        if len(labels) < 2 or c >= len(labels): return m.group(0)
        t = SEQ[(k[0] + shift) % len(SEQ)] % len(labels); k[0] += 1
        right = labels.pop(c); labels.insert(t, right)
        labels = [re.sub(r'value="\d+"', 'value="%d"' % i, L, count=1) for i, L in enumerate(labels)]
        first = body.find('<label class="opt">'); last = body.rfind('</label>') + len('</label>')
        return m.group(1) + str(t) + m.group(3) + body[:first] + ''.join(labels) + body[last:] + m.group(5)
    new = BLOCK.sub(fix, h)
    if new != h:
        with open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='') as f: f.write(new)
        fixed += 1
print('Quiz pages rebalanced: %d   already fine: %d' % (fixed, skipped))

if os.name == 'nt' and not os.environ.get('PROMPT'):
    input('Press Enter to close this window...')
