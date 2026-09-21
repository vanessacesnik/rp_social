# Modelo YouTube 1 · o manual do canal

> **Reescrito do zero em 05/08/2026.** O manual anterior tinha 622 linhas e crescia por acúmulo:
> cada erro que o Chefe apontava virava um capítulo NOVO no fim do arquivo, em vez de ser costurado
> dentro da etapa a que pertencia. O resultado foi que o passo a passo numerado envelheceu enquanto
> o documento engordava, e toda vez que eu reconstruía o pipeline eu lia o passo a passo, seguia o
> passo a passo, e perdia exatamente as lições que tinham ficado fora dele.
>
> Aconteceu duas vezes no mesmo dia. A trava de energia entrou no `corta_fino` e não no `prepara`,
> e saíram **36 palavras partidas ao meio** nos 14 vídeos. E a etapa 8 se chamava "Cortar o
> silêncio", então eu cortei o silêncio e **não cortei uma única repetição**, apesar de o método
> estar escrito 180 linhas abaixo, num capítulo separado.
>
> **A regra deste manual, agora:** nada de capítulo novo no fim. Lição nova entra DENTRO da etapa,
> como armadilha ou como portão. Se uma lição não couber em nenhuma etapa, é sinal de que falta uma
> etapa.

---

## A REGRA DE OURO

O pipeline são **doze etapas em ordem**, e cada uma tem um **PORTÃO**: uma prova objetiva que
precisa passar antes de a próxima começar. Portão que não passa para o trabalho.

Etapa pulada não é atalho, é retrabalho garantido. Hoje eu renderizei o vídeo 07 **quatro vezes**
por pular conferência, e cada render custa dezoito minutos.

**Nada de render antes da arte estar conferida.** Olhar o defeito no vídeo pronto custa dezoito
minutos; olhar na imagem custa dez segundos.

---

## O QUE É

Vídeo de 8 a 12 minutos para o canal, montado a partir de um trecho de live. Tela dividida:
um painel de apresentação escuro e uma coluna com a gravação dele. O painel não é legenda animada,
é uma peça que **constrói o raciocínio dele** enquanto ele fala.

**Duração** 8 a 12 minutos, mais 10 segundos de arte de encerramento.
**Entrega** uma pasta em `~/Desktop/conteudo youtube/NN - Título/` com `video.mp4`,
`thumbnail.png` e `legenda.txt`.

---

## O LAYOUT

Tela de 1920x1080, dois blocos sólidos separados por 32px de respiro.

| | montagem A (ímpares) | montagem B (pares) |
|---|---|---|
| painel | `left: 32` · 1252x1016 | `left: 636` · 1252x1016 |
| coluna | `left: 1316` · 572x1016 | `left: 32` · 572x1016 |

A conta fecha: 32 + 572 + 32 + 1252 + 32 = 1920. Os vídeos **alternam** o lado, e o CTA que entra
em cada um segue a mesma montagem.

### A paleta escura

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

### A geometria do painel

O painel tem 1252 de largura por 1016 de altura, com margem lateral de 64px, o que dá 1124 de área
útil. A faixa de dados fica em `top: 850` e tem 152 de altura, fechando em 1002.

---

# AS FERRAMENTAS, E ONDE CADA UMA MORA NESTE MAC

Tudo abaixo está instalado e funcionando no MacBook do Chefe. Antes de reclamar que algo não roda,
confira o caminho aqui.

## Os binários

| ferramenta | caminho | versão | para quê |
|---|---|---|---|
| `ffmpeg` | `/opt/homebrew/bin/ffmpeg` | 8.1.1 | corte, concat, recodificação, extração de quadro e de áudio |
| `ffprobe` | `/opt/homebrew/bin/ffprobe` | 8.1.1 | duração, resolução, fps, rotação do contêiner |
| `whisper-cli` | `/opt/homebrew/bin/whisper-cli` | whisper.cpp com BLAS | transcrição com tempo por palavra |
| `node` | `~/.nvm/versions/node/v22.23.1/bin/node` | 22.23.1 | roda o motor do HyperFrames |
| `npm` / `npx` | mesma pasta do node | npm 10.9.8 | `npm run check` e `npm run render` |
| `python3` | `~/.pyenv/shims/python3` | 3.12.8 | todos os scripts do pipeline |
| `op` | `/opt/homebrew/bin/op` | 2.32.1 | lê credencial do cofre 1Password |

**Bibliotecas Python** · `numpy` 2.4.6 (envelope de energia, detecção de silêncio e de palavra
partida) e `pillow` 12.2.0 (recorte de arte, folha de contato).

## Os modelos e motores

**Transcrição** · `~/.local/share/whisper-models/ggml-large-v3-turbo-q5_0.bin`, 0,6 GB. É o único
modelo usado. A invocação padrão é `-l pt -ml 1 -oj`, e o `-ml 1` é o que dá um token por linha com
a pontuação colada na palavra.

**Render** · `hyperframes@0.7.90`, puxado por `npx --yes` a cada chamada, sem instalação local. Os
comandos vêm do `package.json` de cada projeto: `npm run check`, `npm run render`, `npm run dev`
para preview e `npx hyperframes snapshot` para tirar quadro sem renderizar.

**Imagem** · `gpt-image-2`, sempre pela **rota OAuth da assinatura do Chefe**, nunca pela chave paga.
Tudo passa por `~/naia-agent/scripts/naia_image.py`, função `gerar(prompt, saida, size, quality,
refs, timeout, allow_paid_fallback=False)`. Três limitações medidas: só saem os tamanhos
`1536x1024`, `1024x1536` e `1254x1254`; `quality` é forçado para `auto` pelo gateway; e tamanho
errado levanta erro em vez de redimensionar escondido. Confira a rota antes de gerar com
`python3 ~/naia-agent/scripts/naia_image.py --check`. Se a saída marcar `rota=api-paga`, avise o
Chefe, porque o OAuth caiu e está gastando crédito.

## As skills que este modelo consome

