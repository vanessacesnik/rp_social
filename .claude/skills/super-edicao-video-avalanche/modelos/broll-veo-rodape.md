# MODELO: B-ROLL VEO NO RODAPE (pipeline completo classico)

> Migrado VERBATIM da skill `edicao-video-avalanche` em 2026-07-25, na unificação da
> `super-edicao-video-avalanche`. Nada foi resumido: o que estava escrito continua escrito.
> Acervo deste modelo: `scripts/broll-veo-rodape, assets/broll-veo-rodape, referencia/broll-veo-rodape` (os caminhos `scripts/`, `assets/`, `references/`
> citados no texto abaixo agora vivem sob essas pastas).
> O que e COMUM a todos os modelos (perguntas de abertura, plataforma, corte fino,
> gancho e QA) mora em `nucleo/` e vale aqui tambem.

---

# Edição de Vídeo Avalanche (v3)

Transforma talking-head cru (iPhone 9:16) em reels com b-roll IA no estilo Avalanche, b-roll 16:9 no RODAPÉ e o Chefe em cima.
Doc completo: `references/metodo-completo.md`. Canon dos personagens: `references/personagens-canon.md`. Scripts-base: `scripts/`.
Refs da lagosta: `assets/openclaw-refs/`. CTA fixo pronto: `assets/CTA_TAKE_FIXO_1080x1920.mp4`.
Base da hierarquia de ganchos: `references/cortes-virais-107-transcricoes.txt` (107 cortes virais de podcast/live +1M views, transcritos 2026-07-19, a fonte de onde saiu a ordem de escolha do GANCHO VIRAL).

## REGRAS INVIOLÁVEIS
1. **B-roll image-first:** SEMPRE `gpt-image-2` (imagem) → crop 16:9 → **Veo 3.1 fast IMAGE-TO-VIDEO**. NUNCA texto→vídeo direto.
2. **B-roll SEMPRE no RODAPÉ** (16:9, full width, altura 608). O Chefe inteiro em cima. NUNCA b-roll no meio. Se o vídeo já tem legenda baixa, **cortar o teto morto** acima da cabeça (`crop=1080:1312:0:~400`) e `vstack` o b-roll embaixo.
3. **Veo câmera TRAVADA + `negativePrompt` OBRIGATÓRIO** (proíbe alterar corpo/membros/pernas/look/cenário/texto; lagosta NUNCA vira formiga). Imagem aprovada = verdade absoluta, Veo só ANIMA.
4. **Safe-area** no prompt da imagem (conteúdo no centro 70%, topo/base 18% só ambiente) — o crop nunca come conteúdo.
5. **QUINTETO sempre em cena** (Denderson + Naia + OpenClaw + **Claudinho** + **Codexzinho** — canon oficial desde 2026-06-27) + extras conforme a fala (Davi SDR, clientes, time, João). Cenas de agência real. Canon dos 5 em `references/personagens-canon.md`; fonte única: `~/naia-agent/knowledge/personagens/SQUAD-AVALANCHE-CLAUDINHO.md` (Claudinho = mascote do Claude Code, cabeça de bloco laranja `>‹`; Codexzinho = nuvem-flor lavanda `>_`; OpenClaw = lagosta). Tema da disputa Claudinho vs OpenClaw quando fizer sentido.
6. **OpenClaw no canon das refs** (`assets/openclaw-refs/`): cabeça vermelho-cereja TEXTURIZADA (speckled/dimpled) cara-de-cria, corpo de CRIANÇA com moletom Avalanche. NUNCA inseto/bola-lisa.
7. **CHECKPOINT:** gerar as imagens, **abrir no Mac e esperar o Chefe aprovar a lagosta** ANTES de animar no Veo.

## TRIAGEM DE CORTES DE LIVE (validada no LOTE 49, 2026-07-19 — o Chefe aprovou o resultado)
Quando chegar um LOTE de cortes de live (vários vídeos), NÃO editar tudo: transcrever todos e triar antes com a skill **`triagem-cortes-live`** (regras completas lá). Resumo dos critérios: só edita quem tem **começo, meio e fim autossuficientes** (contexto que se sustenta sem a live); classifica em **ANÚNCIO** (gancho forte + prova concreta + fala com público frio), **PERFIL** (ensina/autoridade, tolera jargão) ou **DESCARTE** (fragmento de meio de conversa, voz de terceiro dominando, demo presa numa tela que não aparece, redundância com um corte mais forte, risco de compliance). Cauda com frase incompleta = tail-trim permitido (corta só a frase que não fecha). Pra lote grande, usar o formato **sanduíche econômico** (imagem estática 10s + crossfade em vez de Veo no b-roll; CTA único animado 1x e reaproveitado) — brief replicável em `~/Desktop/LOTE49-18-07/BRIEF-EDICAO.md`.

