# MODELO: GENNARO (elemento na palavra exata)

> Migrado VERBATIM da skill `edicao-video-gennaro` em 2026-07-25, na unificação da
> `super-edicao-video-avalanche`. Nada foi resumido: o que estava escrito continua escrito.
> Acervo deste modelo: `scripts/gennaro, elements/gennaro, assets/gennaro, referencia/gennaro` (os caminhos `scripts/`, `assets/`, `references/`
> citados no texto abaixo agora vivem sob essas pastas).
> O que e COMUM a todos os modelos (perguntas de abertura, plataforma, corte fino,
> gancho e QA) mora em `nucleo/` e vale aqui tambem.

---

# EDICAO DE VIDEO ESTILO GENNARO v2 (talking-head 9:16, elementos na palavra exata)

Formato: o Chefe fala em talking-head vertical 1080x1920, a voz corre continua por baixo, e a cada
1,5 a 2,5s entra um estado visual novo. A cabeca falante NUNCA aparece pelada: sempre tem legenda
gigante e, na maioria dos cortes, um elemento grafico entrando exatamente quando ele fala a coisa
que o elemento representa. Abre com a promessa ou um numero nos 2 primeiros segundos e fecha com
"COMENTA / EU QUERO" mais um toast de DM. O metodo completo esta em `referencia/` (dossie + frames).

O trabalho e 80% marcar os timestamps certos (o elemento entra na palavra exata) e 20% gerar os
assets. Densidade e sincronia sao o que da a sensacao premium; sem elas vira imitacao.

---

## REGRAS INEGOCIAVEIS (leia antes de tocar em qualquer arquivo)

1. **Regua de margem por classe de elemento, medida pela TINTA.** A tela do celular mostra so os
   ~886px centrais do 1080. A area UTIL, ja com respiro dentro do que a tela mostra, e: texto largo
   em `[160,920]` (~760px), legendas ate ~740px (`[170,910]`), elementos pequenos ate `[130,950]`.
   A medicao que vale e a TINTA renderizada dos PNGs (alpha>150), nunca a caixa do layout: texto em
   `white-space:nowrap` transborda a propria caixa, entao o `getBoundingClientRect` subestima a
   largura real. `scripts/measure_ink.py` (varre os PNGs por alpha) e a fonte de verdade.
2. **Prova em crop de celular, conferida A OLHO, antes de entregar.** Alem das medicoes, gere 4 a 6
   frames-chave ja cortados na proporcao da tela do celular com `scripts/proof_celular.py`
   (`crop=886:1920:97:0` depois `scale=590:1280`) e confira no olho: nada encostando, respiro
   visivel dos dois lados. A guia numerica sozinha nao basta; o crop mostra o que o Chefe ve.
3. **Na duvida, MANTEM.** No corte fino, so tira muleta clara. Verbo "ta/to" (esta/estou) fica,
   anafora de estilo fica, pausa dramatica antes de numero ou climax fica. A frase tem que
   continuar natural sem a palavra. Melhor natural que picotado.
4. **Honestidade de citacao.** Logo de marca so entra se a narracao REALMENTE nomeia a marca ou se a
   marca esta de fato na tela. Nunca inventar citacao. Se um trecho ja tem um chip, a logo enriquece
   o chip existente em vez de virar elemento novo.
5. **Palavrao fica no audio e FORA da legenda.** A voz e intacta; a legenda nao transcreve o palavrao.
6. **Zero travessao em tudo que aparece na tela** (legenda, card, chip, toast). Use virgula ou frase
   curta. `scripts/qa_final.py` conta em/en-dash nas legendas E no HTML de cada elemento do plano, e
   REPROVA (exit 1) se achar qualquer um.
7. **Animacao SO por `window.__seek(t)`.** O render tira screenshot com `animations:'disabled'`, entao
   `@keyframes` / `transition` CSS NAO aparecem: o overlay sai congelado no video e voce so descobre
   no `verify_motion.py`, depois de gastar o render inteiro. Toda animacao e posicionada por JS dentro
   do `__seek`.
