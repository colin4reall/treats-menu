#!/usr/bin/env python3
"""Regenerate the offline QR codes after editing prices in index.html.

Usage:  python3 tools/make_offline_qr.py
Needs:  pip install segno
Output: qr/treats-menu-offline-*.png  (then: git add -A && git commit -m "new offline QR" && git push)
"""
import json, re, os, sys
import segno

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
OUT  = os.path.join(ROOT, "qr")

def fold(s):
    """Flatten to ASCII - several scanners mis-decode non-ASCII QR payloads."""
    return (str(s).replace("\u00e9","e").replace("\u00f1","n")
                  .replace("\u00b7","-").replace("\u2014","-"))

raw = re.search(r'<script type="application/json" id="menu-data">(.*?)</script>',
                open(HTML, encoding="utf-8").read(), re.S).group(1)
data = json.loads(raw)

def build(descriptions):
    out = ["TREATS CAFE & RESTAURANT", "All prices in Ghana Cedis (GHS)", ""]
    for c in data["categories"]:
        out.append(fold(c["name"]).upper())
        w = min(max(len(fold(i["name"])) for i in c["items"]), 30)
        for it in c["items"]:
            n = fold(it["name"])
            n = n if len(n) <= w else n[:w-1] + "..."
            line = f"{n}{' '*(w-len(n))} GHS {it['price']}"
            if descriptions and it.get("desc"):
                line += " | " + fold(it["desc"])
            out.append(line)
        out.append("")
    return "\n".join(out).rstrip()

os.makedirs(OUT, exist_ok=True)
full, compact = build(True), build(False)
for text, err, name in ((full, "l", "treats-menu-offline-full.png"),
                         (compact, "m", "treats-menu-offline-compact.png")):
    segno.make(text, error=err, encoding="ascii", boost_error=False) \
         .save(os.path.join(OUT, name), scale=5, border=4)
    print(f"  {name}  {len(text.encode())} bytes  EC-{err.upper()}")
open(os.path.join(OUT, "treats-menu-offline.txt"), "w", encoding="utf-8").write(full)
print("  treats-menu-offline.txt")