| skill | caminho | o que se pega dela |
|---|---|---|
| `super-edicao-video-avalanche` | `~/.claude/skills/super-edicao-video-avalanche` | este manual, os 25 scripts e a biblioteca de componentes |
| `quinteto-pixel-art-3d-voxel` | `~/naia-agent/.claude/skills/quinteto-pixel-art-3d-voxel` | o bloco de estilo VERBATIM e os cinco PNGs canon |
| `infograficos` | `~/.claude/skills/infograficos` | a estrutura da página de deck: pill, cards, herói, densidade |
| `impeccable` | `~/.claude/skills/impeccable` | a régua de movimento e as proibições de composição |
| `descricao-personagens-avalanche` | `~/.claude/skills/descricao-personagens-avalanche` | o canon dos personagens no estilo anime, quando for o caso |

**Os cinco PNGs de referência dos personagens**, que toda arte ancora por `images.edit`, ficam em
`~/naia-agent/.claude/skills/quinteto-pixel-art-3d-voxel/assets/`: `denderson.png`, `naia.png`,
`openclaw.png`, `claudinho.png`, `codexzinho.png`. Tem também `quinteto-trabalhando.png`, que é a
cena de grupo aprovada, e `naia_nano_alt.png`, uma alternativa gerada por outro modelo que **não**
se usa aqui.

## Os 25 scripts do pipeline

Todos em `~/.claude/skills/super-edicao-video-avalanche/scripts/youtube-1/`, e cada um tem o porquê
escrito no próprio cabeçalho.

**Fundação**
`bordas.py` a trava de energia que encosta toda borda de corte no silêncio ·
`prepara.py` master, gancho, remoção de tela morta e esqueleto ·
`prepara_cta.py` o mesmo para um CTA, sem gancho e com cabeçalho permanente ·
`remapeia.py` leva mapa e blocos do master antigo para o novo depois da trava ·
`aplica_remocao.py` reancora o mapa quando o diretor declarou remoção sem aplicar

**Arte**
`arte.py` o motor de prompt ÚNICO, com `base_pixel()` e `base_info_pixel()` ·
`crop_artes.py` leva a arte de 1536x1024 para os 1252x690 do painel, calibrando o fundo ·
`gen_thumb.py` a thumbnail · `gen_encerramento.py` a arte de encerramento

**Cenas**
`build.py` junta esqueleto e blocos, embrulha as saídas, junta o CSS e audita ·
`infografico_cheio.py` faz a arte ocupar o painel e recolhe a marca ·
`blocos_cta.py` gerador determinístico de cenas de CTA (só para rascunho, o padrão é escrever à mão)

**Corte**
`mapa_corte.py` gera o material de leitura, com pausa marcada e nível de voz ·
`perfil_voz.py` separa a voz dele da de outra pessoa, por timbre ·
`acha_dispensavel.py` apoio na leitura do que é muleta ·
`corta_fino.py` corta silêncio por energia e conteúdo por lista, num passe só ·
`corta_silencio.py` a versão antiga, mantida só como referência histórica ·
`reancora_cortes.py` reancora tempos depois de um corte

**Prova**
`audita_2s.py` acusa janela de 2 segundos sem movimento no painel ·
`prova_emendas.py` transcreve em volta de cada emenda para conferir o sentido ·
`emenda_encerramento.py` tira o preto entre o fim do conteúdo e o card

**Fecho**
`finaliza.py` corte, prova geométrica, arte de encerramento e pacote ·
`insere_cta.py` acha o vão entre frases e encaixa o CTA ·
`reancora_cta.py` desloca os capítulos da legenda depois da inserção ·
`merge_video.py` utilitário de junção

---

# AS QUATRO FERRAMENTAS QUE PRECISAM DE MANUAL PRÓPRIO

## 1 · HYPERFRAMES, o motor que renderiza o painel

É um motor que roda uma **página HTML com GSAP** num Chrome headless, captura quadro a quadro por
screenshot e monta o MP4. Ou seja: o painel do vídeo é um site, e animação de site é o que a gente
escreve. Vem por `npx --yes hyperframes@0.7.90`, sem instalação local.

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

Dentro dela, **tudo que aparece no tempo é um `clip`**, com quatro atributos obrigatórios:
```html
<div id="cNN" class="clip livre" data-start="14.30" data-duration="4.12" data-track-index="2">
```

`data-track-index` separa as camadas: **0** é a coluna da gravação, **1** o rótulo de capítulo,
**2** as cenas do painel e **3** o cabeçalho da marca. Dois clips na mesma trilha não podem se
sobrepor, nem por 0,02s.

O áudio é um elemento próprio, fora do painel:
```html
<audio id="audio-chefe" src="assets/chefe.m4a" data-start="0" data-duration="529.51"></audio>
```

> **AS QUATRO DURAÇÕES.** Root, cabeçalho, vídeo da coluna e áudio precisam ter a duração certa.
> Esquecer uma delas apagou a coluna da gravação num vídeo inteiro e comeu treze segundos de fala.

A timeline vive num `<script>` no fim, sempre `gsap.timeline({ paused: true })`, e o motor busca por
ela em `window.__timelines["main"]`.

### Os quatro comandos

| comando | o que faz |
|---|---|
| `npm run check` | lint, runtime, layout, motion e contraste. **É o portão da etapa 7** |
| `npm run render` | renderiza. 18 minutos para um vídeo de 9 |
| `npm run dev` | preview interativo no navegador |
| `npx hyperframes snapshot --at "12.4,33.1" --no-end -o snaps` | tira quadro sem renderizar |

O `snapshot` é o que evita render desperdiçado: tire um quadro perto do FIM de cada cena, que é
quando todo o conteúdo já entrou e é onde a colisão aparece.

### O que o `check` reprova, e o que ele NÃO pega

Reprova: colisão de texto, elemento fora da área, contraste abaixo de AA, sobreposição de clip,
tween de opacidade direto num elemento de clip, e saída de cena sem desligamento explícito.

**Não pega:** evento de timeline escrito depois de `</html>`, que vira código morto silencioso.
Quem pega isso é a auditoria do `build.py`. E não pega janela parada, que é o `audita_2s.py`.