8. **`ELEMS` em ordem cronologica crescente e nome so com `[A-Za-z0-9_]`.** A janela de cada elemento e
   fechada pelo offset do seguinte, e o nome vira pasta, arquivo e URL. O `cut_plan.py` agora reprova
   as duas coisas na hora, em vez de gerar janela negativa e sumir com o elemento em silencio.

---

## LAYOUT DO WORKSPACE

Trabalhe sempre numa pasta nova em `entregas/<slug>-gennaro/`, sem sobrescrever entrega anterior.
Estrutura canonica (a raiz e a raiz do servidor estatico, por isso os caminhos absolutos batem):

```
entregas/<slug>-gennaro/
  original.mp4          video talking-head de origem
  audio16k.json         whisper word-level da base (passo b)
  elements/             copie de skills/edicao-video-gennaro/elements/ e adapte o texto
  fonts/                copie de skills/edicao-video-gennaro/assets/fonts/  (servido em /fonts)
  img/                  saidas do gpt-image-2 (servido em /img)
  logos/                svg oficiais (servido em /logos)
  captions/             captions.json (gerado)
  render/               plan.json, cut_filter.txt, punch_filter.txt, render_all.sh, build.sh (gerados)
  build/                png_*, mov_*, mp4 intermediarios
  proof/celular/        provas em crop de celular
  FINAL_<slug>_gennaro.mp4
```

Preparar a pasta e subir o servidor (todos os scripts recebem o workspace por `GEN_WORK`):

```bash
SK="$HOME/.claude/skills/edicao-video-gennaro"        # esta skill
WORK="$HOME/naia-agent/entregas/<slug>-gennaro"       # workspace da entrega
mkdir -p "$WORK"/{elements,fonts,img,logos,captions,render,build,proof/celular}
cp "$SK"/elements/*.html "$SK"/elements/_base.css "$SK"/elements/_lib.js "$WORK"/elements/
cp "$SK"/assets/fonts/*.ttf "$WORK"/fonts/
GEN_WORK="$WORK" bash "$SK"/scripts/serve.sh 8100 &   # deixa rodando; mata no fim
```

---

## PASSO A PASSO CANONICO

### a. Confirmar o arquivo certo
Antes de editar, confirme que o `original.mp4` e mesmo o video pedido. Bata nome, `mtime`, duracao
e resolucao por `ffprobe`, e ouca/leia uma amostra da transcricao pra casar o tema com o pedido. So
depois de bater, copie pra `entregas/<slug>-gennaro/original.mp4`. Se nao bater, pare e confirme.

### b. Transcricao word-level e corte fino
1. Transcreva a base com whisper em nivel de palavra. O whisper grava com o NOME DO VIDEO
   (`original.json`), entao o `mv` faz parte do passo, senao o `cut_plan.py` para dizendo que falta
   `audio16k.json`:
   ```bash
   whisper original.mp4 --model medium --language pt --word_timestamps True --output_format json -o .
   mv original.json audio16k.json
   ``` Os tempos de
   palavra vem SEMPRE dessa transcricao da base (o original costuma ser VFR; tempo remapeado erra na
   borda do corte e derruba palavra).
2. Preencha o bloco de config no topo de `scripts/cut_plan.py` (slug, `BASE_DUR`, fillers medidos,
   elementos, punches, cores) e rode `GEN_WORK="$WORK" python3 scripts/cut_plan.py`. Ele calcula:
   pausas acima de ~0,35s viram respiro de 0,16 a 0,28s (mais respiro na transicao de bloco, nunca
   zerar a pausa); muletas dispensaveis saem por intervalo medido (silaba inteira, sem sobra, sem
   comer a vizinha); as muletas alvo sao "ta?", "ne?", "o", "cara", "e ai", falsos comecos e
   repeticoes; o resto de `REGRAS INEGOCIAVEIS #3` decide o que fica.
