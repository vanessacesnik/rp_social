// Deterministic HTML -> transparent PNG sequence renderer.
// Each element HTML must define window.__seek(tSeconds) that positions its animation.
// Usage: node seek_render.mjs <htmlAbsPath> <outDir> <durationSec> <fps> [dsf] [start] [W] [H]
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

const [, , htmlPath, outDir, durStr, fpsStr, dsfStr, startStr, wStr, hStr] = process.argv;
const dur = parseFloat(durStr);
const fps = parseInt(fpsStr, 10);
// Dimensao parametrizavel: o overlay de tela cheia e 1080x1920, mas a strip do sanduiche e
// 1080x232 e a faixa da VSL e 1080x608. Renderizar tudo em 1920 de altura gerava PNG com
// 1688px de transparencia inutil por frame.
const W = wStr ? parseInt(wStr, 10) : 1080;
const H = hStr ? parseInt(hStr, 10) : 1920;
const DSF = dsfStr ? parseFloat(dsfStr) : 2;
const START = startStr ? parseFloat(startStr) : 0;

fs.mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({
  args: [
    '--force-color-profile=srgb',
    '--font-render-hinting=none',
    '--disable-lcd-text',
    '--hide-scrollbars',
    '--allow-file-access-from-files',
  ],
});
const page = await browser.newPage({
  viewport: { width: W, height: H },
  deviceScaleFactor: DSF,
});
page.on('console', m => { if (m.type() === 'error') console.error('PAGE-ERR:', m.text()); });
page.on('pageerror', e => console.error('PAGE-EXC:', e.message));
const url = htmlPath.startsWith('http') ? htmlPath : ('file://' + path.resolve(htmlPath));
await page.goto(url);
await page.waitForFunction('typeof window.__seek === "function"', { timeout: 15000 });
await page.evaluate(async () => { await document.fonts.ready; });
// Espera os assets. ANTES isto tinha .catch(()=>{}): se a imagem nao carregasse, o timeout era
// engolido e o card ia pro video VAZIO, sem erro nenhum. Agora falha alto.
try {
  await page.waitForFunction('!window.__assetsReady || window.__assetsReady()===true', { timeout: 15000 });
} catch (e) {
  console.error(`ASSETS_FAIL: __assetsReady nunca ficou true em ${url} (imagem/fonte nao carregou).`);
  await browser.close();
  process.exit(1);
}
// warm one seek so layout settles
await page.evaluate((t) => window.__seek(t), 0);

const n = Math.round(dur * fps);
const base = Math.round(START * fps);
for (let i = 0; i < n; i++) {
  const t = START + i / fps;
  await page.evaluate((t) => window.__seek(t), t);
  await page.screenshot({
    path: `${outDir}/f${String(base + i).padStart(5, '0')}.png`,
    omitBackground: true,
    clip: { x: 0, y: 0, width: W, height: H },
    animations: 'disabled',
  });
}
await browser.close();

// Guard de "renderizou nada": PNG 1080x1920 totalmente transparente comprime pra poucos KB.
// Se NENHUM frame passa do limiar, o elemento nao desenhou (seletor errado, __seek que nao
// posiciona, css que nao carregou) e o build seguiria em frente com um overlay invisivel.
const EMPTY_KB = 8;
let maxKb = 0;
for (let i = 0; i < n; i++) {
  const fp = `${outDir}/f${String(base + i).padStart(5, '0')}.png`;
  try { maxKb = Math.max(maxKb, fs.statSync(fp).size / 1024); } catch {}
}
if (maxKb < EMPTY_KB) {
  console.error(`EMPTY_RENDER: nenhum frame passa de ${EMPTY_KB}KB (maior=${maxKb.toFixed(1)}KB) em ${outDir}. ` +
                `O elemento nao desenhou nada. Confira window.__seek, o css e o console da pagina.`);
  process.exit(1);
}
console.log(`RENDERED ${n} frames -> ${outDir} (maior frame ${maxKb.toFixed(1)}KB)`);