### As armadilhas do motor

> **Fade de saída aplicado no próprio elemento de clip briga com o motor**, que já gerencia a
> visibilidade. O `build.py` embrulha cada cena com saída num `<div id="cNN-in">` interno,
> redireciona o tween para ele e escreve um `tl.set(..., {opacity: 0})` no instante exato do corte.

> **Se o fade termina antes do fim da cena, sobra painel preto.** Toda saída é atrasada para
> terminar no instante do corte.

> **`data-duration` no clip do gancho tem que casar com o `ini` da cena 2**, senão o motor acusa
> sobreposição na mesma trilha, mesmo por 0,02s.

> **Animar `top`, `left`, `fontSize`, `padding` ou `margin` faz a captura tremer**, porque cada
> quadro é um screenshot e o layout recalcula. Só `transform`, `opacity`, `width` de barra e
> `filter`.

> **Blur e clip-path funcionam**, porque a captura é por screenshot e não por composição de vídeo.
> É o que dá cara de peça cara sem custar nada.

---

## 2 · IMPECCABLE, de onde vem a régua de movimento

Skill de design de frontend, versão 3.0.6, em `~/.claude/skills/impeccable`, com 51 arquivos.
Sub-comandos em `reference/`: `animate`, `motion-design`, `typography`, `spatial-design`,
`interaction-design`, `bolder`, `quieter`, `polish`, `critique`, `audit`, entre outros.

**O que NÃO se usa dela.** Metade é interação: hover, foco, formulário, estado de carregamento,
`prefers-reduced-motion`, responsividade. Num vídeo renderizado quadro a quadro nada disso existe.
Então **não se roda `/impeccable animate` na composição e aceita a saída**. Ela também exige um
`PRODUCT.md` e um brief confirmado antes de editar arquivo, o que não faz sentido aqui.

**O que se usa, e que reprovou quatro coisas que eu já tinha escrito:**

De `reference/motion-design.md`:
- **A régua 100/300/500.** 100 a 150 ms para feedback instantâneo, 200 a 300 ms para troca de
  estado, 300 a 500 ms para mudança de layout, 500 a 800 ms para entrada.
- **Saída é 75% da entrada.**
- **Curva exponencial, nunca bounce.** `expo.out` na entrada, `quart.inOut` na ida e volta,
  `quart.out` em número e barra. Bounce e elastic estão na lista de "tacky e amadorista".
- **Transform e opacidade são o piso, não o teto.** Blur, filtro, clip-path e máscara são material
  legítimo, desde que não se anime propriedade que dirige layout.
- **Stagger com teto.** Dez itens a 50 ms dão 500 ms no total; acima disso, reduza o passo.

Das proibições absolutas do `SKILL.md`, que valem também para o prompt dos infográficos:
- **borda lateral colorida** como acento em card, item de lista ou alerta;
- **texto com gradiente** por `background-clip`;
- **glass como padrão**;
- **o molde do número gigante** com rótulo pequeno e estatísticas de apoio;
- **grade de cards idênticos** com ícone, título e texto repetida sem fim.

Da seção de cor: **OKLCH, nunca `#000` nem `#fff`**, e todo neutro tingido na direção da cor da
marca. A nossa paleta já nasce assim, `#0F172A` e `#F7F5F0` em vez de preto e branco.

---

## 3 · INFOGRÁFICO COM OS NOSSOS PERSONAGENS

A skill `infograficos` em `~/.claude/skills/infograficos` custou **quatro tentativas** até o Chefe
aprovar, e o acerto está codificado nela e no `PADRAO-VISUAL.md`.

### Os três acabamentos, e qual é o nosso

| acabamento | quando | onde vive |
|---|---|---|
| anime ultra realista | default da skill | a própria `infograficos` |
| **pixel art 3D voxel** | **o padrão deste modelo de vídeo** | `quinteto-pixel-art-3d-voxel` |
| paper craft | quando ele pedir papel, diorama ou scrapbook | `descricao-personagens-avalanche` |

**Aqui é sempre pixel art**, com o precedente dark do LS Club, e o fundo é `#0F172A` em vez do
off-white da skill, porque a arte é colada num painel escuro.

### As regras fixas, que são decisão do Chefe e não se negociam

1. **O QUINTETO COMPLETO**, sempre os cinco: Denderson, Naia, OpenClaw, Claudinho, Codexzinho.
2. **Personagens SEMPRE TRABALHANDO**, operando painel, apontando para um card, carregando um bloco,
   subindo no elemento-herói. **Nunca parados em fila, nunca posando.**
3. **SEM plaquinha de nome** embaixo deles.
4. Fundo claro é o default da skill; **aqui é escuro**, pelo motivo acima.

### O layout-tipo, escolhido pelo conteúdo

| layout | quando usar |
|---|---|
| fluxo horizontal numerado com branch | funil e processo passo a passo · **é o já validado** |
| grade modular com destaque central | visão geral com muitos blocos independentes |
| versus de duas colunas | comparar dois produtos ou dois caminhos |
| hub central com satélites | núcleo com fluxos entrando e saindo |
| pilha 3D isométrica | camadas e arquitetura empilhada |
| listas técnicas com gauges no rodapé | specs e métricas |
| funil 3D vertical com side cards | jornada de conversão |

### Como se gera aqui

Pelo `arte.base_info_pixel()`, que empilha, nesta ordem: o bloco de estilo VERBATIM da skill do
quinteto, a paleta, a tipografia, a contenção de texto, a pontuação, a segurança, o conteúdo
obrigatório, a cena pixel, a tipografia limpa, a **estrutura da página de deck**, a profundidade de
três níveis de leitura, o anti-clichê, os ícones, o canon dos cinco e a área segura.

A estrutura da página tem quatro partes fixas: **moldura** com cantos em colchete e tag mono de
slide no canto superior direito; **header em pill** com borda sólida de acento e título em display
pesada; **cards modulares** com faixa de cor sólida no topo e acento próprio, de modo que a página
lê multi-acento; e **um elemento-herói** visivelmente maior que o resto.

