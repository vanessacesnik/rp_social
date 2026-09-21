# MODELO: HYPERFRAME QUEIMADO (gravação em tela cheia + faixa sobreposta)

Vertical de aula ou explicação, feito de uma gravação de celular mais uma faixa gráfica animada
queimada POR CIMA da imagem, com legenda palavra por palavra colada acima da faixa.

Validado em produção em 2026-07-29 no vídeo da aula do Opus 5 (47,80 s, 1080x1920). O processo
completo, com número, comando e prova de cada etapa, está em
`referencia/processo-video-opus5-2026-07-29.md`.

## A LIÇÃO QUE CRIOU ESTE MODELO

A primeira versão empilhou meio a meio: gravação reduzida a 720x1280 dentro de um canvas de
1080x960 em cima, faixa de 1080x960 embaixo, unidas por `vstack`. O Chefe reprovou na hora:

> "Vc cortou o video errado! Seu trabalho é só queimar o hyperframe em cima do original, Vai ocupar
> a parte de baixo da tela e a parte de cima fica certinho onde está meu rosto! Mas vc colocou o
> video dentro de uma moldura com faixas pretas aos lados, corrija"

**A gravação dele NUNCA é reduzida, cortada ou emoldurada.** Ela ocupa 1080x1920 inteiros. A faixa
entra sobreposta, ocupando só a parte de baixo. Se a faixa não couber, quem encolhe é a faixa.

## QUANDO USAR

Aula, explicação ou tese em vertical, gravada de celular, em que o apoio visual (números, títulos,
gráficos, prints) precisa aparecer sem tirar o rosto da tela. Se o pedido for b-roll cobrindo a
tela, é outro modelo (`broll-fullscreen.md`). Se for quadrado em cima e faixa embaixo, meio a meio,
é o `broll-faixa-hyperframe.md`, e confirme com ele antes, porque foi esse layout que ele reprovou.

## 1. A GRAVAÇÃO: PROBE ANTES DE QUALQUER COISA

```bash
ffprobe -v error -print_format json -show_format -show_streams fala-chefe.mp4
```

iPhone recente entrega HEVC 10 bits, HLG em BT.2020, Dolby Vision perfil 8 e **rotação por matriz**
(tag `rotate: 270`, Display Matrix 90). Consequências que mandam no resto:

- A resolução efetiva é 2160x3840, ou seja 9:16 exato. Cabe em 1080x1920 por escala pura, sem corte
  e sem distorção. É isso que sustenta a tela cheia.
- Sem tonemap a imagem sai lavada. Todo comando de extração aplica:

```bash
TM="zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv"
```

- O arquivo carrega GPS do iPhone (`com.apple.quicktime.location.ISO6709`). Limpar metadado antes de
  republicar o master fora da casa.

## 2. TRANSCRIÇÃO COM TIMESTAMP POR PALAVRA

Sem palavra com timestamp não existe legenda palavra por palavra nem âncora de cena.

```bash
ffmpeg -y -v error -i fala-chefe.mp4 -vn -ac 1 -ar 16000 -c:a libmp3lame -b:a 64k fala-chefe.mp3

curl -s https://api.openai.com/v1/audio/transcriptions \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -F file=@fala-chefe.mp3 -F model=whisper-1 -F language=pt \
 -F response_format=verbose_json \
 -F "timestamp_granularities[]=segment" -F "timestamp_granularities[]=word" \
 -o transcricao.json
```

O Whisper erra grafia de marca e quebra número. Corrigir na LEGENDA, nunca no JSON, com três mapas
no gerador: `MERGE` (juntar tokens, ex. "4" + "5" vira "4.5"), `FIX` (grafia, ex. "Cloud Code" vira
"Claude Code") e `ONSET` (palavra marcada tarde, medida no envelope RMS do próprio áudio em janelas
de 25 ms com limiar de -32 dBFS).

## 3. MATÉRIA-PRIMA VISUAL A PARTIR DO SITE OU DO TEMA

Captura com Playwright, `device_scale_factor=2`, `color_scheme="dark"`, `wait_until="networkidle"`.
Antes de recortar, injetar CSS que zera `animation-duration`, `animation-delay`, `transition-*`,
força `opacity:1`, `transform:none`, `filter:none`, `visibility:visible` nos `.reveal` e marca as
classes de revelado. Depois rolar a página de 600 em 600 px, voltar ao topo, esperar
`document.fonts.ready` e mais 1500 ms.

**Armadilha comprovada:** barra fixa no topo carimba no meio dos blocos altos, porque o Playwright
rola até o elemento antes de recortar. Segundo passe com `.topbar { display: none !important; }` e
recaptura dos blocos.

Os números e títulos saem do HTML real, e a paleta sai do `styles.css` do próprio site. Não inventar
cor nem número.

## 4. GRÁFICOS EM HTML, NO TAMANHO EXATO DO DESTINO

Um HTML único com um cartão por assunto, cada `.card` no tamanho exato da área de destino, e captura
em dobro (`device_scale_factor=2`). Texto renderizado em navegador sai nítido; imagem gerada por IA
não sobrevive a texto pequeno.

