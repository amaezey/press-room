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

UPLOAD_JS = r"""
// ---------------------------------------------------------------- source
// The press works on two arrays: a density plate and a silhouette. The bust
// arrives as two traced masks; an uploaded picture has to be turned into the
// same pair. Transparency gives both at once, which is why a cutout PNG is
// the good case.

const DEFAULT_PLATES = {};
let SOURCE = null;
const SRCMAX = 2400;              // cap the read so a huge file cannot eat memory

function note(t){ el('srcnote').textContent = t; }

// The segmented controls are the visible half of a pair of hidden radios, so
// everything downstream still reads el('ko').checked and friends.
function paintSegs(){
  document.querySelectorAll('.seg button').forEach(b => {
    b.classList.toggle('on', el(b.dataset.id).checked);
  });
}
function bindSegs(){
  document.querySelectorAll('.seg button').forEach(b => {
    b.onclick = () => { el(b.dataset.id).checked = true; sync(); render(); };
  });
}

function setPlates(blue, body, t){
  plates = {blue: blue, body: body};
  ready = 2;
  note(t);
  render();
}

// draw the picture into the square: contain, centred, never cropped. Fully
// clear margins are trimmed first, since there is nothing in them to lose.
function readImage(img){
  const nw = img.naturalWidth || img.width, nh = img.naturalHeight || img.height;
  if (!nw || !nh) throw new Error('empty');
  const k = Math.min(1, SRCMAX / Math.max(nw, nh));
  const aw = Math.max(1, Math.round(nw*k)), ah = Math.max(1, Math.round(nh*k));
  const A = document.createElement('canvas'); A.width = aw; A.height = ah;
  const actx = A.getContext('2d', {willReadFrequently:true});
  actx.drawImage(img, 0, 0, aw, ah);
  const ad = actx.getImageData(0, 0, aw, ah).data;

  let clear = 0, x0 = aw, y0 = ah, x1 = -1, y1 = -1;
  for (let y = 0; y < ah; y++) for (let x = 0; x < aw; x++){
    if (ad[(y*aw+x)*4+3] < 16){ clear++; continue; }
    if (x < x0) x0 = x;
    if (x > x1) x1 = x;
    if (y < y0) y0 = y;
    if (y > y1) y1 = y;
  }
  // a stray pixel or two of anti-aliasing is not a cutout
  const cutout = clear > aw*ah*0.01;
  if (!cutout || x1 < 0){ x0 = 0; y0 = 0; x1 = aw-1; y1 = ah-1; }
  const bw = x1-x0+1, bh = y1-y0+1;

  const s = Math.min(N/bw, N/bh);
  const dw = Math.max(1, Math.round(bw*s)), dh = Math.max(1, Math.round(bh*s));
  const dx = (N-dw) >> 1, dy = (N-dh) >> 1;
  const B = document.createElement('canvas'); B.width = N; B.height = N;
  const bctx = B.getContext('2d', {willReadFrequently:true});
  bctx.imageSmoothingEnabled = true;
  bctx.imageSmoothingQuality = 'high';
  bctx.drawImage(A, x0, y0, bw, bh, dx, dy, dw, dh);
  return {data: bctx.getImageData(0,0,N,N).data,
          cutout: cutout, w: nw, h: nh, dx: dx, dy: dy, dw: dw, dh: dh};
}

// on a full-frame photo the ground says which way round it is: a dark ground
// means the picture is carried by its light areas. Sampled inside the drawn
// rectangle, not the letterbox, or the empty bars would decide it.
function guessFlip(src){
  if (src.cutout) return false;
  const d = src.data;
  let sum = 0, n = 0;
  const lim = v => Math.min(N-1, Math.max(0, v));
  const ry0 = lim(src.dy+1), ry1 = lim(src.dy+src.dh-2);
  const rows = ry0 === ry1 ? [ry0] : [ry0, ry1];
  for (let x = src.dx; x < src.dx+src.dw; x += 4)
    for (const y of rows){
      const i = (y*N+x)*4;
      sum += 0.2126*d[i] + 0.7152*d[i+1] + 0.0722*d[i+2];
      n++;
    }
  return n ? (sum/n/255) < 0.45 : false;
}

function pct(hist, total, p){
  const want = total*p;
  let acc = 0;
  for (let i = 0; i < 256; i++){ acc += hist[i]; if (acc >= want) return i; }
  return 255;
}

// A pinhole in a rough cutout should close. A real opening, the hole in a ring
// or the gap under an arm, should not. So label each pocket of background and
// fill only the ones that never reach the edge and stay under a cap set by the
// size of the shape itself.
function fillHoles(m){
  const n = N*N;
  let fg = 0;
  for (let i = 0; i < n; i++) if (m[i]) fg++;
  const cap = Math.max(600, fg*0.01);
  const seen = new Uint8Array(n), st = new Int32Array(n), pocket = new Int32Array(n);
  for (let s = 0; s < n; s++){
    if (m[s] || seen[s]) continue;
    let sp = 0, np = 0, edge = false;
    seen[s] = 1; st[sp++] = s;
    while (sp){
      const i = st[--sp], x = i % N, y = (i-x)/N;
      pocket[np++] = i;
      if (x === 0 || y === 0 || x === N-1 || y === N-1) edge = true;
      if (x > 0   && !m[i-1] && !seen[i-1]){ seen[i-1] = 1; st[sp++] = i-1; }
      if (x < N-1 && !m[i+1] && !seen[i+1]){ seen[i+1] = 1; st[sp++] = i+1; }
      if (y > 0   && !m[i-N] && !seen[i-N]){ seen[i-N] = 1; st[sp++] = i-N; }
      if (y < N-1 && !m[i+N] && !seen[i+N]){ seen[i+N] = 1; st[sp++] = i+N; }
    }
    if (!edge && np <= cap) for (let j = 0; j < np; j++) m[pocket[j]] = 1;
  }
}

// stray specks around a rough cutout print as dirt. Dirt is small in absolute
// terms, so the relative rule needs a ceiling: without it a real detail beside
// a large subject counts as a speck and is binned with the rubbish.
function dropSpecks(m){
  const n = N*N, lab = new Int32Array(n), st = new Int32Array(n), areas = [0];
  let cur = 0;
  for (let s = 0; s < n; s++){
    if (!m[s] || lab[s]) continue;
    cur++;
    let sp = 0, area = 0;
    lab[s] = cur; st[sp++] = s;
    while (sp){
      const i = st[--sp], x = i % N, y = (i-x)/N;
      area++;
      if (x > 0   && m[i-1] && !lab[i-1]){ lab[i-1] = cur; st[sp++] = i-1; }
      if (x < N-1 && m[i+1] && !lab[i+1]){ lab[i+1] = cur; st[sp++] = i+1; }
      if (y > 0   && m[i-N] && !lab[i-N]){ lab[i-N] = cur; st[sp++] = i-N; }
      if (y < N-1 && m[i+N] && !lab[i+N]){ lab[i+N] = cur; st[sp++] = i+N; }
    }
    areas[cur] = area;
  }
  let big = 0;
  for (let c = 1; c <= cur; c++) if (areas[c] > big) big = areas[c];
  const min = Math.min(big*0.01, 400);   // 400px is a blob about 20 across
  for (let i = 0; i < n; i++) if (m[i] && areas[lab[i]] < min) m[i] = 0;
}

// turn the held picture into the two plates, at the current Ink from / Cutout
function rebuild(){
  if (!SOURCE) return;
  const d = SOURCE.data, n = N*N, cutout = SOURCE.cutout;
  const fromLight = val('flip') === 1;
  const alpha = new Float32Array(n), ink = new Float32Array(n);
  for (let i = 0; i < n; i++){
    alpha[i] = d[i*4+3]/255;
    // perceptual luminance, so a red and a blue of the same brightness agree
    const l = (0.2126*d[i*4] + 0.7152*d[i*4+1] + 0.0722*d[i*4+2])/255;
    ink[i] = fromLight ? l : 1-l;
  }

  // auto-level on the 2nd and 98th percentile of what is inside the shape, so
  // one blown highlight cannot flatten the whole plate
  const hist = new Int32Array(256);
  let inShape = 0;
  for (let i = 0; i < n; i++) if (alpha[i] > 0.5){ hist[Math.round(ink[i]*255)]++; inShape++; }
  if (inShape > 500){
    const lo = pct(hist, inShape, 0.02), hi = pct(hist, inShape, 0.98);
    if (hi - lo > 6){
      const a0 = lo/255, r = 1/((hi/255) - a0);
      for (let i = 0; i < n; i++){
        const v = (ink[i]-a0)*r;
        ink[i] = v < 0 ? 0 : (v > 1 ? 1 : v);
      }
    }
  }

  const blue = new Float32Array(n);
  for (let i = 0; i < n; i++) blue[i] = ink[i]*alpha[i];

  // transparency gives the silhouette directly. Without it we have to carve
  // one out of the density, which is what the Cutout slider is for.
  const mask = new Uint8Array(n);
  if (cutout) for (let i = 0; i < n; i++) mask[i] = alpha[i] > 0.5 ? 1 : 0;
  else { const t = val('cut')/100; for (let i = 0; i < n; i++) mask[i] = blue[i] > t ? 1 : 0; }
  fillHoles(mask);
  dropSpecks(mask);
  // the cleaned shape gates the ink too, or the specks we just binned would
  // still print as dirt. Only for a cutout: on a full frame the picture is
  // the whole sheet and the mask is a carve for the knockout, nothing more.
  if (cutout) for (let i = 0; i < n; i++) blue[i] *= mask[i];
  const body = new Float32Array(n);
  for (let i = 0; i < n; i++) body[i] = mask[i];

  el('rowCut').classList.toggle('off', cutout);
  setPlates(blue, body, (cutout ? 'cutout ' : 'no transparency ') + SOURCE.w + '×' + SOURCE.h);
}

// Loads are async, so a slow one must not land on top of a later pick. Each
// gets a ticket and only the newest is allowed to finish.
let loadSeq = 0, picked = false;
function useBlob(blob, name, restored){
  const seq = ++loadSeq;
  const url = URL.createObjectURL(blob);
  const im = new Image();
  const fail = () => {
    if (seq !== loadSeq) return;
    // a saved file that will not decode would fail again on every reload
    if (restored){ forget(); useDefault(); return; }
    note('could not read that image');
  };
  im.onload = () => {
    URL.revokeObjectURL(url);
    if (seq !== loadSeq) return;
    try {
      SOURCE = readImage(im);
      if (name) el('filename').textContent = name;
      el('flip').value = guessFlip(SOURCE) ? 1 : 0;
      rebuild();
    } catch (e){ fail(); }
  };
  im.onerror = () => { URL.revokeObjectURL(url); fail(); };
  im.src = url;
}

// keep the last upload across a reload. The file, not the plates, so Ink from
// and Cutout still work afterwards.
function idb(fn){
  try {
    const rq = indexedDB.open('press-room', 1);
    rq.onupgradeneeded = () => rq.result.createObjectStore('src');
    rq.onsuccess = () => { try { fn(rq.result); } catch (e){} };
    rq.onerror = () => {};
  } catch (e){}
}
function keep(blob){ idb(db => db.transaction('src','readwrite').objectStore('src').put(blob,'img')); }
function forget(){ idb(db => db.transaction('src','readwrite').objectStore('src').delete('img')); }

function useDefault(){
  el('filename').textContent = 'Choose a picture';
  loadSeq++;                      // anything still decoding loses its ticket
  picked = true;                  // and the saved file must not come back
  SOURCE = null;
  el('rowCut').classList.add('off');
  if (DEFAULT_PLATES.blue) setPlates(DEFAULT_PLATES.blue, DEFAULT_PLATES.body, 'bust 700×700');
}

for (const k of ['blue','body']){
  const im = new Image();
  im.onload = () => {
    const c = document.createElement('canvas'); c.width = N; c.height = N;
    const cx = c.getContext('2d', {willReadFrequently:true});
    cx.drawImage(im, 0, 0, N, N);
    const d = cx.getImageData(0, 0, N, N).data;
    const a = new Float32Array(N*N);
    for (let i = 0; i < N*N; i++) a[i] = d[i*4]/255;   // the mask is greyscale
    DEFAULT_PLATES[k] = a;
    if (DEFAULT_PLATES.blue && DEFAULT_PLATES.body){
      const claimed = picked;   // did anything land while the bust was loading
      useDefault();
      picked = claimed;
      idb(db => {
        const rq = db.transaction('src').objectStore('src').get('img');
        rq.onsuccess = () => {
          if (rq.result && !picked) useBlob(rq.result, 'your last picture', true);
        };
      });
    }
  };
  im.src = SRC[k];
}

el('file').onchange = e => {
  const f = e.target.files && e.target.files[0];
  if (!f) return;
  picked = true;
  if (!/^image\//.test(f.type)){ note('that is not an image'); return; }
  if (f.size > 40e6){ note('too big, keep it under 40 MB'); return; }
  keep(f);
  useBlob(f, f.name);
};
"""

