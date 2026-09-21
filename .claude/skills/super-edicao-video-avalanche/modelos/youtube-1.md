# Modelo YouTube 1 · o manual do canal · v3

> **Reescrito em 06/08/2026 por ordem do Chefe**, fundindo quatro documentos que tinham virado
> quatro verdades diferentes sobre a mesma máquina: o `youtube-1.md` v2 (05/08), o
> `MANUAL-GROK-EDICAO-YOUTUBE.md` (05/08), o `MANUAL-KIMI-EDICAO-YOUTUBE.md` (06/08) e a ordem de
> serviço `REVISAO-TELA-CHEIA.md` (06/08). Os três primeiros eram forks do mesmo pipeline, e onde
> discordavam um deles estava vencido.
>
> **O que este arquivo faz:** pega a melhor prática de cada um, resolve as contradições em favor da
> lição mais nova e mais medida, e coloca na frente de tudo as três leis que o Chefe cravou em
> 06/08/2026. Este manual **vence** os três anteriores em qualquer conflito. Os antigos ficam ao
> lado só como histórico (`youtube-1.ANTIGO.md`, `youtube-1.v2-2026-08-05.md`).
>
> **A regra de escrita deste manual, herdada e mantida:** nada de capítulo novo no fim. Lição nova
> entra DENTRO da etapa a que pertence, como armadilha ou como portão. Se uma lição não couber em
> nenhuma etapa, falta uma etapa.

---

# AS TRÊS LEIS

Elas vêm antes do pipeline porque **elas mandam no pipeline**. Cada uma tem uma prova objetiva que
roda em código e retorna erro. Lei sem prova é frase, e frase não segura entrega.

## LEI 1 · O corte NUNCA encosta na fala

Nenhuma palavra parte ao meio. Nenhuma sílaba some. Nenhuma consoante final é decepada. Nenhuma
emenda dobra palavra, quebra frase ou inverte sentido.

Isso não é cuidado, é procedimento. **Tempo de palavra do whisper nunca decide onde cortar**, porque
ele estica o intervalo por cima da pausa e encurta a cauda (no vídeo 05 ele jurou que a palavra "ou"
durava 4,48 segundos). Quem acha borda é energia, e mora em `bordas.py`.

Prova: `bordas.confere()` com zero emenda com som dos dois lados · detector de palavra partida com
zero · `prova_emendas.py` lido emenda por emenda. Detalhe completo nas etapas 4 e 10.

## LEI 2 · A geometria é impecável, sem exceção

Nunca texto vazando da própria caixa. Nunca texto em cima de outro texto. Nunca texto em cima de
elemento nenhum. Nunca elemento em cima de elemento que não seja camada declarada de propósito.

A área útil é fechada: **nada passa de `left: 1188` nem de `top: 1002`**. Todo texto vive dentro de
uma caixa com padding próprio e `line-height` com respiro. Número que conta tem coluna de largura
fixa, porque número muda de largura enquanto conta.

Prova: `npm run check` com zero erro, mais inspeção de snapshot no FIM de cada cena e no MEIO de
cada animação de contagem. Detalhe na etapa 8.

## LEI 3 · A tela NUNCA fica vazia

O painel ao lado da gravação existe para prender atenção do primeiro ao último segundo. Painel oco,
mesmo por meio segundo, reprova a entrega.

Três consequências práticas, e as três são obrigatórias:

1. **Faixa de baixo permanente.** Uma `#faixa-fix` global (`top: 850`, altura 152, `#1B2438`) cobre
   o vídeo inteiro como clip único de `data-start="0"` com a duração do master. Ela **nunca** vai a
   `opacity: 0`. O que troca é o miolo dela (rótulo, dado, chips, ticks, mini-barra), por crossfade
   interno. A faixa não é legenda: ela narra o raciocínio.
2. **Acima da faixa, sempre estrutura.** Componente da biblioteca, arte ou infográfico. Cena de
   "chip mais headline mais subtítulo" boiando em `#0F172A` é painel oco e reprova.
3. **A troca é por hold, nunca por buraco.** O elemento que sai **segura** até o próximo já estar
   visível. Overlap de 0,3 a 0,6s é permitido e desejável. Fade-out total da cena antes de a
   seguinte entrar é proibido. Cada cena cobre do seu início até o início da seguinte, absorvendo os
   silêncios: a timeline soma a duração do master sem buraco e sem sobreposição, nem por 0,02s.

Prova: tiling completo auditado no build, snapshot a cada ~3s sem janela oca, e `audita_2s.py` no
render. **O `audita_2s` sozinho não basta**, porque movimento mínimo não é tela cheia.

> **De onde veio.** O montador do vídeo 07 achou 13 buracos porque os agentes cortaram cada cena no
> fim exato da fala. O Chefe olhou o lote e mandou revisar os 14. Esta lei é a resposta.

---

# O QUE É

Vídeo de 8 a 12 minutos para o canal, montado a partir de um trecho de live, mais 10 segundos de
arte de encerramento. Tela dividida: um painel de apresentação escuro e uma coluna com a gravação
dele. O painel não é legenda animada, é uma peça que **constrói o raciocínio dele** enquanto ele
fala. Gancho forte puxado do miolo abre o vídeo, CTA entra no meio, encerramento canônico fecha.

**Entrega:** uma pasta em `~/Desktop/conteudo youtube/NN - Título/` (com sufixo de lote quando
houver, por exemplo `NN - Título kimi/`) contendo:

- `NN - Título.mp4`, o vídeo com **o mesmo nome da pasta** (regra do Chefe de 06/08/2026, nunca
  `video.mp4`)
- `thumbnail.png`
- `legenda.txt`

E no workspace do vídeo: `plano.json`, prova de emendas, saída do `audita_2s.py` e a folha de
contato das artes.

---

# O LAYOUT

Tela de 1920x1080, dois blocos sólidos separados por 32px de respiro.

| | montagem A (ímpares) | montagem B (pares) |
|---|---|---|
| painel | `left: 32` · 1252x1016 | `left: 636` · 1252x1016 |
| coluna | `left: 1316` · 572x1016 | `left: 32` · 572x1016 |

A conta fecha: 32 + 572 + 32 + 1252 + 32 = 1920. Os vídeos **alternam** o lado, e o CTA que entra em
cada um segue a mesma montagem (CTA 1 nos ímpares, CTA 2 nos pares).

## A paleta escura

| uso | cor |
|---|---|
| fundo da tela | `#0B0D12` |
| painel e cartão | `#0F172A` |
| faixa e bloco de dado | `#1B2438` |
| borda de cartão | `#2E3A4E` |
| texto | `#F7F5F0` |
| texto secundário | `#94A3B8` |
| acento frio | `#4FD8EF` |
| acento quente | `#F5402E` |
| acento positivo | `#24D869` |

**Zero gradiente em qualquer lugar**, linear, radial ou cônico. A riqueza vem de dois tons sólidos
em blocos separados. Zero emoji, zero travessão em texto de tela.

## A geometria do painel, que é a LEI 2 em números

O painel tem 1252 de largura por 1016 de altura, com margem lateral de 64px, o que dá **1124 de área
útil**. A faixa permanente fica em `top: 850` com 152 de altura, fechando em 1002.

**Nada de texto além de `left: 1188` ou `top: 1002`.** Arte e infográfico ocupam 1252x690 em
`top: 170`, de ponta a ponta do painel.

---

# AS FERRAMENTAS, E ONDE CADA UMA MORA NESTE MAC

Tudo abaixo está instalado e funcionando no MacBook do Chefe. Antes de reclamar que algo não roda,
confira o caminho aqui.

## Os binários

