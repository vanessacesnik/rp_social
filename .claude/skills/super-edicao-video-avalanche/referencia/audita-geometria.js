/* audita-geometria.js · o PORTÃO DA LEI 2 do modelo YouTube 1.
 *
 * Por que existe (06/08/2026). O `npm run check` do HyperFrames só amostra 9 instantes do
 * vídeo inteiro e só reprova elemento que estoura um container que CLIPA. Ele deixou passar,
 * no vídeo 01, uma unidade de medida transbordando 39px por baixo da borda do card. Quem
 * pegou foi esta auditoria.
 *
 * O que ele mede, em TODA cena, em quatro instantes de cada uma (entrada, dois terços do
 * meio e o fim):
 *   1. tinta_fora_direita / tinta_fora_baixo · texto passando de left:1188 ou top:1002
 *   2. tinta_vaza_caixa_* · texto passando da borda interna do próprio card
 *   3. colisao_tinta · texto por cima de texto
 *
 * Ele mede a TINTA (os rects dos nós de texto), não a caixa do elemento. Medir caixa dá
 * centenas de falsos positivos, porque caixa larga com texto curto "colide" sem colidir de
 * verdade. No vídeo 01 a medição por caixa acusou 973 e a medição por tinta acusou 5, e as 5
 * eram reais.
 *
 * Também só olha os clips ATIVOS no instante: fora do render o motor não gerencia a
 * visibilidade, então sem esse filtro todas as cenas do vídeo aparecem empilhadas.
 *
 * COMO RODAR
 *   cd <proj> && python3 -m http.server 8791 --bind 127.0.0.1 &
 *   e no browser (MCP playwright, ou qualquer Chrome) abra http://127.0.0.1:8791/index.html
 *   e execute esta função. Ela devolve {amostras, violacoes, lista}.
 *
 * PORTÃO: `violacoes` tem que ser ZERO antes do render. Qualquer achado volta para o bloco,
 * nunca para o render.
 */
() => {
  const tl = window.__timelines["main"];
  const painel = document.querySelector('#painel');
  const PB = painel.getBoundingClientRect();
  const LIM_R = PB.left + 1188, LIM_B = PB.top + 1002, TOL = 2;

  const clips = Array.from(document.querySelectorAll('.clip')).map(c => ({
    el: c, s: parseFloat(c.dataset.start), d: parseFloat(c.dataset.duration)
  })).filter(c => isFinite(c.s) && isFinite(c.d));

  const tempos = [];
  clips.filter(c => c.el.dataset.trackIndex === '2').forEach(c => {
    tempos.push(+(c.s + 0.9).toFixed(2), +(c.s + c.d * 0.3).toFixed(2),
                +(c.s + c.d * 0.6).toFixed(2), +(c.s + c.d - 0.12).toFixed(2));
  });
  const T = [...new Set(tempos)].filter(t => t > 0).sort((a, b) => a - b);

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

  const tinta = el => {
    let box = null;
    for (const n of el.childNodes) {
      if (n.nodeType !== 3 || !n.textContent.trim()) continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      for (const r of rg.getClientRects()) {
        if (r.width < 1 || r.height < 1) continue;
        box = box
          ? {l: Math.min(box.l, r.left), t: Math.min(box.t, r.top),
             r: Math.max(box.r, r.right), b: Math.max(box.b, r.bottom)}
          : {l: r.left, t: r.top, r: r.right, b: r.bottom};
      }
    }
    return box;
  };

  const ehCaixa = el => {
    const cs = getComputedStyle(el);
    return (parseFloat(cs.borderTopWidth) > 0 ||
            (cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)'))
      && el.id !== 'painel' && cs.overflow !== 'hidden';
  };

  const sel = el => el.id ? '#' + el.id
    : (typeof el.className === 'string' && el.className.trim()
        ? '.' + el.className.trim().split(/\s+/)[0] : el.tagName);

  // um elemento deliberadamente recuado (opacidade baixa, tipico do "bloco que recua com blur")
  // e fundo, nao colisao: so entra na regra de colisao quem esta legivel de verdade.
  const legivel = el => {
    let n = el, op = 1;
    while (n && n !== document.body) { op *= parseFloat(getComputedStyle(n).opacity || '1'); n = n.parentElement; }
    return op >= 0.35;
  };

  const achados = {};
  const reg = (regra, alvo, t, det) => {
    const k = regra + '|' + alvo;
    if (!achados[k]) achados[k] = {regra, alvo, t, det, n: 0};
    achados[k].n++;
  };

  for (const t of T) {
    tl.pause(); tl.seek(t);
    const ativos = clips.filter(c => t >= c.s - 0.001 && t < c.s + c.d + 0.001).map(c => c.el);
    let todos = [];
    for (const a of ativos) todos = todos.concat(Array.from(a.querySelectorAll('*')));
    todos = todos.filter(visivel);

    const inks = [];
    for (const e of todos) { const b = tinta(e); if (b) inks.push({e, b}); }

    for (const {e, b} of inks) {
      if (e.closest('.faixa')) continue;
      if (b.r > LIM_R + TOL) reg('tinta_fora_direita', sel(e), t, Math.round(b.r - LIM_R) + 'px');
      if (b.b > LIM_B + TOL) reg('tinta_fora_baixo', sel(e), t, Math.round(b.b - LIM_B) + 'px');
    }

    for (const c of todos.filter(ehCaixa)) {
      const r = c.getBoundingClientRect(), cs = getComputedStyle(c);
      const lim = {
        r: r.right - parseFloat(cs.borderRightWidth) - parseFloat(cs.paddingRight) + 4,
        b: r.bottom - parseFloat(cs.borderBottomWidth) - parseFloat(cs.paddingBottom) + 4
      };
      for (const f of Array.from(c.querySelectorAll('*')).filter(visivel)) {
        const b = tinta(f); if (!b) continue;
        if (b.b > lim.b + TOL) reg('tinta_vaza_caixa_baixo', sel(c) + ' > ' + sel(f), t, Math.round(b.b - lim.b) + 'px');
        if (b.r > lim.r + TOL) reg('tinta_vaza_caixa_direita', sel(c) + ' > ' + sel(f), t, Math.round(b.r - lim.r) + 'px');
      }
    }

    for (let i = 0; i < inks.length; i++) {
      for (let j = i + 1; j < inks.length; j++) {
        const A = inks[i], B = inks[j];
        if (A.e.contains(B.e) || B.e.contains(A.e)) continue;
        if (!legivel(A.e) || !legivel(B.e)) continue;
        const ox = Math.min(A.b.r, B.b.r) - Math.max(A.b.l, B.b.l);
        const oy = Math.min(A.b.b, B.b.b) - Math.max(A.b.t, B.b.t);
        if (ox > TOL && oy > TOL) reg('colisao_tinta', sel(A.e) + ' x ' + sel(B.e), t, Math.round(ox) + 'x' + Math.round(oy));
      }
    }
  }

  const lista = Object.values(achados).sort((a, b) => a.t - b.t);
  return {amostras: T.length, violacoes: lista.length, lista};
}
