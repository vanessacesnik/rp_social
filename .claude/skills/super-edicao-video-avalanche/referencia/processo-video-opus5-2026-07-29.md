# Processo completo de produção do vídeo da aula do Opus 5

Reconstrução feita a partir dos arquivos reais do job em `/opt/naia-agent/workspace/video-hyperframes-opus5/`, do
histórico de comandos das sessões (`/home/naia/.claude/projects/-opt-naia-agent/*.jsonl`) e da inspeção direta
de cada mídia com `ffprobe`, `identify` e Pillow. Todo número citado aqui vem de um arquivo ou da saída de um
comando registrado, e a origem está indicada em cada caso. O que não pôde ser provado pelos arquivos está
listado na seção 14.

Horários em BRT (fuso do servidor). O histórico de sessão grava em UTC, então cada carimbo abaixo é o UTC do
log menos 3 horas.

---

## 1. Panorama em uma tela

O produto final é um vertical de 47,80 s, 1080x1920, com a gravação do Chefe ocupando a tela inteira e uma
faixa gráfica de apoio queimada por cima na parte de baixo, mais legenda palavra por palavra acima dessa faixa.

O caminho teve duas versões finais. A primeira (`entrega/video-final-opus5-1080x1920.mp4`) encaixava a gravação
numa moldura com bordas desfocadas nas laterais e foi reprovada pelo Chefe. A segunda
(`entrega/video-final-v2-1080x1920.mp4`) tem a gravação em tela cheia sem corte e é a versão aprovada.

Quatro frentes rodaram em paralelo no começo: captura do site, download e transcrição da gravação, desenho dos
infográficos e montagem no HyperFrames. Os IDs de subagente aparecem no histórico como `agent-ab6c0de6606d6123f`
(assets do site e gráficos), `agent-ae204ebae245c2aab` (gravação e transcrição), `agent-a7477e525227f80e5`
(composição HyperFrames), `agent-a88deb7ccc39d7622` (composição v1 em ffmpeg e legenda),
`agent-a4af664492873a0e4` e `agent-a3cb12180c7e9a64e` (diagnóstico e refazimento v2).

---

## 2. Insumos de entrada

### 2.1 A gravação do Chefe

O arquivo chegou por download autenticado do Google Drive, passando pelo proxy da Maton, às 03:57:40 BRT:

```bash
set -a && . ./.env && set +a && cd /opt/naia-agent/workspace/video-hyperframes-opus5 && \
curl -sL --max-time 900 -o fala-chefe.mp4 -w "HTTP:%{http_code} size:%{size_download} time:%{time_total}\n" \
  -H "Authorization: Bearer $MATON_API_KEY" \
  "https://api.maton.ai/google-drive/drive/v3/files/1Lr3EH93IjRI4M4bNVNyz_FaFg4p5mT7Z?alt=media&supportsAllDrives=true"
```

`ffprobe -v error -print_format json -show_format -show_streams fala-chefe.mp4` devolve, no arquivo que está
no disco hoje:

| Propriedade | Valor | Origem |
|---|---|---|
| Container | `mov,mp4,m4a,3gp,3g2,mj2`, major brand `qt ` | format |
| Tamanho | 302.706.024 bytes (288,7 MiB) | format.size |
| Duração | 47,801667 s | format.duration |
| Bitrate total | 50.660.329 bps | format.bit_rate |
| Vídeo | HEVC (hvc1), perfil Main 10, `yuv420p10le` | stream 0 |
| Resolução armazenada | 3840x2160 | stream 0 |
| Rotação | tag `rotate: 270` e Display Matrix `rotation: 90` | stream 0 side_data |
| Resolução efetiva na tela | 2160x3840 (9:16 exato) | consequência da matriz de rotação |
| Taxa de quadros | `r_frame_rate 30/1`, média `430200/14341` | stream 0 |
| Quadros | 1434 | stream 0 nb_frames |
| Bitrate de vídeo | 50.366.882 bps | stream 0 |
| Cor | `bt2020nc` / primaries `bt2020` / transfer `arib-std-b67` (HLG) | stream 0 |
| Dolby Vision | perfil 8, nível 7, `bl_present_flag 1` | stream 0 side_data |
| Áudio | AAC LC, 48.000 Hz, estéreo, 196.546 bps, 2243 quadros | stream 1 |
| Streams extras | 5 streams de dados `mebx` (metadados do iPhone) | streams 2 a 6 |
| Câmera | Apple iPhone 15 Pro Max, software 26.5.2 | format.tags |
| Data de criação | 2026-07-29T03:46:54-03:00 | format.tags |

Dois pontos que mandam no resto do processo. O primeiro é que o vídeo é 9:16 nativo depois da rotação, então
cabe em 1080x1920 por escala pura, sem corte e sem distorção, que é exatamente o que a versão 2 faz. O segundo
é que a captura é HLG em BT.2020 com Dolby Vision, e por isso todo comando de extração aplica tonemapping para
BT.709 antes de qualquer coisa, senão a imagem sai lavada e sem contraste.

O arquivo também carrega metadados de localização do iPhone (`com.apple.quicktime.location.ISO6709`). Quem for
republicar o master fora daqui deve limpar os metadados antes.

### 2.2 A transcrição

O áudio foi extraído em MP3 mono 16 kHz para caber no limite de upload da API:

```bash
ffmpeg -y -v error -i fala-chefe.mp4 -vn -ac 1 -ar 16000 -c:a libmp3lame -b:a 64k .../fala-chefe.mp3
```

A transcrição saiu do Whisper da OpenAI, modelo `whisper-1`, com granularidade de palavra pedida explicitamente:

```bash
curl -s -w "\nHTTP:%{http_code}\n" https://api.openai.com/v1/audio/transcriptions \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -F file=@fala-chefe.mp3 \
 -F model=whisper-1 \
 -F language=pt \
 -F response_format=verbose_json \
 -F "timestamp_granularities[]=segment" \
 -F "timestamp_granularities[]=word" \
 -o whisper-raw.json
```

O JSON bruto virou `fala-chefe-transcricao.json` por cópia direta, sem edição. Estrutura conferida agora:
chaves `task`, `language`, `duration`, `text`, `segments`, `words`, `usage`. `task` é `transcribe`, `language`
é `portuguese`, `duration` é 47,79999923706055. São 10 segmentos e **139 palavras**, e cada item de `words` tem
apenas três campos: `word`, `start`, `end`, ou seja, tem timestamp por palavra, que é o que sustenta a legenda.
Os segmentos trazem os campos habituais do verbose (`tokens`, `avg_logprob`, `compression_ratio`,
`no_speech_prob`).

O texto reconhecido tem três erros de grafia que foram corrigidos depois na legenda, não no JSON: "Cloud Code"
no lugar de "Claude Code", "Cloud MD" no lugar de "CLAUDE.md" e a quebra de "4.5" em dois tokens "4" e "5".

O arquivo `fala-chefe-transcricao.md` (10.437 bytes) é a versão legível para leitura humana, escrita a partir
do JSON.

### 2.3 O site publicado

O site de origem é `https://instrucoes-opus5.denderson.ai/`, cujo projeto vive em
`/opt/naia-agent/workspace/instrucoes-opus5/`. O `build.py` de lá declara na docstring que monta o
`index.html` a partir do HTML da aula já publicada no painel de consultorias
(`/opt/naia-agent/workspace/tutorial-claude-md-opus5/build/tutorial-ablacao-claude-md.html`), sem reescrever
conteúdo, e fixa `BASE_URL = "https://instrucoes-opus5.denderson.ai"`.

Para o vídeo, o site foi baixado cru para dentro do job:

```bash
curl -s https://instrucoes-opus5.denderson.ai -o site.html
curl -s "https://instrucoes-opus5.denderson.ai/styles.css?v=505c1f6d55" -o styles.css
```

