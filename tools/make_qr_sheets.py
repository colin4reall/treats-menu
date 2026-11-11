#!/usr/bin/env python3
"""Generate print-ready QR sheets.

  python3 tools/make_qr_sheets.py              # both sheets, default URLs
  python3 tools/make_qr_sheets.py --venue      # table tent points at the venue wifi
  python3 tools/make_qr_sheets.py --venueqr    # big tent too

Print sizes:
  big-tent-banner.png          2400x1200  -> screen / A4 / A3
  big-tent-banner-print.png    6000x3000  -> A1 / A0 banner (about 180 DPI at A1)
  table-tent-sheet.png         1200x1700  -> A5 / A4 portrait table tent
"""
import os, re, json, subprocess, sys
import segno
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "qr")
os.makedirs(OUT, exist_ok=True)

ONLINE = "https://colin4reall.github.io/treats-menu/"

def lan_ip():
    for dev in ("en0", "en1", "en2"):
        ip = subprocess.run(["ipconfig", "getifaddr", dev],
                            capture_output=True, text=True).stdout.strip()
        if ip and not ip.startswith("169.254"):
            return ip
    return "192.168.1.50"

VENUE = f"http://{lan_ip()}:8080/"

def offline_payload():
    """Compact ASCII menu (names + prices) - small enough for a mini QR."""
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    raw = re.search(r'<script type="application/json" id="menu-data">(.*?)</script>',
                    html, re.S).group(1)
    data = json.loads(raw)

    def fold(s):
        return (str(s).replace("é", "e").replace("ñ", "n")
                      .replace("·", "-").replace("—", "-"))

    out = ["TREATS CAFE & RESTAURANT", "All prices in Ghana Cedis (GHS)", ""]
    for c in data["categories"]:
        out.append(fold(c["name"]).upper())
        w = min(max(len(fold(i["name"])) for i in c["items"]), 30)
        for it in c["items"]:
            n = fold(it["name"])
            n = n if len(n) <= w else n[:w - 1] + "..."
            out.append(f"{n}{' ' * (w - len(n))} GHS {it['price']}")
        out.append("")
    return "\n".join(out).rstrip()

OFFLINE_TEXT = offline_payload()

def fnt(name, size):
    p = f"/System/Library/Fonts/Supplemental/{name}"
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

def gradient(size, c0=(194, 24, 91), c1=(110, 14, 54)):
    w, h = size
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / max(1, h - 1)
        d.rectangle([0, y, w, y],
                    fill=(int(c0[0] + (c1[0] - c0[0]) * t),
                          int(c0[1] + (c1[1] - c0[1]) * t),
                          int(c0[2] + (c1[2] - c0[2]) * t)))
    return im

def qr_img(url, px, ec="h"):
    """Render at an exact integer module scale - never resample a QR."""
    p = os.path.join(OUT, "_tmp.png")
    qr = segno.make(url, error=ec, encoding="ascii", boost_error=False)
    border = 4
    modules = qr.symbol_size(scale=1, border=border)[0]
    scale = max(1, round(px / modules))
    qr.save(p, scale=scale, border=border)
    im = Image.open(p).convert("RGB")
    os.remove(p)
    return im, im.width