> **DENSIDADE ALTA É REGRA.** Sete blocos mais o herói mais os personagens. Página de três blocos
> não é este padrão e reprova. Cada infográfico resume o **trecho inteiro** do vídeo, não uma frase.

A skill mãe pede borda de gradiente no header. **Aqui não**, porque a regra global do Chefe é zero
gradiente. Vai borda sólida na cor de acento.

### As três armadilhas do quinteto

Elas voltam em toda geração e já reprovaram peça quatro vezes só hoje. Confira as três em **toda**
peça, ampliando o recorte se precisar:

1. **OpenClaw sai formiga.** A cabeça é um OVAL ALTO E ARREDONDADO, contorno contínuo, sem
   segmentação, sem cintura, sem mandíbula, com dois olhos enormes e AFASTADOS ocupando um terço do
   rosto. Calça preta cobrindo as pernas inteiras, tênis branco, **sem rabo**, nunca inseto.
2. **Codexzinho sai de cabeça grande demais.** A nuvem-flor é PEQUENA e proporcional ao corpo.
3. **Naia sai anime.** Ela é sprite como os outros, cabelo de pixel com degrau duro, blazer preto,
   circuito ciano no antebraço, nunca ilustração pintada.

---

## 4 · GERAÇÃO DE IMAGEM PELA ROTA OAUTH

**Modelo:** `gpt-image-2`, o mesmo da Naia Hermes.
**Rota:** a **assinatura ChatGPT do Chefe**, pelo OAuth do Codex CLI. **Não gasta crédito de API.**
**Camada única:** `~/naia-agent/scripts/naia_image.py`. Nenhuma skill fala com a OpenAI direto.

```python
from naia_image import gerar
r = gerar(prompt, "saida.png", size="1536x1024", quality="high",
          refs=[...], timeout=900, allow_paid_fallback=False)
print(r["rota"])   # "oauth" ou "api-paga"
```

O `refs` é o equivalente ao antigo `images.edit`: manda os PNGs canon dos personagens junto e é
**isso que segura a identidade** de cada um.

### As três limitações desta rota, medidas e não supostas

1. **Tamanho.** Só saem cravados `1536x1024`, `1024x1536` e `1254x1254`. O backend materializa
   sempre cerca de 1,573 megapixel NA PROPORÇÃO pedida, então `1024x1024` volta como `1254x1254`.
   Os dois que este modelo usa são nativos e saem exatos.
2. **`quality` não é controlável.** O gateway força o campo para `auto`. Não há degradação: sai a
   mesma resolução máxima e o mesmo detalhe das imagens que a Hermes entrega.
3. **Falha em vez de disfarçar.** Tamanho errado levanta erro e deixa a imagem crua no disco, em vez
   de redimensionar escondido.

### Antes de gerar, confira a rota

```
python3 ~/naia-agent/scripts/naia_image.py --check
```

Se a saída de uma geração marcar **`rota=api-paga`**, o OAuth caiu e está gastando crédito do Chefe.
**Avise ele.** Renovar depende de `codex login`, que é interativo e só ele faz.

Sempre passe `allow_paid_fallback=False`, que é o padrão dos geradores deste modelo, para o script
falhar em vez de cair na chave paga sem avisar.

### O recorte, que vem depois

A arte sai em 1536x1024 (3:2) e o painel usa 1252x690 (1,814). O `crop_artes.py` faz a ponte:
mede a caixa de conteúdo, corta só a margem vazia repartida entre topo e rodapé, **calibra o fundo
para exatamente `#0F172A`** (o modelo devolve em torno de `#020C1D`) e completa a proporção com
barra lateral da mesma cor, o que é invisível no painel. Foto aceita corte lateral; **infográfico
nunca é cortado**, porque infográfico picotado reprova a entrega.

---

## O cofre

Credencial nunca vive em arquivo nem em commit. Tudo no cofre `Naia-sistemas` do 1Password, lido
assim:

```
set -a; . ~/.config/naia/op.env; set +a
op read "op://Naia-sistemas/<Item>/<campo>"
```

Itens que este trabalho tocou: `WaveSpeed/credential`, `OpenRouter-API-Key/credential` e
`Google-Gemini/veo_key_aq_1`. Os três são da frente de animação de imagem, que foi **descartada**.

---

# AS DOZE ETAPAS

## Etapa 1 · Cortar o trecho da live

Recorta o pedaço da live que vira o vídeo, com `ffmpeg -ss` e `-t`, recodificando para h264 a 30fps.
O `corta.sh` da sessão guarda os limites de cada trecho: **nunca jogue esse arquivo fora**, porque
os `bruto.mp4` são apagados das pastas de entrega e a live é a única fonte de recuperação.

**PORTÃO** · a duração do bruto bate com o pedido, e o arquivo abre e decodifica inteiro.

---

## Etapa 2 · Transcrever com tempo por palavra

```
ffmpeg -i bruto.mp4 -ac 1 -ar 16000 audio16k.wav
whisper-cli -m ~/.local/share/whisper-models/ggml-large-v3-turbo-q5_0.bin -l pt -ml 1 -oj -of palavras -f audio16k.wav
```

O `-ml 1` dá um token por linha, com a pontuação colada na palavra. Remonte as palavras (o token que
não começa com espaço é continuação da anterior) e guarde em `pal.json` no formato
`[["palavra", inicio, fim], ...]`.

> **ARMADILHA QUE MANDA NO MANUAL INTEIRO.** O whisper **ESTICA o intervalo da palavra por cima da
> pausa**. No vídeo 05 ele jurou que a palavra "ou" durava 4,48 segundos. Isso significa que
> **tempo de palavra do whisper NUNCA decide onde cortar**. Ele serve para saber O QUE foi dito e
> mais ou menos QUANDO, nunca para achar a borda do som. Quem acha borda é energia.

**PORTÃO** · o número de palavras é coerente com a duração (uma fala normal dá 2 a 3 palavras por
segundo) e a última palavra termina perto do fim do arquivo.

---