`site.html` tem 84.980 bytes e `styles.css` tem 28.060 bytes. Esses dois arquivos serviram para duas coisas:
extrair os números e títulos reais que aparecem nos gráficos e copiar os tokens de design em vez de inventar
paleta. O `manifest.json` registra isso de forma explícita em `design_tokens.origem`: "styles.css do proprio
site (nao inventado)".

### 2.4 Assets externos

O único material externo são quatro imagens do YouTube, detalhadas na seção 4.

---

## 3. O site virando matéria-prima visual

### 3.1 Primeiro passe: `capture_site.py`

O script (4.172 bytes) abre o site publicado com Playwright e recorta elemento por elemento. Parâmetros exatos,
lidos do arquivo:

* URL: `https://instrucoes-opus5.denderson.ai/`
* Navegador: Chromium via `playwright.sync_api`, com `--force-color-profile=srgb` e `--font-render-hinting=none`
* Viewport: 1920x1080, `device_scale_factor=2` (tudo sai em dobro, então 1 px de CSS vira 2 px de imagem)
* Locale `pt-BR`, `color_scheme="dark"`
* Navegação: `page.goto(URL, wait_until="networkidle", timeout=90000)`

Antes de qualquer recorte ele injeta um bloco de CSS chamado `FORCE_VISIBLE` que zera `animation-duration`,
`animation-delay`, `transition-duration` e `transition-delay` de tudo, força `opacity: 1`, `transform: none`,
`filter: none` e `visibility: visible` em `.reveal` e filhos, e troca `scroll-behavior` para `auto`. Em seguida
marca todos os `.reveal` com as classes que o site usa para considerar um bloco revelado
(`is-visible`, `in`, `visible`, `show`, `revealed`). Sem isso, os blocos com animação de entrada sairiam
translúcidos ou deslocados na captura.

Depois disso ele rola a página inteira de 600 em 600 px com pausa de 60 ms por passo, para disparar qualquer
IntersectionObserver e carregar conteúdo preguiçoso, volta ao topo, espera 2500 ms, chama `document.fonts.ready`
e espera mais 1500 ms. Só então captura.

Os treze alvos são casados por seletor CSS, e cada um vira um arquivo numerado:

| Arquivo | Seletor | Descrição no script |
|---|---|---|
| `01-hero.png` | `section.hero` | Hero completo |
| `02-player.png` | `section.videobox` | Área do player (fonte, vídeo do Boris) |
| `03-indice.png` | `nav.toc-wrap` | Índice dos 9 blocos |
| `04-bloco-1.png` a `11-bloco-8.png` | `#bloco-1` a `#bloco-8` | Um arquivo por bloco da aula |
| `12-bloco-9-download.png` | `#bloco-9` | Bloco do mapa para download |
| `13-download-cta.png` | `.dl-wrap` | Botão de download em close |

Cada captura faz `el.scroll_into_view_if_needed()`, espera 400 ms e chama `el.screenshot(path=...)`, guardando a
`bounding_box` no relatório JSON que o script imprime. No fim tira ainda a página inteira com
`page.screenshot(path=..., full_page=True)`, que virou `14-fullpage.png`.

### 3.2 Por que existiu um segundo passe: `capture_site_pass2.py`

A docstring do próprio arquivo diz o motivo, sem rodeio: "Passe 2: recaptura blocos e fullpage com a topbar
sticky escondida (na passagem 1 ela sobrepunha o conteudo no meio dos blocos altos)".

O que aconteceu é que o site tem uma barra fixa no topo. Como o Playwright rola até o elemento antes de
recortar, nos blocos mais altos que a janela a barra ficava carimbada no meio da imagem. Entre os dois passes
houve uma inspeção de CSS procurando exatamente por isso:

```bash
python3 - <<'PY'
import re
c=open('styles.css',encoding='utf-8').read()
for m in re.finditer(r'([^{}]+)\{[^{}]*position:\s*(fixed|sticky)[^{}]*\}',c):
    print("STICKY RULE:", m.group(1).strip()[:120], '->', m.group(2))
PY
```

O passe 2 é idêntico ao primeiro com uma linha a mais no CSS injetado, `.topbar { display: none !important; }`,
e refaz os doze blocos mais a página inteira, sobrescrevendo os arquivos ruins. A lista `TARGETS` do passe 2 não
inclui `01-hero.png`, e o carimbo de horário confirma que esse arquivo ficou como estava: 03:57, contra 03:58 e
03:59 de todos os outros (conferido com `find -printf '%T'`).

### 3.3 O que essas capturas viraram

As dimensões reais estão em `inventario.json`, gerado por um varredor Pillow que abriu cada arquivo:
`01-hero.png` é 3840x2760, `02-player.png` é 3840x1622, `14-fullpage.png` é 3840x37682 (6,1 MB), e os blocos
saem em 2032 px de largura por alturas de 2366 a 4968 px. Tudo em dobro por causa do `device_scale_factor=2`.

Na composição final essas capturas acabaram como material de consulta e reserva, não como quadro. O
`manifest.json` lista onze delas em `assets_reserva`, e no `index.html` do HyperFrames não há nenhuma
referência a `assets/site/`. O que entrou no vídeo a partir do site foram os dados e os textos: números,
títulos dos nove blocos, paleta e famílias tipográficas, todos redesenhados em HTML autoral para caber no
formato do vídeo. O `ROTEIRO-VISUAL.md` marca essa origem cena a cena na coluna "Asset / origem", com valores
como "HTML autoral · números do site" e "Títulos reais de `instrucoes-opus5.denderson.ai`".

---

## 4. O thumb do YouTube e a imagem do Boris

### 4.1 De onde vieram

As quatro imagens saíram do endpoint público de thumbnails do YouTube, em um único laço, às 03:55:45 BRT,
antes de qualquer outra coisa:

```bash
cd /opt/naia-agent/workspace/video-hyperframes-opus5/assets && \
for f in maxresdefault hqdefault sddefault maxres2; do
  curl -s -o "boris-$f.jpg" -w "$f: HTTP %{http_code} bytes=%{size_download}\n" \
    "https://img.youtube.com/vi/qyPCVqFUyDo/$f.jpg"
done
```

O ID `qyPCVqFUyDo` é o mesmo vídeo embutido no site: o `manifest.json` registra em `fontes_de_conteudo.palestra`
a URL `https://www.youtube.com/watch?v=qyPCVqFUyDo`, e a verificação do site feita mais cedo no dia mostra o
iframe `https://www.youtube-nocookie.com/embed/qyPCVqFUyDo?hl=pt-BR&rel=0` com título
"Boris Cherny: Stop Hobbling Your AI, palestra no Y Combinator".

Logo após o download, um script Pillow mediu o desvio padrão de cada arquivo para detectar aquele cinza chapado
que o YouTube devolve quando a resolução pedida não existe. As quatro passaram, e aí foram renomeadas:

```bash
mkdir -p boris && mv boris-maxresdefault.jpg boris/01-boris-thumb-oficial-1280x720.jpg \
 && mv boris-maxres2.jpg boris/02-boris-palco-yc-1280x720.jpg \
 && mv boris-sddefault.jpg boris/03-boris-thumb-sd-640x480.jpg \
 && mv boris-hqdefault.jpg boris/04-boris-thumb-hq-480x360.jpg
```

### 4.2 O que cada arquivo é, conferido agora

Medidas obtidas com `identify -format "%f %wx%h %m qualidade=%Q %b"` e com Pillow, e conteúdo conferido
visualmente em cópia reduzida:

| Arquivo | Origem | Dimensão | Formato | Peso | MD5 | Conteúdo |
|---|---|---|---|---|---|---|
| `01-boris-thumb-oficial-1280x720.jpg` | `maxresdefault.jpg` | 1280x720 | JPEG q90 | 303.363 B | `c58d0b85dda797989dc2cdeb04859a56` | A capa oficial: fundo laranja, foto do Boris, texto "In conversation with Boris Cherny", "Head of Claude Code, Anthropic" e o selo "Y Startup School 2026" |
| `02-boris-palco-yc-1280x720.jpg` | `maxres2.jpg` | 1280x720 | JPEG q89 | 40.121 B | `af589acf64a91878348f59c1bc9265f3` | Um quadro real da entrevista: Boris sentado em poltrona, moletom azul-marinho, microfone de lapela, mão erguida gesticulando, fundo escuro de palco com o "Y" no canto |
| `03-boris-thumb-sd-640x480.jpg` | `sddefault.jpg` | 640x480 | JPEG q90 | 80.431 B | `5236d6b6e0db83318b865fa769021b09` | Mesma capa oficial em 4:3 com tarjas |
| `04-boris-thumb-hq-480x360.jpg` | `hqdefault.jpg` | 480x360 | JPEG q50 | 17.743 B | `9da583d1decb1c6b9e1d52a99ae653e5` | Mesma capa oficial, resolução baixa |

Para provar que a 01 e a 02 são imagens diferentes de fato, e não a mesma em tamanhos diferentes, medi as duas
em escala reduzida: brilho médio 126,0 contra 39,8, e diferença média por canal de 99,2 em 255. A 02 é a imagem
escura de palco.

Vale registrar o que ela **não** é: `maxres2.jpg` é a segunda thumbnail que o próprio YouTube expõe para o
vídeo. Não foi extraída do vídeo por `ffmpeg`, não foi recortada de screenshot e não passou por edição nenhuma.

### 4.3 Tratamento

Nenhum dos quatro arquivos foi recortado, redimensionado ou recomprimido. A prova é o MD5: as cópias dentro do
projeto HyperFrames batem byte a byte com os originais em `assets/boris/`.

```bash
cp ../assets/boris/01-boris-thumb-oficial-1280x720.jpg assets/boris-thumb.jpg   # 04:08
cp ../assets/boris/02-boris-palco-yc-1280x720.jpg      assets/boris-palco.jpg   # 04:12
cp assets/boris-thumb.jpg assets/boris-thumb-b.jpg                              # 04:18
```

`boris-thumb-b.jpg` é uma cópia idêntica de `boris-thumb.jpg` (mesmo MD5 `c58d0b85...`). Ela existe porque a
mesma capa aparece em duas cenas com animações diferentes, e o HyperFrames trata cada `<img>` como um elemento
próprio na timeline. Duplicar o arquivo evita que o dedup de quadros estáticos confunda os dois usos.

Todo o tratamento visual foi feito em CSS na hora do render, não no arquivo. No `index.html`:

* `.shot img { width: 100%; height: 100%; object-fit: cover; }` para a capa, dentro de `#s01shot { height: 520px; }`
* `.bgshot img { ... filter: brightness(0.62) saturate(0.8); }` para a foto de palco, que entra como fundo escurecido

### 4.4 Onde cada uma aparece no vídeo

Pelo `index.html` (marcação e timeline GSAP) cruzado com o `ROTEIRO-VISUAL.md`:

* **S01, de 0,00 s a 4,84 s**, `boris-thumb.jpg`. A capa ocupa o quadro e faz push-in: entra com
  `scale 1.14 → 1` em 1,1 s e depois vai de `1 → 1.06` por 3,6 s. Em 1,62 s um traço coral risca o "4.5"
  (`#s01strike`, `scaleX 0 → 1` em 0,3 s) e em 1,86 s o "5" entra em escala com `expo.out`.
* **S04, de 11,50 s a 14,54 s**, `boris-thumb-b.jpg`. A mesma capa volta menor com o crédito
  "BORIS CHERNY / criador do Claude Code · Y Combinator". Entra com `scale 1.09 → 1` em 0,9 s a partir de 11,6 s.
* **S05, de 14,54 s a 17,62 s**, `boris-palco.jpg`. O quadro da entrevista entra como fundo escurecido, com
  `scale 1.12 → 1.0` em 3,3 s, e por cima vai a citação "Stop Hobbling Your AI", a tradução e a assinatura
  "Boris Cherny · Y Combinator".

O `DESIGN.md` do projeto registra a regra editorial que amarra isso: a fonte é creditada como "Boris Cherny ·
criador do Claude Code · Y Combinator", e as palavras "entrevista" e "palestra" não aparecem em quadro nenhum,
para o vídeo não contradizer a legenda do site.

O frame de prova da abertura está em
`entrega/frames/01-t03.60s-abertura-thumbnail-boris-opus45-para-5.png` (1080x960, 995.127 bytes).

---

## 5. `graficos.html` e `render_graficos.py`

### 5.1 O que é

`graficos.html` (24.647 bytes) é um documento único com dezesseis cartões, `#g01` a `#g16`, cada um desenhado no
tamanho exato da metade de baixo do vertical. A regra base do arquivo:

```css
.card{
  width:1080px; height:960px; background:var(--bg); color:var(--ink);
  padding:64px 72px; display:flex; flex-direction:column; position:relative;
  overflow:hidden;
}
```

Os tokens são cópia do site, declarados no `:root` do próprio arquivo: `--bg:#050505`, `--surface:#0d0d10`,
`--surface-2:#131317`, `--line:rgba(255,255,255,.09)`, `--ink:#ededed`, `--ink-soft:#b6b6b6`,
`--ink-faint:#7f7f7f`, `--coral:#d97757`, `--coral-soft:#e79274`, `--coral-press:#b85c40`.

As quatro famílias vêm do Google Fonts por `<link>`, com os eixos declarados na própria URL:
`Bricolage Grotesque` (opsz 12..96 nos pesos 400, 600, 700 e 800), `Inter` (400 a 700), `JetBrains Mono`
(400, 500, 700) e `Newsreader` (itálico e romano, opsz 6..72). O papel de cada uma segue o `DESIGN.md`:
Bricolage para número e título, Inter para corpo, JetBrains Mono para rótulo em caixa alta com tracking
largo, Newsreader itálico só para citação.

Cada cartão tem a mesma anatomia: um `.eyebrow` em mono com um traço coral de 44x2 px antes do texto, um
`.body` que centraliza o conteúdo e um `.foot` com borda superior de 1 px. Os números-herói usam
`.big { font-family: var(--font-display); font-weight: 800; line-height: .84; letter-spacing: -.035em }`,
e o par antes e depois usa `.duo .n { font-size: 150px }` com `.delta { font-size: 88px; color: var(--coral) }`.

Os dezesseis assuntos, pelos nomes de arquivo definidos em `render_graficos.py`: 498 para 108 linhas,
composição do arquivo, 54,8 por cento cortável, redundância contra modelo antigo, 80 por cento da Anthropic
contra 81 nosso, tokens de 9.692 para 1.832, a ironia dos 10.482 tokens, teto de 200 contra 498, critério de
2 sessões, método de 8 passos, uma entrada e quatro saídas, seis que nunca saem, escada contra tríade,
4 de 136 skills, seis erros em 30 linhas e o endcard com a URL do site.

### 5.2 Como virou imagem

`render_graficos.py` (2.140 bytes) abre o HTML local no Chromium e recorta cartão por cartão:

```python
SRC = "file:///opt/naia-agent/workspace/video-hyperframes-opus5/graficos.html"
ctx = b.new_context(viewport={"width": 1080, "height": 960}, device_scale_factor=2, locale="pt-BR")
page.goto(SRC, wait_until="networkidle", timeout=60000)
page.evaluate("() => document.fonts.ready")
page.wait_for_timeout(2000)
```