3. A emenda e corte seco (jump cut) em video E audio no MESMO ponto, com micro-fade de audio de
   ~10ms em cada emenda pra matar o clique. Sync perfeito por construcao; nunca crossfade sobreposto
   (dessincroniza A/V ao longo de dezenas de emendas). Nunca cortar palavra pela metade nem matar a
   ultima palavra da frase.
4. QA de clique por salto de amostra (feito no `scripts/qa_final.py`): o maior `|step|` numa janela
   de +-25ms ao redor da emenda tem que ficar bem abaixo do p99.9 global do video.

### c. Punch-ins de rosto (aplicados no BASE, antes dos overlays)
4 a 6 zooms nas frases FORTES (promessa, numero, virada). Alterne enquadramento: um "close" ~1.17x,
o proximo "wide" ~1.12x. Zoom centrado (scale uniforme + crop 1080x1920 central) mantem o rosto
INTEIRO; confira por frame que nao corta testa nem queixo. As janelas ancoram nas PALAVRAS de enfase
pelo tempo word-level da base. `cut_plan.py` ja escreve `render/punch_filter.txt` a partir de
`PUNCH_DEF`. Aplicar no base garante que legenda e elementos fiquem na safe area, compostos por cima
do base ja com zoom.

### d. Roteiro de elementos na PALAVRA exata
Cada elemento entra no timestamp em que a fala diz a coisa que ele representa. O vocabulario:
- **Cold open (0 a 2s)**: card de gancho com a promessa ou o numero. Se houver numero, um contador.
- **Chips empilhando**: em enumeracoes, um retangulo por item, o ativo forte e os ditos escurecem.
- **Contadores animados**: em numeros e ROI, valor subindo ate assentar (com um tick no assento).
- **Badges**: nas viradas.
- **Mockups / paineis**: quando cita uma ferramenta ou mostra um resultado.
- **Recap final com checks**: a transformacao resumida em lista com marcadores.
- **Fecho assinatura**: `elements/e_cta.html` ja traz o layout fixo. "COMENTA" menor em cima
  (kicker, letter-spacing largo), "EU QUERO" GIGANTE coral numa linha propria com entrada pop/pulse,
  um composer de comentario estilo Instagram embaixo, o toast de DM do Denderson escorregando do topo
  e um ding no fim. Centralize o texto gigante por `left:50%` + `translateX(-50%) scale(...)` (o
  layout centraliza e o scale entra por cima), nunca medindo largura por JS e deslocando.
Marque cada momento como um elemento em `ELEMS` no `cut_plan.py`, com o offset no tempo do original.

### e. Legendas
Caixa alta, `Montserrat` Black, 2 a 3 palavras por vez sincronizadas com a fala, largura maxima
~740px, sempre fora do rosto (faixa baixa, acima do primeiro plano). Keyword colorida: coral (`c`,
`#F5402E`) pra enfase, verde (`g`, `#24D869`) pra dinheiro ou coisa positiva, uma cor por frase.
Meca a PIOR linha (a mais larga), nao a media, e caia a fonte se a pior linha furar (~52 a 61px).
Faca a curadoria manual dos erros do whisper (nomes, numeros, pontuacao); para maxima limpeza,
autore as legendas a mao no molde de `render/captions_curated.py` (ver exemplo em
`entregas/gennaro-video3/render/captions_curated.py`). Palavrao fica no audio e fora da legenda.

### f. Imagens gpt-image-2 (2 a 3 por video)
Cubra 2 a 3 momentos de fala forte com uma imagem gerada, entrando com moldura animada. Escolha o
momento pela fala exata (o assunto da imagem) e prefira janelas mais "secas" (so cabeca falante).
1. Escreva os prompts num `jobs.json` (`{"nome":"prompt da cena", ...}`) e rode
   `GEN_WORK="$WORK" python3 scripts/gen_images.py jobs.json`. O script ja aplica dark premium,
   paleta Avalanche e a trava "NO readable text" (texto dentro de imagem gerada sai errado; so
   formas de UI, icones e labels minusculos). Saida em `img/<nome>.png`.