| ferramenta | caminho | para quê |
|---|---|---|
| `ffmpeg` | `/opt/homebrew/bin/ffmpeg` | corte, concat, recodificação, extração de quadro e de áudio |
| `ffprobe` | `/opt/homebrew/bin/ffprobe` | duração, resolução, fps, rotação do contêiner |
| `whisper-cli` | `/opt/homebrew/bin/whisper-cli` | transcrição com tempo por palavra |
| `node` | `~/.nvm/versions/node/v22.23.1/bin/node` | roda o motor do HyperFrames |
| `npm` / `npx` | mesma pasta do node | `npm run check` e `npm run render` |
| `python3` | `~/.pyenv/shims/python3` | todos os scripts do pipeline |
| `op` | `/opt/homebrew/bin/op` | lê credencial do cofre 1Password |

**Bibliotecas Python** · `numpy` (envelope de energia, detecção de silêncio e de palavra partida) e
`pillow` (recorte de arte, folha de contato).

## Os modelos e motores

**Transcrição** · `~/.local/share/whisper-models/ggml-large-v3-turbo-q5_0.bin`. É o único modelo
usado. Invocação padrão `-l pt -ml 1 -oj`, e o `-ml 1` é o que dá um token por linha com a pontuação
colada na palavra.

**Render** · `hyperframes@0.7.90`, puxado por `npx --yes` a cada chamada, sem instalação local.

**Imagem** · `gpt-image-2`, sempre pela **rota OAuth da assinatura do Chefe**, nunca pela chave paga.
Tudo passa por `~/naia-agent/scripts/naia_image.py`, função
`gerar(prompt, saida, size, quality, refs, timeout, allow_paid_fallback=False)`.

**Arte de encerramento** · `~/workspace/t1-full/enc10.mp4`, md5
`4381202476f6a3d79fe03455f434e5ec`. É idêntica em todos os vídeos do canal. **Nunca gerar uma
nova.**

**CTAs** · CTA 1 nos ímpares (montagem A), CTA 2 nos pares (montagem B). O CTA tem que obedecer as
mesmas três leis do vídeo em que entra: peça antiga que deixa o painel oco não serve.

| peça | arquivo | estado em 06/08/2026 |
|---|---|---|
| CTA 1 novo | `~/workspace/cta1-kimi/CTA1-kimi.mp4` | existe, renderizado |
| CTA 2 novo | `~/workspace/cta2-kimi/` | **projeto pronto, MP4 NÃO renderizado** |
| CTA 1 antigo | `~/Desktop/conteudo youtube/CTAs/CTA1.mp4` | existe, anterior à lei da tela cheia |
| CTA 2 antigo | `~/Desktop/conteudo youtube/CTAs/CTA2.mp4` | existe, anterior à lei da tela cheia |

> **PENDÊNCIA REGISTRADA.** Enquanto o `CTA2-kimi.mp4` não for renderizado a partir de
> `~/workspace/cta2-kimi/proj`, todo vídeo PAR trava na etapa 11. Renderizar antes de começar um par,
> ou usar o CTA2 antigo declarando a escolha no reporte. Não inventar um terceiro CTA.

## As skills que este modelo consome

| skill | caminho | o que se pega dela |
|---|---|---|
| `super-edicao-video-avalanche` | `~/.claude/skills/super-edicao-video-avalanche` | este manual, os 25 scripts e a biblioteca de componentes |
| `quinteto-pixel-art-3d-voxel` | `~/naia-agent/.claude/skills/quinteto-pixel-art-3d-voxel` | o bloco de estilo VERBATIM e os cinco PNGs canon |
| `infograficos` | `~/.claude/skills/infograficos` | a estrutura da página de deck: pill, cards, herói, densidade |
| `impeccable` | `~/.claude/skills/impeccable` | a régua de movimento e as proibições de composição |
| `descricao-personagens-avalanche` | `~/.claude/skills/descricao-personagens-avalanche` | o canon dos personagens |
| `hyperframes*` | `~/.claude/skills/hyperframes*` | contrato de composição, CLI, keyframes e mídia |

Os cinco PNGs canon ficam em
`~/naia-agent/.claude/skills/quinteto-pixel-art-3d-voxel/assets/`: `denderson.png`, `naia.png`,
`openclaw.png`, `claudinho.png`, `codexzinho.png`, mais `quinteto-trabalhando.png` como cena de
grupo. O `naia_nano_alt.png` **não** se usa aqui.

## Os 25 scripts do pipeline

Todos em `~/.claude/skills/super-edicao-video-avalanche/scripts/youtube-1/`, cada um com o porquê
escrito no próprio cabeçalho.

**Fundação** · `bordas.py` a trava de energia que encosta toda borda de corte no silêncio ·
`prepara.py` master, gancho, remoção e esqueleto · `prepara_cta.py` o mesmo para um CTA, sem gancho
e com cabeçalho permanente · `remapeia.py` leva mapa e blocos do master antigo para o novo ·
`aplica_remocao.py` reancora o mapa quando o diretor declarou remoção sem aplicar

**Arte** · `arte.py` o motor de prompt ÚNICO, com `base_pixel()` e `base_info_pixel()` ·
`crop_artes.py` leva a arte de 1536x1024 para os 1252x690 do painel, calibrando o fundo ·
`gen_thumb.py` · `gen_encerramento.py`

**Cenas** · `build.py` junta esqueleto e blocos, embrulha as saídas, junta o CSS e audita ·
`infografico_cheio.py` faz a arte ocupar o painel e recolhe a marca · `blocos_cta.py` gerador
determinístico de cenas de CTA (rascunho, o padrão é escrever à mão)

**Corte** · `mapa_corte.py` gera o material de leitura com pausa marcada e nível de voz ·
`perfil_voz.py` separa a voz dele da de outra pessoa por timbre · `acha_dispensavel.py` apoio na
leitura de muleta · `corta_fino.py` corta silêncio por energia e conteúdo por lista num passe só ·
`corta_silencio.py` versão antiga, só referência histórica · `reancora_cortes.py`

**Prova** · `audita_2s.py` acusa janela de 2 segundos sem movimento no painel · `prova_emendas.py`
transcreve em volta de cada emenda para conferir o sentido · `emenda_encerramento.py` tira o preto
entre o fim do conteúdo e o card

**Fecho** · `finaliza.py` · `insere_cta.py` acha o vão entre frases e encaixa o CTA ·
`reancora_cta.py` desloca os capítulos depois da inserção · `merge_video.py`

Componentes: `referencia/componentes-painel.md` e `.html`, com os sete tipos de cena.

---

# AS QUATRO FERRAMENTAS QUE PRECISAM DE MANUAL PRÓPRIO

## 1 · HYPERFRAMES, o motor que renderiza o painel

Um motor que roda uma **página HTML com GSAP** num Chrome headless, captura quadro a quadro por
screenshot e monta o MP4. O painel do vídeo é um site, e animação de site é o que a gente escreve.

### A estrutura de um projeto

```
proj/
  index.html          a composição, montada pelo build.py (nunca editada à mão)
  hyperframes.json    aponta paths: blocks, components, assets
  package.json        os quatro comandos
  meta.json           id e nome do projeto
  assets/             chefe.mp4, chefe.m4a, as artes .png e a pasta fonts/
  renders/            a saída, com data e hora no nome
```

### O contrato do HTML

A raiz declara a composição inteira:
```html
<div id="root" data-composition-id="main" data-start="0" data-duration="529.54"
     data-width="1920" data-height="1080">
```

Dentro dela, **tudo que aparece no tempo é um `clip`**:
```html
<div id="cNN" class="clip livre" data-start="14.30" data-duration="4.12" data-track-index="2">
```

`data-track-index` separa as camadas: **0** é a coluna da gravação, **1** o rótulo de capítulo,
**2** as cenas do painel e **3** o cabeçalho da marca. Dois clips na mesma trilha não podem se
sobrepor, nem por 0,02s. A `#faixa-fix` da LEI 3 entra dentro de `#painel` como clip único cobrindo
`0` até a duração do root, em trilha própria, acima das cenas na pilha visual e ancorada na base do
painel.

O áudio é um elemento próprio, fora do painel:
```html
<audio id="audio-chefe" src="assets/chefe.m4a" data-start="0" data-duration="529.51"></audio>
```