Rodado com `timeout 180 python3 render_graficos.py`. Como o viewport é 1080x960 e o `device_scale_factor` é 2,
cada PNG sai em **2160x1920**, que é a metade de baixo em dobro. O `manifest.json` explica a decisão em
`formato_alvo.observacao`: "todo grafico foi desenhado no canvas 1080x960 e renderizado a 2x (2160x1920) para
permitir zoom/pan sem perder nitidez".

O script também mede overflow dentro de cada cartão antes de salvar, comparando `scrollHeight` com
`clientHeight` e `scrollWidth` com `clientWidth`, e devolve isso no JSON de saída. Foi esse medidor que
disparou a rodada de ajuste de tipografia às 04:03, quando nove regras de tamanho de fonte foram aumentadas de
uma vez em `graficos.html` (por exemplo `.legend .lb` de 22 para 25 px, `.six .c .t` de 30 para 34 px,
`.vs .q` de 31 para 33 px), cada substituição protegida por `assert a in s`.

O cartão `g16` foi criado depois dos outros quinze: às 04:04 o dicionário `NAMES` de `render_graficos.py`
ganhou a linha `"g16": "g16-endcard-url-do-site"` e o script rodou de novo.

As dimensões finais estão em `inventario.json`: os dezesseis arquivos em `assets/graficos/` são todos
2160x1920, pesando de 100,3 KB (`g02`) a 218,5 KB (`g12`).

### 5.3 O destino desses PNGs

Aqui vale a mesma ressalva do site. Os dezesseis infográficos foram desenhados como assets de cena e estão
listados no `manifest.json`, mas na montagem final o HyperFrames não carrega nenhum deles: as cenas equivalentes
foram redesenhadas direto em HTML animado dentro do `index.html`, para que barra, número e cartão pudessem
crescer com GSAP em vez de aparecer como imagem estática. `grep "assets/" video/index.html` só devolve as três
imagens do Boris. Os PNGs continuam no repositório como referência de arte aprovada e como material pronto para
carrossel ou post estático.

---

## 6. O render no HyperFrames

### 6.1 Versão e projeto

A CLI usada é a **0.7.64**, pinada em todos os comandos e também no `package.json` gerado
(`"render": "npx --yes hyperframes@0.7.64 render"`). O projeto nasceu às 04:07:

```bash
cd /opt/naia-agent/workspace/video-hyperframes-opus5 && \
timeout 400 npx --yes hyperframes@0.7.64 init video --non-interactive --example blank
```

Isso criou `video/` com `index.html`, `hyperframes.json`, `package.json`, `meta.json`, `CLAUDE.md` e `AGENTS.md`.
O `meta.json` marca `"createdAt": "2026-07-29T07:07:27.148Z"`, que é 04:07:27 BRT. O `hyperframes.json` aponta
o registry oficial e liga `media.autoProxy`.

### 6.2 O papel do `manifest.json`

Este ponto costuma confundir, então vale ser exato: `manifest.json` **não** é o arquivo que o HyperFrames lê.
Ele é o manifesto do job, escrito às 04:05, antes de a gravação existir na montagem, e serve como contrato
entre as frentes. Sua estrutura:

* `projeto` e `estado`, com o valor `"FASE DE ASSETS - video nao montado"` congelado no momento em que foi escrito.
* `formato_alvo`, que fixa 1080x1920 para o final, gravação do Chefe na metade de cima e composição HyperFrames
  em 1080x960 na metade de baixo, mais a justificativa do render em dobro.
* `fontes_de_conteudo`, com os quatro endereços de origem: o site, o dossiê de apuração
  (`tutorial-claude-md-opus5/APURACAO.md`), o HTML da aula e a URL do vídeo do Boris.
* `design_tokens`, com as dez cores e as quatro fontes copiadas do `styles.css` do site.
* `roteiro_visual_proposto`, uma lista de **20 cenas**, cada uma com `cena`, `dur_s`, `nome`, `asset` e
  `direcao`. As durações somam 93 s e são explicitamente estimativas.
* `assets_reserva`, com catorze caminhos.
* `pendencia_bloqueante`, que diz com todas as letras: "a gravacao do Chefe (metade de cima). As duracoes acima
  sao estimativa de ritmo e serao remapeadas contra os timestamps da fala real".

Foi exatamente isso que aconteceu. Quando a transcrição ficou pronta, as 20 cenas estimadas viraram **15 cenas**
ancoradas em palavra falada, e o resultado está documentado em `ROTEIRO-VISUAL.md` e implementado no
`video/index.html`. Comparando os dois arquivos: o manifesto abria em thumbnail do Boris por 4 s de estimativa,
o roteiro final abre em thumbnail por 4,84 s porque "versão 5" cai em 1,58 s a 2,04 s da fala real.

### 6.3 A composição

`video/index.html` tem 665 linhas hoje (a primeira versão completa foi escrita às 04:18 com 43.965 caracteres).
A estrutura segue o contrato do HyperFrames descrito no `CLAUDE.md` do projeto:

```html
<div id="root" data-composition-id="main" data-start="0" data-duration="47.8"
     data-width="1080" data-height="960">
```

Cada cena é uma `<section class="clip">` com `data-start`, `data-duration` e `data-track-index`, e a timeline
GSAP é criada pausada e registrada no fim do arquivo:

```js
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({ paused: true });
...
window.__timelines["main"] = tl;
```

São 15 cenas mais dois elementos de flash (`#flash1` em `data-start="17.5"` e `#flash2` em
`data-start="27.24"`, ambos com `data-duration="0.4"` na trilha 9). O crossfade padrão está declarado numa
constante, `const X = 0.3`, e nos dois cortes pesados o crossfade é substituído pelo flash coral, como registra
o `DESIGN.md`: "flash coral de 0,12 s no lugar do crossfade, para o corte doer".

As âncoras de cada cena, com início, fim e justificativa contra a fala, estão na tabela cena a cena do
`ROTEIRO-VISUAL.md`. Os cortes: 4,84 / 8,40 / 11,50 / 14,54 / **17,62 (flash)** / 20,50 / 24,42 /
**27,36 (flash)** / 32,42 / 35,60 / 38,60 / 42,20 / 44,20 / 46,60.

O GSAP vem por CDN: `https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js`.

### 6.4 Os renders

Primeiro um render de fumaça com 60 quadros para validar o ambiente:

```bash
npx --yes hyperframes@0.7.64 render --output renders/smoke.mp4 --quality draft
```

Depois três rascunhos completos, cada um seguido de extração de quadros para conferência visual:

```bash
npx --yes hyperframes@0.7.64 render --output renders/apoio-v1.mp4 --quality draft   # 4.7 MB, 47.8s, 52.0s de render
npx --yes hyperframes@0.7.64 render --output renders/apoio-v2.mp4 --quality draft   # 4.7 MB, 47.8s, 55.9s
npx --yes hyperframes@0.7.64 render --output renders/apoio-v3.mp4 --quality draft   # 4.7 MB, 47.8s, 56.0s
```

O `check` completo rodou às 04:28 e voltou com 0 erros e 3 avisos de estilo (arquivo de composição grande,
trilhas 1 e 2 densas), mais quatro achados de layout em nível informativo que dispararam correções reais,
descritos na seção 12.

O render de entrega da faixa:

```bash
npx --yes hyperframes@0.7.64 render --output renders/apoio-metade-baixo-1080x960.mp4 --quality high --fps 30
# saída da CLI: 13.2 MB · 47.8s video · rendered in 59.4s
```

Esse comando rodou duas vezes, às 04:29 e às 04:34, a segunda depois da correção do `immediateRender` e da
reconstrução do clímax S09. O resultado foi copiado para `entrega/` e conferido:

```bash
ffprobe -v error -show_entries stream=... entrega/apoio-metade-baixo-1080x960.mp4
# 1080x960, 30/1 fps, 1434 quadros, 47,80 s, yuv420p, nb_streams=1 (sem áudio)
```

A ausência de áudio é proposital e está registrada no `DESIGN.md`: "30 fps, 47,80 s, sem áudio (o áudio é a voz
do Chefe no vídeo de cima)".

Um último render da faixa aconteceu às 04:57, depois da remoção da URL, gerando `renders/apoio-v2.mp4`
(8.590.337 bytes), que é a faixa que entrou nas duas versões finais.

---

## 7. A composição final em ffmpeg, versão 1 (a que foi reprovada)

Esta é a parte que mais interessa, então vai em detalhe, incluindo o erro.

### 7.1 O que a v1 fez com a gravação

Às 04:57 o topo foi renderizado em separado, em segundo plano:

```bash
TM="zscale=t=linear:npl=100,format=gbrpf32le,tonemap=tonemap=hable:desat=0,zscale=p=bt709:t=bt709:m=bt709:r=tv,format=yuv420p"
nohup ffmpeg -y -v warning -stats -i "$SRC" -an -filter_complex \
"[0:v]fps=30,split=2[s1][s2];\
 [s1]scale=720:1280:flags=lanczos,$TM[fg];\
 [s2]scale=270:480:flags=bilinear,$TM,crop=270:240:0:30,gblur=sigma=12,eq=brightness=-0.32:saturation=0.5,scale=1080:960:flags=bicubic[bg];\
 [bg][fg]overlay=180:0[out]" \
 -map "[out]" -frames:v 1434 -c:v libx264 -crf 14 -preset medium -pix_fmt yuv420p -threads 6 \
 topo-1080x960.mp4 > topo_render.log 2>&1 &
```

Traduzindo o que isso produz: a gravação vira uma cópia pequena de 720x1280 e é colocada em `x=180` sobre um
fundo feito da própria imagem, borrada com `gblur=sigma=12` e escurecida com `eq=brightness=-0.32:saturation=0.5`,
num canvas de 1080x960. Como o quadro colado tem 720 px de largura, sobram 180 px de cada lado ocupados só pelo
borrão escuro, e como ele tem 1280 px de altura num canvas de 960, os 320 px de baixo ficam fora.

O resultado é a moldura que o Chefe reprovou. O arquivo ainda está no disco:
`work/topo-1080x960.mp4`, 129.862.302 bytes, e o log do encode em `work/topo_render.log` termina com
`frame= 1434 ... Lsize= 126819kB time=00:00:47.70 bitrate=21779.8kbits/s`.

O áudio foi extraído sem recodificar, para não perder qualidade:

```bash
ffmpeg -y -v error -i fala-chefe.mp4 -vn -c:a copy work/audio-chefe.m4a   # 1.185.404 bytes
```

Antes desse render houve uma bateria de testes de enquadramento, que ficou guardada em `work/`. As opções
comparadas foram A (corte de cobertura a partir do topo), B (corte com deslocamento `y=240`), C (encaixe pela
altura com fundo desfocado) e D (híbrido com o quadro em 660 px de largura), montadas lado a lado em
`work/contact_framing.png`. Também houve teste de tonemapping: `work/tm_none.png`, `work/tm_hable.png` e
`work/tm_mobius.png`, comparados em `work/contact_tm.png`, e uma verificação de que aplicar o tonemap depois do
`scale` dá o mesmo resultado e roda mais rápido (`work/fast_tm.png`).

### 7.2 A montagem v1

```bash
ffmpeg -y -v warning -stats \
 -i topo-1080x960.mp4 \
 -i .../video/renders/apoio-v2.mp4 \
 -framerate 30 -i caps/cap_%05d.png \
 -i audio-chefe.m4a \
 -filter_complex "[0:v][1:v]vstack=inputs=2[base];[base][2:v]overlay=0:650:format=yuv444[ov];[ov]format=yuv420p[v]" \
 -map "[v]" -map 3:a \
 -c:v libx264 -crf 22 -preset slow -profile:v high -level 4.1 -x264-params keyint=60:min-keyint=30 \
 -c:a aac -b:a 192k -ar 48000 -ac 2 \
 -movflags +faststart -r 30 \
 .../entrega/video-final-opus5-1080x1920.mp4
```

O empilhamento é `vstack`, ou seja, dois quadros de 1080x960 viram um de 1080x1920 sem escalar nada. A legenda
entra como sequência de PNG com alfa, sobreposta em `y=650`.

O CRF passou por três valores até fechar. Com `-crf 18` o arquivo saiu com 72.411 kB segundo
`work/final_render.log`. Com `-crf 20`, 51.510.040 bytes. Com `-crf 22`, 34.588.697 bytes, que é a faixa que
cabe no Telegram sem recompressão.

### 7.3 Um erro silencioso: o áudio truncado

O primeiro fechamento incluía `-frames:v 1434` junto do `-map 3:a`. O `ffprobe` do arquivo gerado mostrava
`AUDIO: aac 2ch 48000Hz dur=45.141000`, ou seja, o áudio parava em 45,14 s num vídeo de 47,80 s, porque a
contagem de quadros encerrava o mux antes de o áudio terminar. O comando foi refeito às 05:04 sem `-frames:v`
e o probe passou a mostrar `audio,47.806000,2242`.

O arquivo final da v1 tem 34.654.057 bytes, vídeo H.264 High 1080x1920 a 30 fps com 1434 quadros e 5.597.970
bps, e áudio AAC LC estéreo 48 kHz a 192.807 bps.

### 7.4 A reprovação

Às 05:17:44 o Chefe respondeu, mensagem 13307, texto integral:

> "Vc cortou o video errado! Seu trabalho é só queimar o hyperframe em cima do original, Vai ocupar a parte de
> baixo da tela e a parte de cima fica certinho onde está meu rosto! Mas vc colocou o video dentro de uma
> moldura com faixas pretas aos lados, corrija"

---

## 8. A versão 2, aprovada

### 8.1 Como a medida foi decidida, e não chutada

Antes de refazer o comando, três coisas foram medidas.

**Onde fica o rosto.** `work/v3/measure.py` extrai o vídeo já tonemapeado em escala 1:4 (270x480), amostra 2
quadros por segundo e, para cada amostra, procura na faixa central `x` de 260 a 820 a última linha em que pelo
menos 35 por cento dos pixels passam de luma 62, que é o fim da massa de cabeça, barba e pescoço. Resultado
registrado da execução:

```
amostras=96  (48.0s)
mediana=1124  p90=1252  p95=1323  max=1696
acima de 1120: 53/96
acima de 1200: 15/96
acima de 1280: 7/96
```

Traduzindo para a decisão: uma faixa de 960 px de altura começaria em `y=960` e cortaria a cabeça em 53 das 96
amostras. Uma faixa de 720 px começa em `y=1200` e reduz esse número para 15. Foi por isso que a faixa encolheu
de 960 para 720 de altura. A mensagem de entrega ao Chefe cita o pior caso observado, por volta dos 46 s, com
a boca aberta.

Houve ainda uma varredura de rosto independente com OpenCV, em `work/v2/facescan.py`, usando os classificadores
Haar frontal e de perfil sobre 4 quadros por segundo extraídos em `work/v2/fd/`.

**Se dava para cortar a faixa em vez de reduzir.** Uma análise sobre os 1434 quadros da faixa mediu a caixa
ocupada por conteúdo e testou todas as janelas de 720 px:

```
conteudo real (sem flash): ymin=0  ymax=960  altura=960
melhor janela de 720: y=52..772  306/1434 frames intactos
```

Ou seja, cortar 720 px de qualquer lugar preservaria só 306 dos 1434 quadros. Cortar estava fora, e o caminho
passou a ser reduzir proporcionalmente.