2. A moldura e o Ken Burns vem de `elements/imgcard.html` (param por query string: `src`, `dur`,
   `kb=push|panl|panr`, `accent=cyan|coral|green`, `logos=csv`, `title`). Borda com glow pulsando +
   tracinho correndo, imagem com zoom leve 1.0 a 1.085. Duas imagens parecidas nunca coladas sem
   diferenciar cor de moldura e tipo de movimento. Card com 820px de largura (dentro da safe area).
3. Registre cada imagem como elemento `type='img'` em `ELEMS` e preencha `IMG[nome]` no `cut_plan.py`.

### g. Logos oficiais animadas (so na citacao real)
Quando a narracao nomeia uma plataforma, ferramenta ou marca, entram as logos OFICIAIS no timestamp
exato, com entrada suave + micro bounce e whoosh sutil, dentro da safe area. Baixe de fonte oficial
com `GEN_WORK="$WORK" python3 scripts/fetch_logos.py claude instagram whatsapp meta openai
googlegemini` (Simple Icons via jsDelivr; injeta o fill de marca). Varra a transcricao inteira atras
de TODA citacao e siga `REGRAS INEGOCIAVEIS #4`: so o que foi dito, enriquecendo chip existente
quando houver.

### h. Regua de margem (padrao unico, inegociavel)
Reforco operacional de `REGRAS INEGOCIAVEIS #1` e `#2`. A tela do celular mostra os ~886px centrais
(`x` de 97 a 983). A area UTIL, com respiro DENTRO disso:
- **Texto largo** (cards de gancho, bignum, contadores, recap, cards de lista): ate ~760px,
  faixa `[160,920]`, centrado em `cx=540`. Todo container de texto largo nasce mirando ~760px,
  nunca a largura cheia do quadro.
- **Legendas**: ate ~740px, faixa `[170,910]`.
- **Elementos pequenos** (chips, badges, pills, toasts, stamps): ate `[130,950]` (~820px).

Como encolher sem retrabalhar fonte a fonte: aplicar um scale uniforme no `#stage`
(`#stage{transform:scale(K);transform-origin:540px YCpx;}`) com K do bounding box medido. Scale
uniforme reduz tamanho mantendo hierarquia. Card de gancho com numero gigante em
`white-space:nowrap`: reduza a FONTE ate caber no container (o scale do `#stage` sozinho nao resolve
quando o texto transborda o container).

Fluxo de medicao, nesta ordem:
1. Estimativa rapida: `node scripts/measure_layout.mjs "$WORK" 8100` (Playwright, so orientacao).
2. Fonte de verdade: renderize os PNGs (passo i) e rode `GEN_WORK="$WORK" python3
   scripts/measure_ink.py`. Alvo: 0 item furando. Elemento pequeno declara `kind='small'` no
   `cut_plan.py` pra ser medido na faixa `[130,950]`.
3. Prova final A OLHO: `scripts/proof_celular.py` (passo j).

### i. Render dos overlays (HTML para Playwright para ProRes) e SFX
1. Gere os scripts de build a partir do plano: `GEN_WORK="$WORK" python3 scripts/emit_pipeline.py
   8100`. Ele escreve `render/render_all.sh` e `render/build.sh`.
2. Renderize os overlays: `bash render/render_all.sh`. Cada elemento HTML expoe `window.__seek(t)`
   (determinismo); `scripts/seek_render.mjs` posiciona a animacao frame a frame e grava PNG
   transparente `f%05d.png` (5 digitos; encode com `f%05d.png`), depois vira ProRes 4444 com alpha.
   O `seek_render.mjs` espera `window.__assetsReady` antes de tirar os frames (imagem carregada);
   `imgcard.html` ja implementa isso.