def big_tent(url, note, path, W=2400, H=1200, offline=False):
    k = W / 2400.0
    F_SCRIPT = fnt("Georgia Italic.ttf", int(74 * k))
    F_BLACK  = fnt("Arial Black.ttf", int(104 * k))
    F_BOLD   = fnt("Arial Bold.ttf", int(42 * k))
    F_REG    = fnt("Arial.ttf", int(34 * k))
    F_MONO   = fnt("Courier New Bold.ttf", int(40 * k))
    F_SMALL  = fnt("Arial Bold.ttf", int(26 * k))

    im = gradient((W, H))
    d = ImageDraw.Draw(im)
    d.ellipse([int(-260*k), int(-300*k), int(460*k), int(420*k)], fill=(220, 40, 105))
    d.ellipse([W-int(420*k), H-int(360*k), W+int(220*k), H+int(280*k)], fill=(130, 20, 62))

    x = int(150 * k)
    d.text((x, int(150 * k)), "Treats", font=F_SCRIPT, fill="#FFD9E8")
    d.text((x, int(224 * k)), "CAFE", font=F_BLACK, fill="#FFFFFF")
    d.text((x, int(340 * k)), "AND RESTAURANT", font=F_BOLD, fill="#FFD9E8")
    d.text((x, int(470 * k)), "Scan for our full menu", font=F_BLACK, fill="#FFFFFF")
    d.text((x, int(590 * k)), note, font=F_REG, fill="#FFD9E8")

    bb = d.textbbox((0, 0), url, font=F_MONO)
    tw, pad = bb[2] - bb[0], int(34 * k)
    d.rounded_rectangle([x, int(690 * k), x + tw + pad * 2, int(764 * k)],
                        radius=int(37 * k), fill="#FFFFFF")
    d.text((x + pad, int(706 * k)), url, font=F_MONO, fill="#C2185B")

    qpx = int(720 * k)
    qr, qs = qr_img(url, qpx, ec="h")
    im.paste(qr, (W - int(820 * k) - (qs - qpx) // 2, (H - qpx) // 2 - (qs - qpx) // 2))
    d.rounded_rectangle([W - int(840 * k), (H - int(740 * k)) // 2,
                         W - int(80 * k), (H + int(740 * k)) // 2],
                        radius=int(28 * k), outline="#FFFFFF", width=max(2, int(6 * k)))

    if offline:
        # small fallback QR: the whole menu as text - needs NO internet, ever
        opx = int(300 * k)
        oqr, oqs = qr_img(OFFLINE_TEXT, opx, ec="m")
        ox, oy = int(150 * k), int(830 * k)
        im.paste(oqr, (ox, oy))
        d.rounded_rectangle([ox - int(12*k), oy - int(12*k),
                             ox + oqs + int(12*k), oy + oqs + int(12*k)],
                            radius=int(14*k), outline="#FFFFFF", width=max(2, int(4*k)))
        d.text((ox, oy + oqs + int(26*k)), "NO SIGNAL?", font=F_SMALL, fill="#FFFFFF")
        d.text((ox, oy + oqs + int(62*k)), "Scan for the text menu", font=F_REG, fill="#FFD9E8")

    im.save(path, "PNG")
    print(f"  {os.path.basename(path):30s} {W}x{H}")

def table_tent(url, note, path):
    W, H = 1200, 1700
    F_SCRIPT = fnt("Georgia Italic.ttf", 74)
    F_BLACK  = fnt("Arial Black.ttf", 104)
    F_BOLD   = fnt("Arial Bold.ttf", 42)
    F_REG    = fnt("Arial.ttf", 34)
    F_MONO   = fnt("Courier New Bold.ttf", 30)
    im = gradient((W, H))
    d = ImageDraw.Draw(im)
    d.text((130, 110), "Treats", font=F_SCRIPT, fill="#FFD9E8")
    d.text((130, 184), "CAFE", font=F_BLACK, fill="#FFFFFF")
    d.text((130, 294), "AND RESTAURANT", font=F_BOLD, fill="#FFD9E8")
    d.text((130, 380), "Scan for our menu", font=F_BLACK, fill="#FFFFFF")
    d.text((130, 490), note, font=F_REG, fill="#FFD9E8")

    qr, qs = qr_img(url, 760, ec="h")
    im.paste(qr, ((W - qs) // 2, 580))
    d.rounded_rectangle([196, 556, 1004, 1364], radius=26, outline="#FFFFFF", width=5)

    bb = d.textbbox((0, 0), url, font=F_MONO)
    tw = bb[2] - bb[0]
    d.rounded_rectangle([(W - tw) / 2 - 26, 1420, (W + tw) / 2 + 26, 1492],
                        radius=36, fill="#FFFFFF")
    d.text(((W - tw) / 2, 1437), url, font=F_MONO, fill="#C2185B")
    d.text((190, 1560), "Good drinks - Good food - Great vibes", font=F_REG, fill="#FFD9E8")
    im.save(path, "PNG")
    print(f"  {os.path.basename(path):30s} {W}x{H}")

if __name__ == "__main__":
    use_venue = "--venue" in sys.argv or "--venueqr" in sys.argv
    venue_both = "--venueqr" in sys.argv
    if use_venue:
        t_url, t_note = VENUE, "Join our wifi first - no mobile data needed."
    else:
        t_url, t_note = ONLINE, "Works on any phone. No app needed."
    b_url = VENUE if venue_both else ONLINE
    b_note = "Join our wifi first - no mobile data needed." if venue_both else "Works on any phone. No app needed."

    print("BIG TENT:")
    big_tent(b_url, b_note, os.path.join(OUT, "big-tent-banner.png"))
    big_tent(b_url, b_note, os.path.join(OUT, "big-tent-banner-print.png"), W=6000, H=3000)
    big_tent(b_url, b_note, os.path.join(OUT, "big-tent-banner-combo.png"),
             W=2400, H=1200, offline=True)
    big_tent(b_url, b_note, os.path.join(OUT, "big-tent-banner-combo-print.png"),
             W=6000, H=3000, offline=True)
    print("TABLE TENT:")
    table_tent(t_url, t_note, os.path.join(OUT, "table-tent-sheet.png"))
    print(f"\n  big tent url   : {b_url}")
    print(f"  table tent url : {t_url}")
    if use_venue:
        print("  (venue mode - needs the server running at the venue)")
