# MODELO: FAIXA HYPERFRAME + SANDUICHE

> Migrado VERBATIM da skill `broll-faixa-hyperframe` em 2026-07-25, na unificação da
> `super-edicao-video-avalanche`. Nada foi resumido: o que estava escrito continua escrito.
> Acervo deste modelo: `assets/broll-faixa-hyperframe` (os caminhos `scripts/`, `assets/`, `references/`
> citados no texto abaixo agora vivem sob essas pastas).
> O que e COMUM a todos os modelos (perguntas de abertura, plataforma, corte fino,
> gancho e QA) mora em `nucleo/` e vale aqui tambem.

---

# VSL FAIXA HYPERFRAME (quadrado em cima + faixa Hyperframe embaixo, 100% do vídeo)

Formato: vídeo 9:16 com o conteúdo (rosto do Chefe) num **quadrado em cima** e uma **faixa embaixo
preenchida 100% com b-roll Hyperframe ILUSTRADO**, do início ao fim. Um b-roll novo a cada **10s**.

## REGRA QUE O CHEFE BRIGOU (NÃO ESQUECER)
**NUNCA queimar a frase falada como legenda na faixa.** Cada b-roll da faixa tem que ILUSTRAR a ideia
do trecho: **kicker curto + headline punchy (3-7 palavras, resumo, NÃO a frase) + elementos visuais**
(número contando, barra crescendo/encolhendo, ícones, comparação lado a lado, carimbo back.out, seta,
checklist, gauge). Igual aos b-rolls de uma VSL profissional. (A 1ª versão só queimou a frase = lixo,
o Chefe xingou. A 2ª, ilustrada, ele aprovou.)

## REGRA 2 QUE O CHEFE BRIGOU — FAIXA 100% LIMPA, ZERO ATROPELO (aprovada 2026-06-28)
**Texto e elementos NUNCA podem se esbarrar nem um sobrescrever/cobrir o outro.** O acerto que o Chefe
elogiou ("ficou excelente") foi o **SISTEMA DE ZONAS** — exemplar provado e validado:
`assets/template-bar-ZONAS-1080x742.html` (inspect=0, WCAG AA). Toda barra segue essas zonas, qualquer
que seja a altura da faixa medida (as zonas são horizontais; só o y de kicker/sub/progresso escala com a altura):
- **ZONA ESQUERDA** (x:64 até ~664, largura travada ~600px): kicker no topo + headline + sub opcional (rodapé esquerdo).
- **ZONA DIREITA** (x:712 até ~1016, largura ~304px): o visual (número gigante / gauge / barras / ícone CSS).
- **CORREDOR de 48px** entre as duas zonas (x:664→712) que NINGUÉM invade.
- **RODAPÉ:** barra de progresso (left:64, width:952, bottom:~48).
- **Headline:** largura MÁX ~600px, MÁX 2 linhas. Não coube em 2? Reduz a fonte (range ~64-88px) ou encurta. Nada vaza os limites da faixa nem encosta na barra de progresso.
- **GATE obrigatório:** renderizar SÓ com `lint` sem erro **E `inspect=0` layout issues**. NÃO usar `data-layout-allow-overlap` pra mascarar atropelo real (só pra camada de fundo decorativa de propósito: guias/glow). Conferir frame no MEIO de cada take.

## GANCHO VIRAL (obrigatório desde 2026-07-19)
Todo reels editado ABRE com o gancho, no padrão da skill **`edicao-video-avalanche`** (seção GANCHO VIRAL lá, regras completas): frase-gancho autossuficiente de 3-8s tirada de DENTRO do vídeo, escolhida pela hierarquia (1º número chocante, 2º afirmação contraintuitiva/polêmica, 3º implicação do "você", 4º open loop, 5º pico emocional; nunca abrir em saudação), recortada do arquivo final e colada NA FRENTE (a frase repete no lugar original, cold open). No sanduíche, a headline em 2 LINHAS caixa alta vai na **faixa vermelha `#D32F2F` cobrindo SÓ a região do strip Hyperframe** (232px em 1080p / 464px em 4K), fonte Bricolage Grotesque weight 800 branca com auto-fit; quadrado e b-roll de baixo ficam com o conteúdo original durante o gancho. No formato quadrado + faixa ilustrada (sem strip), a headline vai em card vermelho `#D32F2F` na base do quadro. Corte ~0.15s antes da 1ª palavra, fim em 0.3-0.4s de silêncio ou boundary (whisper word-level, nunca cortar palavra); transição `xfade=fade:0.4` + `acrossfade=d=0.4:c1=tri:c2=nofade`.