3. Monte o video: `bash render/build.sh`. A ordem e **cut+punch numa passada so** (o
   `render/cut_punch_filter.txt` encadeia os dois; era um encode inteiro a mais, com perda de
   recompressao a toa), composite dos overlays, outro com o CTA, concat, mix de SFX. SFX sutis: whoosh 0.12 na entrada de cada elemento, tick no assento do
   contador e nas logos, ding no fim do DM. Sem musica por padrao (so se o Chefe pedir). A voz e
   intacta; confira continuidade nas emendas com `scripts/verify_audio.py`.
4. Mapeamento de inputs do `filter_complex` (o `emit_pipeline.py` ja faz certo, confira ao editar a
   mao): a base e o input 0, os elementos comecam no input 1, as legendas por ultimo; cada `[n:v]`
   mapeado explicitamente pra sua janela `between(t,off,end)`. Confirme por frame que CADA overlay
   aparece na sua janela (um indice deslocado faz overlays sumirem em silencio).

### j. QA final (nada de "pronto" sem isto)
Todo script abaixo sai com **exit 1 quando reprova**. Encadeie com `&&` e trate falha como bloqueio,
nao como aviso.
1. `GEN_WORK="$WORK" python3 scripts/verify_overlays.py` prova que CADA elemento do plano aparece
   MESMO no video final (compara o final com `build/base_punch.mp4` na regiao onde o elemento
   deveria estar). E o unico check que pega indice deslocado no `filter_complex` e mov que nao
   renderizou, os dois erros que entregam um mp4 perfeito e sem o elemento.
2. `GEN_WORK="$WORK" python3 scripts/verify_motion.py` confirma que as animacoes MOVEM de verdade.
   O crop de cada elemento vem da tinta real do PNG dele, entao elemento fora da faixa baixa
   (card de gancho no topo, stamp de canto) e medido onde ele esta de fato.
3. `GEN_WORK="$WORK" python3 scripts/verify_audio.py` confirma voz continua nas emendas e presenca
   dos SFX.
4. `GEN_WORK="$WORK" python3 scripts/qa_final.py` roda durations vs plano, decode limpo, A/V sync,
   click check nas emendas (global e local com a MESMA amostragem) e o guard de travessao em
   legenda e em todo HTML do plano. Imprime `QA_FAIL` com a lista do que reprovou.
5. `GEN_WORK="$WORK" python3 scripts/measure_ink.py` fecha em 0 item furando a regua.
6. `GEN_WORK="$WORK" python3 scripts/proof_celular.py FINAL_<slug>_gennaro.mp4 t1 t2 t3 t4` gera 4 a 6
   provas em crop de celular; abra e confira A OLHO: nada encostando, respiro dos dois lados.

### k. Entrega
`FINAL_<slug>_gennaro.mp4` no workspace + as provas em `proof/celular/`. Mate o servidor estatico.
Reporte pra Naia (nunca direto pro Chefe): caminho do mp4, duracao, o que cada elemento cobre e as
provas. A caption de Telegram (ate 1000 chars) vai em mensagem separada, a pedido.

---

## SCRIPTS (em `scripts/`, todos recebem o workspace por `GEN_WORK`)

- `serve.sh`. Servidor estatico com raiz no workspace (elementos carregam /fonts, /img, /logos, /captions).
- `cut_plan.py`. Planejador word-level (config por video no topo). Escreve captions.json, cut_filter.txt, punch_filter.txt, plan.json.
- `emit_pipeline.py`. Gera render_all.sh + build.sh a partir do plan.json.
- `seek_render.mjs`. Harness HTML para PNG transparente por `window.__seek(t)` (determinismo; espera `__assetsReady`).
- `measure_layout.mjs`. Estimativa rapida de margem por layout (orientacao; nao e a fonte de verdade).
- `measure_ink.py`. Margem pela TINTA renderizada (fonte de verdade). Alvo 0 furos.
- `proof_celular.py`. Provas em crop de celular (886 central para 590x1280).
- `gen_images.py`. Cards gpt-image-2 dark premium, sem texto legivel dentro.
- `fetch_logos.py`. Logos oficiais (Simple Icons) com fill de marca.
- `verify_overlays.py`. **(novo na v2)** Prova que cada overlay do plano aparece no final, comparando
  com a base pre-overlay na bbox do elemento. Exit 1 se algum sumiu.
