# MODELO: VSL LONGA (10-15 min, multi-versao)

> Migrado VERBATIM da skill `edicao-vsl-avalanche` em 2026-07-25, na unificação da
> `super-edicao-video-avalanche`. Nada foi resumido: o que estava escrito continua escrito.
> Acervo deste modelo: `usa assets de broll-faixa-hyperframe e broll-veo-rodape` (os caminhos `scripts/`, `assets/`, `references/`
> citados no texto abaixo agora vivem sob essas pastas).
> O que e COMUM a todos os modelos (perguntas de abertura, plataforma, corte fino,
> gancho e QA) mora em `nucleo/` e vale aqui tambem.

---

# Edição VSL Avalanche (v1 — validada no projeto VSL-20M, 2026-07-20/21)

Transforma VSL crua de iPhone (talking-head vertical) + hooks gravados à parte em N versões finais 1080x1920 com faixa Hyperframe, legendas, imagens ilustrativas e trilha 2 atos. Aprovada pelo Chefe de ponta a ponta.

## FORMATO CANÔNICO (canvas 1080x1920)
- **Bloco do apresentador (topo): 1080x1312** — proporção ~0,82:1 (o que sobra do 9:16 após a faixa).
- **Faixa Hyperframe (rodapé): 1080x608 = 16:9 exato**, 100% do vídeo, 1 take ilustrado a cada 10s.
- **NENHUMA BARRA DE PROGRESSO em nenhum take** (o player VTurb tem a dele). O Chefe gritou essa regra — INEGOCIÁVEL.
- Faixa no padrão de ZONAS da skill `broll-faixa-hyperframe` (zona esquerda kicker+headline ≤2 linhas, corredor 48px, zona direita com O visual, gate `check` com 0 layout issues). Elementos premium variados (count-up, gauge, barras, comparação, carimbo); NUNCA a frase transcrita como legenda; nomes corrigidos na arte (Naia, Claude Code, IA).
- **Legibilidade 50+ (feedback do Chefe, VSL Patricia)**: público maduro NÃO enxerga letra miúda — na faixa 1080x608, mínimos: kicker ≥38px, sub ≥40px, labels de visual ≥32px, bolha de chat ≥34px, headline 72-88px. E OCUPAR o espaço da faixa (margens internas ~40-56px, visual preenchendo a zona direita) — não coube, ENCURTA o texto, nunca reduz a fonte.
- **Paleta por público**: conteúdo do Denderson = Avalanche dark. Conteúdo de terapeutas/Luz da Serra (ex. VSL Patricia) = paletas dos 100 carrosséis do app de terapias (`~/CURSOR 2/luzdaserra-terapias/public/carrossel-modelos*.js`; validadas na seção "PALETAS DO PORTAL DE TERAPIAS" da skill broll-faixa-hyperframe — orgânico botânico, cristais, sino tibetano, mandala etc.), NUNCA o tema Avalanche dark.
- **VSL gravada em TAKES soltos** (ex. Patricia): transcrever todos, buscar o roteiro oficial do sistema do cliente, mapear take→bloco do roteiro, identificar regravações (a mais tardia costuma vencer) e recomeços dentro do take (a instrução de gravação é "errou, respira e recomeça a frase" — cortar a leitura suja, ficar com a última limpa), montar na ordem do roteiro. Nomes Telegram sequenciais = ordem de gravação. GOTCHA: vídeo via Telegram chega comprimido (~464x848) — pedir reenvio "como arquivo" antes de editar.
- Legenda Bricolage ExtraBold palavra-por-palavra (creme #efe6da, 15-20% impacto em vermelho #e02128, sombra+stroke), **COLADA acima da faixa: centro da palavra em y≈1230 do bloco 1312** (clamp de descendentes em y=1300). Correções de exibição: "de A"→"de IA", "Cloud Code"→"Claude Code", "Naya/NAIA"→"Naia", "Anderson"→"Denderson", "R"→"R$".

## SINCRONIA LABIAL — A REGRA Nº1 (o Chefe brigou feio; custou reconstrução total)
**NUNCA cortar/emendar vídeo+áudio por TEMPO.** Trim por tempo quantiza o vídeo pra frame e corta o áudio no sample exato → ~33ms de descasamento POR CORTE que ACUMULA (78 cortes = 0,9s de drift progressivo, lábio totalmente fora no fim do vídeo e em qualquer cold open copiado do miolo).
1. Normalizar a fonte pra **CFR 30fps** primeiro (iPhone é levemente VFR): `src_cfr.mkv`.
2. Todo corte por **ÍNDICE**: vídeo `trim=start_frame=N:end_frame=M`, áudio `atrim=start_sample=N*1600:end_sample=M*1600` (48kHz/30fps → 1600 samples por frame, casados por construção).
3. Após 1.2x (`setpts=PTS/1.2` + `atempo=1.2`), usar `aresample=async` pra absorver arredondamento do atempo.
4. **GATE DE ACEITE: duração de áudio == duração de vídeo, diferença <1 frame** (mismatch é o smoking gun do drift).
5. Emenda de versões: vídeo = head re-encodado + cauda `-c copy` a partir de keyframe forçado; **áudio da versão inteira renderizado contínuo** num único `acrossfade=d=0.4:c1=tri:c2=nofade`, ancorado em `round(OFF*48000)` samples (o acrossfade ancorado no stream AAC do hook cria offset de 1-19ms — proibido; emenda `-c copy` de áudio dá 86ms — proibido).
6. **AUDITORIA LABIAL OBRIGATÓRIA, NÃO AMOSTRAL** antes de entregar: 3 pontos por versão (meio do hook, t≈300, t≈620) — whisper-1 no PRÓPRIO arquivo final, palavra plosiva (p/b/m), frames ±3 do onset lidos com Read, fechamento labial ≤1 frame do onset. Prova extra objetiva: MAD frame-a-frame vs fonte = 0 e correlação cruzada de áudio = 0 samples em 2 pontos por versão. O Chefe NÃO vai assistir 6 vídeos caçando lábio — a carga de prova é NOSSA.

## PIPELINE (ordem validada)
1. **Ingestão**: achar o cru (Downloads, o mais recente), ffprobe, frames de confirmação. Selfie de iPhone vem ESPELHADA (rotation=90 + mirror) → **hflip obrigatório** se houver texto/placa em cena (mostrar preview pro Chefe).
2. **Transcrição** whisper-1 API (word+segment, salvar JSON direto em arquivo) + silencedetect (-30dB:0.35, pad 0.10).
3. **Cortes de roteiro**: propor com timestamps + motivo; **extrair os trechos como clipes e abrir no Mac** pro Chefe assistir o que sai (ele aprova/veta item a item). Silêncios cortados por padrão. 1.2x se não houver legenda queimada.
4. **Enquadramento**: crop aprovado por preview. No VSL-20M: cintura pra cima com zoom = `crop=872:1060:104:400,scale=1080:1312:flags=lanczos` (opção B; largura total com teto de volta = opção A). Altura fixa 1312 força o trade-off — SEMPRE mostrar as 2 opções em frames reais.
5. **Corpo base** com corte frame/sample-exato (regra nº1) + gate + auditoria labial 6 pontos. **Re-transcrever o corpo final** (timeline novo é a fonte da verdade das legendas/faixas/imagens).
6. **Preview de ~20s do formato completo** (crop + 2 takes de faixa + legenda) → aprovação do Chefe ANTES da queima total.
7. **Specs de takes** (janelas iguais ~10s com a fala de cada) → **enxame Workflow** (~4 takes/agente, Opus) desenhando as faixas; exemplar aprovado como referência de estilo.
8. **Bloco legendado** (crop + legendas com timings do transcript do corpo final).
9. **Aberturas**: hooks gravados à parte (aparar pontas, hflip, 1.2x, crop próprio por hook — são closes, Y varia) + cold opens internos garimpados da transcrição (20-30s, frase completa autossuficiente, hierarquia: número chocante > contraintuitivo > "você" > open loop > pico emocional; janelas quantizadas no grid de frames). Cold open = cópia (o trecho repete no lugar original), extraída por índice do corpo final. Transição `xfade=fade:0.4` + `acrossfade c2=nofade` em todas.
10. **Camada de imagens estáticas** (conceito do Chefe): ~1 a cada 30s FLEXÍVEL — critério-mestre é fala impactante; imagem gpt-image-2 ilustrando LITERALMENTE aquele momento, **3.0s na tela cobrindo o bloco inteiro (EXCEÇÃO: imagens de TELA DO SISTEMA/portal ficam 5.0s — o público precisa ler), zoom Ken Burns 1.00→1.06, LEGENDA POR CIMA da imagem** (re-renderizar as palavras da janela), faixa e áudio intactos, entrada/saída secas. **Regra editorial POR PÚBLICO — VSL do Denderson: história pessoal = REALISTA cinematográfico (sem rosto identificável), Naia/agentes/resultados = SQUAD Avalanche (canon em edicao-video-avalanche/references/personagens-canon.md). VSL de CLIENTE (ex. Patricia/terapeutas): TODAS as imagens cinematográficas realistas, NUNCA os personagens Avalanche nem quando fala de IA** (o squad não conversa com o público do cliente; IA vira cena realista — atendimento respondendo sozinho no celular, consultório cheio, telas reais do sistema). +1 imagem EXCLUSIVA por gancho no pico. Janela nunca cruza fronteira de cold open nem contém ponto de xfade. Fluxo: 2 imagens + teste queimado → aprovação de estilo → plano completo (seleção+prompts) → enxame gera → galeria no Mac → aprovação → queimar TUDO num passe só (integrar no vstack do corpo). gpt-image-2: 1024x1536 high, crop central 1024x1244 → 1080x1312; salvar b64 via arquivo (rtk trunca).
11. **Trilha em 2 atos**: TENSÃO do 0 até a frase da abertura do botão/checkout ("E abaixo desse vídeo tem um botão...") → crossfade 2s → VITÓRIA/prosperidade até o fim. **Volume: ~18-19dB abaixo da fala** (loudnorm=I=-34:TP=-6:LRA=6 + volume=0.95; o 0.38/25dB da skill de reels ficou INAUDÍVEL — o Chefe mandou subir). Ponto da virada achado por whisper NO ARQUIVO (transcript full-file tem ~0.3s de jitter — a autoridade é whisper em janela do arquivo real). Virada por versão = virada_corpo + (dur_hook − 0.4). Preview de 44s da virada pro Chefe aprovar música e volume.
12. **Mixagem = ÚLTIMO passe, só áudio**: `-c:v copy` (nb_frames idênticos antes/depois — verificar), mix pra temp + verificação + mv atômico. NUNCA re-encodar vídeo com sync já provado.
13. **Entrega**: pasta ENTREGA/ com nomes `V{n}_{HOOK|INT}{x}_{slug}.mp4`; cópias pros bancos `Desktop/EDIÇÃO DE VÍDEO/` com prefixo `PROJETO_DATA_`. Aviso oficial de "lote fechado" com tabela de provas (durações ao ms, auditoria labial, imagens, virada por versão). "Concluído" só com TUDO em ✅.

## CHECKPOINTS DO CHEFE (na ordem)
Enquadramento/flip → cortes de roteiro (clipes abertos) → preview 20s do formato → [queima total] → 2 imagens+teste → galeria completa → preview da trilha/volume → lote final. Ele responde por partes — travar cada aprovação recebida e seguir; máximo 1 pergunta por vez.

## GOTCHAS (todos vividos no VSL-20M)
- **`ls` pode voltar mascarado/"vazio" pelo hook rtk** — pra timestamps/estado de arquivo, usar `stat -f` direto. NUNCA afirmar "pasta vazia" sem stat/find.
- **Workflow args chega como string**: `const A = (typeof args==='string') ? JSON.parse(args) : args`.
- **Agente "aguardando" está morto**: esperas SEMPRE em foreground com time.sleep; ressuscitar com ordem explícita se parar.
- `-shortest` corta conteúdo quando o áudio é mais curto (corpo → usar apad) mas crava duração quando o áudio é mais longo (hooks → usar -shortest). Decidir por caso, sempre com gate de duração.
- Keyframe forçado pode cair 1-2 frames depois do pedido — o split head/tail usa o keyframe REAL (ffprobe), não o pedido.
- xfade exige `settb=AVTB` nos dois lados. Veo não entra nesta skill (imagens são estáticas com Ken Burns).
- Encode pesado UM por vez com gate `load<45` (INEGOCIÁVEL da skill-mãe).
- Fonte Bricolage variável: instanciar weight via fontTools; render de legenda via Pillow (ffmpeg do Mac sem libass/freetype).
- Multi-versão com cold opens: fronteiras dos INTs e janelas de imagem NUNCA se cruzam; revalidar tudo se o timeline do corpo mudar (remap por palavra-âncora, não por offset fixo).

## VARIANTE: FORMATO EMPILHADO 8:9 (validada na VSL Rita Machado, 21/07 — vídeo HORIZONTAL 16:9)
Quando o cru é paisagem 1920x1080 (VSL de página de vendas): canvas 1920x2160 (8:9) = faixa Hyperframe 16:9 FULL (1920x1080) EM CIMA + vídeo original intacto EMBAIXO. Faixa com zonas proporcionais (corredor ~80px), letras 50+ escaladas (kicker ≥56, sub ≥60, labels ≥48, headline 110-150px). Identidade extraída dos materiais REAIS do cliente (amostragem de pixel das capas/artes; peças reais recortadas nos nichos — nunca desenhar em SVG). Brief timestampado do cliente: validar CADA timestamp contra a transcrição (÷ o fator de aceleração), corrigir texto de tela pro que é FALADO, e recalcular janelas com as INSERÇÕES (depoimentos em 1.0x substituem tela+áudio e somam tempo; na faixa de cima, autorar cartelas de preenchimento pros blocos de inserção). Overlays no bloco de baixo: prints verticais com moldura dourada sobre blur, imagens IA full-frame com Ken Burns, cartelas lower-third na identidade (PIL), cronômetro real quando pedido. Música conforme brief (ex. leve contínua + swell breve), volume SEMPRE recalibrado na voz do locutor (alvo 18-19dB abaixo da fala ativa — o nominal muda por pessoa). GOTCHAS novos: 30 overlays num filtergraph só degrada em swap — encadear por CONCAT de segmentos (≤1 overlay/segmento); `-loop 1` em zoompan de cartela gera frames infinitos; VIGIA por telemetria (Monitor medindo tamanho/duração/hash de áudio do arquivo) em vez de confiar no relato do agente — ETA só por taxa de escrita medida.

## RELAÇÃO COM OUTRAS SKILLS
- `broll-faixa-hyperframe`: fonte do sistema de zonas e do workflow de barras.
- `edicao-video-avalanche`: reels curtos (b-roll Veo, CTA, gancho viral de recorte) — NÃO misturar; lá a música é 25dB abaixo, aqui 18-19dB.
- Personagens/canon: `edicao-video-avalanche/references/personagens-canon.md`.
