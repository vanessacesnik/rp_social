/* audita-tela-cheia.js · o PORTÃO DA LEI 3 do modelo YouTube 1.
 *
 * Por que existe (06/08/2026). O `audita_2s.py` acusa janela de 2 segundos SEM MOVIMENTO, e o
 * `npm run check` não olha densidade nenhuma. Nenhum dos dois vê PAINEL OCO: uma cena pode ter
 * um rótulo piscando no topo, a faixa viva embaixo, e o miolo inteiro vazio por 17 segundos.
 * Foi o que aconteceu no vídeo 01: 94 segundos ocos em 34 janelas, com o `audita_2s` aprovado.
 *
 * O que ele mede: a cada 1 segundo do vídeo inteiro, quanto da REGIÃO ÚTIL do painel (de
 * `top: 170`, logo abaixo do cabeçalho, até `top: 850`, onde começa a faixa) está coberta por
 * elemento visível com tinta, fundo, borda ou imagem.
 *
 * REPROVA quando a cobertura fica abaixo de 10% da região, ou quando há menos de 2 elementos
 * visíveis. Esses dois limiares vieram de calibrar contra o vídeo 01: cena boa fica entre 25% e
 * 60%; cena com só headline e subtítulo dá 5%; painel vazio dá 0%.
 *
 * COMO RODAR
 *   cd <proj> && python3 -m http.server 8791 --bind 127.0.0.1 &
 *   abrir http://127.0.0.1:8791/index.html e executar esta função.
 *
 * PORTÃO: `instantes_ocos` tem que ser ZERO antes do render.
 *
 * COMO CONSERTAR o que ele acusa (nesta ordem):
 *   1. A cena entra tarde. O primeiro elemento estrutural tem que estar visível no
 *      `data-start` do clip, não 2 segundos depois. O conteúdo se preenche depois, a
 *      ESTRUTURA nasce junto.
 *   2. A cena esvazia antes de acabar. Nada de fade-out geral antes do corte: o último estado
 *      segura até o clip terminar.
 *   3. A cena é esparsa (só headline e subtítulo). Falta bloco no meio: cards, fluxo, lista,
 *      barras, ticks, ancorados na fala daquele trecho.
 */
() => {
  const tl = window.__timelines["main"];
  const painel = document.querySelector('#painel');
  const PB = painel.getBoundingClientRect();
  const REG = {l: PB.left, t: PB.top + 170, r: PB.right, b: PB.top + 850};
  const AREA = (REG.r - REG.l) * (REG.b - REG.t);

  const clips = Array.from(document.querySelectorAll('.clip')).map(c => ({
    el: c, s: parseFloat(c.dataset.start), d: parseFloat(c.dataset.duration), tr: c.dataset.trackIndex
  })).filter(c => isFinite(c.s) && isFinite(c.d));

  const raiz = document.querySelector('[data-composition-id]');
  const DUR = parseFloat(raiz.dataset.duration);

  const visivel = el => {
    let n = el, op = 1;
    while (n && n !== document.body) {
      const cs = getComputedStyle(n);
      if (cs.display === 'none' || cs.visibility === 'hidden') return false;
      op *= parseFloat(cs.opacity || '1');
      if (op < 0.06) return false;
      n = n.parentElement;
    }
    return true;
  };

  const ocos = [];
  for (let t = 0.5; t < DUR; t += 1.0) {
    tl.pause(); tl.seek(t);
    const ativos = clips.filter(c => c.tr === '2' && t >= c.s - 0.001 && t < c.s + c.d + 0.001).map(c => c.el);
    let area = 0, n = 0;
    for (const a of ativos) {
      for (const e of Array.from(a.querySelectorAll('*'))) {
        if (!visivel(e)) continue;
        const cs = getComputedStyle(e);
        const temTinta = Array.from(e.childNodes).some(x => x.nodeType === 3 && x.textContent.trim());
        const temFundo = (cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)')
          || parseFloat(cs.borderTopWidth) > 0 || e.tagName === 'IMG';
        if (!temTinta && !temFundo) continue;
        const r = e.getBoundingClientRect();
        const l = Math.max(r.left, REG.l), rr = Math.min(r.right, REG.r);
        const tt = Math.max(r.top, REG.t), bb = Math.min(r.bottom, REG.b);
        if (rr > l && bb > tt) { area += (rr - l) * (bb - tt); n++; }
      }
    }
    const pct = area / AREA;
    if (pct < 0.10 || n < 2) ocos.push({t: +t.toFixed(1), pct: +(pct * 100).toFixed(1), elems: n});
  }

  const janelas = [];
  for (const o of ocos) {
    const u = janelas[janelas.length - 1];
    if (u && o.t - u.fim <= 1.6) { u.fim = o.t; u.min = Math.min(u.min, o.pct); }
    else janelas.push({ini: o.t, fim: o.t, min: o.pct});
  }

  return {
    duracao: DUR,
    instantes_ocos: ocos.length,
    janelas: janelas.map(j => ({de: j.ini, ate: j.fim, dur: +(j.fim - j.ini + 1).toFixed(1), min_pct: j.min}))
  };
}
