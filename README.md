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