## GANCHO VIRAL (padrão obrigatório desde 2026-07-19 — validado em 21 vídeos do LOTE 1, o Chefe aprovou)
Todo reels editado ABRE com um gancho, seja qual for o formato (pipeline completo, sanduíche econômico, b-roll). O gancho é uma frase-gancho tirada de DENTRO do próprio vídeo, autossuficiente, 3-8s, recortada do arquivo FINAL já editado e colada NA FRENTE do vídeo integral. A frase se repete no lugar original: é intencional, estilo cold open dos cortes virais (é cópia, não recorte do meio).

**Hierarquia de escolha do gancho** (derivada da análise dos 107 cortes virais +1M views em `references/cortes-virais-107-transcricoes.txt`), nesta ordem: 1º número específico chocante (dinheiro, quantidade, prazo); 2º afirmação contraintuitiva ou polêmica; 3º implicação direta do espectador ("você"); 4º open loop, promessa de revelação; 5º pico emocional. Regra transversal: a primeira frase NUNCA é saudação ou contexto, o corte abre na temperatura máxima. A agente escolhe a frase sozinha (sem aprovar), pegando o timestamp da frase completa na transcrição.

**Visual do trecho-gancho (formato sanduíche 4K 2160x3840):** faixa vermelha sólida `#D32F2F` cobrindo SOMENTE a região do strip Hyperframe (y=2160→2624, 464px em 4K; em 1080p: y=1080→1312, 232px), com a headline em 2 LINHAS, CAIXA ALTA, derivada da frase (R$ e números literais). Fonte Bricolage Grotesque variável no eixo weight 800, branca, bloco centrado na faixa, fontsize auto-fit com teto 175px (4K), margens laterais ≥150px, gap ~34px. O quadrado do talking-head (topo) e a área de imagens (base) permanecem com o conteúdo ORIGINAL durante o gancho.

**Corte do gancho:** ~0.15s antes da 1ª palavra; fim com 0.3-0.4s de silêncio ou boundary natural. Whisper word-level pros timestamps, NUNCA cortar palavra no meio.

**Transição gancho→vídeo:** `xfade=transition=fade:duration=0.4:offset=(dur_gancho−0.4)` no vídeo + `acrossfade=d=0.4:c1=tri:c2=nofade` no áudio. O `c2=nofade` evita engolir a primeira palavra do vídeo quando ele abre falando.

**Implementação de referência (1 ffmpeg por vídeo):** filtergraph com `split` do input, `trim` do trecho-gancho, `overlay` do PNG da headline (gerado via PIL porque o drawtext do ffmpeg Homebrew não tem freetype), `xfade` + `acrossfade`, encode `libx264 crf 18 preset medium 30fps yuv420p` + `aac 192k 48kHz`. Estrutura do filtergraph exemplar (LOTE49 v04):
```
[0:v]split=2[vh][vo];
[0:a]asplit=2[ah][ao];
[vh]trim=<ini>:<fim>,setpts=PTS-STARTPTS[hookraw];
[hookraw][1:v]overlay=0:0:format=auto,format=yuv420p[hookv];   # [1:v] = PNG da headline na faixa vermelha
[vo]trim=start=0,setpts=PTS-STARTPTS,format=yuv420p[origv];
[hookv][origv]xfade=transition=fade:duration=0.4:offset=<dur_gancho-0.4>,format=yuv420p[outv];
[ah]atrim=<ini>:<fim>,asetpts=PTS-STARTPTS[hooka];
[ao]atrim=start=0,asetpts=PTS-STARTPTS[origa];
[hooka][origa]acrossfade=d=0.4:c1=tri:c2=nofade[outa]
```

**Verificação obrigatória por vídeo:** (a) `ffprobe` duração = original + gancho − 0.4; (b) frame do MEIO do gancho, conferir headline certa E vídeo certo por baixo (houve bug real de input trocado); (c) frame do meio do xfade; (d) whisper ~2.5s na emenda, nenhuma palavra cortada.