- `verify_motion.py`. Confirma que os overlays animam (burst + diff), com crop por elemento vindo da
  tinta renderizada. Exit 1 se algum ficou congelado.
- `verify_audio.py`. Voz continua nas emendas + presenca de SFX.
- `qa_final.py`. QA completo que REPROVA (exit 1): duracao vs plano, decode, A/V sync, click nas
  emendas, safe area, punch e travessao em legenda + HTML dos elementos.

## ELEMENTOS (em `elements/`)

`_base.css` (design system: cores Avalanche, chip, card, pill, toast, glows) e `_lib.js` (helpers de
easing e o contrato `window.__seek`) sao a base de todo elemento. `caption_track.html`,
`imgcard.html` e `e_cta.html` sao os canonicos reutilizaveis. Em `elements/exemplos/` estao moldes
adaptaveis de cada arquetipo (hook, contador, chips, recap). Ao criar um elemento novo, parta de um
molde existente, mantenha `#stage` e `window.__seek(t)`, e nasca mirando a faixa `[160,920]`.

## DEPENDENCIAS

Node + Playwright (Chromium ja instalado), ffmpeg/ffprobe, whisper CLI, Python 3 com Pillow. Chave
`OPENAI_API_KEY` em `~/naia-agent/.env` (usada pelo `gen_images.py`).

## REFERENCIA

Metodo completo, os dois formatos, o vocabulario dos 8 elementos e a tabela dos 25 videos estao no
dossie apontado em `referencia/README.md`, junto dos 8 frames de referencia visual.

---

## GOTCHAS DE OPERACAO (aprendidos rodando o pipeline de ponta a ponta)

- **Texto de card se escreve COM ACENTO.** Montserrat tem os glifos e a legenda do whisper ja vem
  acentuada, entao card escrito em "MILHOES / SO NO BRASIL / POR MES" fica gritando erro de
  portugues do lado de uma legenda correta. Isso so aparece na prova em crop de celular, ou seja,
  depois do render inteiro. Escreva certo desde o primeiro HTML.
- **Re-renderizou PNG? Re-encode o `.mov`.** O `render_all.sh` faz PNG e ProRes juntos, mas quando
  voce conserta um elemento e roda so o `seek_render.mjs`, o `build.sh` continua consumindo o
  `build/mov_<nome>.mov` ANTIGO. O video sai com a versao velha e nenhum check acusa, porque o
  overlay esta la, so que errado. Sempre rode o `ffmpeg ... prores_ks` do elemento logo depois.
- **Nunca dispare `render_all.sh` com `&` dentro de um wrapper que retorna.** O grupo de processos
  morre junto com o wrapper e voce fica com meia sequencia de PNG e log vazio, sem erro nenhum.
  Rode em primeiro plano no job longo.
- **Meca a regua ANTES do build.** `measure_ink.py` roda assim que os PNGs existem. Furou, conserta e
  re-renderiza so o elemento afetado: bem mais barato que descobrir depois de montar o video.
- **Dupla centralizacao e o furo de layout mais comum.** `.chip`/`.card` do `_base.css` ja tem
  `left:50%`, e o JS aplica `translateX(-50%)`. Se o CSS do elemento ainda trouxer um
  `margin-left:-<metade>px`, o bloco anda meia largura pra esquerda e cola na borda. Use um so.
- **Texto `white-space:nowrap` maior que o container sangra pra DIREITA**, entao a tinta mede
  `cx` deslocado e o `R` estoura enquanto o `L` continua certinho. Cx longe de 540 no
  `measure_ink.py` significa texto transbordando, nao card descentrado.
- O workspace fecha em torno de **1,3 GB** (PNG + ProRes). Os PNGs sao insumo do `measure_ink.py` e
  do `verify_overlays.py`: so limpe depois que o Chefe aprovar a entrega.

---

