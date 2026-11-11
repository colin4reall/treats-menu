Treats Cafe menu site.
Built from the CAKES menu posters. Edit index.html (menu-data block) to change items or prices.

## Regenerating the offline QR after a price change

The offline QR embeds the menu as text, so it must be regenerated whenever
`index.html` changes:

```sh
pip install segno
python3 tools/make_offline_qr.py
git add -A && git commit -m "new offline QR" && git push
```

## Which QR to use

| File | Needs internet | Notes |
|---|---|---|
| `qr/treats-menu-print-sheet.png` | Yes | Pretty menu with photos. Best for table tents. |
| `qr/treats-menu-offline-print-sheet.png` | **No** | Full menu as text. Works with zero signal. |
| `qr/treats-menu-offline-full.png` | **No** | All 57 items + descriptions. |
| `qr/treats-menu-offline-compact.png` | **No** | Names + prices only, denser, more scannable. |
| `qr/treats-menu-qr.svg` | Yes | Vector, for print at any size. |

Print both on the same tent: the online one for the pretty menu, the offline
one for when the wifi is down.

## Three ways to get the menu to a guest

| Option | Needs internet | Photos | Pretty | Maintenance |
|---|---|---|---|---|
| `qr/treats-menu-print-sheet.png` | Yes | Yes | Yes | none - updates itself |
| PWA (same URL, installed) | No, *after* first visit | Yes | Yes | none - auto-updates |
| `qr/treats-menu-offline-*.png` | **Never** | No | Plain text | re-print when prices change |
| `qr/treats-menu-venue-local.png` | **Never** | Yes | Yes | needs a machine on at the venue |

### The PWA (already enabled)

`sw.js` + `manifest.webmanifest` are live. Once a guest opens the menu, the page
and all 17 photos are cached on their phone, and "Add to Home Screen" gives them
an app icon. It then works with no signal at all.

### The venue-local server (truly zero internet, keeps the photos)

On the machine at the restaurant:

```sh
python3 tools/make_venue_qr.py          # detects this machine's LAN IP, writes the QR
python3 -m http.server 8080 --bind 0.0.0.0 --directory .
```

Guests join the restaurant wifi and scan `qr/treats-menu-venue-local.png`.
Full pretty menu with photos, no internet.

Caveats: the machine must stay on, the router needs a static/reserved lease for
that IP (or re-run `make_venue_qr.py` if it changes), and some guest networks
enable "client isolation", which blocks device-to-device traffic - test on the
real wifi before printing.

## Which file to print where

| Print job | File | Size | Print at |
|---|---|---|---|
| **Big tent** - window, wall, entrance banner | `qr/big-tent-banner-print.png` | 6000x3000 | A1 or A0 landscape (~180 DPI) |
| Big tent - small/quick | `qr/big-tent-banner.png` | 2400x1200 | A3 landscape |
| **Table tents** - tables, counter, cups | `qr/table-tent-sheet.png` | 1200x1700 | A5 or A4 portrait |
| Table tent (venue wifi only) | `python3 tools/make_qr_sheets.py --venue` | 1200x1700 | A5 or A4 portrait |

Regenerate after a price change:
```sh
python3 tools/make_qr_sheets.py
```

Both sheets print the URL as readable text under the QR, so anyone who cannot
scan (no camera, cracked screen, QR sticker damaged) can still type it in.
