#!/usr/bin/env python3
"""Build the press room.

Writes index.html at the repository root, ready to serve. The two plates and
her traced outline live beside this file as base64 PNGs."""
import json, pathlib

D = pathlib.Path(__file__).parent
OUT = D.parent / 'index.html'
BLUE = (D / 'mask-blue.txt').read_text().strip()
BODY = (D / 'mask-body.txt').read_text().strip()

INKS = [
    ('Cobalt', '#2148B8'), ('Royal Blue', '#2058D4'), ('Ultramarine', '#263E99'),
    ('Electric Blue', '#173AE3'), ('Slate Blue', '#4773A5'), ('Powder Blue', '#9EB8D3'),
    ('Cyan', '#159DDA'), ('Botanical Green', '#008A4B'), ('Mint Green', '#5EB783'),
    ('Terracotta', '#C65F38'), ('Safety Orange', '#E55D2B'), ('Tangerine', '#E46C2D'),
    ('Signal Red', '#C83232'), ('Brick Red', '#B64032'), ('Oxblood', '#8F3434'),
    ('Aubergine', '#63365F'), ('Charcoal', '#30343A'), ('Warm Charcoal', '#302D2E'),
    ('Carbon', '#242321'),
]
# the ten approved palettes, verbatim from design-system/colors.json
PALETTES = [
    ('Custom', '', []),
    ('Cobalt', 'pure one-ink', ['Cobalt']),
    ('Terracotta', 'pure one-ink', ['Terracotta']),
    ('Signal Red', 'pure one-ink', ['Signal Red']),
    ('Aubergine', 'pure one-ink', ['Aubergine']),
    ('Charcoal + Signal Red', 'chromatic + black', ['Signal Red', 'Charcoal']),
    ('Cobalt + Terracotta', 'complementary duotone', ['Cobalt', 'Terracotta']),
    ('Ultramarine + Safety Orange', 'overprint duotone', ['Ultramarine', 'Safety Orange']),
    ('Botanical Green + Oxblood', 'complementary duotone', ['Botanical Green', 'Oxblood']),
    ('Cyan + Brick Red', 'overprint duotone', ['Cyan', 'Brick Red']),
    ('Mint Green + Warm Charcoal', 'chromatic + black', ['Mint Green', 'Warm Charcoal']),
]

SUBSTRATES = [
    ('Neutral White', '#FAFAF7'), ('Cool Gray', '#E9E9E5'), ('Pale Beige', '#F5F1E8'),
    ('app Paper', '#FAFAFA'), ('app Surface', '#FFFFFF'),
    ('app dark', '#121212'), ('app panel dark', '#1D1D1D'), ('about dark', '#0D0D0D'),
    ('Transparent', ''),
]
# name, screen, cell px, gamma, contrast, grain, threshold
# name, screen kind, screen 0-100, gamma 0-100, contrast 0-100, grain, threshold
PROCESSES = [
    ('Crisp screening', 'dot', 36, 29, 25, 0, 0),
    ('Clean plate separation', 'none', 27, 29, 21, 0, 0),
    ('Coarse halftone', 'dot', 11, 29, 24, 0, 0),
    ('Risograph grain', 'dot', 27, 27, 24, 0.35, 0),
    ('Cyanotype-like exposure', 'none', 27, 18, 45, 0, 0),
    ('Photocopy breakup', 'dot', 42, 39, 63, 0.22, 0.42),
    ('Newspaper screening', 'line', 26, 29, 29, 0.08, 0),
]

def opts(rows, sel=0):
    return ''.join(
        f'<option value="{i}"{" selected" if i == sel else ""}>{r[0]}</option>'
        for i, r in enumerate(rows))