RANDOM_JS = r"""
// ---------------------------------------------------------------- random
// A whole recipe at once. It leaves Source alone: the picture is not part of
// the recipe, and nobody wants the flip switch thrown under them.

function randomise(){
  const between = (a, b) => a + Math.floor(Math.random()*(b-a+1));
  const chance = p => Math.random() < p;
  const anyInk = () => between(0, INKS.length-1);

  el('sub').value = between(0, SUBS.length-2);   // last one is Transparent
  const two = !chance(0.2);
  el('two').checked = two; el('one').checked = !two;

  // hold to an approved palette most of the time, since that is the point of
  // having ten of them. The rest of the time take two inks freely.
  if (chance(0.6)){
    const pi = between(1, PAL.length-1);
    el('pal').value = pi;
    const names = PAL[pi][2];
    el('ink1').value = inkIndex(names[0]);
    el('ink2').value = inkIndex(names.length > 1 ? names[1] : names[0]);
    el('over').checked = PAL[pi][1] === 'overprint duotone';
  } else {
    el('pal').value = 0;
    el('ink1').value = anyInk();
    el('ink2').value = anyInk();
    el('over').checked = chance(0.35);
  }
  el('ko').checked = !el('over').checked;

  el('str1').value = between(80, 115);
  el('str2').value = between(80, 115);

  // a second ink in the shadows is a decision, so it stays off most of the time
  el('sha1').value = chance(0.25) ? anyInk() : -1;
  el('hil1').value = chance(0.20) ? anyInk() : -1;
  el('sha2').value = chance(0.25) ? anyInk() : -1;
  el('hil2').value = chance(0.20) ? anyInk() : -1;

  // the offset is what makes the back face a second impression rather than a
  // copy, so keep it clear of zero and inside the sheet
  const sgn = () => chance(0.5) ? 1 : -1;
  el('offx').value = sgn() * between(40, 200);
  el('offy').value = sgn() * between(10, 90);
  el('order').checked = chance(0.3);
  el('kamt').value = chance(0.7) ? 100 : between(30, 95);

  // each process carries its own screen, contrast and gamma. Take those, then
  // knock them about a little so two draws of the same process differ.
  const pi = between(0, PROCS.length-1);
  el('proc').value = pi;
  const jog = (v, d) => Math.max(0, Math.min(100, v + between(-d, d)));
  el('cell').value = jog(PROCS[pi].cell, 9);
  el('con').value  = jog(PROCS[pi].contrast, 8);
  el('gam').value  = jog(PROCS[pi].gamma, 7);

  // no ceiling on these: any number of them, anywhere on the travel. The
  // counter still reports when a roll goes past what the work calls for,
  // which is the counter's job, not a reason to hold the dice back.
  el('work').value = chance(0.35) ? 1 : 0;
  IMPS.forEach(id => {
    el(id).value = between(+el(id).min, +el(id).max);
  });

  document.querySelectorAll('input[type=range]').forEach(r => {
    const o = r.parentElement.querySelector('output');
    if (o) o.textContent = r.value;
  });
  sync();
  limitImperfections();
  render();
}
"""

