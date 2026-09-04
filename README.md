# Press room

A two-plate printing press for one image, in the browser.

The source study is a marble bust printed twice, blue in front and orange
behind. Both impressions are the same photograph, the second moved 87 across
and 16 down. This tool recovers that as two plates and lets you re-ink,
re-screen and re-register them.

Live: https://human-eyes-press-room.netlify.app

## Controls

**Palette** picks one of the ten approved palettes, or leave it on Custom.
Mode reads back which of the four print modes the current pair resolves to:
pure one-ink, chromatic plus black, complementary duotone, overprint duotone.

**Front face** and **Back face** each take an ink from nineteen, a strength,
and separate inks for their shadows and highlights. The back face also takes
an offset, which is what makes it a second impression rather than a copy.

**Reproduction** has seven processes: crisp screening, clean plate separation,
coarse halftone, risograph grain, cyanotype-like exposure, photocopy breakup,
newspaper screening. Screen, contrast and gamma are free afterwards. Knockout
removes the plate beneath across the shape on top; overprint lets them mix.

**Imperfections** are registration drift, uneven ink density, grain and dry
edge. The counter shows how many are in play against what the work calls for,
up to two for contemporary and two to three for tactile. It reports, it never
moves a slider you set. Grain is seeded from the recipe, so a setting always
reproduces its own marks.

PNG and SVG both save, with or without a background.

## Build

    python3 build/press-room.py

Writes `index.html`. `build/mask-blue.txt` is the front plate and
`build/mask-body.txt` is her outline, traced as one connected shape so the
knockout cannot run past her profile. Both are base64 PNGs.

Netlify serves the repository root.