## LIÇÕES OPERACIONAIS (esteira LOTE 49, 2026-07-19)
- **Limpeza direta dos finais:** cortar silêncio e repetição no VÍDEO JÁ MONTADO (não só no cru), pra não entregar cauda morta.
- **CTA centralizado nativo:** o texto do CTA vai na GERAÇÃO (na hora de criar o take/asset centralizado), NÃO como overlay ou rescale por cima depois.
- **Pasta de entrega por lote:** entregas centralizadas numa pasta única no Desktop por lote, nomes padronizados por vídeo.
- **INEGOCIÁVEL — nunca paralelizar encodes 4K sem lançamento escalonado:** 60s entre lançamentos + gate de `load<45` antes de subir o próximo. Fan-out cego de 12+ ffmpeg já causou OOM e colapso do Mac (load 177, swap 37GB); 5 simultâneos de partida fria chegou a load 78 / swap 53GB. Encode 4K é sério, sobe UM de cada vez com o portão de carga.

## PIPELINE
1. **Ingestão:** ffprobe; extrair áudio. Conferir se o vídeo já tem legenda (printar frames) e onde ela está.
2. **Corte de roteiro (LIGADO por padrão):** transcrever (Whisper word-level), reler o roteiro, cortar partes que não mudam o contexto (leituras verbatim, subtramas, repetições). **Apresentar os cortes pro Chefe aprovar** (timestamps + tempo/custo). Cortar em pausas limpas. **Na mesma leitura, escolher a FRASE DO GANCHO** (≤5s) pelos critérios de viralização/expectativa/polêmica (ver passo 9b) — sem precisar aprovar.
3. **Corte de silêncio (LIGADO por padrão):** `scripts/silence_cut.py` (silencedetect -30dB:0.35, PAD 0.10). Legenda queimada anda junto. Some ~10-18s.
4. **1.2x:** só se o vídeo NÃO tiver legenda queimada (se tiver, pula o 1.2x pra não estranhar). 
5. **Planejar b-roll:** nº takes = ceil(dur/8); janelas contíguas iguais; mapear fala→cena (**quinteto**: Denderson+Naia+OpenClaw+Claudinho+Codexzinho + extras).
6. **Gerar imagens** (`scripts/01_gen_images.py`): gpt-image-2 1536x1024 high + crop `crop=1536:864:0:80`. → **abrir no Mac, aprovar.**
7. **Animar** (`scripts/02_animate.py`): Veo 3.1 fast image-to-video 16:9, câmera travada + `negativePrompt`. Pool de chaves (rotação no 429).
8. **Legenda — PADRÃO: Bricolage palavra por palavra (aprovado pelo Chefe 2026-07-18):** fonte **Bricolage Grotesque, instância `'96pt ExtraBold'`** (`assets/fonts/BricolageGrotesque-var.ttf`), **UMA palavra por vez** na caixa original da fala (mista, sem forçar caps), creme `#efe6da` com **palavras de impacto em vermelho `#e02128`** (~15-20% das words, nunca frases inteiras), sombra + stroke escuros pra legibilidade, render via **Pillow** (`scripts/06_captions_bricolage.py` — ffmpeg do Mac não tem libass). Tamanho ~120px reduzindo até caber em 90% da largura. **NUNCA cobrir a boca**: posicionar na região queixo/pescoço (no quadrado 1080 do sanduíche, centro da palavra em y≈960) e VERIFICAR com Read os piores frames de boca aberta. Corrigir na EXIBIÇÃO os erros de nome do Whisper (OpenClaw, Claude Code, Naia, "vibe codando um SaaS"…), mantendo os timings. Alternativas: Submagic Ella só se o Chefe pedir; vídeo que já vem legendado → mantém a queimada e sobe a faixa via crop do teto.
9. **Montar** (`scripts/03_assemble.py`): faixa b-roll no rodapé (borda coral 6px) + crop do teto + vstack; legenda visível acima do b-roll. → gera o CORPO.
9b. **GANCHO / cold open** (`scripts/05_hook.py`) — o padrão VIGENTE é o **GANCHO VIRAL** documentado na seção acima (faixa vermelha `#D32F2F` na região do strip, headline 2 linhas Bricolage weight 800, corte 0.15s antes, xfade fade 0.4 + acrossfade `c2=nofade`, hierarquia dos 107 cortes). O texto abaixo é o histórico do padrão v4 (efeito no clip + faixa coral), mantido como referência do script:
   **PADRÃO v4 (LIGADO por padrão)**: copiar a **FRASE COMPLETA mais forte** pro comecinho — **SÓ o Chefe falando, SEM b-roll**, com um **efeito** que diferencia do resto (`pb` preto-e-branco / `vhs` / `fantasma` / `tv_velha`) E a **mesma frase escrita numa faixa coral** na tela (gancho audiovisual: sonoro + visual). Depois **transição animada** (`xfade=fadeblack`) pro corpo. A frase **continua no lugar original** (é cópia, não recorte). Fonte do clip = talking-head sem b-roll (ex.: `cutvid_tight.mp4`). Ordem final: **gancho → transição → corpo → CTA (se o Chefe aprovar, ver passo 10) → música**.
   - **FRASE COMPLETA, nunca cortada na metade:** A/B têm que pegar a frase inteira (do início ao fim da fala), mesmo que passe um pouco de 5s. NUNCA cortar no meio da frase.
   - **Faixa visual (padrão v4):** texto em **MÁXIMO 2 LINHAS**, fonte ~50% menor (range 66→28px, escolhe a que cabe em 2 linhas), faixa posicionada em **centro + 15%** (terço inferior, y≈1248). Isso já está no `05_hook.py`.
   - **A agente ESCOLHE a frase sozinha (sem aprovar)**, pelos critérios: (1) potencial de viralização, (2) gera expectativa pra ver o vídeo todo, (3) frase forte e polêmica. Pega o timestamp da frase **completa** na transcrição e roda o `05_hook.py`.
