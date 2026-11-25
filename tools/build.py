#!/usr/bin/env python3
"""Сборка index.html: данные курса подставляются в tools/template.html.
Запуск из корня репозитория: python3 tools/build.py"""
import json, re, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
cfg = json.loads((root / "config" / "structure.json").read_text(encoding="utf-8"))
lang = cfg["lang"]
rd = lambda p: (root / p).read_text(encoding="utf-8")

lessons, tests = {}, {}
for part in cfg["parts"]:
    for lid in part["lessons"]:
        lessons[lid] = rd(f"lessons/{lid}.md")
    if part.get("afterTest"):
        tests[part["afterTest"]] = rd(f"tests/{part['afterTest']}.md")

one = {"title": cfg["title"], "overview": rd("config/overview.md"),
       "lessons": lessons, "tests": tests, "exam": ""}
data = {"structure": {"parts": [
            {"part": i + 1, "title": {"ru": p["title"], "en": p["title"]}, "lessons": p["lessons"],
             **({"afterTest": p["afterTest"]} if p.get("afterTest") else {})}
            for i, p in enumerate(cfg["parts"])]},
        "ru": one, "en": one}

s = rd("tools/template.html")
s = s.replace("__COURSE_DATA__", json.dumps(data, ensure_ascii=False), 1)

def sub(a, b):
    global s
    assert a in s, a[:60]
    s = s.replace(a, b, 1)

sub('let lang = (()=>{try{const l=localStorage.getItem(LANG_KEY);return l==="en"?"en":"ru";}catch{return "ru";}})();', f'let lang = "{lang}";')
sub('const STATE_KEY="ds-course-exam-state-v1", LANG_KEY="ds-course-exam-lang";',
    f'const STATE_KEY="{cfg["storage"]}-state-v1", LANG_KEY="{cfg["storage"]}-lang";')
sub("</style>", ".lang-switch{display:none!important}\n#showExam{display:none!important}\n  </style>")
sub(r"\[([^\]]+)\]\((https?:[^)\s]+)\)", r"\[([^\]]+)\]\(((?:https?:|materials\/)[^)\s]+)\)")
sub("<title>Data Analytics and Fundamentals of Data Science – подготовка к зачету</title>", f"<title>{cfg['title']}</title>")
sub('<html lang="ru">', f'<html lang="{lang}">')
sub('<div class="brand-icon">DS</div>', f'<div class="brand-icon">{cfg["icon"]}</div>')
blk = re.search(rf"  {lang}:\{{.*?\n  \}}", s, re.S).group(0)
nb = blk
for k, v in cfg["ui"].items():
    nb, n = re.subn(rf'(\b{k}:)"(?:[^"\\]|\\.)*"', lambda m: f'{m.group(1)}"{v}"', nb, count=1)
    assert n == 1, k
s = s.replace(blk, nb, 1)
(root / "index.html").write_text(s, encoding="utf-8")
print("index.html", len(s) // 1024, "KB")
