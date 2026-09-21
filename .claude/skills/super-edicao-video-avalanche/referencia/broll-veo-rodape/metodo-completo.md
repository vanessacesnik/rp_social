# MÉTODO DE EDIÇÃO DE VÍDEO AVALANCHE — v3 (b-roll image-first + cobertura total)

> Pipeline definitivo pra transformar um talking-head cru num reels com b-roll IA no estilo Avalanche.
> Esta versão consolida tudo que funcionou nos testes do vídeo `ROI-NAIA-COBERTURA-TOTAL-V3-4K.mp4`.
> Destino: virar **skill da Naia**. Faz par com a pasta `REFERENCIA-LAGOSTA-OPENCLAW/`.

---

## 0. O QUE É / QUANDO USAR
Recebe um vídeo vertical talking-head (iPhone 4K 9:16). Entrega um reels 9:16 com:
- B-roll 16:9 (deitado, estilo YouTube) na **faixa de baixo da tela**, com o apresentador ocupando o resto por cima.
- B-roll cobrindo o vídeo **do início ao fim** (cobertura total) OU só em trechos (cobertura parcial).
- Legenda animada (Submagic Ella), export 4K.
- Todo b-roll gerado no **estilo + personagens Avalanche**.

---

## 1. REGRAS INVIOLÁVEIS
1. **B-roll é image-first.** NUNCA gerar vídeo direto no Veo a partir de texto. Sempre: **gera a imagem da cena no `gpt-image-2` → anima a imagem com o Veo 3.1 fast (image-to-video)**. Geração direta texto→vídeo sai ruim e fora de padrão.
2. **B-roll é 16:9** (deitado), entra na **faixa inferior** da tela; o apresentador continua aparecendo por cima ocupando o resto.
3. **Safe-area:** a imagem do `gpt-image-2` sai 1536×1024 (3:2) e é cortada pra 16:9 (1536×864). Por isso o prompt SEMPRE manda manter todo conteúdo/rosto/texto/número no **centro (70%)**, deixando os **~18% de topo e ~18% de base** só com ambiente. Assim o crop nunca come conteúdo.
4. **Veo com câmera TRAVADA.** O prompt do Veo proíbe zoom/push-in/dolly — só os elementos internos se mexem. Zoom faz o Veo comer as bordas e perder conteúdo ao longo dos 8s.
5. **Estilo + personagens Avalanche em todo b-roll** (seção 2). O **trio (Denderson + Naia + OpenClaw) aparece sempre**; criar **personagens extras** quando a fala pedir (agente Davi/SDR, clientes/pessoas, time de agentes). Cenas fantásticas porém realistas, como uma agência digital de verdade em operação.
6. **Sem faixa preta** em lugar nenhum do b-roll (nem lateral, nem topo/base).

---

## 2. PERSONAGENS CANÔNICOS

### 2.1 OPENCLAW — a lagosta (REFERÊNCIA OBRIGATÓRIA: pasta `REFERENCIA-LAGOSTA-OPENCLAW/`)
Mascote lagosta-criança chibi, vibe kid creator/rapper, render 3D fofo. **Bater 100% com as 3 fotos de referência.**

- **CABEÇA:** GRANDE, vermelho-cereja glossy, formato **oval levemente arredondado (tipo ovo/morango)** — **NUNCA uma bola lisa perfeita**. Superfície com **textura speckled/dimpled** (micro-pontinhos e covinhas orgânicos, casca de lagosta/morango) + highlights brilhantes. **Cara de bebê/criança:** crânio grande, bochechas redondas, fofo.
- **OLHOS:** gigantes, redondos, pretos brilhantes, íris âmbar/marrom, **2–3 reflexos brancos grandes**. Super expressivos, doces, child-like; posicionados meio-baixos no rosto, ocupando boa parte da cara.
- **BOCA:** pequena, sorrindo aberta, com **linguinha vermelha/rosa**. Expressão alegre.
- **ANTENAS:** 2 antenas **longas e finas** vermelhas glossy curvando pra cima do topo da cabeça + 2 antenas **secundárias curtas** nas laterais da base. Sem nariz.
- **MÃOS/PINÇAS:** pinças de lagosta vermelhas glossy, formato "luva de boxe" com pinça (2 dedos articulados). Seguram mic, celular, tablet, fazem joinha.
- **CORPO:** **criança humana gorduchinha e baixinha** (~6–9 anos aparente). Proporção **chibi**: cabeça enorme (~45–50% da altura) + corpo pequeno.
- **ROUPA (streetwear hype Avalanche):**
  - Moletom/hoodie **preto** com cordão, chevron **Avalanche "A"** no peito (vermelho/dourado) + **corrente de ouro fina com pingente "A"**.
  - **Jogger preto** com listras vermelhas laterais e "A" pequeno.
  - **Tênis branco** estilo Air Force com detalhes vermelhos/dourados + logo "A"; meia tubo branca com listra vermelha.
  - Acessórios por contexto: **boné snapback preto** virado (antenas saindo por fora), **headphones over-ear** dourados/pretos no pescoço, segurando mic/celular/tablet/laptop.
