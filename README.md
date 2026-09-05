# Press room

Design exploration tool to create print-inspired variations.

Using concepts and references from the excellent
[mono-color](https://github.com/yanliudesign/mono-color-skill) skill by Yan Liu.

Live: https://human-eyes-press-room.netlify.app

## Controls

- **Source** the default image or your own picture, dropped or picked
  (PNG with transparent background works best). Reset leaves it alone.
- **Background** colour.
- **Palette** ink colour, with ten ready-made presets or pick your own combo.
- **Front face** ink, strength, shadow ink and highlight ink, each with
  its own mix.
- **Back face** as above, x and y position.
- **Reproduction** process, screen, contrast, gamma, knockout or overprint,
  and which face sits on top.
- **Imperfections** registration, ink density, grain, dry edge.
- **Download** as PNG or SVG, transparent background optional

## Run

    python3 -m http.server 8777

`index.html` is the whole app. `mask-blue.png` and `mask-body.png` are the two
plates for the default image. Netlify serves the repository root.