## O QUE MUDOU DA v1 PARA A v2 (2026-07-25)

A v1 entregava video bom, mas os guardas dela nao guardavam: dava pra reprovar em silencio e ainda
ler "pronto". Corrigido, com teste de runtime em cima de cada item.

1. **`qa_final.py` nunca reprovava.** Ele imprimia os cliques de audio encontrados, mas o veredito
   final so olhava travessao e o script sempre saia com codigo 0. Agora acumula falhas e sai 1.
2. **O click check era enviesado.** O p99.9 global amostrava 1 a cada 7 amostras e o maximo local
   usava todas, o que rebaixava o limiar e inventava clique. Agora os dois usam o mesmo passo.
3. **Travessao so era conferido na legenda**, apesar da regra dizer "tudo que aparece na tela".
   Agora varre tambem o HTML de cada elemento do plano e o do CTA.
4. **Overlay podia sumir sem ninguem notar.** Indice deslocado no `filter_complex` ou mov que nao
   renderizou entregam mp4 perfeito e sem o elemento. Nasceu o `verify_overlays.py`.
5. **`verify_motion.py` media todo mundo na mesma faixa baixa da tela.** Elemento fora dali dava
   "STATIC?!" falso ou "MOVE OK" falso. Agora o crop vem da tinta real de cada elemento.
6. **`ELEMS` fora de ordem gerava janela negativa** e o elemento sumia calado, porque a janela e
   fechada pelo offset do seguinte. Agora e erro na hora, junto com nome repetido e nome invalido.
7. **Elemento ancorado num trecho cortado colava na borda em silencio.** Agora avisa qual elemento,
   qual tempo e qual corte engoliu a ancora.
8. **SFX do fecho estavam cravados** em `NEW_DUR+0.2` e `NEW_DUR+1.7`, assumindo `OUTRO=3.9`. Mudar a
   duracao do fecho jogava o ding pra fora. Agora derivam de `OUTRO`.
9. **Punches sobrepostos** faziam o segundo zoom ganhar do primeiro sem aviso. Agora avisa.
10. **Asset que nao carregava era engolido** por um `.catch(() => {})` no `seek_render.mjs`, e o card
    ia vazio pro video. Agora falha alto, e uma sequencia toda transparente tambem reprova.
11. **Uma geracao de x264 a menos:** cut e punch viraram uma passada so (`cut_punch_filter.txt`).
    No teste de runtime deu a mesma duracao com decode limpo e quase metade do tempo de parede.
12. **Transcricao sem `--word_timestamps`, `original.mp4`/`audio16k.json` faltando ou json de outro
    whisper** viravam stack trace. Agora sao mensagens que dizem o que fazer.
13. **Legenda larga demais** so aparecia depois do render inteiro. O planejador agora estima a
    largura em pixel e lista as piores linhas antes de voce gastar o render.
14. **Pillow 14 vai remover `Image.getdata()`**, usado no diff de movimento. Trocado por `ImageStat`,
    que tambem evita materializar milhoes de pixels numa lista.
15. **A skill so renderizava se morasse dentro da arvore que tem o `node_modules`.** Em ESM o
    `import 'playwright'` resolve pela pasta DO SCRIPT, nao pelo cwd, entao instalar a skill em
    `~/.claude/skills` quebrava tudo com `ERR_MODULE_NOT_FOUND`. `seek_render.mjs` e
    `measure_layout.mjs` agora procuram o playwright em varias raizes (`PLAYWRIGHT_ROOT`, a skill,
    `GEN_WORK`, `~/naia-agent`, `~`) e dizem exatamente o que instalar se nao acharem.

Validado em workspace sintetico (video 1080x1920 com silencios reais, transcricao word-level, dois
elementos e um punch): os 6 guardas novos do planejador dispararam, o QA reprovou travessao em
elemento e duracao fora do plano e passou limpo depois da correcao, o detector de overlay acusou
AUSENTE sem o overlay e PRESENTE com ele, e a fusao cut+punch bateu a duracao do metodo antigo.