## Etapa 3 · Dirigir: o mapa, o gancho e as artes

O diretor lê a transcrição e escreve três arquivos no projeto:

**`mapa.json`** · a lista de cenas, cada uma com `id`, `ini`, `dur`, `tipo` e a `fala` daquele
trecho. Tipos: `gancho`, `texto`, `cartela`, `imagem`, `infografico`. Mais o campo `remover`, com os
trechos de tela morta que saem antes de tudo.

**`gancho.json`** · o trecho que vai para a frente do vídeo, com as linhas do cartaz.

**`artes.md`** · o que cada peça de arte precisa mostrar.

> **ARMADILHA** · cena que dura menos de 3 segundos não comporta três linhas entrando em sequência:
> a última nasce depois de o fade de saída já ter começado e aparece sumindo.

**PORTÃO** · as cenas cobrem o vídeo inteiro sem buraco e sem sobreposição, a soma bate com a
duração do master, e nenhuma fala citada no mapa está fora da transcrição.

---

## Etapa 4 · Montar o master, com a TRAVA DE BORDA

```
python3 scripts/youtube-1/prepara.py <NN> <A|B>
```

Ele tira a tela morta, recorta o gancho, cola o gancho na frente e escreve o esqueleto.

> **A ARMADILHA QUE CUSTOU 36 PALAVRAS PARTIDAS.** Esta etapa cortava usando o tempo de palavra do
> whisper, e o whisper encurta o fim da palavra. Medido nos 14 entregues: 36 palavras decepadas,
> quase todas na abertura, e a pior caía de -18 dB direto para -56 em 6 milissegundos, que é vogal
> cortada ao meio. **O gancho é o pior caso**, porque é recorte de duas bordas e é o primeiro som
> que o espectador ouve.
>
> **A trava agora é obrigatória e mora em `bordas.py`:** toda borda de corte é empurrada para dentro
> do silêncio mais próximo antes de virar comando de ffmpeg. Dois limiares, -45 dB acha o silêncio e
> -58 dB acha a cauda da palavra, porque consoante final tem energia baixa e morreria com um limiar
> só. Guarda assimétrica de 0,06s antes e 0,20s depois, porque o problema é sempre na cauda.

Outras armadilhas desta etapa, todas já corrigidas no script:

- Pedaço de fração de segundo sobrando de um trecho removido carrega timestamp quebrado, e o concat
  com `-c copy` **infla o arquivo inteiro**: no 13 um rabo de 0,01s virou 595s em 1710s. Fora
  qualquer pedaço abaixo de 0,25s.
- O gancho é medido no corte ORIGINAL mas recortado do arquivo já limpo. Sem mapear, ele sai de
  outro lugar do vídeo.
- O clip do gancho tem que terminar exatamente onde a cena 2 começa, senão o motor acusa
  sobreposição de clip.
- O master é a fonte da verdade e o script é **idempotente**: rodar de novo não recodifica, porque
  o MOV de origem some do Downloads assim que a pasta é limpa.

Encostar as bordas muda a duração de cada trecho, então tudo que vem depois anda alguns centésimos.
O `prepara.py` grava `remap.json` e o `remapeia.py` converte `mapa.json` e `blocos/*.html` do master
antigo para o novo, de forma exata e monótona.

**PORTÃO** · o `bordas.confere()` roda sozinho no fim e tem que dar **zero emenda com som dos dois
lados**. Se der mais que zero, uma palavra foi partida e não se avança.

---

## Etapa 5 · Gerar as artes

**O motor de prompt é um só e mora em `scripts/youtube-1/arte.py`.** Nenhum vídeo escreve o seu
próprio: o `gen_artes.py` do projeto só declara as peças e importa de lá. Cópia editada diverge, e
divergência custou caro.

### O padrão é PIXEL ART 3D com o quinteto

Toda arte sai em pixel art 3D voxel com os cinco personagens Avalanche **agindo dentro da cena**.
Fotografia realista foi tentada e descartada pelo Chefe.

- **O bloco de estilo é cópia VERBATIM da skill `quinteto-pixel-art-3d-voxel`.** A própria skill
  manda isso, porque prompt improvisado com "voxel render", "Minecraft" ou "cubos" puxa direto para
  o LEGO de plástico frio que ele reprovou.
- **Toda peça ancora nos cinco PNGs canon** por `images.edit`.
- **O fundo é `#0F172A`**, não o off-white da skill, porque a arte é colada num painel escuro.
- **A tipografia NÃO é pixelada.** Texto em pixel art não se lê no celular. Cena pixelada,
  interface limpa por cima, que é o que jogo HD-2D faz.

### Os três blocos obrigatórios em toda peça

**`CONTEUDO_OBRIGATORIO`** · o que ele lê em voz alta tem que estar ESCRITO e legível na imagem,
palavra por palavra. Tarja cinza, barra de placeholder, lorem ipsum, texto borrado e tela vazia
**reprovam a peça**. Foi o defeito da imagem do WhatsApp do 07, que ele descreveu como "o mockup
feio do caralho com telefone com imagem com nada na tela".

**`SEGURANCA`** · proibido é marca alheia, logo, endereço, endpoint, token, IP, telefone e e-mail
reais. **A regra antiga proibia tela, campo e botão, e foi ela que esvaziou a imagem do 07.**
Agora o proibido é o dado real, não a interface.

**`SEM_CLICHE`** · vindo das proibições da skill `impeccable`: nada de grade de cards idênticos com
ícone, título e texto repetida sem fim; nada do molde do número gigante com rótulo pequeno; nada de
borda lateral colorida como acento; nada de texto com gradiente; nada de simetria por simetria.

### Infográfico é diferente de imagem

Infográfico usa `arte.base_info_pixel()`, que carrega a estrutura da skill `infograficos`:

- **moldura** com cantos em colchete e tag mono de slide no canto superior direito;
- **header em pill**, banner arredondado com borda sólida de acento e título em display pesada;
- **cards modulares** com faixa de cor sólida no topo, cada um com o próprio acento, de modo que a
  página lê MULTI-ACENTO;