O script de captura mede overflow comparando `scrollHeight` com `clientHeight` antes de salvar, e é
esse medidor que aponta tipografia apertada. Toda substituição de tamanho de fonte vai protegida por
`assert a in s`.

## 5. A FAIXA NO HYPERFRAMES

CLI **pinada** em todos os comandos (`npx --yes hyperframes@<versão> ...`), projeto criado com
`init video --non-interactive --example blank`.

- Cada cena é uma `<section class="clip">` com `data-start`, `data-duration`, `data-track-index`.
- Timeline GSAP criada pausada e registrada em `window.__timelines["main"]`.
- **Cada corte é ancorado no timestamp real da fala**, não em estimativa de ritmo. O roteiro
  estimado serve pra planejar; quando a transcrição chega, as cenas são remapeadas contra a palavra
  falada.
- Crossfade padrão curto e, nos dois ou três cortes que precisam doer, flash coral no lugar do
  crossfade.
- A faixa é renderizada **sem áudio**: o áudio do produto é a voz do Chefe.
- Rodar `check` a cada rodada e conferir os quadros extraídos, nunca o log.

Bugs reais que o `check` e a conferência visual pegaram, e valem pra qualquer render:
`<i>` inline ignora `height` e `scaleX` (as barras saem vazias, corrige com `display:block`);
`fromTo` com `immediateRender` liga o elemento desde o quadro zero; overflow proposital se marca com
`data-layout-allow-overflow` em vez de ser escondido.

## 6. A MEDIDA DECIDE A ALTURA DA FAIXA, NÃO O GOSTO

Antes de escolher onde a faixa começa, medir onde o rosto termina. O script extrai o vídeo já
tonemapeado em escala 1:4, amostra 2 quadros por segundo e, na faixa central de x, procura a última
linha em que pelo menos 35% dos pixels passam de luma 62, que é o fim da massa de cabeça, barba e
pescoço.

Saída real do vídeo de referência:

```
amostras=96  (48.0s)
mediana=1124  p90=1252  p95=1323  max=1696
acima de 1120: 53/96      -> faixa de 960 cortaria o queixo em 53 das 96 amostras
acima de 1200: 15/96      -> faixa de 720 reduz para 15
```

Foi assim que a faixa encolheu de 960 para 720 de altura. **Cortar a faixa está fora**: a análise das
janelas de 720 px sobre os 1434 quadros mostrou que a melhor janela preservaria só 306 quadros
intactos. Quando não couber, reduz proporcionalmente, nunca corta.

Reduzir 1080x960 para 720 de altura dá 810 de largura, sobrando 135 px de cada lado. Das três opções
testadas lado a lado (cor chapada, coluna de borda replicada, cobertura desfocada) venceu a
**replicação da coluna de borda**, porque o fundo da faixa é quase preto uniforme e a replicação faz
o flash e a sangria continuarem cobrindo a largura inteira, sem barra visível.

## 7. O COMANDO DE COMPOSIÇÃO (a entrega de verdade)

```bash
ffmpeg -hide_banner -y \
  -i "$BASE/fala-chefe.mp4" \
  -i "$BASE/entrega/faixa-1080x960.mp4" \
  -loop 1 -framerate 30 -t 47.81 -i "$V3/ramp.png" \
  -framerate 30 -start_number 0 -i "$V3/caps/cap_%05d.png" \
  -filter_complex "
    [0:v]${TM},format=yuv444p,scale=1080:1920:flags=lanczos,setsar=1[base];
    [1:v]scale=810:720:flags=lanczos,setsar=1,split=3[p0][pl][pr];
    [pl]crop=1:720:0:0,scale=135:720[l];
    [pr]crop=1:720:809:0,scale=135:720[r];
    [l][p0][r]hstack=inputs=3,format=yuv444p,tpad=stop_mode=clone:stop_duration=1[panel];
    [3:v]tpad=stop_mode=clone:stop_duration=1[caps];
    [base][2:v]overlay=0:960:eof_action=pass[b1];
    [b1][panel]overlay=0:1200:eof_action=pass[b2];
    [b2][caps]overlay=0:900:eof_action=pass,format=yuv420p[vout]
  " \
  -map "[vout]" -map 0:a \
  -c:v libx264 -preset slow -crf 18 -profile:v high -level 4.1 \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -r 30 -video_track_timescale 30000 \
  -c:a copy -movflags +faststart "$OUT"
```

Camada por camada: a gravação sai do HLG para BT.709 e é escalada para 1080x1920 (redução exata pela
metade, sem corte) · a faixa é reduzida proporcionalmente para 810x720 e ganha 135 px de borda
replicada de cada lado · a `ramp.png` é um PNG de 1080x240 com alfa que preenche a emenda entre
`y=960` e `y=1200` com curva de opacidade `t^2.2` · a legenda entra em `y=900` · o áudio passa
intacto com `-c:a copy`.

### Três armadilhas que já quebraram entrega

1. **`-frames:v N` junto de `-map <áudio>` trunca o áudio.** O mux encerra na contagem de quadros e o
   áudio para antes do fim (aconteceu: 45,14 s num vídeo de 47,80 s). Nunca usar `-frames:v` no
   comando que muxa áudio.