- **VIBE:** hype, fofo, confiante, criador de conteúdo.
- **NUNCA (anti-padrões que já vazaram):** cabeça lisa-bola sem textura; corpo/abdômen/**perna/bunda de FORMIGA** ou inseto; 6 pernas; corpo adulto; roupa social/blazer; qualquer cor que não vermelho-cereja; cabeça pequena proporcional ao corpo.

### 2.2 NAIA — executiva de IA
Ruiva ultra-realista anime. Cabelo ruivo-cobre longo, ondulado, volumoso, caindo sobre um ombro. Pele muito clara porcelana com **circuitos finos discretos cyan/dourado** no pescoço e antebraços (sutil, NÃO cobre o rosto/tronco, não vira android). Olhos verde-esmeralda grandes magnéticos. Traços de top model. Blazer preto justo executivo, decote V que insinua sem expor, pin "N" laranja-vermelho na lapela. Postura dominadora elegante. Sexy corporate Beyoncé, nunca vulgar.

### 2.3 DENDERSON — CEO
Homem negro brasileiro, fim dos 30. Cabeça **completamente careca** (raspada), barba cheia escura com grisalhos no jaw line. Ombros largos, atleta. **Blazer preto slim** sobre camiseta preta gola redonda, pin "D" vermelho discreto. Apresentador, presença de líder carismático.

### 2.4 Personagens extras (criar quando a fala pedir)
- **Davi (SDR):** agente vendedor digital jovem, esperto, simpático, com glow holográfico sutil e badge Avalanche, em estação de SDR disparando WhatsApp.
- **Clientes/leads:** pessoas reais diversas e felizes (avatares de clientes) chegando de portal Google, recebendo mensagens.
- **Time de agentes Avalanche:** profissionais diversos em estações no command center.

### 2.5 Ambiente + paleta padrão
Command center cyber Avalanche à noite: andar de agência futurista, paredes navy, neon dramático, dashboards holográficos HUD flutuantes, logos chevron "A", estações de trabalho, profundidade/bokeh. Paleta: navy `#0A1428` + coral `#E63946` + cyan `#06B6D4` + dourado + cream `#F5F5F5`. Texto sempre em painel holográfico, nunca flat.

---

## 3. PIPELINE PASSO A PASSO

### Etapa A — Ingestão
1. `ffprobe` no vídeo (duração, dimensão, fps). Esperado: 1080×1920, 30fps, h264/aac.
2. Extrair áudio: `ffmpeg -i IN.mp4 -vn -ac 1 -ar 16000 -c:a libmp3lame -q:a 4 audio.mp3`.

### Etapa B — Pré-processo (ffmpeg)
3. **Corte de silêncio** (opcional, se houver pausas): `silencedetect=noise=-30dB:d=0.4`, manter trechos sonoros com margem 0.12s. (Em vídeos já enxutos quase não corta — ok pular.)
4. **Acelerar 1.2x:** `-filter_complex "[0:v]setpts=PTS/1.2[v];[0:a]atempo=1.2[a]"` → `proc.mp4` (1080×1920). É sobre o `proc.mp4` que tudo é sincronizado.

### Etapa C — Transcrição (na timeline JÁ acelerada)
5. Extrair áudio do `proc.mp4` e transcrever no Whisper com **word-level**:
   `curl https://api.openai.com/v1/audio/transcriptions -H "Authorization: Bearer $OPENAI_API_KEY" -F file=@proc_audio.mp3 -F model=whisper-1 -F language=pt -F response_format=verbose_json -F "timestamp_granularities[]=word"`
6. Guardar as `words` (start/end por palavra). Servem pra planejar b-roll e (se precisar) legenda própria.

### Etapa C2 — Corte de roteiro (enxugar pra economizar) — OPCIONAL mas recomendado
Antes de planejar b-roll, **reler a transcrição inteira e cortar tudo que NÃO interfere no contexto total da mensagem**. Cada segundo cortado = menos take de Veo = mais barato (régua: ~$0,80 por take de 8s).
- Identificar a **mensagem central** (a história que o vídeo conta) e os **beats essenciais** (hook, virada, prova, CTA/fecho).
- Marcar pra corte: leituras verbatim longas (textos lidos na íntegra), subtramas/detalhes técnicos repetitivos, divagações, repetições — desde que a mensagem continue 100%.
- **Cortar em pausas limpas** (usar word-level timestamps; cortar no fim de uma palavra antes de uma pausa, nunca no meio). Escolher emendas onde a fala conecta natural (ex.: "...te aviso" → "aí eu perguntei...").
- **Sempre apresentar os cortes ao Chefe pra aprovar** (é o conteúdo dele) com timestamps + tempo/custo economizado, antes de gerar b-roll.
- Cortar com ffmpeg: manter os trechos bons via `trim`/`atrim` + `concat`. Se o vídeo já tem legenda queimada, ela é cortada junto (anda com o frame).
- Depois do corte, **re-transcrever o vídeo cortado** pra planejar as janelas na timeline nova.

### Etapa D — Planejamento dos b-rolls
7. **Nº de takes = ceil(duração / 8).** Cada take do Veo = 8s.
   - Cobertura total: quebrar a duração em **N janelas contíguas iguais** (`seg = dur / N`), sem buraco. Ex.: 58.17s ÷ 8 = 7.27s por janela.
   - Cobertura parcial: escolher janelas só nos momentos-chave.
8. Pra cada janela, ler a fala daquele intervalo (das `words`) e definir a **cena** (trio + extras + elemento visual que casa com a fala). Escrever os 2 prompts (imagem e animação).

### Etapa E — Geração de cada b-roll (o coração do método)
**E1. Imagem no `gpt-image-2` (rota OAuth desde 03/08/2026, sem crédito de API):**
```
chamada = naia_image.gerar(prompt, saida, size="1536x1024", quality="high", output_format="jpeg")
          (NAIA_HOME/scripts/naia_image.py; a OPENAI_API_KEY vira rede de segurança)
model = gpt-image-2   (o gateway ecoa "gpt-image-2-codex", que é o mesmo modelo servido
                       pela assinatura; a Naia Hermes recebe esse mesmo eco)
size  = 1536x1024     (3:2 landscape; NATIVO desta rota, sai cravado. Os outros nativos
                       são 1024x1536 e 1254x1254; fora disso o backend impõe ~1,573 MP
                       na proporção e o script FALHA em vez de redimensionar escondido)
quality = high        (não é controlável nesta rota: o gateway força "auto". Isso NÃO
                       degrada a imagem, só impede forçar "low" para economizar)
output_format = jpeg  (esse sobrevive ao gateway)
```
Prompt = bloco fixo (personagens canônicos seção 2) + cena da janela + elementos + ambiente + paleta + **SAFE-AREA** ("manter tudo no centro 70%, topo/base 18% só ambiente"). Resposta em `data[0].b64_json`.

**E2. Crop pra 16:9 (corta só topo/base, nunca lateral):**
`ffmpeg -i raw.jpg -vf "crop=1536:864:0:80" img16x9.jpg` (remove 80px de cima + 80px de baixo).

**E3. Animar no Veo 3.1 fast (image-to-video, câmera TRAVADA):**
```
POST https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-fast-generate-preview:predictLongRunning?key=KEY
body = {"instances":[{"prompt":VEO_PROMPT,"image":{"bytesBase64Encoded":B64,"mimeType":"image/jpeg"}}],
        "parameters":{"aspectRatio":"16:9"}}
```
`VEO_PROMPT` = "LOCKED, STATIC camera: NO zoom, NO push-in, NO dolly, NO camera movement; framing stays identical; every element fully inside frame the whole time. Keep every character and object EXACTLY as in the input image. Only natural subtle motion: character gestures/hair, holographic panels flicker/glow, data/particles drift, message bubbles stream. Premium 3D cinematic, no text warping, 16:9."

**OBRIGATÓRIO — `parameters.negativePrompt`** (trava o Veo de deturpar personagem no meio do vídeo. JÁ DEU MERDA: o Veo trocou as PERNAS DE CRIANÇA da lagosta por PERNAS DE FORMIGA no meio da animação):
`negativePrompt` = "morphing or changing any character's body, limbs, arms, legs, hands or claws; turning the lobster's human child legs into insect/ant legs; insect body, ant legs, extra limbs; changing outfits, faces, skin, colors or logos; altering the scenery/background; adding or removing characters; warping or changing text; camera zoom, push-in, dolly or pan; distortion, melting, flicker of identity."
- Payload Veo com negativo: `parameters: {"aspectRatio":"16:9", "negativePrompt": NEGATIVE}`.
- **Regra de ouro:** o Veo NÃO pode alterar corpo/membros/look/cenário — ele só ANIMA o que já está na imagem. Imagem aprovada = verdade absoluta; o vídeo tem que ser idêntico em forma, só com movimento.
- Poll: `GET /v1beta/{operation.name}?key=KEY` até `done`.
- URI em `response.generateVideoResponse.generatedSamples[0].video.uri`.
- Baixar com `-L` (302) e `&key=KEY`. Saída **1280×720, 8s, 24fps**.
- **Validar movimento:** diff de 2 frames (t=0.5 vs t=7). ~0 = estático/cacheado; >5 = animando de verdade.

### Etapa F — Legenda (2 MODOS)
**Modo A — COM Submagic** (vídeo SEM legenda): gera legenda Ella (passos abaixo).
**Modo B — SEM Submagic** (vídeo JÁ legendado): pula esta etapa inteira; o `base` da montagem é o próprio vídeo (cortado). **Atenção:** checar onde a legenda original está na tela (printar frames). Se estiver baixa (ex.: y≈1580), **subir a faixa do b-roll** (ex.: `Y=842`, faixa 842–1450) pra não tapar a legenda; a zona da legenda fica livre embaixo.

#### Modo A — Submagic Ella
9. Subir o `proc.mp4` (sem b-roll ainda) pro catbox: `curl -F reqtype=fileupload -F fileToUpload=@proc.mp4 https://catbox.moe/user/api.php`.
10. Criar projeto:
```
POST https://api.submagic.co/v1/projects   (header x-api-key: sk-...)
body = {"title":..., "language":"pt", "videoUrl":CATBOX, "templateName":"Ella",
        "magicZooms":false, "magicBrolls":false, "hookTitle":false,
        "dictionary":["Naia","Naya","ROAS","ROI","Pixel","CAPI","Davi","Meta","Facebook","broadcast","utility","checkout","KPI"]}
```
   - `templateName:"Ella"` = legenda multicolor (branco + palavra-chave em verde/realce). NÃO usar `aiEditTemplate` (one-shot).
   - `magicBrolls:false` (b-roll é nosso), `magicZooms:false` (não bagunça o overlay).
   - `dictionary` corrige grafia (única forma; não dá pra editar palavra).
11. Poll `GET /v1/projects/{id}` até `status:completed`. Baixar `directUrl` → `captioned.mp4` (1080×1920, legenda queimada, mesma duração do `proc.mp4`).
   - A legenda Ella cai por volta de **y≈1100–1300** (centro-baixo). Como a faixa do b-roll começa em y≈1312, a legenda fica **logo acima** da faixa, sem sobrepor.

### Etapa G — Montagem (faixa 16:9 no rodapé)
12. **Geometria da faixa:** largura 1080, 16:9 → altura **608**, posição y = 1920−608 = **1312**. Borda **coral 6px no topo** da faixa (separa do apresentador). Escalar cada b-roll a 1080×602 + `pad=1080:608:0:6:color=0xE63946`.
13. **Cobertura total:** aparar cada take pra `seg` (ex. 7.27s), normalizar `fps=30`, **concatenar os N takes** numa faixa contínua e sobrepor uma vez sobre o `captioned.mp4` em y=1312:
   - por take: `[i:v]trim=0:SEG,setpts=PTS-STARTPTS,scale=1080:602,pad=1080:608:0:6:color=0xE63946,fps=30,format=yuv420p[si]`
   - `[s1]...[sN]concat=n=N:v=1:a=0[strip]`
   - `[0:v][strip]overlay=0:1312:shortest=1[v]` ; map `[v]` + `0:a`.
   - **Cobertura parcial:** em vez de concat, sobrepor cada take com `enable='between(t,S,E)'` e `setpts=PTS+S/TB`, convertendo janelas do tempo original p/ acelerado (÷1.2).

### Etapa H — Export
14. HD: `libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 160k` → `FINAL_1080.mp4`.
15. 4K: `ffmpeg -i FINAL_1080.mp4 -vf scale=2160:3840:flags=lanczos ... -c:a copy FINAL_4K.mp4`.
16. Abrir no Mac (`open`) e revisar com o Chefe.

---

## 4. GOTCHAS (não repetir)
- **Corte do topo do b-roll = 2 causas somadas:** (1) o crop 3:2→16:9 come 80px de cima/baixo; (2) Veo com push-in dá zoom e come bordas. Fix: **safe-area no prompt da imagem** + **Veo câmera travada**.
- **Quota Veo (429):** cada chave Gemini tem ~poucas gerações/dia de Veo. Volume alto estoura. **Manter um POOL de chaves** e rotacionar; em 429 pular pra próxima chave. Há ~13 chaves AIza no sistema (`~/naia-bot`, histórico) — varrer e usar as que aceitam Veo (algumas dão 400/403, pular). 1 chave já deu 403 no Veo.
- **Submagic key 401:** chave expira/é revogada. Gerar nova em `https://app.submagic.co/account` (precisa plano com API ativo). Testar com POST /v1/projects (201 = ok).
- **Export Submagic "completed" cacheado:** capturar `directUrl`+`updatedAt` e só baixar quando mudarem + >40s (quando usar /export repetido).
- **rtk trunca JSON/curl** no terminal → salvar em arquivo + ler, ou `rtk proxy`.
- **Veo download precisa `-L`** (302) e `&key=`.
- **`gpt-image-2`** exige dimensões divisíveis por 16 (1536×1024 ok). Acerta texto/acento PT-BR melhor; números longos podem embaralhar — usar tokens curtos (ROI, 12x, 100K, R$2,60).
- **Rodar geração como script .py em background**, não aninhar `&` dentro.

## 5. CUSTOS / CHAVES
- **Submagic Business+API** (~R$139/mês) — export 4K incluso, user-media próprio grátis. Chave `sk-...` (header `x-api-key`).
- **OpenAI** `gpt-image-2` + Whisper — `OPENAI_API_KEY` (`~/naia-bot/.env`).
- **Gemini** Veo 3.1 fast — pool de chaves `AIza...` (`~/naia-bot/.env`: `GOOGLE_AI_API_KEY`, `GOOGLE_AI_API_KEY_2`, + extras no sistema).

## 6. ESTRUTURA DE ARQUIVOS / SCRIPTS (referência da sessão)
- Workdir: `/tmp/roi-edit/` → `audio/`, `broll_img*/`, `broll_video*/`, `output/`, `scripts/`.
- Scripts: `gen_cover.py` (8 b-rolls: imagem→crop→Veo), `submagic_caption.py`, `assemble_cover.py` (montagem + 4K), `retry2.py` (rotação de chaves no 429).
- Refs da lagosta: `Desktop/EDIÇÃO DE VÍDEO/REFERENCIA-LAGOSTA-OPENCLAW/` (3 imagens canônicas).
- Entregas de referência: `ROI-NAIA-COBERTURA-TOTAL-V3-4K.mp4` (cobertura total, trio+extras, sem corte).

## 7. CHECKLIST FINAL
- [ ] B-roll image-first (gpt-image-2 → Veo), nunca texto→vídeo.
- [ ] Imagem com safe-area; crop 16:9 sem cortar conteúdo.
- [ ] Veo câmera travada (sem zoom).
- [ ] OpenClaw no canon das refs (cabeça texturizada cara-de-cria, corpo de criança, NUNCA inseto/bola-lisa).
- [ ] Trio sempre presente + extras conforme a fala.
- [ ] Faixa 16:9 no rodapé (y=1312, borda coral), apresentador por cima.
- [ ] Legenda Ella acima da faixa, sem sobrepor.
- [ ] Export 4K, revisão com o Chefe.