- **elemento-herói** que domina o centro: número gigante, gauge circular, pilha 3D isométrica,
  funil 3D ou fluxo horizontal numerado;
- **densidade ALTA**: sete blocos mais o herói mais os personagens.

> **ARMADILHA** · página de três blocos **não é** esse padrão e reprova. O Chefe olhou a versão de
> três blocos e disse que esperava os infográficos detalhados da skill. Cada infográfico resume o
> **trecho inteiro** do vídeo, não uma frase dele.

### As três armadilhas do quinteto, que já reprovaram peça quatro vezes

1. **OpenClaw sai formiga.** A cabeça tem que ser um OVAL ALTO E ARREDONDADO, com dois olhos
   enormes e AFASTADOS, sem segmentação, sem cintura, sem mandíbula. Calça cobrindo as pernas
   inteiras, sem rabo, nunca inseto.
2. **Codexzinho sai de cabeça grande demais.** A nuvem é PEQUENA e proporcional ao corpo.
3. **Naia sai anime.** Ela é sprite como os outros, cabelo de pixel com degrau duro, blazer, nunca
   ilustração pintada.

> **ARMADILHA DE ACENTO** · o gpt-image-2 derruba acento em algumas palavras por mais que a
> ortografia vá soletrada. "ATÉ" saiu "ATE" três vezes seguidas no mesmo título. Quando teimar,
> **troque a palavra** por uma que não dependa de acento em vez de gastar geração.

**PORTÃO, E É AQUI QUE HOJE EU PERDI UMA HORA** · recorte as peças com `crop_artes.py` e **OLHE UMA
POR UMA** antes de qualquer render. Confira: as três armadilhas do quinteto, a ortografia com
acento, o texto todo dentro do próprio cartão, densidade de sete blocos nos infográficos, e zero
tarja no lugar de conteúdo. Peça reprovada volta para a geração, não para o render.

---

## Etapa 6 · Escrever as cenas

**A régua vive em `referencia/componentes-painel.md` e o código pronto em
`referencia/componentes-painel.html`.** O agente ESCOLHE o componente pelo raciocínio do trecho e
copia o código, não reinventa.

> **A REGRA** · nenhuma cena de conteúdo é feita só de texto entrando. Toda cena tem uma ESTRUTURA
> que se MONTA na frente do espectador, e o que se monta é o raciocínio dele. Headline com três
> linhas em fade continua existindo, mas **só para a cena de virada, uma ou duas por vídeo**.
> Palavras dele: "quero animação bonita, profunda, com complexidade, com didática, que ilustre de
> verdade o que está sendo dito no vídeo".

Os sete componentes: **fluxo** (primeiro isso, depois aquilo), **contador** (número que se forma),
**barras** (comparação de grandeza), **antes e depois** (o problema se monta e a solução assume o
eixo), **lista viva** (inventário que soma), **linha do tempo** (o que acontece quando) e
**destaque migrante** (o foco anda por uma grade já visível).

### A régua de movimento, herdada da skill `impeccable`

Metade da `impeccable` é interação e num vídeo renderizado não existe, então não se roda
`/impeccable animate` na composição e aceita a saída. O que se herda é a régua, e ela reprovou
quatro coisas que eu tinha escrito:

- **Curva exponencial, nunca bounce.** `expo.out` na entrada, `quart.inOut` na ida e volta,
  `quart.out` em número contando e barra crescendo. `back`, `elastic` e `bounce` são proibidos.
- **Saída é mais rápida que entrada**, cerca de 75% da duração.
- **Duração pela régua 100/300/500.** 100 a 150 ms para acender um item, 200 a 300 ms para troca de
  estado, 300 a 500 ms para mudança de layout, 500 a 800 ms para entrada de cena.
- **Transform e opacidade são o piso, não o teto.** `blur`, `filter` e `clip-path` são liberados e
  funcionam, porque o HyperFrames captura por screenshot. Bloco que recua com `blur(3px)` lê como
  profundidade de verdade.

### As armadilhas de código que já mataram vídeo

> **`tl.fromTo({v:0}, {...})` MATA O SCRIPT INTEIRO.** O GSAP lê a assinatura como
> `(target, from, to)`, estoura `Cannot create property 'parent' on number` e **nenhuma cena do
> vídeo anima**, não só a do contador. Contador vai sempre em `tl.to({v:0}, {...})`.

> **`fromTo` na entrada da faixa deixa o texto INICIAL invisível.** Ele trava a opacidade em zero
> desde a criação da timeline, então a faixa entra vazia e só aparece na primeira troca. Use
> `immediateRender: false`.

> **Número de 84px com `line-height: 1` transborda a própria caixa** e cai em cima do rótulo de
> baixo. O respiro vai no rótulo, com `margin-top`.

> **Duas trocas de faixa a menos de 0,55s uma da outra fazem a faixa piscar sem assentar.** A troca
> inteira leva 0,50s. Quando ele lista cinco itens em dois segundos, **junte os itens numa linha só**.

> **Empurrão que não move pixel.** Clonar `tl.to({x: 24})` duas vezes: só o primeiro move. Alterne o
> destino.

> **Faixa fatiada em partes iguais** mostra a etapa 2 enquanto ele fala da 4. Custou três renders no
> vídeo 05. Todo passo é ancorado no tempo REAL da palavra, medido no `pal.json`.

> **Evento de timeline depois de `</html>`** é código morto que o `check` não pega. O `build.py`
> audita isso.

Regras fixas: animação só por `transform`, `opacity`, `width` de barra e `filter`; nada de `top`,
`left`, `fontSize`, `padding` ou `margin`; zero travessão; nada colide; nada passa de `left: 1188`
ou `top: 1002`; IDs prefixados pela cena; nunca inventar número que ele não disse.

**PORTÃO** · saldo de `<div>` igual a zero, e os tempos idênticos aos do `mapa.json`, sem
arredondar.

---

## Etapa 7 · Montar e fazer o infográfico ocupar o painel