10. **CTA no FINAL — PERGUNTAR ANTES DE ENTREGAR (regra do Chefe 2026-07-18):** antes de montar a entrega final, **perguntar ao Chefe se ESTE vídeo leva o CTA** (`assets/CTA_TAKE_FIXO_1080x1920.mp4`) — não é mais automático. Se ele aprovar: anexar com **transição suave** (`xfade=fade:0.7`); atenção: o asset do CTA NÃO tem stream de áudio (cauda fica muda sem música de fundo). Se ele recusar: entregar só o corpo. (`scripts/04_build_final.py` faz CTA + música.)
11. **Música de fundo BAIXINHA:** mixar trilha BEM discreta: loudnorm=I=-34:TP=-6:LRA=6 (achata o crescendo) + volume=0.38 (~25dB abaixo da fala, `amix normalize=0`, fade in/out). NUNCA sobrepõe a fala. (O Chefe costuma passar a própria trilha de suspense.)
12. **Export 4K** (lanczos) + **salvar nos bancos**: `Desktop/EDIÇÃO DE VÍDEO/BANCO-IMAGENS-GPT`, `BANCO-VIDEOS-VEO`, `VIDEOS-FINAIS-4K` (nome `PROJETO_DATA_arquivo`). Abrir no Mac.

## PARÂMETROS
- gpt-image-2: `images/generations`, size 1536x1024 (b-roll) / 1024x1536 (CTA vertical), quality high, divisível por 16. Resp `data[0].b64_json`. Chave `OPENAI_API_KEY` em `~/naia-bot/.env`.
- Veo: `veo-3.1-fast-generate-preview:predictLongRunning?key=`, body image-to-video + `parameters:{aspectRatio, negativePrompt}`. Baixar com `-L` + `&key=`. Saída 720p 8s. **Pool de chaves Gemini** (varrer `~/naia-bot` + histórico; 429=pular). Custo ~$0,10/s (720p) → take 8s = $0,80; imagem ~$0,165. Vídeo 60s ≈ $8 (~R$40).
- Submagic: `api.submagic.co/v1/projects` header `x-api-key`, templateName "Ella". Chave nova em app.submagic.co/account (a antiga expira/401).

## GOTCHAS
- Corte do topo do b-roll = crop 80px + zoom do Veo → safe-area + Veo travado resolvem.
- xfade exige timebase igual: `settb=AVTB` nos dois lados.
- rtk trunca JSON/curl no terminal → salvar em arquivo + Read.
- Rodar gerações como .py em background; ffmpeg deste Mac sem libass (legenda própria = Pillow).
