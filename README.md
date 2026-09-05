# Press room

Design exploration tool to create print-inspired variations.

Using concepts and references from the excellent
[mono-color](https://github.com/yanliudesign/mono-color-skill) skill by Yan Liu.

Live: https://human-eyes-press-room.netlify.app

## Controls

- **Source** your own picture (PNG with transparent background works best).
- **Background** colour.
- **Palette** ink colour, with ten ready-made presets or pick your own combo.
- **Front face** ink, strength, shadow ink, highlight ink.
- **Back face** as above, x and y position.
- **Reproduction** process, screen, contrast, gamma, knockout or overprint,
  and which face sits on top.
- **Imperfections** registration, ink density, grain, dry edge.
- **Download** as PNG or SVG, transparent background optional

## Build

    python3 build/press-room.py

Writes `index.html`, which is the whole app. `build/mask-blue.txt` and
`build/mask-body.txt` are the two masks, stored as base64 PNGs. Netlify serves
the repository root.