HTML = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Press room</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Cormorant+Garamond:wght@600&display=swap">
<style>
:root{{--f-sans:"Instrument Sans","Segoe UI",system-ui,sans-serif;
--f-mono:"JetBrains Mono",ui-monospace,monospace;
--f-serif:"Cormorant Garamond","Iowan Old Style",Georgia,serif;--sheet:#EDECE7;--edge:#26251F;--dim:#6E6C66;
--line:#CFCEC8;color-scheme:light}}
*{{box-sizing:border-box}}
html,body{{height:100%}}
body{{margin:0;background:var(--sheet);color:var(--edge);
font:400 14px/20px var(--f-sans);display:flex;flex-direction:column;overflow:hidden}}
h1,h2,h3,p{{margin:0}}

.top{{flex:none;display:flex;align-items:baseline;gap:12px;
padding:9px 16px;border-bottom:1px solid var(--edge)}}
.top h1{{font:600 20px/1 var(--f-serif);color:#63365F;letter-spacing:-.01em}}
.top h1 em{{font-style:italic;font-weight:600}}
.top .readout{{font:400 12px/16px var(--f-mono);color:var(--dim)}}

.wrap{{flex:1;display:flex;min-height:0}}
.panel{{width:328px;flex:none;overflow-y:auto;border-right:1px solid var(--edge);
background:#F4F3EE}}
.stage{{flex:1;min-width:0;min-height:0;display:flex;flex-direction:column;
align-items:flex-start;gap:10px;padding:12px 16px}}
#out{{flex:1;min-height:0;height:100%;width:auto;aspect-ratio:1;
border:1px solid var(--line);display:block}}
.acts{{flex:none;display:flex;gap:8px}}
@media(max-width:820px){{
  body{{overflow:auto}} .wrap{{flex-direction:column-reverse}}
  .panel{{width:100%;border-right:0;border-top:1px solid var(--edge)}}
  #out{{width:100%;height:auto;flex:none}}
}}

fieldset{{border:0;border-bottom:1px solid var(--line);margin:0;padding:0 0 14px}}
legend{{display:block;width:100%;padding:13px 16px 8px;
font:500 11px/15px var(--f-mono);letter-spacing:.11em;text-transform:uppercase;
color:var(--dim)}}
.row{{display:grid;grid-template-columns:84px 1fr 34px;gap:10px;align-items:center;
padding:0 16px;margin-top:9px}}
.row label{{font:400 13px/18px var(--f-sans);color:var(--edge)}}
.row output{{font:400 12px/16px var(--f-mono);color:var(--dim);text-align:right}}
select,input[type=range]{{width:100%;margin:0}}
select{{font:400 13px/18px var(--f-sans);height:30px;padding:0 8px;
border:1px solid var(--line);background:#fff;color:var(--edge);border-radius:4px}}
input[type=range]{{accent-color:#63365F;height:30px}}
.chk{{display:flex;align-items:center;gap:9px;padding:0 16px;margin-top:10px;
font:400 13px/18px var(--f-sans)}}
.chk input{{margin:0;accent-color:#63365F}}
.row.off{{opacity:.42}}
.row.off input,.row.off select{{pointer-events:none}}
button.act{{border:1px solid var(--line);background:#fff;cursor:pointer;
padding:0 14px;height:30px;font:400 13px/18px var(--f-sans);
color:var(--edge);border-radius:4px}}
button.act:hover{{border-color:var(--edge)}}
</style>

<div class="top"><h1><em>Press</em> room</h1>
<span class="readout" id="recipe"></span></div>

<div class="wrap">
  <div class="panel">
    <fieldset><legend>Background</legend>
      <div class="row"><label>Background</label>
        <select id="sub">{opts(SUBSTRATES)}</select><output></output></div>
    </fieldset>

    <fieldset><legend>Palette</legend>
      <div class="row"><label>Approved</label>
        <select id="pal">{opts(PALETTES)}</select><output></output></div>
      <div class="row"><label>Mode</label>
        <span id="mode" style="font:400 13px/18px var(--f-sans)"></span><output></output></div>
    </fieldset>

    <fieldset><legend>Front face</legend>
      <div class="row"><label>Ink</label>
        <select id="ink1">{opts(INKS, 15)}</select><output></output></div>
      <div class="row"><label>Strength</label>
        <input type="range" id="str1" min="0" max="130" value="100"><output>100</output></div>
      <div class="row"><label>Shadows</label>
        <select id="sha1"><option value="-1">one ink</option>{opts(INKS, -1)}</select><output></output></div>
      <div class="row"><label>Highlights</label>
        <select id="hil1"><option value="-1">paper</option>{opts(INKS, -1)}</select><output></output></div>
    </fieldset>

    <fieldset><legend>Back face</legend>
      <div class="row"><label>Ink</label>
        <select id="ink2">{opts(INKS, 10)}</select><output></output></div>
      <div class="row"><label>Strength</label>
        <input type="range" id="str2" min="0" max="130" value="100"><output>100</output></div>
      <div class="row"><label>Across</label>
        <input type="range" id="offx" min="-300" max="300" value="138"><output>138</output></div>
      <div class="row"><label>Down</label>
        <input type="range" id="offy" min="-300" max="300" value="25"><output>25</output></div>
      <div class="row"><label>Shadows</label>
        <select id="sha2"><option value="-1">one ink</option>{opts(INKS, -1)}</select><output></output></div>
      <div class="row"><label>Highlights</label>
        <select id="hil2"><option value="-1">paper</option>{opts(INKS, -1)}</select><output></output></div>
    </fieldset>

    <fieldset><legend>Reproduction</legend>
      <div class="row"><label>Process</label>
        <select id="proc">{opts(PROCESSES)}</select><output></output></div>
      <div class="row"><label>Screen</label>
        <input type="range" id="cell" min="0" max="100" value="27"><output>27</output></div>
      <div class="row"><label>Contrast</label>
        <input type="range" id="con" min="0" max="100" value="25"><output>25</output></div>
      <div class="row"><label>Gamma</label>
        <input type="range" id="gam" min="0" max="100" value="29"><output>29</output></div>
      <div class="chk"><input type="radio" name="meet" id="ko" value="ko" checked>
        <label for="ko">Knockout</label>
        <input type="radio" name="meet" id="over" value="over" style="margin-left:14px">
        <label for="over">Overprint</label></div>
      <div class="row"><label>Knockout</label>
        <input type="range" id="kamt" min="0" max="100" value="100"><output>100</output></div>
      <div class="chk"><input type="checkbox" id="order">
        <label for="order">Back face on top</label></div>
    </fieldset>

    <fieldset><legend>Imperfections</legend>
      <div class="row"><label>Work</label>
        <select id="work"><option value="0">Contemporary, up to 2</option>
        <option value="1">Tactile, 2 to 3</option></select><output id="ncount"></output></div>
      <div class="row"><label>Registration</label>
        <input type="range" id="reg" min="0" max="100" value="0"><output>0</output></div>
      <div class="row"><label>Ink density</label>
        <input type="range" id="den" min="0" max="100" value="0"><output>0</output></div>
      <div class="row"><label>Grain</label>
        <input type="range" id="gra" min="0" max="100" value="0"><output>0</output></div>
      <div class="row"><label>Dry edge</label>
        <input type="range" id="dry" min="0" max="100" value="0"><output>0</output></div>
    </fieldset>
  </div>

  <div class="stage">
    <canvas id="out" width="1400" height="1400"></canvas>
    <div class="acts">
      <button class="act" id="swap">Swap</button>
      <button class="act" id="reset">Reset</button>
      <button class="act" id="dl">PNG</button>
      <button class="act" id="svg">SVG</button>
      <label class="chk" style="padding:0;margin:0"><input type="checkbox" id="alpha">
        <span>Transparent</span></label>
    </div>
  </div>
</div>

<script>
const INKS = {[[n, h] for n, h in INKS]!r}.map(a=>({{name:a[0],hex:a[1]}}));
const SUBS = {[[n, h] for n, h in SUBSTRATES]!r}.map(a=>({{name:a[0],hex:a[1]}}));
const PROCS = {[list(p) for p in PROCESSES]!r}.map(a=>({{
  name:a[0],screen:a[1],cell:a[2],gamma:a[3],contrast:a[4],grain:a[5],thresh:a[6]}}));

const SRC = {{blue:"data:image/png;base64,{BLUE}",
              body:"data:image/png;base64,{BODY}"}};

const N = 1400;
const out = document.getElementById('out');
const ctx = out.getContext('2d', {{willReadFrequently:true}});
const plates = {{}};
let ready = 0;

function hex2rgb(h){{h=h.replace('#','');return [parseInt(h.slice(0,2),16),
  parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)];}}

for (const k of ['blue','body']) {{
  const im = new Image();
  im.onload = () => {{
    const c = document.createElement('canvas'); c.width=N; c.height=N;
    const cx = c.getContext('2d', {{willReadFrequently:true}});
    cx.drawImage(im,0,0,N,N);
    const d = cx.getImageData(0,0,N,N).data;
    const a = new Float32Array(N*N);
    for (let i=0;i<N*N;i++) a[i] = d[i*4]/255;   // the mask is greyscale
    plates[k] = a;
    if (++ready === 2) render();
  }};
  im.src = SRC[k];
}}

function el(id){{return document.getElementById(id);}}
function val(id){{return +el(id).value;}}

// one plate's density, after strength, gamma, contrast and a registration shift
function shape(a, strength, gamma, contrast, dx, dy){{
  const o = new Float32Array(N*N);
  for (let y=0;y<N;y++){{
    const sy = y - dy; if (sy<0||sy>=N) continue;
    for (let x=0;x<N;x++){{
      const sx = x - dx; if (sx<0||sx>=N) continue;
      let v = a[sy*N+sx];
      if (v<=0) continue;
      v = Math.pow(v, gamma);
      v = (v - 0.5) * contrast + 0.5;
      v *= strength;
      o[y*N+x] = v<0?0:(v>1?1:v);
    }}
  }}
  return o;
}}

// uneven ink density: a slow field across the plate
function unevenness(amount){{
  const f = new Float32Array(N*N);
  for (let y=0;y<N;y++) for (let x=0;x<N;x++){{
    const v = Math.sin(x/190+1.1)*Math.cos(y/240-0.4)
            + 0.5*Math.sin((x+y)/95);
    f[y*N+x] = 1 - amount*(0.5+0.5*v);
  }}
  return f;
}}

let noise = null, noiseKey = '';
function recipeSeed(){{
  const k = [SUBS[val('sub')].name, INKS[val('ink1')].name, INKS[val('ink2')].name,
             PROCS[val('proc')].name, val('cell'), val('con'), val('gam')].join('|');
  let h = 2166136261;
  for (let i=0;i<k.length;i++) {{ h ^= k.charCodeAt(i); h = Math.imul(h, 16777619); }}
  return [Math.abs(h) % 2147483647 || 1, k];
}}
function grainField(){{
  const [seed, key] = recipeSeed();
  if (noise && noiseKey === key) return noise;
  noise = new Float32Array(N*N);
  noiseKey = key;
  let s = seed;
  for (let i=0;i<N*N;i++){{ s = (s*1103515245+12345)&0x7fffffff; noise[i]=(s%1000)/1000; }}
  return noise;
}}

// her outline, traced offline as one connected shape so stray ink cannot
// pull it past her profile. The back face uses the same shape, moved.
function outline(dx, dy){{
  const b = plates.body, out = new Uint8Array(N*N);
  for (let y=0;y<N;y++){{
    const sy = y - dy; if (sy<0||sy>=N) continue;
    for (let x=0;x<N;x++){{
      const sx = x - dx; if (sx<0||sx>=N) continue;
      if (b[sy*N+sx] > 0.5) out[y*N+x] = 1;
    }}
  }}
  return out;
}}

function sampleCell(d, x0, y0, w){{
  let sum=0, n=0;
  const xs=Math.max(0,Math.floor(x0)), ys=Math.max(0,Math.floor(y0));
  const win=Math.max(1,Math.round(w));
  for (let y=ys;y<ys+win && y<N;y++)
    for (let x=xs;x<xs+win && x<N;x++){{ sum+=d[y*N+x]; n++; }}
  return n? sum/n : 0;
}}

// a real amplitude-modulated screen: one mark per cell, sized by local density
function screenPlate(c, d, colFn, proc, cell, dryAmt){{
  const g = grainField();
  if (proc.screen === 'none'){{
    const img = c.createImageData(N,N); const p = img.data;
    for (let i=0;i<N*N;i++){{
      let v = d[i]; if (v<=0.004) continue;
      if (proc.thresh) v = v>proc.thresh?1:0;
      if (proc.grain) v *= (1 - proc.grain*g[i]);
      const col = colFn(v);
      p[i*4]=col[0]; p[i*4+1]=col[1]; p[i*4+2]=col[2]; p[i*4+3]=Math.round(255*Math.min(1,v));
    }}
    return img;
  }}
  if (cell < 2.2) {{                       // finer than the grid can draw
    const img = c.createImageData(N,N); const p = img.data;
    const per = Math.max(1, Math.round(cell*2));
    for (let y=0;y<N;y++) for (let x=0;x<N;x++){{
      const i=y*N+x; let v=d[i]; if (v<=0.004) continue;
      if (proc.thresh) v = v>proc.thresh?1:0;
      if (proc.grain) v *= (1 - proc.grain*g[i]);
      // an ordered threshold: the dot becomes the pixel itself
      const t = (((x%per)*2 + (y%per)*3) % (per*per) + 0.5) / (per*per);
      if (v < t) continue;
      const col = colFn(v);
      p[i*4]=col[0]; p[i*4+1]=col[1]; p[i*4+2]=col[2]; p[i*4+3]=255;
    }}
    return img;
  }}
  const img = c.createImageData(N,N); const p = img.data;
  const line = proc.screen === 'line';
  for (let cy=0; cy<N; cy+=cell){{
    const iy = Math.floor(cy);
    for (let cx=0; cx<N; cx+=cell){{
      const ix = Math.floor(cx);
      let v = sampleCell(d, ix, iy, cell);
      if (v<=0.004) continue;
      if (proc.thresh) v = v>proc.thresh?1:0;
      const gi = iy*N + ix;
      if (proc.grain) v *= (1 - proc.grain*g[gi]);
      if (dryAmt) v *= (1 - dryAmt*g[(gi+7)%(N*N)]);
      if (v<=0) continue;
      const col = colFn(v);
      const r = (line? cell*0.62 : cell*0.62) * Math.sqrt(Math.min(1,v));
      const midx = cx + cell/2, midy = cy + cell/2;
      for (let y=Math.max(0,Math.floor(midy-r)); y<Math.min(N,Math.ceil(midy+r)); y++){{
        for (let x=Math.max(0,Math.floor(midx-r)); x<Math.min(N,Math.ceil(midx+r)); x++){{
          const dxp = x-midx, dyp = y-midy;
          const inside = line ? Math.abs(dyp) <= r : (dxp*dxp+dyp*dyp) <= r*r;
          if (!inside) continue;
          const i = (y*N+x)*4;
          p[i]=col[0]; p[i+1]=col[1]; p[i+2]=col[2]; p[i+3]=255;
        }}
      }}
    }}
  }}
  return img;
}}

function colourFn(inkHex, shaHex, hilHex, paperRGB){{
  const ink = hex2rgb(inkHex);
  const sha = shaHex? hex2rgb(shaHex) : null;
  const hil = hilHex? hex2rgb(hilHex) : null;
  return (v) => {{
    // v is density: 1 is the shadow, near 0 is the highlight
    let a = ink;
    if (sha && v > 0.62) a = sha;
    else if (hil && v < 0.38) a = hil;
    return a;
  }};
}}

function render(){{
  if (ready < 2) return;
  const sub = SUBS[val('sub')], proc = PROCS[val('proc')];
  const paper = sub.hex? hex2rgb(sub.hex) : [250,250,247];
  const dots = Math.round(14 + Math.pow(val('cell')/100, 1.6) * 686);
  const cell = N / dots;
  const con = 0.2 + val('con')/100 * 3.8;
  const gam = 0.2 + val('gam')/100 * 2.8;
  const ease = v => (v/100)*(v/100);          // fine at the bottom of the travel
  const reg = ease(val('reg'))*40, den = ease(val('den'))*0.45,
        gra = ease(val('gra'))*0.8, dry = ease(val('dry'))*0.6;

  ctx.clearRect(0,0,N,N);
  if (sub.hex) {{ ctx.fillStyle = sub.hex; ctx.fillRect(0,0,N,N); }}

  const p1 = shape(plates.blue, val('str1')/100, gam, con, 0, 0);
  // the second impression is the same plate, moved: measured at 87,16 on the
  // 880px study, which is 138,25 on this canvas
  const p2 = shape(plates.blue, val('str2')/100, gam, con,
                   val('offx') + Math.round(reg), val('offy') + Math.round(reg*0.6));

  if (den){{ const f = unevenness(den);
    for (let i=0;i<N*N;i++){{ p1[i]*=f[i]; p2[i]*=f[i]; }} }}

  const pr = Object.assign({{}}, proc, {{grain: Math.max(proc.grain, gra)}});

  const c1 = colourFn(INKS[val('ink1')].hex,
    val('sha1')>=0? INKS[val('sha1')].hex : null,
    val('hil1')>=0? INKS[val('hil1')].hex : null, paper);
  const c2 = colourFn(INKS[val('ink2')].hex,
    val('sha2')>=0? INKS[val('sha2')].hex : null,
    val('hil2')>=0? INKS[val('hil2')].hex : null, paper);

  const over = el('over').checked, backOnTop = el('order').checked;
  // last in the list is the plate that prints on top
  const layers = backOnTop ? [[p1,c1],[p2,c2]] : [[p2,c2],[p1,c1]];

  const tmp = document.createElement('canvas'); tmp.width=N; tmp.height=N;
  const tctx = tmp.getContext('2d', {{willReadFrequently:true}});
  layers.forEach(([d, cf], idx) => {{
    const top = idx === layers.length - 1;
    let plate = d;
    // a knockout removes the lower plate across the whole silhouette of the
    // upper one, not only where its dots happened to fall
    if (!over && !top) {{
      const upper = layers[layers.length-1][0];
      plate = new Float32Array(N*N);
      const amt = val('kamt')/100;
      if (amt >= 0.995) {{
        // the whole shape goes, tone and all
        const backTop = el('order').checked;
        const sil = backTop ? outline(val('offx') + Math.round(reg),
                                      val('offy') + Math.round(reg*0.6))
                            : outline(0, 0);
        for (let i=0;i<N*N;i++) plate[i] = sil[i] ? 0 : d[i];
      }} else {{
        // only ink above this level knocks out, so the plate beneath keeps its
        // lighter passages: at 0 almost nothing is removed
        const lvl = 0.9 - amt * 0.885;
        for (let i=0;i<N*N;i++) plate[i] = upper[i] > lvl ? 0 : d[i];
      }}
    }}
    const img = screenPlate(tctx, plate, cf, pr, cell, dry);
    tctx.clearRect(0,0,N,N);
    tctx.putImageData(img,0,0);
    ctx.globalCompositeOperation = over && !top ? 'multiply' : 'source-over';
    if (over && top) ctx.globalCompositeOperation = 'multiply';
    ctx.drawImage(tmp,0,0);
  }});

  // wet ink: the plate that printed second dominates where they overlap,
  // which is what makes the order visible under overprint
  if (over) {{
    const [, topCf] = layers[layers.length-1];
    const topD = layers[layers.length-1][0], botD = layers[0][0];
    const lap = new Float32Array(N*N);
    let any = false;
    for (let i=0;i<N*N;i++) {{
      const v = Math.min(topD[i], botD[i]);
      if (v > 0.12) {{ lap[i] = topD[i]; any = true; }}
    }}
    if (any) {{
      const img = screenPlate(tctx, lap, topCf, pr, cell, dry);
      tctx.clearRect(0,0,N,N); tctx.putImageData(img,0,0);
      ctx.globalCompositeOperation = 'source-over';
      ctx.globalAlpha = 0.72; ctx.drawImage(tmp,0,0); ctx.globalAlpha = 1;
    }}
  }}
  ctx.globalCompositeOperation = 'source-over';

  el('mode').textContent = resolveMode();
  el('recipe').textContent =
    [sub.name,
     INKS[val('ink1')].name + ' ' + val('str1') + '%',
     INKS[val('ink2')].name + ' ' + val('str2') + '%',
     resolveMode(),
     proc.name + ', screen ' + val('cell')]
    .concat(reg? ['registration ' + reg + 'px'] : []).join(' / ');
}}

// the screen slider only bites on a screened process
function sync(){{
  const p = PROCS[val('proc')];
  const live = p.screen !== 'none';
  el('cell').closest('.row').classList.toggle('off', !live);
  el('cell').disabled = !live;
  const ko = el('ko').checked;
  el('kamt').closest('.row').classList.toggle('off', !ko);
  el('kamt').disabled = !ko;
}}

const PAL = {json.dumps([list(x) for x in PALETTES])};

function inkIndex(name){{
  for (let i=0;i<INKS.length;i++) if (INKS[i].name === name) return i;
  return -1;
}}

// which of the four print modes the current pair resolves to
function resolveMode(){{
  const a = INKS[val('ink1')].name, b = INKS[val('ink2')].name;
  const blacks = ['Carbon','Charcoal','Warm Charcoal'];
  if (a === b || val('str2') === 0) return 'pure one-ink';
  if (blacks.includes(a) || blacks.includes(b)) return 'chromatic + black';
  if (el('over').checked) return 'overprint duotone';
  return 'complementary duotone';
}}

// the skill allows 0-2 effects on contemporary work, 2-3 on tactile
const IMPS = ['reg','den','gra','dry'];
function limitImperfections(){{
  // the skill's count is a rule about the recipe, not a licence to move a
  // slider someone set: this reports, it never overrides
  const tactile = val('work') === 1;
  const lo = tactile ? 2 : 0, hi = tactile ? 3 : 2;
  const on = IMPS.filter(id => val(id) > 0).length;
  const out = on < lo || on > hi;
  el('ncount').textContent = on + '/' + hi;
  el('ncount').style.color = out ? '#C83232' : '';
  el('ncount').title = out
    ? (tactile ? 'tactile work takes 2 to 3' : 'contemporary work takes up to 2')
    : '';
}}

function bind(){{
  document.querySelectorAll('select,input').forEach(n => {{
    n.addEventListener('input', () => {{
      const o = n.parentElement.querySelector('output');
      if (o && n.type === 'range'){{
        o.textContent = n.value;
      }}
      if (IMPS.includes(n.id) || n.id === 'work') limitImperfections();
      if (n.id === 'pal' && val('pal') > 0) {{
        const names = PAL[val('pal')][2];
        el('ink1').value = inkIndex(names[0]);
        el('ink2').value = inkIndex(names.length > 1 ? names[1] : names[0]);
        if (PAL[val('pal')][1] === 'overprint duotone') el('over').checked = true;
      }}
      if (['ink1','ink2'].includes(n.id)) el('pal').value = 0;
      limitImperfections();
  sync();
      if (n.id === 'proc'){{
        const p = PROCS[+n.value];
        el('cell').value = p.cell;
        el('con').value = p.contrast;
        el('gam').value = p.gamma;
        for (const id of ['cell','con','gam'])
          el(id).parentElement.querySelector('output').textContent = el(id).value;
      }}
      render();
    }});
  }});
  sync();
  el('swap').onclick = () => {{
    const a = el('ink1').value; el('ink1').value = el('ink2').value; el('ink2').value = a;
    render();
  }};
  el('reset').onclick = () => {{
    el('sub').value=0; el('ink1').value=15; el('ink2').value=10;
    el('str1').value=100; el('str2').value=100;
    el('offx').value=138; el('offy').value=25;
    el('sha1').value=-1; el('hil1').value=-1; el('sha2').value=-1; el('hil2').value=-1;
    el('proc').value=0; el('cell').value=36; el('con').value=25; el('gam').value=29;
    el('reg').value=0; el('den').value=0; el('gra').value=0; el('dry').value=0;
    el('ko').checked=true; el('over').checked=false; el('order').checked=false;
    el('kamt').value=100;
    document.querySelectorAll('input[type=range]').forEach(r=>{{
      r.parentElement.querySelector('output').textContent = r.value;
    }});
    render();
  }};
}}

// the same screen written as vector marks instead of painted pixels
function buildSVG(){{
  const sub = SUBS[val('sub')], proc = PROCS[val('proc')];
  const dots = Math.round(14 + Math.pow(val('cell')/100, 1.6) * 686);
  const cell = N / dots;
  const con = 0.2 + val('con')/100 * 3.8, gam = 0.2 + val('gam')/100 * 2.8;
  const ease = v => (v/100)*(v/100);
  const reg = ease(val('reg'))*40, den = ease(val('den'))*0.45,
        gra = ease(val('gra'))*0.8, dry = ease(val('dry'))*0.6;
  const p1 = shape(plates.blue, val('str1')/100, gam, con, 0, 0);
  const p2 = shape(plates.blue, val('str2')/100, gam, con,
                   val('offx') + Math.round(reg), val('offy') + Math.round(reg*0.6));
  if (den){{ const f = unevenness(den); for (let i=0;i<N*N;i++){{ p1[i]*=f[i]; p2[i]*=f[i]; }} }}
  const backTop = el('order').checked;
  let lower = backTop ? p1 : p2;
  const upper = backTop ? p2 : p1;
  if (el('ko').checked && val('kamt')/100 >= 0.995){{
    const sil = backTop ? outline(val('offx')+Math.round(reg),
                                  val('offy')+Math.round(reg*0.6))
                        : outline(0,0);
    const cut = new Float32Array(N*N);
    for (let i=0;i<N*N;i++) cut[i] = sil[i] ? 0 : lower[i];
    lower = cut;
  }}
  const g = grainField(), line = proc.screen === 'line';
  const marks = (d) => {{
    if (proc.screen === 'none') return {{d:'', n:0}};
    let out = '', n = 0;
    for (let cy=0; cy<N; cy+=cell){{
      const iy = Math.floor(cy);
      for (let cx=0; cx<N; cx+=cell){{
        const ix = Math.floor(cx);
        let v = sampleCell(d, ix, iy, cell);
        if (v<=0.02) continue;
        if (proc.thresh) v = v>proc.thresh?1:0;
        const gi = iy*N+ix, gm = Math.max(proc.grain, gra);
        if (gm) v *= (1 - gm*g[gi]);
        if (dry) v *= (1 - dry*g[(gi+7)%(N*N)]);
        if (v<=0.02) continue;
        const r = cell*0.62*Math.sqrt(Math.min(1,v));
        const x = (cx+cell/2).toFixed(1), y = (cy+cell/2).toFixed(1);
        const rr = r.toFixed(1), d2 = (r*2).toFixed(1);
        out += line
          ? 'M'+x+' '+y+'m-'+rr+',-'+(r*0.34).toFixed(1)+'h'+d2
            +'v'+(r*0.68).toFixed(1)+'h-'+d2+'z'
          : 'M'+x+' '+y+'m-'+rr+',0a'+rr+','+rr+' 0 1,0 '+d2+',0a'+rr+','+rr+' 0 1,0 -'+d2+',0';
        n++;
      }}
    }}
    return {{d:out, n:n}};
  }};
  const cLower = backTop ? INKS[val('ink1')].hex : INKS[val('ink2')].hex;
  const cUpper = backTop ? INKS[val('ink2')].hex : INKS[val('ink1')].hex;
  const a = marks(lower), b = marks(upper);
  const bg = (sub.hex && !el('alpha').checked)
    ? '<rect width="'+N+'" height="'+N+'" fill="'+sub.hex+'"/>' : '';
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="'+N+'" height="'+N
    + '" viewBox="0 0 '+N+' '+N+'">' + bg
    + '<path fill="'+cLower+'" d="'+a.d+'"/><path fill="'+cUpper+'" d="'+b.d+'"/></svg>';
  return {{svg:svg, marks:a.n+b.n}};
}}

function saveBlob(blob, ext){{
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = [INKS[val('ink1')].name, INKS[val('ink2')].name,
                PROCS[val('proc')].name].join(' ')
                .replace(/[^a-z0-9]+/gi,'-').toLowerCase() + '.' + ext;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 4000);
}}

bind();

el('dl').onclick = () => {{
  if (!el('alpha').checked) {{ out.toBlob(b => saveBlob(b,'png'), 'image/png'); return; }}
  const sub = el('sub').value; el('sub').value = SUBS.length-1;
  el('sub').dispatchEvent(new Event('input'));
  out.toBlob(b => {{ saveBlob(b,'png'); el('sub').value = sub;
                    el('sub').dispatchEvent(new Event('input')); }}, 'image/png');
}};
el('svg').onclick = () => saveBlob(new Blob([buildSVG().svg],{{type:'image/svg+xml'}}),'svg');
</script>
</body></html>
'''

OUT.write_text(HTML)
print('wrote %s  %.0f KB' % (OUT, len(HTML) / 1024))