HTML = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Press room</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect x='2' y='5' width='20' height='20' fill='%2363365F'/%3E%3Crect x='10' y='9' width='20' height='20' fill='%23E55D2B' fill-opacity='.86'/%3E%3C/svg%3E">
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

.top{{flex:none;display:flex;align-items:center;gap:13px;height:44px;
padding:0 16px;background:#F4F3EE;border-bottom:1px solid var(--edge)}}
.top .bar{{flex:none;display:flex;box-shadow:0 0 0 1px rgba(38,37,31,.2)}}
.top .bar i{{display:block;width:15px;height:15px}}
.top h1{{font:600 12px/1 var(--f-mono);letter-spacing:.185em;
text-transform:uppercase;color:var(--edge);white-space:nowrap}}
.top .readout{{flex:1;min-width:0;padding-left:13px;
border-left:1px solid var(--line);
font:400 11px/16px var(--f-mono);letter-spacing:.02em;color:var(--dim);
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}

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
.row{{display:grid;grid-template-columns:84px minmax(0,1fr) 34px;gap:10px;align-items:center;
padding:0 16px;margin-top:9px}}
.row label{{font:400 13px/18px var(--f-sans);color:var(--edge)}}
.row output{{font:400 12px/16px var(--f-mono);color:var(--dim);text-align:right}}
select,input[type=range]{{width:100%;min-width:0;margin:0}}
select{{font:400 13px/18px var(--f-sans);height:30px;padding:0 8px;
border:1px solid var(--line);background:#fff;color:var(--edge);border-radius:4px}}
input[type=range]{{accent-color:#63365F;height:30px}}
.chk{{display:flex;align-items:center;gap:9px;padding:0 16px;margin-top:10px;
font:400 13px/18px var(--f-sans)}}
.chk input{{margin:0;accent-color:#63365F}}
.off{{opacity:.42}}
.off input,.off select,.off button{{pointer-events:none}}
.seg{{display:flex;height:30px;min-width:0;border:1px solid var(--line);
border-radius:4px;background:#fff;overflow:hidden}}
.seg button{{flex:1;min-width:0;padding:0 4px;border:0;
border-right:1px solid var(--line);background:transparent;cursor:pointer;
font:400 12px/16px var(--f-sans);color:var(--dim);
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.seg button:last-child{{border-right:0}}
.seg button:not(.on):hover{{background:#F4F3EE;color:var(--edge)}}
.seg button.on{{background:#63365F;color:#fff}}
.file{{position:relative;display:flex;align-items:center;gap:7px;height:30px;
padding:0 9px;border:1px solid var(--line);background:#fff;border-radius:4px;
cursor:pointer;font:400 12px/16px var(--f-mono);color:var(--dim);min-width:0}}
.file:hover{{border-color:var(--edge)}}
.file:focus-within{{border-color:var(--edge);box-shadow:0 0 0 2px rgba(99,54,95,.22)}}
.file input{{position:absolute;inset:0;opacity:0;pointer-events:none}}
.file span{{min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
button.act{{border:1px solid var(--line);background:#fff;cursor:pointer;
padding:0 14px;height:30px;font:400 13px/18px var(--f-sans);
color:var(--edge);border-radius:4px}}
button.act:hover{{border-color:var(--edge)}}
</style>

<div class="top"><span class="bar"><i id="chip1"></i><i id="chip2"></i></span>
<h1>Press room</h1>
<span class="readout" id="recipe"></span></div>

<div class="wrap">
  <div class="panel">
    <fieldset><legend>Source</legend>
      <div class="row"><label>Image</label>
        <label class="file"><input type="file" id="file" accept="image/*">
          <span id="filename">Choose a picture</span></label><output></output></div>
      <div class="row"><label>Ink from</label>
        <select id="flip"><option value="0">Dark areas</option>
        <option value="1">Light areas</option></select><output></output></div>
      <div class="row off" id="rowCut"><label>Cutout</label>
        <input type="range" id="cut" min="0" max="100" value="50"><output>50</output></div>
      <div class="row"><label>Picture</label>
        <span id="srcnote" style="font:400 11px/16px var(--f-mono);color:var(--dim)"></span><output></output></div>
    </fieldset>

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
      <div class="row"><label>Impressions</label>
        <div class="seg"><button type="button" data-id="one">One</button>
        <button type="button" data-id="two">Two</button></div>
        <input type="radio" name="np" id="one" hidden>
        <input type="radio" name="np" id="two" checked hidden><output></output></div>
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
        <select id="proc">{opts(PROCESSES, 2)}</select><output></output></div>
      <div class="row"><label>Screen</label>
        <input type="range" id="cell" min="0" max="100" value="64"><output>64</output></div>
      <div class="row"><label>Contrast</label>
        <input type="range" id="con" min="0" max="100" value="24"><output>24</output></div>
      <div class="row"><label>Gamma</label>
        <input type="range" id="gam" min="0" max="100" value="29"><output>29</output></div>
      <div class="row" id="rowMeet"><label>Faces meet</label>
        <div class="seg"><button type="button" data-id="ko">Knockout</button>
        <button type="button" data-id="over">Overprint</button></div>
        <input type="radio" name="meet" id="ko" checked hidden>
        <input type="radio" name="meet" id="over" hidden><output></output></div>
      <div class="row"><label>Knockout</label>
        <input type="range" id="kamt" min="0" max="100" value="100"><output>100</output></div>
      <div class="chk"><input type="checkbox" id="order">
        <label for="order">Back face on top</label></div>
    </fieldset>

    <fieldset><legend>Imperfections</legend>
      <div class="row"><label>Work</label>
        <select id="work" title="contemporary takes up to 2, tactile 2 to 3">
        <option value="0">Contemporary</option>
        <option value="1">Tactile</option></select><output id="ncount"></output></div>
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
      <button class="act" id="rand">Random</button>
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
let plates = {{}};
let ready = 0;

function hex2rgb(h){{h=h.replace('#','');return [parseInt(h.slice(0,2),16),
  parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)];}}

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

  const two = el('two').checked;
  const over = el('over').checked, backOnTop = two && el('order').checked;
  // last in the list is the plate that prints on top
  const layers = !two ? [[p1,c1]]
    : (backOnTop ? [[p1,c1],[p2,c2]] : [[p2,c2],[p1,c1]]);

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
  if (over && layers.length > 1) {{
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
  el('chip1').style.background = INKS[val('ink1')].hex;
  el('chip2').style.background = INKS[val('ink2')].hex;
  el('chip2').hidden = !two;
  el('recipe').textContent =
    [sub.name, INKS[val('ink1')].name + ' ' + val('str1') + '%']
    .concat(two ? [INKS[val('ink2')].name + ' ' + val('str2') + '%'] : [])
    .concat([resolveMode(), proc.name + ', screen ' + val('cell')])
    .concat(reg? ['registration ' + reg + 'px'] : []).join(' / ');
}}

// the screen slider only bites on a screened process
function sync(){{
  paintSegs();
  const two = el('two').checked;
  for (const id of ['ink2','str2','offx','offy','sha2','hil2'])
    el(id).closest('.row').classList.toggle('off', !two);
  el('rowMeet').classList.toggle('off', !two);
  el('order').closest('.chk').classList.toggle('off', !two);
  const p = PROCS[val('proc')];
  const live = p.screen !== 'none';
  el('cell').closest('.row').classList.toggle('off', !live);
  el('cell').disabled = !live;
  const ko = el('ko').checked && two;
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
  if (!el('two').checked) return 'pure one-ink';
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
      if (n.id === 'file') return;
      if (n.id === 'flip' || n.id === 'cut') {{
        const oc = n.parentElement.querySelector('output');
        if (oc && n.type === 'range') oc.textContent = n.value;
        rebuild(); return;
      }}
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
  bindSegs();
  el('rand').onclick = randomise;
  el('swap').onclick = () => {{
    const a = el('ink1').value; el('ink1').value = el('ink2').value; el('ink2').value = a;
    render();
  }};
  el('reset').onclick = () => {{
    forget(); el('file').value=''; el('flip').value=0; el('cut').value=50;
    useDefault();
    el('sub').value=0; el('ink1').value=15; el('ink2').value=10;
    el('str1').value=100; el('str2').value=100;
    el('offx').value=138; el('offy').value=25;
    el('sha1').value=-1; el('hil1').value=-1; el('sha2').value=-1; el('hil2').value=-1;
    el('proc').value=2; el('cell').value=64; el('con').value=24; el('gam').value=29;
    el('reg').value=0; el('den').value=0; el('gra').value=0; el('dry').value=0;
    el('ko').checked=true; el('over').checked=false; el('order').checked=false;
    el('two').checked=true; el('one').checked=false;
    el('kamt').value=100;
    document.querySelectorAll('input[type=range]').forEach(r=>{{
      r.parentElement.querySelector('output').textContent = r.value;
    }});
    sync();
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
  const two = el('two').checked;
  const backTop = two && el('order').checked;
  let lower = two ? (backTop ? p1 : p2) : new Float32Array(N*N);
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

{UPLOAD_JS}
{RANDOM_JS}

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