> **AS CINCO DURAÇÕES.** Root, cabeçalho, rótulo, vídeo da coluna e áudio precisam todos ter a
> duração do master. Esquecer uma apagou a coluna da gravação num vídeo inteiro e comeu treze
> segundos de fala.

A timeline vive num `<script>` no fim, sempre `gsap.timeline({ paused: true })`, e o motor busca por
ela em `window.__timelines["main"]`.

### Os quatro comandos

| comando | o que faz |
|---|---|
| `npm run check` | lint, runtime, layout, motion e contraste. **É o portão da LEI 2** |
| `npm run render` | renderiza |
| `npm run dev` | preview interativo no navegador |
| `npx hyperframes snapshot --at "12.4,33.1" --no-end -o snaps` | tira quadro sem renderizar |

### O que o `check` reprova, e o que ele NÃO pega

Reprova: colisão de texto, elemento fora da área, contraste abaixo de AA, sobreposição de clip,
tween de opacidade direto num elemento de clip, e saída de cena sem desligamento explícito.

**Não pega:** evento de timeline escrito depois de `</html>`, que vira código morto silencioso (quem
pega é a auditoria do `build.py`); janela parada (é o `audita_2s.py`); e painel oco que respeita a
geometria (é a inspeção de snapshot da etapa 8).

### As armadilhas do motor

> **Fade de saída aplicado no próprio elemento de clip briga com o motor**, que já gerencia a
> visibilidade. O `build.py` embrulha cada cena com saída num `<div id="cNN-in">` interno,
> redireciona o tween para ele e escreve um `tl.set(..., {opacity: 0})` no instante exato do corte.

> **Se o fade termina antes do fim da cena, sobra painel preto.** Toda saída é atrasada para
> terminar no instante do corte. Isso é LEI 3 dentro do build.

> **`data-duration` do clip do gancho tem que casar com o `ini` da cena 2**, senão o motor acusa
> sobreposição na mesma trilha, mesmo por 0,02s.

> **Animar `top`, `left`, `fontSize`, `padding` ou `margin` faz a captura tremer**, porque cada
> quadro é um screenshot e o layout recalcula. Só `transform`, `opacity`, `width` de barra e
> `filter`.

> **Blur e clip-path funcionam**, porque a captura é por screenshot e não por composição de vídeo.
> É o que dá cara de peça cara sem custar nada.

> **`<style>` embutido no HTML do bloco, fora do `<head>`, faz o validador não aplicar o
> posicionamento** e o check acusa overlaps fantasmas. CSS sempre nos arquivos de CSS do bloco, que
> o `build.py` injeta no head.

> **O gerador de esqueleto pode COMER o marcador `<!--JS-->` do bloco** (medido no vídeo 05 em
> 06/08/2026). Quando isso acontece o build sai com a casca estática e **nenhuma animação de
> cena, nenhuma troca de faixa**, e nada acusa: o `check` passa, a auditoria de geometria passa e
> a de tela cheia passa, porque a casca parada está lá. Confira a contagem de `tl.` do
> `index.html` contra a soma dos blocos antes de renderizar.

> **O GSAP lê `filter: none` como `brightness(0)`.** Pulso de brilho declarado a partir do neutro
> implícito pisca o bloco em PRETO PURO metade do tempo (medido em `brightness(0.0001)`). Declare
> o neutro explícito: `fromTo(..., { filter: "brightness(1)" }, { filter: "brightness(1.14)" })`.

> **`npx hyperframes snapshot` posiciona a timeline com o `seek` padrão do GSAP, que SUPRIME
> callback.** A folha de contato dele mostra a faixa com o texto de abertura em todas as cenas e
> todo contador zerado, o que parece defeito e não é. Quadro que vale é o extraído do render.

> **O browser do MCP é COMPARTILHADO pela frota.** Com vários vídeos em produção ao mesmo tempo,
> a medição de um sai com o DOM de outro. Por isso a auditoria roda pelo
> `scripts/youtube-1/audita_painel.py`, que sobe um Chrome próprio, confere a identidade do
> projeto (duração da raiz e número de cenas) e só então mede.

## 2 · IMPECCABLE, de onde vem a régua de movimento

Skill de design de frontend em `~/.claude/skills/impeccable`.

**O que NÃO se usa dela.** Metade é interação: hover, foco, formulário, estado de carregamento,
`prefers-reduced-motion`, responsividade. Num vídeo renderizado quadro a quadro nada disso existe.
Não se roda `/impeccable animate` na composição e aceita a saída.

**O que se usa**, de `reference/motion-design.md`:

- **A régua 100/300/500.** 100 a 150 ms para acender um item, 200 a 300 ms para troca de estado,
  300 a 500 ms para mudança de layout, 500 a 800 ms para entrada de cena.
- **Saída é 75% da entrada.**
- **Curva exponencial, nunca bounce.** `expo.out` na entrada, `quart.inOut` na ida e volta,
  `quart.out` em número e barra. `back`, `elastic` e `bounce` são proibidos.
- **Transform e opacidade são o piso, não o teto.** Blur, filtro, clip-path e máscara são material
  legítimo, desde que não se anime propriedade que dirige layout.
- **Stagger com teto.** Dez itens a 50 ms dão 500 ms no total; acima disso, reduza o passo.

Das proibições absolutas do `SKILL.md` dela, que valem também no prompt dos infográficos: borda
lateral colorida como acento, texto com gradiente por `background-clip`, glass como padrão, o molde
do número gigante com rótulo pequeno, e grade de cards idênticos repetida sem fim.

Da seção de cor: **OKLCH, nunca `#000` nem `#fff`**, todo neutro tingido na direção da marca. A nossa
paleta já nasce assim.

## 3 · INFOGRÁFICO COM OS NOSSOS PERSONAGENS

### Os três acabamentos, e qual é o nosso

| acabamento | quando | onde vive |
|---|---|---|
| anime ultra realista | default da skill | a própria `infograficos` |
| **pixel art 3D voxel** | **o padrão deste modelo de vídeo** | `quinteto-pixel-art-3d-voxel` |
| paper craft | quando ele pedir papel, diorama ou scrapbook | `descricao-personagens-avalanche` |

Aqui é sempre pixel art, e o fundo é `#0F172A` em vez do off-white da skill, porque a arte é colada
num painel escuro.

### As regras fixas, que são decisão do Chefe e não se negociam

1. **O QUINTETO COMPLETO**, sempre os cinco: Denderson, Naia, OpenClaw, Claudinho, Codexzinho.
2. **Personagens SEMPRE TRABALHANDO**, operando painel, apontando para um card, carregando um bloco,
   subindo no elemento-herói. Nunca parados em fila, nunca posando.
3. **SEM plaquinha de nome** embaixo deles.
4. **A tipografia NÃO é pixelada.** Cena pixelada, interface limpa por cima, que é o que jogo HD-2D
   faz. Texto em pixel art não se lê no celular.

### O layout-tipo, escolhido pelo conteúdo

| layout | quando usar |
|---|---|
| fluxo horizontal numerado com branch | funil e processo passo a passo · **o já validado** |
| grade modular com destaque central | visão geral com muitos blocos independentes |
| versus de duas colunas | comparar dois produtos ou dois caminhos |
| hub central com satélites | núcleo com fluxos entrando e saindo |
| pilha 3D isométrica | camadas e arquitetura empilhada |
| listas técnicas com gauges no rodapé | specs e métricas |
| funil 3D vertical com side cards | jornada de conversão |

### A estrutura da página, que vem da skill `infograficos`

Quatro partes fixas: **moldura** com cantos em colchete e tag mono de slide no canto superior
direito; **header em pill** com borda sólida de acento (a skill mãe pede gradiente, aqui não, a
regra global do Chefe é zero gradiente) e título em display pesada; **cards modulares** com faixa de
cor sólida no topo, cada um com o próprio acento, de modo que a página lê multi-acento; e um
**elemento-herói** visivelmente maior que o resto.

> **DENSIDADE ALTA É REGRA.** Sete blocos mais o herói mais os personagens. Página de três blocos
> não é este padrão e reprova. Cada infográfico resume o **trecho inteiro**, não uma frase.