```
python3 scripts/youtube-1/build.py <dir>
python3 scripts/youtube-1/infografico_cheio.py <dir>
python3 scripts/youtube-1/build.py <dir>
```

O `build.py` junta esqueleto e blocos de forma determinística, ordena as cenas por tempo, embrulha
os fades de saída num invólucro interno (fade no próprio clip briga com o motor), atrasa toda saída
para terminar no instante do corte e junta o CSS de cada bloco.

> **A REGRA DO INFOGRÁFICO CHEIO.** Numa cena de infográfico a arte vai de **ponta a ponta do
> painel**, 1252x690, e o cabeçalho da marca com o rótulo de capítulo **somem**. Palavras dele:
> "seria muito melhor o infográfico estar maior, ocupando mais espaço na tela, do que ter lá em cima
> aquele Avalanche IA aplicada a negócios e a equipe da Naia. Esse título não é necessário, porque
> no próprio infográfico já tem a equipe que trabalha por você". A única coisa que divide a tela com
> a arte é a faixa do rodapé, que não é repetição, é a narração viva.

> **ARMADILHA** · o rótulo de capítulo é reacendido pelo próprio bloco a cada troca de cena, com
> tween próprio, e **ganha de qualquer fade** porque vem depois na timeline. Brigar por opacidade
> não resolve: o texto dele **vira vazio** na cena de arte.

> **ARMADILHA** · quando duas cenas de arte são vizinhas, o par esconde/devolve da marca devolve ela
> no meio da segunda. Janelas coladas têm que ser **fundidas numa só**.

**PORTÃO** · `npm run check` com **zero erro**. Warning de arquivo grande e de trilha densa pode
ficar; erro, não. Layout tem que dar zero problema nas amostras.

---

## Etapa 8 · Renderizar

```
cd <dir>/proj && npm run render
```

Dezoito minutos para um vídeo de nove. **Só entra aqui com a etapa 5 e a etapa 7 aprovadas.**

**PORTÃO** · `audita_2s.py` no render, que amostra o painel a dois quadros por segundo e acusa
qualquer janela de 2 segundos sem movimento, com o tempo exato.

---

## Etapa 9 · O CORTE FINO, que são DUAS coisas e não uma

> **A ETAPA QUE EU ERREI HOJE, E O PORQUÊ.** Esta etapa se chamava "Cortar o silêncio". Eu cortei o
> silêncio, o script rodou, imprimiu "77 emendas" e pareceu sucesso. **Zero repetição foi cortada**,
> porque cortar repetição é uma SEGUNDA função do mesmo script, que só roda se receber uma lista, e
> a lista sai de um passo de leitura que não estava escrito em lugar nenhum do passo a passo.
>
> A etapa agora se chama o que ela é, e tem os dois lados obrigatórios.

### 9a · O silêncio sai por ENERGIA, e o whisper não opina

A extensão real de cada palavra sai da energia do áudio, não do que o whisper declara. Dentro da
janela que ele aponta, procura-se onde o som de fato está acima do piso, e é ESSE pedaço que fica
protegido. O silêncio em volta vira cortável, mesmo estando "dentro" da palavra segundo o whisper.

Dois limiares: **-45 dB** acha o silêncio, **-58 dB** acha a cauda da palavra. Guarda de 0,06s antes
e 0,20s depois.

### 9b · O conteúdo sai por LEITURA, e é obrigatório

```
python3 scripts/youtube-1/mapa_corte.py video.mp4 palavras.json mapa.txt
```

Gera o material de análise: a transcrição com **cada pausa marcada com a duração** e **o nível de
voz de cada fala**. Um agente lê isso e devolve um JSON com os trechos a remover, classificados:

- **REPETIÇÃO** · ele diz a mesma coisa duas ou três vezes seguidas. É o vício mais comum dele, e
  no vídeo 07 apareceu **nos primeiros dez segundos**: "3 mil que se cadastraram" duas vezes
  seguidas, e "lançamento pago" três vezes em nove segundos.
- **MULETA** · frase inteira que sai sem prejuízo nenhum para a mensagem.
- **INVASÃO** · áudio de outra pessoa vazando na chamada, mais a espera dele até mutar. Identifica
  por **TIMBRE**, com `perfil_voz.py`: f0, centroide espectral e rolloff. **Nunca por volume**, que
  confunde ele falando baixo com outra pessoa entrando.
- **VENCIDO** · data que já passou, promoção encerrada, qualquer coisa que envelheceu. No 07 ficou
  "a imersão que eu vou fazer no dia 10 de junho", com a data vencida, mesmo estando marcada como
  alerta no mapa desde o começo.

O corte de conteúdo usa **blocos definidos pelo silêncio medido**, nunca o instante proposto pelo
agente: o trecho a remover vira o bloco de fala inteiro que o contém, com 70% de contenção, e uma
trava de exagero que recusa remover mais que 1,35 vez o pedido mais 1,5 segundo.

> Três desenhos falharam antes deste, cada um pego pela prova: cortar no instante proposto deu "eu
> vou até sequer saibam"; exigir borda perto de pausa recusou tudo; usar vão de palavra do whisper
> deu "tiras na vida". E a trava de exagero pegou uma **inversão de sentido**: "eu não estou falando
> que você não vai mais usar plataformas" ia virar "que você não vai mais usar plataformas".

```
python3 scripts/youtube-1/corta_fino.py render.mp4 saida.mp4 --words palavras.json --conteudo cortes.json --cauda 0 --plano plano.json
```

**PORTÃO, DUPLO E OBRIGATÓRIO:**

1. **`plano.json` com `conteudo` maior que zero.** Se der zero, ou o vídeo não tem uma repetição em
   dez minutos (o que nunca aconteceu) ou a etapa 9b foi pulada. Zero de conteúdo sem uma
   justificativa escrita **reprova a entrega**.
2. **Zero palavra partida**, medido por queda de fala com corpo (-30 dB ou mais alto) para silêncio
   em 6 milissegundos:

