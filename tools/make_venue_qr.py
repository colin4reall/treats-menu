#!/usr/bin/env python3
"""Generate a QR for a menu served from the restaurant's OWN wifi (no internet needed).

Run this on the machine that will serve the menu at the venue. It detects that
machine's LAN IP and writes a QR pointing at it.

  1. python3 tools/make_venue_qr.py
  2. python3 -m http.server 8080 --bind 0.0.0.0 --directory .
  3. print qr/treats-menu-venue-local.png and put it on the table

Guests join the restaurant wifi, scan, and get the full pretty menu with photos -
works with zero internet. Keep the server machine on and the address stable
(use a static/reserved DHCP lease on the router).
"""
import os, re, socket, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "qr")
PORT = 8080

def lan_ip():
    for dev in ("en0", "en1", "en2", "bridge0"):
        try:
            ip = subprocess.run(["ipconfig", "getifaddr", dev],
                                capture_output=True, text=True).stdout.strip()
            if ip and not ip.startswith("169.254"):
                return ip, dev
        except Exception:
            pass
    return socket.gethostbyname(socket.gethostname()), "auto"

ip, dev = lan_ip()
url = f"http://{ip}:{PORT}/"
print(f"interface : {dev}")
print(f"menu URL  : {url}")

try:
    import segno
except ImportError:
    sys.exit("pip install segno")

os.makedirs(OUT, exist_ok=True)
path = os.path.join(OUT, "treats-menu-venue-local.png")
segno.make(url, error="m", encoding="ascii", boost_error=False).save(path, scale=8, border=4)
print(f"QR written: {path}")

# plain-text fallback for anyone whose scanner dislikes a bare IP
open(os.path.join(OUT, "treats-menu-venue-local.txt"), "w").write(
    f"Treats Cafe menu (restaurant wifi)\n{url}\n\n"
    "Join our wifi, then open the link or scan the QR.\n"
)
print("also wrote treats-menu-venue-local.txt")
