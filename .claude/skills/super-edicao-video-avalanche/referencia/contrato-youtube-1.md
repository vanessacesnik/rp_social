# Contrato de cena · vídeo T1 · versão 2 (geometria nova)

Você escreve UM arquivo de cena. Não edite nenhum arquivo compartilhado.

## Saída
Escreva `/Users/naiarodrigues/workspace/t1-full/blocos2/<SEU_ARQUIVO>.html` com DUAS seções
separadas exatamente por estas marcas, e NADA fora delas:

```
<!--HTML-->
... a div da sua cena ...
<!--JS-->
... suas linhas de timeline GSAP ...
```

Sem `<html>`, sem `<style>`, sem `<script>`, sem comentário fora das marcas.

## Canvas
Painel útil 1252x1016. NÃO existe mais cabeçalho: a logo some depois do gancho, então
a cena usa a tela inteira, do topo ao rodapé. Nada acima de 34 nem abaixo de 1000.

Classes prontas (use, não redefina):
- `.beat` (JÁ posicionado no topo, em 34) com `<span class="beat-num">NN</span><span class="beat-txt">RÓTULO</span>`
- `.headline` (left 64, width 1090, peso 800) — posicione com `style="top: 92px"`, reduza a fonte se o texto for longo (o padrão 76px só cabe em 1 linha curta; use 40 a 56px)
- `.sub` (left 64, width 1000, 28px, cinza) — `style="top: NNNpx"`
- `.pill` (left 64, width 1124, altura 100) com `<span class="pill-num">X</span><span class="pill-txt">texto</span>`; variante `.pill-alerta`
- `.barra-rot`, `.barra-tubo` (altura 46, DÊ SEMPRE `width` inline), `.barra-fill` (DÊ SEMPRE `background` inline), `.barra-val` (DÊ SEMPRE `left` inline, use 1010px)
- Cena com imagem: `<div class="img-area grande"><img id="cXX-img" src="assets/ARQUIVO.png" alt="" /></div>`
  Se for INFOGRÁFICO, use `class="img-area grande info"` (ele aparece inteiro, dentro da moldura).
  A área já fica em top 146, altura 690, largura cheia. Não mude.
- Faixa de dados embaixo da imagem: `<div class="faixa" style="top: 850px">` com
  `.faixa-rot`, `.faixa-dado` e `<div class="ticker-linha">` de `<span class="tick">` (máximo 6, cada um com no máximo 15 caracteres)

Cores: texto `#0F172A`, cinza `#5D5B54`, cyan `#0E7490` (só sobre fundo claro), coral `#F5402E`,
verde `#24D869`, cyan claro `#4FD8EF` (só sobre fundo escuro `#0F172A`).

## Regras que reprovam
1. A cena é `<div id="cXX" class="clip livre" data-start="X" data-duration="Y" data-track-index="2">` com os tempos EXATOS que eu te passei.
2. Animação SÓ por `transform` e `opacity` (x, y, scale, rotation) ou por `width` de barra. NUNCA anime `top`, `left`, `fontSize`, `padding` ou `margin`.
3. **A tela nunca passa 2 segundos sem movimento**, e o movimento vem do CONTEÚDO: número contando, barra crescendo, item entrando, destaque migrando. Proibido barra de progresso, varredura, partícula, brilho decorativo. Distribua eventos por TODA a duração, no máximo 2 segundos entre um e o próximo.
4. Zero travessão em texto de tela. Vírgula, parênteses ou o middot.
5. Acentuação correta em português.
6. Nada colide: headline em 92 com 2 linhas de 56px termina perto de 220; o que vier depois começa em 240 ou mais. Em cena com imagem, a headline fica em top 70 e precisa caber em UMA linha (termina antes de 140).
7. O texto sai da FALA daquele momento, que eu te passo. Headline curta, afirmativa, em minúsculas. Nunca invente número que ele não disse.
8. IDs únicos prefixados pela cena (`#cXX-barra-a`), e variáveis JS também (`cXXn`).
9. **Todo elemento que você anima já precisa estar visível naquele instante, e o container dele
   também.** Animar um rótulo que mora dentro de uma faixa que só entra depois é movimento que não
   existe na tela: o espectador vê a tela parada, mesmo com o evento marcado na timeline.

## Exemplo válido
```
<!--HTML-->
<div id="cXX" class="clip livre" data-start="94.37" data-duration="32.00" data-track-index="2">
  <div class="beat"><span class="beat-num">A</span><span class="beat-txt">O RÓTULO</span></div>
  <div class="headline" style="top: 92px; font-size: 56px">a frase da cena</div>
  <div id="cXX-kpi" style="position:absolute; left:64px; top:300px; font-weight:900; font-size:190px; color:#F5402E; letter-spacing:-0.045em">0</div>
</div>
<!--JS-->
tl.fromTo("#cXX .beat", { opacity: 0, x: -26 }, { opacity: 1, x: 0, duration: 0.5 }, 94.52);
const cXXn = { v: 0 };
tl.to(cXXn, { v: 12.5, duration: 6, ease: "none", onUpdate: () => {
  document.getElementById("cXX-kpi").textContent = cXXn.v.toFixed(1).replace(".", ",");
} }, 95.3);
```