```python
H=0.002; w=int(16000*H); n=len(a)//w
db = 20*np.log10(np.sqrt(np.maximum((a[:n*w].reshape(n,w)**2).mean(1), 1e-12)))
q=[]
for i in range(3, n-3):
    if db[i-3] > -30 and db[i+3] < -55:
        if q and i*H - q[-1] < 0.10: continue
        q.append(round(i*H, 2))
```

3. **`prova_emendas.py`** transcreve oito segundos em volta de cada emenda grande e acusa palavra
   dobrada. Leia a saída: ele repete de propósito às vezes ("chama de downsell. Downsell, pessoal,
   é..."), e isso é falso positivo que só o ouvido resolve.

---

## Etapa 10 · Arte de encerramento

Use o `enc10.mp4` canônico, md5 `4381202476f6a3d79fe03455f434e5ec`, que é idêntico nos treze vídeos
do canal. **Não gere um novo**, senão o card fica diferente dos outros.

> **ARMADILHA** · o `emenda_encerramento.py` mede brilho com `-ss`, que faz busca imprecisa e pode
> ler o quadro do card em vez do último quadro do conteúdo, jurando "nada a tirar" quando existem
> quadros pretos. Meça quadro a quadro decodificando de verdade.

**PORTÃO** · zero quadro preto entre o fim do conteúdo e o card, e o card entra direto de um quadro
com imagem.

---

## Etapa 11 · Inserir o CTA

Todo vídeo leva um CTA no meio, sem exceção. Duas peças prontas em `~/Desktop/conteudo youtube/CTAs/`:
`CTA1.mp4` (montagem A) e `CTA2.mp4` (montagem B). **CTA 1 nos ímpares, CTA 2 nos pares.**

O CTA é montado pelo `prepara_cta.py` e tem quatro diferenças do vídeo: não tem gancho, o cabeçalho
da marca fica a peça inteira, não tem rodapé nem carimbo de cena (a faixa cobre o rodapé e o carimbo
cai dentro do cabeçalho), e o conteúdo nasce em `top: 200`.

**Onde o CTA entra** foi o que deu mais trabalho, e o método levou quatro tentativas:

1. pausa mais próxima do meio · **errado**, entrou dentro de "só que aí, na semana seguinte";
2. fim de segmento do whisper · **errado**, o segmento quase nunca pontua;
3. fim de palavra com pontuação · **quase**, mas o whisper adianta o fim e o casamento pegava o
   silêncio ANTERIOR, devolvendo o vídeo com um "Certo?" solto;
4. **o VÃO entre a palavra que fecha a frase e a que abre a próxima** · certo. O silêncio medido tem
   que COMEÇAR dentro desse vão, e o corte vai 60 ms antes de a fala voltar.

**PORTÃO** · transcreva oito segundos em volta das DUAS emendas e leia. A entrada tem que cair
depois de uma frase fechada, e a saída tem que retomar sem palavra órfã.

---

## Etapa 12 · Fechar o pacote

**Thumbnail** `gen_thumb.py`.

**Legenda** com título, descrição, convite, link, hashtags, capítulos e o estudo de SEO. O bloco
publicável fica entre a régua que segue "COLE DAQUI PARA BAIXO" e a que antecede "FIM DO QUE VAI
PARA O YOUTUBE", e **tem que ficar abaixo de 5000 caracteres**.

**Capítulos** · o YouTube exige o primeiro em `00:00`, no mínimo três, ordem crescente e no mínimo
10 segundos entre um e outro. Acrescente um capítulo `Um recado rápido (pode pular)` no instante da
entrada do CTA.

> **ARMADILHA** · **qualquer mudança de duração invalida TODOS os capítulos posteriores.** Corte
> fino, encerramento e CTA mudam a duração, então os capítulos são reancorados no arquivo FINAL, não
> antes. Reancorar é achar a fala de cada capítulo na transcrição nova, não fazer regra de três.

**PORTÃO** · extraia sete segundos a partir de cada capítulo escrito, transcreva isolado e confirme
que abre na fala que o título anuncia. Capítulo que não bate reprova.

---

# COMO SE TRABALHA

## Paralelizar, sempre

Render é CPU no Mac, arte é chamada de API, escrita de cena é agente. **São recursos diferentes e
não têm motivo para esperar um pelo outro.** Cada vídeo vira três frentes simultâneas: um agente por
bloco de cenas, um de arte e um de pós. E vídeos diferentes rodam ao mesmo tempo.

Serializar isso custou meio dia hoje, e o Chefe apontou: "paralelize, subagentes dividindo funções,
e você me entrega isso na metade do tempo".

## O que reprova a entrega

- Vídeo publicado sem CTA no meio.
- **Corte com zero trecho de conteúdo**, ou seja, etapa 9b pulada.
- Palavra cortada ao meio, medida pelo detector de queda em 6 ms.
- Repetição, muleta ou data vencida que sobreviveu ao corte.
- Pausa acima de 1 segundo dentro do conteúdo.
- Emenda que dobra palavra, quebra frase ou inverte sentido.
- CTA entrando no meio de uma frase, ou devolvendo o vídeo com palavra órfã.
- Capítulo que não bate com a fala, ou legenda acima de 5000 caracteres.
- Qualquer janela de 2 segundos sem movimento no painel.
- Infográfico espremido, ou com título repetido em cima dele.
- Infográfico de três blocos, sem herói e sem dispositivo de apoio.
- Cena de conteúdo que é só headline com três linhas em fade.
- Arte com tarja no lugar de conteúdo, OpenClaw formiga, Codexzinho de cabeça grande, Naia anime.
- Slide que aparece antes ou depois da frase que ele ilustra.
- Travessão em texto de tela, gradiente, emoji na interface.
- Número que aparece pronto em vez de contar.
- `back`, `elastic` ou `bounce` no easing.
- Evento de timeline fora do `<script>`.

## A entrega

Arquivo final, a folha de contato com um quadro de cada cena, a saída do `audita_2s.py`, o
`plano.json` mostrando quantos trechos de silêncio e **quantos de conteúdo** saíram, e a prova de
palavra partida com resultado zero.

**O Chefe não precisa confiar, ele confere.**