**Como preencher a largura.** Reduzir 1080x960 para 720 de altura dá 810 de largura (fator 0,75 exato nos dois
eixos), sobrando 135 px de cada lado. `work/v3/pads.py` montou três opções lado a lado em
`work/v3/pads_sheet.png`: A0 com cor chapada `#040404`, A1 com a coluna de borda replicada e A2 com cobertura
desfocada. Venceu a A1, porque o fundo da faixa é quase preto uniforme e a replicação da coluna de borda faz o
flash coral e a sangria continuarem cobrindo a largura inteira, sem barra visível.

### 8.2 O comando final

Está inteiro em `work/v3/render.sh`, que é o script de verdade da entrega:

```bash
TM="zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv"

ffmpeg -hide_banner -y \
  -i "$BASE/fala-chefe.mp4" \
  -i "$BASE/entrega/apoio-metade-baixo-1080x960.mp4" \
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
  -c:a copy \
  -movflags +faststart \
  "$OUT"
```

Camada por camada:

1. **`[base]`**: a gravação sai do HLG BT.2020 para BT.709 pelo tonemap `hable` com `desat=0`, e só então é
   escalada para 1080x1920 com Lanczos. Como o original é 2160x3840 depois da rotação, isso é redução exata pela
   metade, sem corte e sem mudança de proporção. A gravação ocupa a tela inteira.
2. **A faixa**: `scale=810:720` reduz a faixa inteira proporcionalmente, sem cortar nada. O `split=3` cria três
   cópias; de duas delas se recorta 1 px de largura (`crop=1:720:0:0` e `crop=1:720:809:0`) e cada tirinha é
   esticada para 135 px. O `hstack=inputs=3` cola borda esquerda, faixa e borda direita, fechando os 1080.
3. **A rampa**: `ramp.png` é um PNG estático de 1080x240 com alfa, colocado em `y=960`. Ele preenche a zona
   entre `y=960` e `y=1200` com `#040404` numa curva de opacidade `t^2.2`, de transparente no topo até opaco
   encostando na faixa, para a emenda não aparecer.
4. **A legenda**: os PNGs `caps/cap_%05d.png` entram em `y=900`.
5. **O `tpad=stop_mode=clone:stop_duration=1`** repete o último quadro da faixa e da legenda por 1 s a mais,
   detalhe explicado na seção 12.
6. **Áudio**: `-c:a copy`. O áudio original passa intacto, sem recodificação.

O `ffprobe` do resultado: 1080x1920, H.264 High, `yuv420p`, `bt709` nos três campos de cor, 30/1 fps, 1434
quadros, 47,80 s de vídeo e 47,80 s de áudio, vídeo a 21.005.216 bps, áudio AAC 196.754 bps, arquivo com
126.735.884 bytes.

### 8.3 Verificação de que a correção pegou

`work/v3/audit.py` amostra 24 instantes ao longo dos 47,8 s e testa três coisas, comparando o render contra a
fonte tonemapeada na mesma escala:

```
video: dif media=2.75  pior=3.14  (so compressao h264)
pad  : dif media=0.00  pior=0.09  (0 = replicacao perfeita)
coluna mais escura do frame inteiro, pior caso=23.6 (barra preta daria ~0 em todos os frames)
```

A primeira linha prova que a região `y=0..950` do resultado é a gravação original, com diferença compatível só
com compressão. A segunda prova que os 135 px de cada lado acompanham a coluna de borda. A terceira prova que
não existe coluna preta em lugar nenhum do quadro, que era a queixa do Chefe.

---

## 9. A legenda queimada palavra por palavra

Pedido do Chefe, mensagem 13298 às 04:41:18, texto integral:

> "termine o video, legenda fonte bricolage grotesque acima da faixa hyperframe.. colada na hyperframe...
> palavra por palavra a legenda com palavras chave destacadas com a cor laranja do logo do claude"

O gerador é `work/gen_captions.py` na versão 1 e `work/v3/gen_captions_v2.py` na versão 2. Os dois produzem
uma sequência de PNGs RGBA com Pillow, não usam `drawtext` do ffmpeg.

### 9.1 De onde saem os tempos

Da própria transcrição, declarado no cabeçalho do script: "Fonte de verdade dos tempos:
fala-chefe-transcricao.json (words[] do Whisper)". O código lê
`json.load(open(f"{BASE}/fala-chefe-transcricao.json"))["words"]`.

Três camadas de correção foram aplicadas por cima do Whisper:

* **`MERGE`**, para juntar tokens que o Whisper quebrou: índice 23 vira `"4.5"` fundindo 23 e 24, índice 55 vira
  `"CLAUDE.md"` fundindo 55 e 56.
* **`FIX`**, para corrigir grafia: índices 41 e 42 viram `"Claude"` e `"Code"` no lugar de "Cloud Code".
* **`ONSET`**, para corrigir três palavras que o Whisper marcou tarde: `{76: 27.06, 108: 37.56, 109: 38.66}`.
  O comentário do código explica o método: "medido no envelope RMS do proprio audio: silencio nitido seguido de
  ataque forte". A medição foi feita em janelas de 25 ms com passo de 10 ms sobre PCM mono 16 kHz extraído do
  original, com limiar de -32 dBFS, e o resultado ficou salvo em `work/db.npy` (38.352 bytes).

As 139 palavras foram agrupadas em **40 blocos** de legenda, declarados na lista `CHUNKS` por intervalo de
índices, do `(0, 2)` ao `(135, 138)`. Dentro de um bloco, as palavras acendem uma a uma no `start` de cada uma;
a primeira palavra de cada bloco acende no início do bloco.

### 9.2 Tipografia

Arquivo de fonte: `/home/naia/.fonts/BricolageGrotesque.ttf`, 408.496 bytes. Conferido com `fc-scan` e com
Pillow: é uma fonte variável com três eixos, Optical size de 12 a 96, Weight de 200 a 800 e Width de 75 a 100.

```python
FONT_SIZE = 58
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
font.set_variation_by_axes([96, 800, 100])   # opsz 96 / wght 800 (ExtraBold) / wdth 100
```

A saída da execução registra as métricas resultantes: `ascent=54 descent=16 line_h=78 space_w=15.9`. O espaço
entre palavras é o espaço da fonte multiplicado por 1,35, e a largura máxima de texto é 950 px dentro de uma
banda de 1080. O layout quebra em no máximo duas linhas procurando o corte que deixa as duas mais parecidas em
largura, e na prática a saída informa `blocos com 2 linhas: 0`, ou seja, todos os quarenta blocos couberam em
uma linha só. As três linhas mais largas foram "e não tendo nenhum resultado" com 802 px, "Eu duvidei por um
minuto" com 668 px e "deletar o seu CLAUDE.md" com 661 px.

Cada estado é desenhado em três passadas para o texto sobreviver a qualquer fundo: sombra deslocada 5 px para
baixo com contorno de 8 px, desfoque gaussiano de raio 7 e alfa reduzido a 62 por cento; contorno preto de
`STROKE_W = 5` px com alfa 225 nas palavras acesas e 130 nas apagadas; e por fim o preenchimento.

### 9.3 As palavras em laranja

A cor é `CORAL = (217, 119, 87)`, com o comentário `# #d97757 - laranja do logo do Claude`, o mesmo valor do
token `--coral` do site e do `DESIGN.md`.

A regra de pintura está em três linhas:

```python
aceso = i <= lit
cor = (CORAL if kw else WHITE) if aceso else WHITE
a = 255 if aceso else DIM_ALPHA        # DIM_ALPHA = 105
```