## FLUXO
1. **Medir/definir a faixa:** `cropdetect` em vários pontos do vídeo (`ffmpeg -ss T -t 1 -i v -vf cropdetect=24:2:0 -f null -`). A região com conteúdo dá o bloco de cima; a faixa = `altura_total - altura_conteúdo` na base. (Ex.: vídeo 1080x1920, conteúdo top 1076px, faixa = **1080x844 em y=1076**.) **Proporção da faixa é flexível** — o Chefe aprovou **16:11 = 1080x742 em y=1178** (faixa menor, talking-head maior em cima): escalar o talking-head pra 1080x1920 e **sobrepor** a faixa nos 742px de baixo (rosto fica no terço superior, não cobre). Quadrado-em-cima (1080x1080 + faixa 840) continua válido. Linha coral fina (`drawbox` 4px) no encaixe separa bem.
2. **Transcrever** com a API `whisper-1` (NÃO local) — mp3 em caminho ASCII.
3. **Quebrar em takes de 10s:** N = ceil(duração/10). Gerar specs `{id, dur, fala}` por take (a fala = texto da transcrição naquela janela, pro agente saber o que ilustrar). Gerar `specs<N>.json`.
4. **Gerar os N b-rolls (paralelo):** Workflow `assets/workflow-bar-ilustrado.js` (1080x844), em lotes (~4 takes/agente). Cada agente LÊ o specs.json, pega a fala dos seus takes e **desenha** a barra ilustrando (kicker+headline+elementos), valida e renderiza pra `brolls/bar/bar-<id3>.mp4`. Args não são usados (agente lê o specs do disco) — relançar via `scriptPath`.
5. **Montar:** `assets/montar_faixa.sh` — espera os N renders, **concatena** as barras na ordem (`concat` → bar-track 1080x844), **sobrepõe** na faixa: `overlay=0:<y_da_faixa>` mantendo a faixa preta coberta 100% e o **áudio do vídeo** (`-map 0:a`). Salva e abre.

## GOTCHAS
- **Verificar frame:** sampleie no MEIO de cada take (start+5s), NUNCA no início do take (multiplo de 10) — lá a barra está entrando (opacity 0) e parece preta. Já me enganei 2x assim.
- **Concatenar exige mesmos params** (todas as barras saem do mesmo render → ok). A última barra é mais curta (resto da duração).
- **Subagentes + hook RTK:** `npx hyperframes@x` quebra; usar caminho absoluto do npx do nvm + dangerouslyDisableSandbox, ou `npm run`.
- **Esperador de verdade:** waiters em background com `sleep` real (o truque `ffmpeg anullsrc -t 5` roda instantâneo, NÃO espera). O arquivo de saída aparece parcial durante o encode → só considerar pronto quando o log de montagem disser "PRONTO" (não pela mera existência do arquivo).
- Template da barra: `assets/template-bar-1080x844.html` (placeholders). Mas o AGENTE deve AUTORAR ilustrado, não só trocar texto no template (template é só base de estilo/dimensão).

## ASSETS
- `template-bar-ZONAS-1080x742.html` — **EXEMPLAR PROVADO (preferir este)**: barra 16:11 com o SISTEMA DE ZONAS (kicker+headline+sub na esquerda, número 73% na direita, progresso no rodapé). inspect=0, WCAG AA, aprovado pelo Chefe. Os agentes leem ELE pra absorver estilo + zonas.
- `template-bar-1080x844.html` — base antiga (1080x844, Avalanche dark), sem o sistema de zonas explícito.
- `workflow-bar-ilustrado.js` — workflow que desenha N barras ilustradas em paralelo (lê specs.json). Brief já carrega o CONTRATO DE ZONAS anti-atropelo (zona esquerda/direita + corredor 48px + gate inspect=0). Ajustar dims/N/ROOT no topo por job.
- `montar_faixa.sh` — espera os renders, concatena a faixa e sobrepõe no vídeo (ajustar y da faixa e caminho do vídeo no topo do script).

---

# FORMATO SANDUÍCHE — VEO + HYPERFRAME (aprovado pelo Chefe 2026-07-16, "ficou foda demais")