2. **Camada com exatamente a mesma duração do base descobre o último quadro.** Qualquer arredondamento
   deixa o último frame sem faixa e sem legenda, e aparece a camisa dele embaixo. Corrige com
   `tpad=stop_mode=clone:stop_duration=1` em toda camada sobreposta.
3. **Áudio nunca se recodifica na composição.** `-c:a copy` sempre.

## 8. A LEGENDA PALAVRA POR PALAVRA

PNG RGBA com Pillow, um por estado, nunca `drawtext` do ffmpeg.

- Fonte Bricolage Grotesque variável, `set_variation_by_axes([96, 800, 100])` (opsz 96, wght 800
  ExtraBold, wdth 100), corpo 58.
- Palavras agrupadas em blocos; dentro do bloco cada palavra acende no `start` dela.
- Palavra apagada: branca com alfa 105. Acesa: branca opaca, ou **coral `#d97757` (217,119,87), o
  laranja do logo do Claude**, se estiver no conjunto de palavras-chave.
- Três passadas por estado pra sobreviver a qualquer fundo: sombra deslocada 5 px com contorno de
  8 px e desfoque 7, contorno preto de 5 px, e o preenchimento.
- Largura máxima de 950 px em banda de 1080, quebrando em no máximo duas linhas pelo corte que deixa
  as linhas mais parecidas.
- **Colada na faixa quer dizer folga pequena e medida.** Na versão aprovada: banda em `y=900..1200`,
  base do texto em `y=1170`, faixa começando em `y=1200`, folga de 30 px. A verificação mediu o pixel
  mais baixo com alfa em todos os estados: pior caso a 8 px da faixa, sem nunca invadir.
- Eficiência: desenhar só os estados únicos e criar os quadros como links simbólicos
  (`os.symlink`). No vídeo de referência foram 129 estados para 1434 quadros.

## 9. VERIFICAÇÃO, SEMPRE DE FORA E COM CONTROLE POSITIVO

Três provas rodaram antes de entregar, e é esse o padrão:

**A gravação continua intacta.** Amostrar instantes ao longo do vídeo e comparar a região de cima do
resultado contra a fonte tonemapeada na mesma escala. Diferença média de 2,75 e pior caso 3,14 =
só compressão H.264. Medir também a coluna mais escura do quadro inteiro: pior caso 23,6 prova que
não existe barra preta (barra daria perto de 0).

**A borda replicada bate.** Diferença média 0,00 e pior 0,09 entre os 135 px de pad e a coluna de
borda.

**O que devia sumir sumiu.** Quando ele mandar tirar algo (uma URL, um logo), não basta editar o
código. Recortar gabaritos do render ANTIGO, rodar casamento de template
(`cv2.TM_CCOEFF_NORMED`, limiar 0,70) sobre todos os quadros dos dois vídeos e usar o antigo como
**controle positivo**:

```
CONTROLE (faixa antiga): score maximo 1.000 · 65 frames acima do limiar
ENTREGA (final):         score maximo 0.409 · 0 frames acima do limiar
VEREDITO: o detector funciona e NAO ha URL no video final
```

Guardar o arquivo antigo justamente para servir de controle.

## 10. ENTREGA

O master sai grande (o de referência ficou com 126 MB em CRF 18). O bot do Telegram não envia acima
de 50 MB, então a saída é **recomprimir só para transporte**, mantendo o áudio copiado:

```bash
ffmpeg -v error -y -i video-final.mp4 -c:v libx264 -preset slow -crf 24 -c:a copy \
  -movflags +faststart /tmp/video-final-telegram.mp4    # ~38 MB
```

Entregar a cópia e dizer a ele, em uma linha, que o master ficou salvo para edição. Nunca entregar só
a cópia comprimida sem avisar, nem apertar o CRF do render principal para caber no mensageiro.

Provas que acompanham a entrega: quadros extraídos em pontos-chave (2, 9, 18, 30, 34 e 46 s no vídeo
de referência), em 1080x1920, conferidos a olho antes de mandar.

## 11. REPETIR DO ZERO, EM ONZE PASSOS

1. Baixar a gravação e rodar `ffprobe` antes de tudo; tratar tonemap e rotação desde o primeiro comando.
2. Extrair MP3 mono 16 kHz e transcrever com `timestamp_granularities[]=word`.
3. Capturar o site com Playwright em 2x, matando animação e barra fixa por CSS injetado.
4. Desenhar os gráficos em HTML no tamanho exato do destino e capturar em dobro.
5. Montar a faixa no HyperFrames com a CLI pinada, ancorando cada animação na fala real.
6. Compor no ffmpeg com a gravação intacta em tela cheia e a faixa queimada por cima.
7. Medir onde está o rosto antes de escolher a altura da faixa.
8. Gerar a legenda como PNG RGBA, um estado por transição, e sobrepor com `overlay`.
9. `tpad=stop_mode=clone` em toda camada com a mesma duração do base.
10. `-c:a copy`, e nunca `-frames:v` no comando que muxa o áudio.
11. Verificar de fora, com controle positivo, e só então entregar.
