# Press room

Design exploration tool to create print-inspired variations.

Using concepts and references from the excellent
[mono-color](https://github.com/yanliudesign/mono-color-skill) skill by Yan Liu.

Live: https://human-eyes-press-room.netlify.app

## Controls

- **Paper** background colour, plus ten ready-made palettes.
- **Front face** ink, strength, shadow ink, highlight ink.
- **Back face** the same four, plus across and down.
- **Reproduction** process, screen, contrast, gamma, knockout or overprint,
  and which face sits on top.
- **Imperfections** registration, ink density, grain, dry edge.

## Build

    python3 build/press-room.py

Writes `index.html`, which is the whole app. `build/mask-blue.txt` and
`build/mask-body.txt` are the two masks, stored as base64 PNGs. Netlify serves
the repository root.