Palavra ainda não falada aparece branca com alfa 105. Quando acende, vira branca opaca se for palavra comum, ou
coral opaca se estiver no conjunto `KEYWORDS`. O conjunto tem 28 índices, comentados um a um no código: Opus,
versão 5, versão 4.5, tempo, dinheiro, resultado, Boris, Claude Code, deletar, CLAUDE.md, executei, Opus 5,
10 vezes, IA, passo a passo, resetar, melhor modelo.

### 9.4 Posição em relação à faixa

Aqui está a diferença entre as duas versões, e é a diferença que atende ao "colada na hyperframe".

| | v1 (`work/gen_captions.py`) | v2 (`work/v3/gen_captions_v2.py`) |
|---|---|---|
| Tamanho da banda PNG | 1080x300 | 1080x300 |
| Overlay no canvas | `y=650` | `y=900` |
| `BASELINE_BOTTOM` na banda | 295 | 270 |
| Base do texto no canvas | `y=945` | `y=1170` |
| Topo da faixa | `y=960` | `y=1200` |
| Folga entre texto e faixa | 15 px | 30 px |
| Escurecimento de fundo | gradiente dentro do próprio PNG da legenda | rampa separada, `ramp.png` |

A saída da execução da v2 confirma tudo de uma vez:

```
banda y=900..1200 | bottom do texto y=1170 | faixa comeca em y=1200 (folga 30 px)
rampa: y=960..1200 (240px) cor #040404, curva t^2.2
blocos=40 estados_unicos=129 frames=1434
```

Por eficiência o gerador desenha só os **129 estados únicos** e cria os 1434 quadros como links simbólicos
apontando para o estado correspondente (`os.symlink`), o que dá uma pasta `caps/` com 1563 entradas e poucos
megabytes. Conferido agora: `work/v3/caps` tem 129 arquivos `state_*` e 1434 `cap_*`.

Uma verificação independente mediu o pixel mais baixo com alfa diferente de zero em todos os 129 estados:

```
linha mais baixa com pixel de legenda: 292 na banda -> y=1192 no canvas
topo da faixa: y=1200  ->  folga = 8 px  (estado state_004_00.png)
sobrepoe a faixa? NAO
```

Ou seja, no pior estado a legenda chega a 8 px da faixa e nunca invade.

### 9.5 Como a legenda entra no vídeo

Não há filtro de texto no ffmpeg. A sequência de PNGs entra como entrada de vídeo e é sobreposta:

```bash
-framerate 30 -start_number 0 -i "$V3/caps/cap_%05d.png"
...
[b2][caps]overlay=0:900:eof_action=pass,format=yuv420p[vout]
```

---

## 10. Verificação adversarial da URL removida

Às 04:47:26 o Chefe pediu, mensagem 13300:

> "unico detalhe é que no ultimo frame do video vc colocou o link do site, deve colocar só o cta, o link só
> vamos mandar no direc"

A URL foi retirada do `index.html` em quatro edições cirúrgicas às 04:55: saiu o `<div class="urlbox"
id="s14url">instrucoes-opus5.denderson.ai</div>` da cena S14, saiu o `#s15url` do fecho, e saíram as duas linhas
de timeline que animavam esses elementos. A faixa foi renderizada de novo, virando `renders/apoio-v2.mp4`.

A prova de que sumiu não foi feita por leitura de código. `work/varredura_url.py` recorta dois gabaritos da
faixa antiga, que tinha a URL, e roda casamento de template (`cv2.TM_CCOEFF_NORMED`, limiar 0,70) sobre todos os
1434 quadros dos dois vídeos, usando o antigo como controle positivo. Resultado registrado:

```
template A (S14): 780x56   contraste std=42.7
template B (S15): 605x34   contraste std=41.4

--- CONTROLE POSITIVO: faixa ANTIGA (tinha a URL) (1434 frames) ---
score maximo em todo o video: 1.000
frames acima do limiar 0.7: 65
   URL DETECTADA de t=45.17s a t=46.77s (frames 1355-1403)
   URL DETECTADA de t=47.27s a t=47.77s (frames 1418-1433)

--- ENTREGA: video final 1080x1920 (1434 frames) ---
score maximo em todo o video: 0.409
frames acima do limiar 0.7: 0

VEREDITO: detector funciona (achou no antigo) e NAO ha URL no video final.
```

A faixa antiga foi preservada em `work/apoio-v1-COM-URL-backup.mp4` (13.835.411 bytes) justamente para servir de
controle, e os dois gabaritos ficaram guardados em `entrega/frames-final/prova-template-URL-usado-na-varredura-S14.png`
e `...-S15.png`.

---

## 11. Entregáveis e pesos

Estado atual de `entrega/`, medido com `du -b`:

| Arquivo | Bytes | O que é |
|---|---|---|
| `video-final-v2-1080x1920.mp4` | 126.735.884 (120,9 MiB) | **Master aprovado.** Gravação em tela cheia, faixa queimada embaixo, legenda, áudio copiado do original |
| `video-final-opus5-1080x1920.mp4` | 34.654.057 (33,0 MiB) | Versão 1, reprovada, com a gravação dentro de moldura |
| `apoio-metade-baixo-1080x960.mp4` | 8.590.337 (8,2 MiB) | Só a faixa do HyperFrames, sem áudio, entregue antes ao Chefe |
| `frames/` | 7 PNGs | Provas da faixa: composição 9:16 em 1080x1920 mais seis quadros-chave em 1080x960 |
| `frames-final/` | 10 PNGs | Provas da versão 1, incluindo o último quadro só com CTA e os gabaritos da varredura |
| `frames-v2/` | 6 PNGs | Provas da versão 2 em 2, 9, 18, 30, 34 e 46 s, todos 1080x1920 |

Também vive em `work/` o material intermediário pesado: `topo-1080x960.mp4` com 129.862.302 bytes (o topo
emoldurado da v1), `apoio-v1-COM-URL-backup.mp4` com 13.835.411 bytes e `audio-chefe.m4a` com 1.185.404 bytes.

### Por que existiu uma versão reduzida para o Telegram

O master da v2 tem 120,9 MiB, e o bot do Telegram não envia arquivo desse tamanho (a Bot API limita o upload a
50 MB). A saída foi uma recompressão só para transporte:

```bash
ffmpeg -v error -y -i video-final-v2-1080x1920.mp4 \
  -c:v libx264 -preset slow -crf 24 -c:a copy -movflags +faststart /tmp/video-final-v2-telegram.mp4
# saída registrada: 38.8 MB · 1080x1920 · 47.800000 s
```

Repare que o áudio continua copiado, e só o vídeo foi recomprimido, de CRF 18 para CRF 24. A mensagem de entrega
deixou isso explícito para o Chefe: "O arquivo original ficou em 126 MB, acima do limite do Telegram, então
mandei uma cópia em qualidade alta de 38 MB. O master está salvo aqui se você quiser pra edição".

Na versão 1 o mesmo problema foi resolvido de outro jeito, apertando o CRF do próprio render final até o arquivo
caber: 72.411 kB com CRF 18, 51.510.040 bytes com CRF 20 e 34.588.697 bytes com CRF 22.

---

## 12. Erros do caminho e correções

Em ordem cronológica, só o que os arquivos e os logs comprovam.

**Topbar carimbada nas capturas do site (03:58).** O primeiro passe do Playwright pegou a barra fixa por cima do
conteúdo nos blocos altos. Corrigido com um segundo script que injeta `.topbar { display: none !important; }` e
recaptura doze blocos mais a página inteira.

**Tipografia pequena demais nos infográficos (04:03).** O medidor de overflow do `render_graficos.py` apontou
cartões apertados. Nove regras de tamanho foram aumentadas de uma vez em `graficos.html`, cada substituição
protegida por `assert`.

**Faltava o endcard (04:04).** O cartão `g16` foi acrescentado ao dicionário `NAMES` depois e renderizado em
separado.