Variante validada na esteira Criativos Workshop Bruno (24 vídeos): **3 camadas empilhadas (vstack) em 1080x1920**:
- **TOPO (1080x1080):** talking-head em QUADRADO, rosto BEM CENTRALIZADO.
- **MEIO (1080x232):** strip Hyperframe fina — pill de kicker à esquerda + headline 1 LINHA caixa alta (~56-72px, max-width ~760px) + 1 elemento visual animado à direita (x:820-1016). Padding 64px. NÃO é legenda: ilustra a IDEIA do trecho. 1 strip por janela de 8s.
- **BAIXO (1080x608):** b-roll VEO 3.1 fast IMAGE-TO-VIDEO 16:9 (gpt-image-2 ultra realista → crop 16:9 → aprovação do Chefe → Veo com câmera travada + negativePrompt). 1 take por janela de 8s (mesmas janelas das strips).

Pipeline: corte de silêncio + **1.2x SEMPRE** → transcrever (whisper-1 API, words) → specs por janela de 8s → [strips Hyperframe ∥ imagens gpt-image-2 → CHECKPOINT aprovação → Veo] → montar: `crop=1080:1080:0:0` do canvas (com áudio) + concat strips (trim na duração) + concat Veo `scale=1080:608,fps=30` (trim) + vstack. Sem linha de separação (a strip clara já separa).

## ENQUADRAMENTO DO QUADRADO (o Chefe brigou — INEGOCIÁVEL)
O crop do quadrado (largura full × largura, offset y) tem que deixar o rosto CENTRALIZADO o vídeo inteiro: extrair ~8 frames espalhados, escolher o offset eliminando o teto morto SEM nunca cortar a cabeça (nem quando a pessoa se inclina), gerar previews e VERIFICAR com Read antes de montar. Offset varia por vídeo (ex: 576px→y=90-120; 720px→y=40-210).

## REGRA DO TEMPORIZADOR GLOBAL (o Chefe já corrigiu 2x — INEGOCIÁVEL)
A barra de progresso no rodapé de CADA composição (barra 1080x840 ou strip 1080x232) NUNCA vai de 0→100% dentro do próprio take. Ela anima LINEAR (`ease:'none'`, duração = data-duration inteira, transform-origin left) **da fração inicial à fração final do take no vídeo todo** (fração = fronteira_do_take / duração_total), pra que na concatenação vire UM temporizador contínuo do início ao fim. Calcular as frações por take e passar no brief de cada agente. Verificar na montagem: frames dos dois lados de uma fronteira (t=9.5/10.5) têm que mostrar o preenchimento contínuo, sem reset.

## PALETAS DO PORTAL DE TERAPIAS (conteúdo Luz da Serra/terapeutas)
Não usar o tema Avalanche dark: extrair paletas dos 100 modelos de carrossel do app (`~/CURSOR 2/luzdaserra-terapias/public/carrossel-modelos*.js`). Validadas em produção: Orgânico botânico (creme #f8f6f0 + sálvia #8fb56f + marrom #3a2413), Cristais (off-white rosado #faf4f2 + rosé #c58aa6 + ameixa), Sino tibetano (marfim #fdf7e4 + dourado #e0a92e), Mandala floral (#f7f6ea + oliva #8aa06a), Chá e ervas (#f7efe1 + caramelo #b08a5a), Jardim secreto (#faf7fb + lilás #b08fc7), Madeira clara (#f4f4ee + verde-cinza #8f9a8c), Aquarela pastel (#f5efe2 + #9c8058), Orquídea (#eef4ea + #4f7a52), Vitral suave (#f2fbfc + teal #1fa6b8) e as NOTURNAS Noite estrelada (#0c1330 + creme lunar #f2efe6 + luar #cdd8ff) e Floresta noturna (#0b1a12 + verde-luar #9fe08a). Trio por vídeo: 2 claras + 1 noturna. Texto de acento sempre na variante escura (AA); dor/negativo em tom da paleta (nunca vermelho berrante).

## GOTCHAS NOVOS (esteira 2026-07-16)
- **Agente "aguardando" está morto:** poll do Veo e esperas de render SEMPRE num script python EM FOREGROUND (`time.sleep` no loop, timeout Bash 600000) — nunca "armar watcher" e parar.
- **Workflow com args:** o runtime pode entregar `args` como string — abrir o script com `const A = (typeof args==='string') ? JSON.parse(args) : args`.
- Veo 3.1 fast sai 24fps — normalizar com `fps=30` na montagem.
- Strips não levam CTA/música da skill Avalanche quando o vídeo é de cliente (ex: Bruno).
- Entregas centralizadas numa pasta única no Desktop quando for lote (ex: "Criativos Workshop Bruno"); nomes `V{n}_FAIXA-{PALETA}.mp4` / `V{n}_SANDUICHE-VEO-HYPER.mp4`.
