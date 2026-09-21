// QUICK layout estimate via Playwright getBoundingClientRect. wide-text [160,920], captions [170,910], small [130,950].
// This is only a fast pre-check: the layout box does NOT see nowrap text overflow, so the box can read "ok"
// while the pixels vault the edge. measure_ink.py (rendered alpha) is the source of truth; run it before entrega.
// Usage: node measure_layout.mjs <absWorkspace> [port]   (serve.sh must be running on that port)
import fs from 'fs';
import path from 'path';
// Resolve o playwright de onde ele estiver: a skill pode viver FORA da arvore que tem o
// node_modules (em ESM o `import 'playwright'` resolve pela pasta DO SCRIPT, nao pelo cwd, entao
// mover a skill pra ~/.claude/skills quebrava o render com ERR_MODULE_NOT_FOUND).
// Ordem: PLAYWRIGHT_ROOT do ambiente, a propria skill, o workspace (GEN_WORK), ~/naia-agent, ~.
import { createRequire } from 'module';
import os from 'os';
function loadChromium() {
  const bases = [
    process.env.PLAYWRIGHT_ROOT,
    path.dirname(new URL(import.meta.url).pathname),
    process.env.GEN_WORK,
    path.join(os.homedir(), 'naia-agent'),
    os.homedir(),
  ].filter(Boolean);
  const erros = [];
  for (const b of bases) {
    try {
      const req = createRequire(path.join(b, 'noop.js'));
      const pw = req('playwright');
      if (pw && pw.chromium) return pw.chromium;
    } catch (e) { erros.push(`${b}: ${e.code || e.message}`); }
  }
  console.error('PLAYWRIGHT_NAO_ENCONTRADO. Tentei:\n  ' + erros.join('\n  ') +
    '\nInstale com `npm i playwright` ou aponte PLAYWRIGHT_ROOT pra pasta que tem node_modules/playwright.');
  process.exit(1);
}
const chromium = loadChromium();
const WORK = process.argv[2]; // absolute workspace dir
const PORT = process.argv[3] || '8100';
const U = `http://127.0.0.1:${PORT}`;
const WIDE=[160,920], CAP=[170,910], SMALL=[130,950];
const plan = JSON.parse(fs.readFileSync(`${WORK}/render/plan.json`));
const enc = s => encodeURIComponent(s);
// img cards from plan carry a name only; build url like render_all does (title empty ok for measure)
const D=e=>(e.dur||e.movlen||5);
function urlFor(e){
  if(e.type==='img'||e.kind==='img'){ return `${U}/elements/imgcard.html?src=${enc('/img/x.png')}&dur=${D(e)}&kb=push&accent=cyan`; }
  return `${U}/elements/${e.name}.html?dur=${D(e)}`;
}
const b = await chromium.launch({args:['--force-color-profile=srgb','--font-render-hinting=none','--hide-scrollbars','--allow-file-access-from-files']});
const pg = await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
pg.on('pageerror',e=>console.log('  PAGE-EXC',e.message));
function measureFn(){
  const stage=document.getElementById('stage'); const all=stage.querySelectorAll('*');
  let L=1e9,R=-1e9,any=false;
  for(const el of all){
    let o=1,n=el; while(n&&n!==document.body){const s=getComputedStyle(n);o*=parseFloat(s.opacity);if(s.display==='none'||s.visibility==='hidden'){o=0;break;}n=n.parentElement;}
    if(o<=0.02)continue;
    let r=el.getBoundingClientRect(); if(r.width<=0||r.height<=0)continue;
    if(r.width>=1076&&r.height>=1912)continue;
    let cl=r.left,cr=r.right,a=el.parentElement;
    while(a&&a!==document.body){const s=getComputedStyle(a);
      if(/(hidden|clip)/.test(s.overflow+s.overflowX+s.overflowY)){const ar=a.getBoundingClientRect();cl=Math.max(cl,ar.left);cr=Math.min(cr,ar.right);}
      a=a.parentElement;}
    if(cr<=cl)continue;
    L=Math.min(L,cl);R=Math.max(R,cr);any=true;
  }
  return any?{L,R}:null;
}
async function measureEl(url,dur){
  await pg.goto(url,{waitUntil:'domcontentloaded'});
  await pg.waitForFunction('typeof window.__seek==="function"',{timeout:15000});
  await pg.evaluate(async()=>{await document.fonts.ready;});
  await pg.waitForFunction('!window.__assetsReady||window.__assetsReady()===true',{timeout:8000}).catch(()=>{});
  let gL=1e9,gR=-1e9;
  for(let t=0;t<=dur+1e-6;t+=0.1){
    await pg.evaluate(tt=>window.__seek(+tt.toFixed(2)),t);
    const m=await pg.evaluate(measureFn); if(!m)continue;
    if(m.L<gL)gL=m.L; if(m.R>gR)gR=m.R;
  }
  return {L:gL,R:gR};
}
function flag(L,R,band){const[a,z]=band;const bad=L<a-0.5||R>z+0.5;return bad?`*** FURA [${a},${z}] ***`:'ok';}
let bad=0;
console.log('-- elements (banda texto largo [160,920]) --');
for(const e of plan.elements){
  const {L,R}=await measureEl(urlFor(e),D(e));
  const f=flag(L,R,WIDE); if(f.startsWith('***'))bad++;
  console.log(`${e.name.padEnd(13)} L=${L.toFixed(0).padStart(4)} R=${R.toFixed(0).padStart(4)} W=${(R-L).toFixed(0).padStart(4)} cx=${((L+R)/2).toFixed(0)} -> ${f}`);
}
// captions
const capFile=`${WORK}/captions/captions.json`;
if(fs.existsSync(capFile)){
  const caps=JSON.parse(fs.readFileSync(capFile));
  await pg.goto(`${U}/elements/caption_track.html`,{waitUntil:'domcontentloaded'});
  await pg.waitForFunction('typeof window.__seek==="function"',{timeout:15000});
  await pg.evaluate(async()=>{await document.fonts.ready;});
  let cL=1e9,cR=-1e9,worst='';
  for(const ev of caps){const t=(ev.s+ev.e)/2; await pg.evaluate(tt=>window.__seek(tt),t);
    const r=await pg.evaluate(()=>{const el=document.getElementById('ci');const x=el.getBoundingClientRect();return{l:x.left,r:x.right,txt:el.textContent};});
    if(r.l<cL)cL=r.l; if(r.r>cR){cR=r.r;worst=r.txt;}}
  const f=flag(cL,cR,CAP); if(f.startsWith('***'))bad++;
  console.log(`\nCAPTIONS       L=${cL.toFixed(0).padStart(4)} R=${cR.toFixed(0).padStart(4)} W=${(cR-cL).toFixed(0)} widest="${worst}" -> ${f}`);
}
// CTA sub-elements
const ctaFile = fs.existsSync(`${WORK}/elements/e_cta.html`)?'e_cta':'e10_cta';
await pg.goto(`${U}/elements/${ctaFile}.html?dur=3.9`,{waitUntil:'domcontentloaded'});
await pg.waitForFunction('typeof window.__seek==="function"',{timeout:15000});
await pg.evaluate(async()=>{await document.fonts.ready;});
const subs=['big','tst','cmp','kick','pl','hn'];
let cg={};
for(let t=0;t<=3.9;t+=0.1){ await pg.evaluate(tt=>window.__seek(+tt.toFixed(2)),t);
  const m=await pg.evaluate((ids)=>{const o={};for(const id of ids){const el=document.getElementById(id);if(!el)continue;const s=getComputedStyle(el);if(parseFloat(s.opacity)<=0.02)continue;const r=el.getBoundingClientRect();if(r.width<=0)continue;o[id]={l:r.left,r:r.right};}return o;},subs);
  for(const k in m){ if(!cg[k])cg[k]={L:1e9,R:-1e9}; cg[k].L=Math.min(cg[k].L,m[k].l); cg[k].R=Math.max(cg[k].R,m[k].r); }
}
console.log(`\n-- CTA sub-elementos (${ctaFile}) --`);
for(const k in cg){ const band = k==='big'?WIDE:SMALL; const f=flag(cg[k].L,cg[k].R,band); if(f.startsWith('***'))bad++;
  console.log(`  #${k.padEnd(5)} L=${cg[k].L.toFixed(0).padStart(4)} R=${cg[k].R.toFixed(0).padStart(4)} W=${(cg[k].R-cg[k].L).toFixed(0).padStart(4)} band=${k==='big'?'wide':'small'} -> ${f}`); }
console.log(`\nNEW-RULER: ${bad} itens furam.`);
await b.close();