**Barras de dado saindo vazias no HyperFrames (04:26).** Diagnóstico anotado no próprio patch: "BUG REAL:
`<i class="bf">` e inline, entao height/scaleX eram ignorados e as barras saiam vazias". Correção de uma linha:
`.bf` ganhou `display: block`.

**Cards encostando na borda (04:26 e 04:29).** O `check` do HyperFrames reportou `container_overflow` de
22,91 px em `#s02lines` dentro de `#s02card`. O cartão passou de `height: 512px` para `542px`. O
`container_overflow` do `#s01img` era o push-in proposital, e foi marcado como intencional com
`data-layout-allow-overflow`. A parede de regras do S07, que o lint acusou como texto ocluído, foi marcada com
`aria-hidden`, `data-layout-allow-overlap` e `data-layout-allow-occlusion`, porque é textura de fundo e não
texto para ler.

**Anel de choque visível desde o quadro zero (04:34).** Anotação do patch: "BUG: `fromTo` com
`immediateRender` liga o anel (opacity .75) desde o quadro 0. Em S09 ele ficava parado no meio da tela por 2,4 s
antes do climax". Correção: `immediateRender: false` nos dois anéis, `#s06ring` e `#s09ring`.

**Clímax com trilho vazio (04:34).** A cena do "10 vezes" tinha as barras entrando tarde, deixando o centro do
quadro vazio. A barra "antes 498" foi antecipada de 30,85 s para 27,85 s e a barra "depois 108" passou a subir
só no payoff, em 31,02 s, com o rótulo aparecendo por transição de opacidade em 30,85 s.

**Link no último quadro (04:47, cobrado pelo Chefe).** As quatro edições descritas na seção 10, mais a varredura
adversarial nos 1434 quadros.

**Áudio truncado em 45,14 s (05:04).** Causado por `-frames:v 1434` no comando de mux. Corrigido removendo o
parâmetro.

**Corte errado da gravação (05:17, cobrado pelo Chefe).** O erro central: a v1 encaixou a gravação em 720x1280
dentro de um canvas de 1080x960, com fundo desfocado preenchendo 180 px de cada lado. A v2 refez tudo com a
gravação em 1080x1920 full-bleed e a faixa reduzida para 810x720 sobre ela, com as bordas replicadas.

**Faixa sumindo no último quadro (05:58).** Depois do primeiro render da v2, uma varredura dos últimos quadros
mostrou a faixa e a legenda acabando antes do vídeo, deixando aparecer a camisa do Chefe embaixo. A causa é que
a faixa e a sequência de legenda têm exatamente 1434 quadros e qualquer arredondamento de tempo deixa o último
quadro descoberto. Correção registrada no diff do `render.sh`: `tpad=stop_mode=clone:stop_duration=1` nas duas
entradas, que congela o último quadro por mais 1 s de folga.

**Erro de dado que quase entrou na arte.** Durante a produção dos gráficos, a queda de 498 para 108 linhas
estava sendo tratada como 81 por cento. São 78,3 por cento. Os 81 por cento são a queda em tokens, de 9.692 para
1.832, que é a métrica comparável com o corte de 80 por cento que a Anthropic fez no próprio system prompt. A
correção gerou cartões separados, `g01` para linhas e `g06` para tokens, e o número que aparece no vídeo é
-78,3 por cento.

**Descartes.** Os rascunhos `smoke.mp4`, `apoio-v1.mp4`, `apoio-v2.mp4` e `apoio-v3.mp4` foram apagados às
04:32 com `rm -f` depois de aprovado o render em qualidade alta. Não há arquivos `.bak` no projeto. A única
menção a `.bak` no repositório é conteúdo de cena, o comando `mv CLAUDE.md CLAUDE.md.bak` que aparece desenhado
no terminal falso da cena S08.

---

## 13. Como repetir o processo do zero

1. Baixar a gravação e rodar `ffprobe` antes de qualquer coisa. Se vier de iPhone recente, esperar HEVC 10 bits
   em HLG BT.2020 com Dolby Vision e rotação por matriz, e tratar tonemap e rotação desde o primeiro comando.
2. Extrair MP3 mono 16 kHz e mandar para o Whisper com `timestamp_granularities[]=word`. Sem palavra com
   timestamp, não existe legenda palavra por palavra nem sincronia de cena.
3. Capturar o site com Playwright em `device_scale_factor=2`, matando animação e barra fixa por CSS injetado, e
   rolar a página inteira antes de recortar.
4. Desenhar os gráficos em HTML no tamanho exato do destino e capturar em dobro. Texto renderizado em navegador
   sai nítido; imagem gerada por IA não sobrevive a texto pequeno.
5. Montar a faixa no HyperFrames com a CLI pinada, ancorando cada animação no timestamp real da fala. Rodar
   `lint` e `check` a cada rodada e conferir os quadros extraídos, não o log.
6. Compor no ffmpeg mantendo a gravação intacta em tela cheia e queimando a faixa por cima. Reduzir a faixa
   proporcionalmente e replicar a coluna de borda para fechar a largura, em vez de cortar ou distorcer.
7. Medir onde está o rosto antes de escolher a altura da faixa. A medida decide, não o gosto.
8. Gerar a legenda como PNG RGBA com Pillow, um estado por transição e links simbólicos por quadro, e sobrepor
   com `overlay`.
9. Usar `tpad=stop_mode=clone` em toda camada que tenha exatamente a mesma duração do vídeo base.
10. Copiar o áudio com `-c:a copy` e nunca usar `-frames:v` no comando que faz o mux do áudio.
11. Verificar de fora: comparar a região do vídeo contra a fonte, medir a coluna mais escura do quadro, varrer
    todos os quadros procurando o que deveria ter sumido, e usar o arquivo antigo como controle positivo.

---

## 14. O que não foi possível determinar pelos arquivos

* **Saída do `hyperframes --version`.** O comando rodou às 04:07, mas a saída não ficou registrada no histórico.
  A versão 0.7.64 está provada pelos comandos `npx --yes hyperframes@0.7.64 ...` e pelo `package.json` gerado,
  não por um `--version` observado.
* **Parâmetros internos de `--quality draft` e `--quality high`.** A CLI não expôs no log qual codec ou CRF usa
  em cada modo. Só o resultado é observável: 4,7 MB no draft e 13,2 MB no high, ambos 1080x960 a 30 fps.
* **Os rascunhos apagados.** `smoke.mp4`, `apoio-v1.mp4`, `apoio-v2.mp4` e `apoio-v3.mp4` não existem mais no
  disco. Os tamanhos citados vêm do que a CLI imprimiu, não de medição do arquivo.
* **O arquivo reduzido para o Telegram.** `/tmp/video-final-v2-telegram.mp4` não está mais no disco. Os 38,8 MB
  vêm da saída do comando que o gerou.
* **Como a gravação foi feita.** Os metadados dizem iPhone 15 Pro Max, software 26.5.2, criada em
  2026-07-29T03:46:54-03:00, com coordenadas de GPS embutidas. Enquadramento, iluminação e microfone usados não
  são determináveis pelos arquivos.
* **Diferença exata entre `renders/apoio-metade-baixo-1080x960.mp4` (13,2 MB) e `renders/apoio-v2.mp4`
  (8,2 MB).** As duas são a mesma composição em momentos diferentes, e o segundo render rodou sem
  `--quality high`, o que explica a queda de tamanho. Não há log que confirme o modo usado nesse render
  específico, então a explicação é inferência a partir da linha de comando, não observação.
* **Quem tomou cada decisão de arte.** O histórico registra os patches e as justificativas escritas no código,
  não a conversa que levou a cada escolha, com exceção das quatro mensagens do Chefe citadas ao longo do texto
  (13295, 13298, 13300 e 13307).