### As três armadilhas do quinteto

Conferir as três em **toda** peça, ampliando o recorte se precisar:

> **A CAUSA RAIZ DAS TRÊS, ACHADA NO VÍDEO 09 EM 09/08/2026.** Os PNGs canon iam anexados em
> `refs` e **nenhuma linha do prompt mandava usá-los**. O modelo recebia as referências e
> desenhava do jeito dele. O conserto é uma linha que ancora explicitamente cada personagem na
> referência correspondente.
>
> E cuidado com o caminho oposto: repetir a proibição ("nunca formiga, nunca inseto, sem
> antena") **piora**, porque repetir a palavra aumenta o peso dela na cena. A tentativa que
> repetiu "formiga" doze vezes saiu com mais formiga. O que funcionou foi ancorar na referência
> e quase não usar negativa.

1. **OpenClaw sai formiga.** A cabeça é um OVAL ALTO E ARREDONDADO, contorno contínuo, sem
   segmentação, sem cintura, sem mandíbula, com dois olhos enormes e AFASTADOS ocupando um terço do
   rosto. Calça preta cobrindo as pernas inteiras, tênis branco, sem rabo, nunca inseto.
2. **Codexzinho sai de cabeça grande demais.** A nuvem-flor é PEQUENA e proporcional ao corpo.
3. **Naia sai anime.** Ela é sprite como os outros, cabelo de pixel com degrau duro, blazer preto,
   circuito ciano no antebraço, nunca ilustração pintada.

## 4 · GERAÇÃO DE IMAGEM PELA ROTA OAUTH

**Modelo** `gpt-image-2`. **Rota** a assinatura ChatGPT do Chefe, pelo OAuth do Codex CLI, que não
gasta crédito de API. **Camada única** `~/naia-agent/scripts/naia_image.py`. Nenhuma skill fala com
a OpenAI direto.

```python
from naia_image import gerar
r = gerar(prompt, "saida.png", size="1536x1024", quality="high",
          refs=[...], timeout=900, allow_paid_fallback=False)
print(r["rota"])   # "oauth" ou "api-paga"
```

O `refs` manda os PNGs canon junto e é **isso que segura a identidade** de cada personagem.

### As três limitações desta rota, medidas e não supostas

1. **Tamanho.** Só saem cravados `1536x1024`, `1024x1536` e `1254x1254`. O backend materializa
   sempre cerca de 1,573 megapixel NA PROPORÇÃO pedida, então `1024x1024` volta como `1254x1254`.
2. **`quality` não é controlável.** O gateway força para `auto`, sem degradação.
3. **Falha em vez de disfarçar.** Tamanho errado levanta erro em vez de redimensionar escondido.

Antes de gerar: `python3 ~/naia-agent/scripts/naia_image.py --check`. Se marcar **`rota=api-paga`**,
o OAuth caiu e está gastando crédito do Chefe: **pare e avise ele**. Renovar depende de
`codex login`, que é interativo e só ele faz. Sempre `allow_paid_fallback=False`.

### O recorte, que vem depois

A arte sai em 1536x1024 (3:2) e o painel usa 1252x690 (1,814). O `crop_artes.py` mede a caixa de
conteúdo, corta só a margem vazia repartida entre topo e rodapé, **calibra o fundo para exatamente
`#0F172A`** (o modelo devolve em torno de `#020C1D`) e completa a proporção com barra lateral da
mesma cor. Foto aceita corte lateral; **infográfico nunca é cortado**.

> **ARMADILHA DO PREFIXO DO ARQUIVO** (medida no vídeo 06 em 06/08/2026). O `crop_artes.py`
> decide o caminho pelo NOME: peça que começa com `img_` entra pelo corte de foto e perde um
> oitavo de cada lado, o que decepa título de infográfico; peça que começa com `info_` completa
> com barra da própria cor e não perde nada. Diorama e qualquer peça com texto nas bordas nascem
> `info_`, mesmo quando parecem foto. O sintoma é texto cortado que volta a acontecer por mais
> que você regere o prompt: a causa é o nome do arquivo, não o modelo.

## O cofre

Credencial nunca vive em arquivo nem em commit. Tudo no cofre `Naia-sistemas` do 1Password:

```
set -a; . ~/.config/naia/op.env; set +a
op read "op://Naia-sistemas/<Item>/<campo>"
```

---

# O PIPELINE · ETAPA 0 MAIS DOZE ETAPAS

Cada etapa tem um **PORTÃO**: uma prova objetiva que precisa passar antes de a próxima começar.
Portão que não passa para o trabalho. Etapa pulada não é atalho, é retrabalho garantido.

Três decisões de arquitetura que a v3 herda do Kimi e que mudam a ordem em relação à v2:

1. **Portão é código, não frase.** Manual que depende de o executor lembrar falha exatamente onde já
   falhou.
2. **O corte de conteúdo acontece ANTES das cenas, nunca depois do render.** Cena escrita para
   conteúdo que vai sair é trabalho jogado fora, e cena picotada pelo corte é emenda estranha no
   painel. A leitura da transcrição decide tudo que sai, e o master já nasce limpo.
3. **UM render por vídeo.** Re-render é falha de processo, não rotina. Conteúdo sai no master,
   defeito visual se caça em snapshot, e o render só roda com tudo aprovado.

---

## Etapa 0 · Pré-voo

Antes de tocar em qualquer arquivo:

1. `python3 ~/naia-agent/scripts/naia_image.py --check` retornando `rota_padrao: oauth`.
2. `md5 ~/workspace/t1-full/enc10.mp4` conferindo com `4381202476f6a3d79fe03455f434e5ec`.
3. Binários presentes: ffmpeg, ffprobe, whisper-cli, node, python3.
4. O bruto existe e decodifica inteiro. Se não existir, regenerar da live com o `corta.sh` **do
   projeto** (nunca de scratchpad de sessão, que é efêmero) ou usar o `master.mp4` do projeto antigo
   como fonte, registrando a escolha.
5. Se o vídeo for PAR, o `CTA2-kimi.mp4` existe. Se não existir, renderizar agora ou declarar o uso
   do CTA2 antigo.

**PORTÃO** · os cinco itens OK. Falhou o OAuth: para tudo e avisa o Chefe.

---

## Etapa 1 · Cortar o trecho da live

Recorta o pedaço da live que vira o vídeo, com `ffmpeg -ss` e `-t`, recodificando para h264 a 30fps.
O `corta.sh` guarda os limites de cada trecho: **nunca jogue esse arquivo fora**, porque os
`bruto.mp4` são apagados das pastas de entrega e a live é a única fonte de recuperação.

**PORTÃO** · a duração do bruto bate com o pedido, e o arquivo abre e decodifica inteiro.

---

## Etapa 2 · Transcrever com tempo por palavra

```
ffmpeg -i bruto.mp4 -ac 1 -ar 16000 audio16k.wav
whisper-cli -m ~/.local/share/whisper-models/ggml-large-v3-turbo-q5_0.bin -l pt -ml 1 -oj -of palavras -f audio16k.wav
```

O `-ml 1` dá um token por linha com a pontuação colada. Remonte as palavras (token que não começa
com espaço é continuação da anterior) em `pal.json` no formato `[["palavra", inicio, fim], ...]` e
gere `leitura.txt`, uma palavra por linha com o tempo, para a etapa 3.

> **A ARMADILHA QUE MANDA NO MANUAL INTEIRO, E QUE É A LEI 1.** O whisper **estica o intervalo da
> palavra por cima da pausa e encurta o fim dela**. Tempo de palavra do whisper serve para saber O
> QUE foi dito e mais ou menos QUANDO, **nunca** para decidir onde cortar. Quem acha borda é energia.

**PORTÃO** · 2 a 3 palavras por segundo de média e a última palavra terminando perto do fim do
arquivo.

---

## Etapa 3 · Direção: leitura, remoções, gancho e artes

Um agente lê a `leitura.txt` INTEIRA e decide três coisas, todas anotadas em tempo do bruto. **É
aqui que o corte de conteúdo é decidido**, antes de existir uma única cena.

### `remover`

Cinco classes, toda remoção sai etiquetada:

- **REPETIÇÃO** · ele diz a mesma coisa duas ou três vezes seguidas. É o vício mais comum dele: no
  vídeo 07 apareceu nos primeiros dez segundos, "3 mil que se cadastraram" duas vezes e "lançamento
  pago" três vezes em nove segundos.
- **MULETA** · frase inteira que sai sem prejuízo nenhum para a mensagem.
- **INVASÃO** · áudio de outra pessoa vazando na chamada, mais a espera dele até mutar. Identifica
  por **TIMBRE**, com `perfil_voz.py` (f0, centroide espectral, rolloff). **Nunca por volume**, que
  confunde ele falando baixo com outra pessoa entrando.
- **VENCIDO** · data que já passou, promoção encerrada, evento futuro que já aconteceu. **Data
  vencida não se marca como alerta, se REMOVE**: alerta em JSON ninguém executa, e foi assim que
  ficou no ar "a imersão que eu vou fazer no dia 10 de junho". Atenção à diferença entre anunciar
  evento futuro (remove) e reencenar uma fala do passado dentro da história (fica).
- **TELA MORTA** · ele mexendo no tablet, arrumando a tela, procurando o slide.

> **ARMADILHA** · número que ele erra e corrige na sequência ("um milhão e meio... não, 750 mil")
> sai inteiro: fica só a versão corrigida. Nunca deixar o número errado no ar.

### `gancho`

O trecho mais forte do miolo, copiado para a frente. **Gancho bom é o que abre um loop que o vídeo
inteiro responde** (no 07: os números do funil até "eu tenho o contato dessas 3 mil aqui"). Frase de
abertura morna reprova, e o primeiro gancho do 07 foi reprovado pelo Chefe exatamente por isso. São
3 a 5 segmentos curtos costurados, 15 a 25 segundos no total.

### `artes.md`

O que cada peça precisa mostrar e em qual trecho ela ancora. Cadência validada no 07: **um
infográfico a cada 60 a 90 segundos**, imagem de apoio nos trechos de demonstração, e nunca dois
infográficos colados sem cena de componente entre eles, a menos que sejam vizinhos de raciocínio,
caso em que as janelas de marca FUNDEM numa só (etapa 7).

### `mapa.json`

A lista de cenas, cada uma com `id`, `ini`, `dur`, `tipo` e a `fala` daquele trecho. Tipos:
`gancho`, `texto`, `cartela`, `imagem`, `infografico`.

> **ARMADILHA** · cena que dura menos de 3 segundos não comporta três linhas entrando em sequência:
> a última nasce depois de o fade de saída já ter começado e aparece sumindo.

**PORTÃO** · a soma dos mantidos menos remoções dá entre 6 e 11 minutos · toda remoção tem classe ·
o gancho tem texto exato conferido na transcrição · as cenas cobrem o vídeo inteiro sem buraco e sem
sobreposição · nenhuma fala citada no mapa está fora da transcrição.

---

## Etapa 4 · Master, com a TRAVA DE BORDA (LEI 1)

```
python3 scripts/youtube-1/prepara.py <NN> <A|B>
```

Ele aplica as remoções no bruto, recorta os segmentos do gancho **do bruto original**, cola o gancho
na frente e escreve o esqueleto. Reencode h264 crf 18, 30fps, aac 192k.

> **A ARMADILHA QUE CUSTOU 36 PALAVRAS PARTIDAS.** Esta etapa já cortou usando o tempo de palavra do
> whisper. Medido nos 14 entregues: 36 palavras decepadas, quase todas na abertura, e a pior caía de
> -18 dB direto para -56 em 6 milissegundos, que é vogal cortada ao meio. **O gancho é o pior caso**,
> porque é recorte de duas bordas e é o primeiro som que o espectador ouve.
>
> **A trava mora em `bordas.py` e é obrigatória:** toda borda de corte é empurrada para dentro do
> silêncio mais próximo antes de virar comando de ffmpeg. Dois limiares, **-45 dB** acha o silêncio e
> **-58 dB** acha a cauda da palavra, porque consoante final tem energia baixa e morreria com um
> limiar só. Guarda assimétrica de **0,06s antes e 0,20s depois**, porque o problema é sempre na
> cauda.

O corte de conteúdo usa **blocos definidos pelo silêncio medido**, nunca o instante proposto pelo
agente: o trecho a remover vira o bloco de fala inteiro que o contém, com 70% de contenção, e uma
trava de exagero recusa remover mais que 1,35 vez o pedido mais 1,5 segundo.

> Três desenhos falharam antes deste, cada um pego pela prova: cortar no instante proposto deu "eu
> vou até sequer saibam"; exigir borda perto de pausa recusou tudo; usar vão de palavra do whisper
> deu "tiras na vida". E a trava de exagero pegou uma **inversão de sentido**: "eu não estou falando
> que você não vai mais usar plataformas" ia virar "que você não vai mais usar plataformas".

Outras armadilhas desta etapa, todas medidas:

- **O concat do ffmpeg estende cada segmento cerca de 6 ms.** Em vídeo longo a deriva acumula (90 ms
  no 07). O `remap.json` tem que ser corrigido medindo as emendas **reais** por correlação cruzada,
  não as computadas, e o `bordas.confere()` roda nas posições reais.
- **A trava pode andar para o lado errado e re-incluir conteúdo removido.** Conferir cada borda
  contra a leitura depois do ajuste.
- **`silencios()` não registra vão menor que 0,10s.** Quando a trava não achar nada, medir o
  envelope de 10 ms na mão e escolher o vale que não corta som, documentando o override.
- **Se depois da remoção sobrar ar morto** (a palavra anterior terminou muito antes), cortar no
  início do bloco de silêncio, não no pedido.
- **Pedaço abaixo de 0,25s é descartado**: timestamp quebrado com `-c copy` infla o arquivo inteiro
  (no 13 um rabo de 0,01s virou 595s em 1710s).
- **O gancho é medido no corte ORIGINAL mas recortado do arquivo já limpo.** Sem mapear, ele sai de
  outro lugar do vídeo.
- **O master é a fonte da verdade e o `prepara.py` é idempotente**: rodar de novo não recodifica.

Encostar as bordas muda a duração de cada trecho, então tudo que vem depois anda alguns centésimos.
O `prepara.py` grava `remap.json` e o `remapeia.py` converte `mapa.json` e `blocos/*.html` do master
antigo para o novo, de forma exata e monótona.

Saídas: `master.mp4`, `master.m4a`, `remap.json`, `pal_master.json`, `mapa_removcoes.json`.

**PORTÃO TRIPLO, E É A PROVA DA LEI 1:**

1. `bordas.confere()` com **zero emenda com som dos dois lados**.
2. **Detector de palavra partida com zero.** Queda de fala com corpo (-30 dB ou mais alto) para
   silêncio em 6 milissegundos:

```python
H=0.002; w=int(16000*H); n=len(a)//w
db = 20*np.log10(np.sqrt(np.maximum((a[:n*w].reshape(n,w)**2).mean(1), 1e-12)))
q=[]
for i in range(3, n-3):
    if db[i-3] > -30 and db[i+3] < -55:
        if q and i*H - q[-1] < 0.10: continue
        q.append(round(i*H, 2))
```

   Se disparar, rodar o mesmo controle no **bruto reencodado sem cortes**: se o bruto dispara no
   mesmo evento, é oclusiva natural da fala, não corte.
3. **Transcrição de 8 segundos em volta de CADA emenda de conteúdo**, lida uma a uma. Frase
   quebrada, palavra dobrada ou inversão de sentido reprovam. Ele repete de propósito às vezes
   ("chama de downsell. Downsell, pessoal, é..."), e isso é falso positivo que só o ouvido resolve.

---

## Etapa 5 · Gerar as artes

**O motor de prompt é um só e mora em `scripts/youtube-1/arte.py`.** Nenhum vídeo escreve o seu
próprio: o `gen_artes.py` do projeto só declara as peças e importa de lá. Cópia editada diverge, e
divergência custou caro.

Toda arte sai em pixel art 3D voxel com os cinco personagens **agindo dentro da cena**. Fotografia
realista foi tentada e descartada pelo Chefe. O bloco de estilo é **cópia VERBATIM** da skill do
quinteto, porque prompt improvisado com "voxel render", "Minecraft" ou "cubos" puxa para o LEGO de
plástico frio que ele reprovou. Fundo `#0F172A`. Toda peça ancora nos cinco PNGs canon.

### Os três blocos obrigatórios em toda peça

**`CONTEUDO_OBRIGATORIO`** · o que ele lê em voz alta tem que estar ESCRITO e legível na imagem,
palavra por palavra. Tarja cinza, barra de placeholder, lorem ipsum, texto borrado e tela vazia
reprovam a peça. Foi o defeito da imagem do WhatsApp do 07, que ele descreveu como "o mockup feio do
caralho com telefone com imagem com nada na tela".

**`SEGURANCA`** · proibido é **dado real**: marca alheia, logo, endereço, endpoint, token, IP,
telefone e e-mail. A regra antiga proibia tela, campo e botão, e foi ela que esvaziou a imagem do 07.
**Interface pode existir**, dado real não.

**`SEM_CLICHE`** · nada de grade de cards idênticos com ícone, título e texto repetida sem fim; nada
do molde do número gigante com rótulo pequeno; nada de borda lateral colorida como acento; nada de
texto com gradiente; nada de simetria por simetria.

> **ARMADILHA DE ACENTO** · o gpt-image-2 derruba acento em palavra teimosa. "ATÉ" saiu "ATE" três
> vezes seguidas no mesmo título. Insistiu duas vezes, **troque a palavra** por uma sem acento em vez
> de gastar geração.

**PORTÃO** · recorte com `crop_artes.py` e **OLHE UMA POR UMA** antes de qualquer build: as três
armadilhas do quinteto, a ortografia com acento, o texto todo dentro do próprio cartão, densidade de
sete blocos nos infográficos, zero tarja no lugar de conteúdo. Folha de contato montada, e na
primeira leva de um vídeo novo, abrir no Preview para o Chefe. Peça reprovada volta para a geração,
nunca para o render.

---

## Etapa 6 · Escrever as cenas

A régua vive em `referencia/componentes-painel.md` e o código pronto em `componentes-painel.html`. O
agente **escolhe** o componente pelo raciocínio do trecho e copia o código, não reinventa.

Os sete componentes: **fluxo** (primeiro isso, depois aquilo), **contador** (número que se forma),
**barras** (comparação de grandeza), **antes e depois** (o problema se monta e a solução assume o
eixo), **lista viva** (inventário que soma), **linha do tempo** (o que acontece quando) e **destaque
migrante** (o foco anda por uma grade já visível).

> **A REGRA** · nenhuma cena de conteúdo é feita só de texto entrando. Toda cena tem uma ESTRUTURA
> que se MONTA na frente do espectador, e o que se monta é o raciocínio dele. Headline com três
> linhas em fade continua existindo, mas **só na cena de virada, uma ou duas por vídeo**. Palavras
> dele: "quero animação bonita, profunda, com complexidade, com didática, que ilustre de verdade o
> que está sendo dito no vídeo".

**Consistência fala e tela é a regra número um:** o que aparece é exatamente o que ele diz naquele
instante, ancorado no `pal_master.json`. Nunca inventar número que ele não disse. Slide que aparece
antes ou depois da frase que ilustra reprova.

### A LEI 3 escrita como código de cena

- **`#faixa-fix` global.** Clip único dentro de `#painel`, `data-start="0"`,
  `data-duration="<duracao_root>"`, `top: 850`, altura 152, `#1B2438`, z-index alto o bastante para
  ficar na base do painel. Conteúdo inicial coerente com o gancho. Ela **nunca** recebe tween de
  opacidade para zero: quem troca é o miolo (rótulo em cyan, texto forte, chips, ticks, mini-barra,
  pill), por crossfade interno com `expo.out` ou `quart`.
- **Faixa por cena.** Ou não existe, ou crossfada com a global sem gap. Faixa local que vai a
  `opacity: 0` e deixa buraco é removida ou anulada.
- **Contiguidade.** Cada cena cobre do seu `ini` até o `ini` da seguinte, absorvendo os silêncios. O
  elemento que sai **segura** até o próximo já estar visível, com overlap de 0,3 a 0,6s. Proibido
  fade-out total antes da próxima entrar. Gap de painel vazio, nem por 0,5s.
- **Cena esparsa não existe.** Em todo trecho de fala solta, acrescentar estrutura ancorada na fala:
  pills, cards, lista, barras, ticks.
- **Pausa longa dentro de cena** (ele mexendo no tablet, pensando) se cobre com montagem lenta de
  slot, zoom contínuo ou respiração de 1 a 2% de scale na faixa. Nunca 2 segundos parados.
- **Cena final** segura SEM fade, com micro-movimento contínuo (pulso de `filter: brightness`,
  repeat finito), senão o `audita_2s` reprova o fecho.

### A LEI 2 escrita como código de cena

- Nada passa de `left: 1188` nem de `top: 1002`.
- Todo texto dentro da própria caixa, com padding interno e `line-height` com respiro.
- **Número que CONTA muda de largura durante a animação.** Foi o único defeito que o Chefe achou no
  07: rótulo ancorado em x fixo colidiu com "750.000" no meio da contagem. Número vai em **coluna de
  largura fixa que não encolhe**, e o rótulo começa depois da caixa.
- **Número de 84px com `line-height: 1` transborda a própria caixa** e cai em cima do rótulo de
  baixo. O respiro vai no rótulo, com `margin-top`.
- IDs prefixados pela cena, para não colidir entre blocos.

### As armadilhas de código que já mataram vídeo

> **`tl.fromTo({v:0}, {...})` MATA O SCRIPT INTEIRO.** O GSAP lê a assinatura como
> `(target, from, to)`, estoura `Cannot create property 'parent' on number` e **nenhuma cena do vídeo
> anima**, não só a do contador. Contador vai sempre em `tl.to({v:0}, {...})`.

> **`fromTo` na entrada da faixa deixa o texto INICIAL invisível.** Ele trava a opacidade em zero
> desde a criação da timeline. Use `immediateRender: false`.

> **Duas trocas de faixa a menos de 0,55s uma da outra fazem a faixa piscar sem assentar.** A troca
> inteira leva 0,50s. Quando ele lista cinco itens em dois segundos, junte os itens numa linha só.

> **Empurrão que não move pixel.** Clonar `tl.to({x: 24})` duas vezes: só o primeiro move. Alterne o
> destino.

> **Faixa fatiada em partes iguais** mostra a etapa 2 enquanto ele fala da 4. Custou três renders no
> vídeo 05. Todo passo é ancorado no tempo REAL da palavra, medido no `pal_master.json`.

> **Evento de timeline depois de `</html>`** é código morto que o `check` não pega. O `build.py`
> audita isso.

Regras fixas: animação só por `transform`, `opacity`, `width` de barra e `filter`; nada de `top`,
`left`, `fontSize`, `padding` ou `margin`; zero travessão; zero gradiente; easings só `expo.out`,
`quart.inOut` e `quart.out`.

**PORTÃO** · saldo de `<div>` igual a zero por bloco · tempos idênticos aos do mapa, sem arredondar ·
tiling completo de 0 até o fim do master, sem buraco e sem sobreposição · zero travessão · zero
gradiente · easings só da régua.

---

## Etapa 7 · Build e o infográfico cheio

```
python3 scripts/youtube-1/build.py <dir>
python3 scripts/youtube-1/infografico_cheio.py <dir>
python3 scripts/youtube-1/build.py <dir>
```

O `build.py` junta esqueleto e blocos de forma determinística, ordena as cenas por tempo, embrulha os
fades de saída no wrapper `cNN-in`, atrasa toda saída para terminar no instante do corte, junta o CSS
de cada bloco e audita.

**As cinco durações** (root, cabeçalho, rótulo, vídeo da coluna e áudio) todas iguais à duração do
master. Esquecer uma apaga a coluna ou come fala.

> **A REGRA DO INFOGRÁFICO CHEIO.** Numa cena de infográfico a arte vai de **ponta a ponta do
> painel**, 1252x690 em `top: 170`, e o cabeçalho da marca com o rótulo de capítulo **somem**.
> Palavras dele: "seria muito melhor o infográfico estar maior, ocupando mais espaço na tela, do que
> ter lá em cima aquele Avalanche IA aplicada a negócios e a equipe da Naia". A única coisa que
> divide a tela com a arte é a faixa do rodapé, que não é repetição, é a narração viva.

> **ARMADILHA** · o rótulo de capítulo é reacendido pelo próprio bloco a cada troca de cena, com
> tween próprio, e ganha de qualquer fade porque vem depois na timeline. Brigar por opacidade não
> resolve: o texto dele **vira vazio** na cena de arte.

> **ARMADILHA** · quando duas cenas de arte são vizinhas, o par esconde e devolve da marca devolve
> ela no meio da segunda. Janelas coladas têm que ser **fundidas numa só**.

> **ARMADILHA** · a `#faixa-fix` não some em cena de infográfico cheio. Nesse caso ela pode narrar o
> infográfico (dado mais ticks), mas a caixa permanece.

**PORTÃO** · `npm run check` com **zero erro**. Warning de arquivo grande e de trilha densa pode
ficar; erro, não.

---

## Etapa 8 · As provas estáticas · a conferência que evita render jogado fora

É a etapa que faz valer as LEIS 2 e 3 antes de gastar quinze minutos de render. Olhar o defeito no
snapshot custa dez segundos; no vídeo pronto, quinze minutos.

```
npx hyperframes snapshot --at "<lista de tempos>" --no-end -o snaps
```

### A auditoria de geometria, que é o portão da LEI 2

O `npm run check` **não basta**: ele amostra 9 instantes do vídeo inteiro e só reprova elemento
que estoura um container que CLIPA. No vídeo 01 ele passou limpo com uma unidade de medida
transbordando 39px por baixo da borda do card.

Quem reprova de verdade é `referencia/audita-geometria.js`. Ele mede a TINTA dos nós de texto
(não a caixa do elemento) em quatro instantes de cada cena, só nos clips ativos naquele
instante, e acusa três coisas: texto passando de `left: 1188` ou `top: 1002`, texto passando da
borda interna do próprio card, e texto por cima de texto.

```
cd <proj> && python3 -m http.server 8791 --bind 127.0.0.1 &
# abrir http://127.0.0.1:8791/index.html no browser e executar a função do arquivo
```

Medir caixa em vez de tinta dá centenas de falsos positivos: no 01 a medição por caixa acusou
973 e a por tinta acusou 5, e as 5 eram reais. Container com `overflow: hidden` não conta,
porque ele já recorta.

**PORTÃO** · `violacoes` igual a ZERO. Qualquer achado volta para o bloco, nunca para o render.

### A auditoria de tela cheia, que é o portão da LEI 3

`referencia/audita-tela-cheia.js`, rodado do mesmo jeito. Ele mede, a cada segundo do vídeo
inteiro, quanto da região útil do painel (de `top: 170` até `top: 850`) está coberta por
elemento visível com tinta, fundo, borda ou imagem. Reprova abaixo de 10% de cobertura ou com
menos de dois elementos visíveis.

**O `audita_2s.py` não substitui isso.** Ele acusa 2 segundos sem MOVIMENTO, e painel oco com
um rótulo piscando no topo passa liso por ele. No vídeo 01 o `audita_2s` aprovou um build com
**94 segundos ocos em 34 janelas**, uma delas de 17 segundos seguidos com o miolo em zero.

Quando ele acusar, conserte nesta ordem: a cena entra tarde (o primeiro elemento estrutural tem
que estar visível no `data-start` do clip, o conteúdo se preenche depois mas a ESTRUTURA nasce
junto); a cena esvazia antes de acabar (nada de fade geral antes do corte, o último estado
segura até o fim do clip); a cena é esparsa (falta bloco no meio, e headline com subtítulo
sozinhos dão 5% de cobertura, que reprova).

**PORTÃO** · `instantes_ocos` igual a ZERO.

### As três varreduras de snapshot, todas obrigatórias:

1. **Fim de cada cena.** É quando todo o conteúdo já entrou e é onde a colisão aparece. Procurar:
   texto fora da caixa, texto sobre texto, texto sobre elemento, número fora da caixa, arte errada na
   cena errada, marca aparecendo por cima de arte, rótulo não esvaziado em cena de arte.
2. **Meio de cada animação de contagem.** Snapshot de fim de cena **não basta** para número que
   conta: a colisão do 07 só existia no meio da contagem, quando "750.000" atingiu a largura máxima.
3. **A cada ~3 segundos ao longo do vídeo inteiro**, procurando painel oco: headline solta sem
   estrutura, faixa sumida, quadro em transição com o elemento antigo já apagado e o novo ainda não
   visível.

**PORTÃO** · zero defeito nas três varreduras. Qualquer defeito volta para a etapa 6 ou 7, **nunca
para o render**.

---

## Etapa 9 · Render

```
cd <dir>/proj && npm run render
```

Entre 6 e 18 minutos conforme a duração. **Só entra aqui com as etapas 5, 7 e 8 aprovadas.** Um
render por vez no Mac.

> **ARMADILHA DE CONTENÇÃO, medida em 06/08/2026.** Dois renders HyperFrames na mesma máquina
> estouram a RAM e o macOS mata o Chrome do render no meio da captura, sem erro útil no log (o lote
> paralelo derrubou o nosso duas vezes). Renderizar com `-w 1`, desacoplado por `nohup` com log em
> arquivo (sobrevive a queda de terminal), e só quando não houver nenhum `chrome-headless-shell`
> ativo:
>
> ```
> while pgrep -f chrome-headless-shell >/dev/null; do sleep 30; done
> nohup npx hyperframes@0.7.90 render -w 1 > render.log 2>&1 &
> ```
>
> Com 1 worker um vídeo de 7:28 levou 6 minutos. Workers em auto sobem 4 Chromes e morrem.

**PORTÃO** · `audita_2s.py` no render: nenhuma janela de 2 segundos sem movimento no painel. Janela
que cai dentro de silêncio que o corte fino vai tirar pode ser descontada, mas o arquivo final tem
que passar limpo.

---

## Etapa 10 · Corte fino de silêncio e as provas de fala

O corte de CONTEÚDO já aconteceu na etapa 3 e 4. **Aqui é só silêncio por energia.**

A extensão real de cada palavra sai da energia do áudio, não do que o whisper declara. Dentro da
janela que ele aponta, procura-se onde o som de fato está acima do piso, e é ESSE pedaço que fica
protegido. O silêncio em volta vira cortável, mesmo estando "dentro" da palavra segundo o whisper.
Dois limiares, -45 dB e -58 dB, guarda de 0,06s antes e 0,20s depois.

```
python3 scripts/youtube-1/corta_fino.py render.mp4 cortado.mp4 \
  --words palavras_master.json --conteudo cortes.json --cauda 0 --plano plano.json
```

`--words` é a transcrição do **master** (mesmo áudio do render). `--conteudo` continua obrigatório
como parâmetro, e no fluxo v3 ele vai **vazio, com justificativa escrita no plano**, porque o
conteúdo já saiu no master. O `plano.json` tem que mostrar o silêncio saindo.

> **POR QUE A REGRA MUDOU.** Na v2 o portão era `conteudo > 0`, e ele existia porque a etapa se
> chamava "cortar o silêncio" e ninguém cortava repetição. Com o corte de conteúdo movido para a
> etapa 3, `conteudo = 0` aqui é o normal, e o que reprova agora é o inverso: **plano com conteúdo
> zero e sem justificativa escrita**, ou master entregue com repetição viva.

**PORTÃO** · detector de palavra partida com zero (mesmo controle no bruto se disparar) ·
`prova_emendas.py` lido em volta de cada emenda grande · `audita_2s.py` aprovado no arquivo cortado ·
nenhuma pausa acima de 1 segundo dentro do conteúdo.

---

## Etapa 11 · Encerramento e CTA

**Encerramento** · o `enc10.mp4` canônico, colado com `emenda_encerramento.py`.

> **ARMADILHA** · o `emenda_encerramento.py` mede brilho com `-ss`, que faz busca imprecisa e pode
> ler o quadro do card em vez do último quadro do conteúdo, jurando "nada a tirar" quando existem
> quadros pretos. Meça quadro a quadro decodificando de verdade.

**CTA** · CTA 1 nos ímpares, CTA 2 nos pares, sempre a peça nova (ver a tabela de CTAs lá em cima).
Onde ele entra levou quatro tentativas até acertar:

1. pausa mais próxima do meio · **errado**, entrou dentro de "só que aí, na semana seguinte";
2. fim de segmento do whisper · **errado**, o segmento quase nunca pontua;
3. fim de palavra com pontuação · **quase**, mas o whisper adianta o fim e o casamento pegava o
   silêncio ANTERIOR, devolvendo um "Certo?" solto;
4. **o VÃO entre a palavra que fecha a frase e a que abre a próxima** · certo. O silêncio medido tem
   que COMEÇAR dentro desse vão, e o corte vai 60 ms antes de a fala voltar. `insere_cta.py` acha.

**PORTÃO** · zero quadro preto entre o fim do conteúdo e o card · 8 segundos transcritos em volta das
DUAS emendas do CTA e lidos: entrada depois de frase fechada, saída sem palavra órfã.

---

## Etapa 12 · Fechar o pacote

**Thumbnail** · `gen_thumb.py`, ou versão nova via `naia_image.gerar` com `refs=[thumb antiga]` para
manter o idioma visual. Rota OAuth, 1536x1024 recortado para 1280x720. Texto curto, exato, sem
acento teimoso. Conferir a imagem antes de entregar.

**Legenda** · título, descrição, convite, link, hashtags, capítulos e o estudo de SEO. O bloco
publicável fica entre "COLE DAQUI PARA BAIXO" e "FIM DO QUE VAI PARA O YOUTUBE", e **abaixo de 5000
caracteres**. O padrão de legenda do canal (CTA de imersão, Instagram, separador de três pontos,
corpo narrado com os números na ordem do vídeo, capítulos, três hashtags) vive na etapa de publicação
e é o que já está no ar nos vídeos publicados.

**Capítulos** · primeiro em `00:00`, mínimo três, ordem crescente, mínimo 10 segundos entre eles,
mais um capítulo `Um recado rápido (pode pular)` no instante da entrada do CTA.

> **ARMADILHA** · **qualquer mudança de duração invalida TODOS os capítulos posteriores.** Corte
> fino, encerramento e CTA mudam a duração, então os capítulos são reancorados no arquivo FINAL.
> Reancorar é achar a fala de cada capítulo na transcrição nova, nunca fazer regra de três.

**PORTÃO** · extraia 7 segundos a partir de cada capítulo escrito, transcreva isolado e confirme que
abre na fala que o título anuncia. Capítulo que não bate reprova. E o MP4 tem o mesmo nome da pasta.

---

# COMO SE TRABALHA

## Paralelizar, sempre

Render é CPU no Mac, arte é chamada de API, escrita de cena é agente. **São recursos diferentes e não
têm motivo para esperar um pelo outro.** O 07 foi feito com seis agentes de cena em paralelo (um por
bloco de raciocínio), um montador, e a thumbnail gerando enquanto o render rodava. **Um vídeo por vez
no Mac** (a contenção de RAM da etapa 9 é real), mas dentro do vídeo tudo paralelo.

## A divisão de trabalho que funcionou

1. O diretor (thread principal) lê a transcrição inteira e fecha remoções, gancho e artes.
2. Um agente monta o master com a trava, e responde pelo portão triplo da LEI 1.
3. Um agente por bloco de cenas, com limites e tipos dados pelo diretor.
4. Um montador resolve a tiling, o infográfico cheio, o check e os snapshots, e responde pelas
   LEIS 2 e 3.
5. A thread principal comanda render, provas, CTA, encerramento e pacote.

Nenhum agente confere o próprio trabalho: o montador audita as cenas que os agentes escreveram, e a
thread principal audita o montador.

## O que reprova a entrega

**Por violar a LEI 1**

- Palavra cortada ao meio, medida pelo detector de queda em 6 ms.
- Emenda que dobra palavra, quebra frase ou inverte sentido.
- Repetição, muleta, invasão, tela morta ou data vencida que sobreviveu.
- Número errado no ar quando ele mesmo se corrigiu na sequência.
- Pausa acima de 1 segundo dentro do conteúdo.
- CTA entrando no meio de frase, ou devolvendo palavra órfã.

**Por violar a LEI 2**

- Qualquer texto fora da própria caixa, em qualquer quadro.
- Qualquer texto por cima de outro texto ou de qualquer elemento.
- Qualquer coisa além de `left: 1188` ou `top: 1002`.
- Número que colide com o rótulo no meio da contagem.
- `npm run check` com erro.

**Por violar a LEI 3**

- Painel oco em qualquer instante, mesmo por 0,5s.
- `#faixa-fix` ausente, ou faixa que vai a `opacity: 0`.
- Cena de conteúdo que é só headline com linhas em fade.
- Buraco ou sobreposição na tiling da timeline, nem por 0,02s.
- Janela de 2 segundos sem movimento no painel, inclusive no fecho.

**Pelo resto**

- Vídeo publicado sem CTA no meio.
- Infográfico de três blocos, espremido, cortado lateralmente ou com a marca por cima.
- Arte com tarja no lugar de conteúdo, OpenClaw formiga, Codexzinho cabeçudo, Naia anime.
- Slide que aparece antes ou depois da frase que ele ilustra.
- Número que aparece pronto em vez de contar.
- `back`, `elastic` ou `bounce` no easing. Gradiente. Emoji. Travessão em tela.
- Marca alheia, endpoint, telefone ou dado real em qualquer arte.
- Rota `api-paga` em qualquer geração de imagem.
- Capítulo que não bate com a fala, ou legenda acima de 5000 caracteres.
- Pasta de entrega sem o MP4 com o nome da pasta.

## A entrega

A pasta com o MP4 nomeado como ela, a thumbnail e a legenda. No workspace: o `plano.json` mostrando
quanto de silêncio saiu, a prova de emendas, a saída do `audita_2s.py`, a prova de palavra partida
com resultado zero e a folha de contato com um quadro de cada cena.

**O Chefe não precisa confiar, ele confere.**

---

# HISTÓRICO DE VERSÕES

| versão | data | o que mudou |
|---|---|---|
| v1 | até 04/08/2026 | 622 linhas crescendo por acúmulo; cada erro virava capítulo no fim, fora do passo a passo. Custou 36 palavras partidas e um lote sem corte de repetição. |
| v2 | 05/08/2026 | reescrita com doze etapas e portão por etapa; lição dentro da etapa. Arquivada em `youtube-1.v2-2026-08-05.md`. |
| Grok | 05/08/2026 | fork com os limites de vazamento em número e a primeira redação da lei da tela cheia. |
| Kimi | 06/08/2026 | fork que moveu o corte de conteúdo para antes das cenas, cravou um render por vídeo e mediu a deriva do concat e a contenção de RAM. |
| **v3** | **06/08/2026** | **esta.** Funde os três forks mais o `REVISAO-TELA-CHEIA.md`, promove as três leis do Chefe ao topo do documento, resolve as contradições (corte de conteúdo no master, nome do MP4, CTA novo) e transforma cada lei num portão com prova em código. |
