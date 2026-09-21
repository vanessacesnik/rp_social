# SANDUÍCHE 2 META (criativos da Imersão)

> Atualizado em 09/08/2026 a partir de `ATUALIZACAO-SKILL-SANDUICHE-2-META.md` (produção
> "Criativos Imersão IA na Prática", Kimi, aprovada pelo Chefe).

## O que é

Um vídeo talking-head do Chefe vira criativo pronto pra rodar na Meta em TODOS os
posicionamentos com o mesmo arquivo. Ele manda só o vídeo; o agente entrega a versão final
editada e emoldurada.

Gatilhos: "sanduíche 2", "modelo da imersão", "criativo pra meta", "mesmo formato dos criativos".

Pipeline de referência pronto e testado no Mac do Chefe, em
`~/workspace/sanduiche2-kimi/pipeline/`: `config.py` (layout, paleta, prompts de cena),
`gen_cenas.py` (imagens), `build_hf.py` (faixa), `compose.py` (queima), `anim_veo.py` (Veo),
`compose_anim.py` (queima animada), `quadro.py` (moldura). Ao replicar num agente sem acesso a
esses scripts, seguir as medidas e regras abaixo (são suficientes para reimplementar).

## A ANATOMIA (vídeo interno, 1080x1920)

De cima pra baixo, quatro camadas:

1. **Cenas do quinteto** (y=0, h=720): cenas pixel-art 3D voxel dos 5 personagens Avalanche
   encenando a fala, UMA imagem a cada chunk de 5 segundos. Não é infográfico, é cena.
2. **Take do Chefe** (y=720, h=608): a gravação em 16:9, com legenda queimada palavra a palavra
   (Bricolage Grotesque, destaque laranja `#E76F00`, janela de 5 palavras, base colada na faixa).
3. **Faixa HyperFrames** (y=1328, h=270): infográfico animado da fala, uma cena por bloco de
   sentido, copy própria escrita da transcrição. Tipografia aprovada: headline 42px, sub 21px,
   chip 20px, stat 88px, pills 18px. SEM barra de progresso (o Chefe removeu).
4. **Título/CTA** (y=1598, h=322): 3 linhas centrais: chip "IMERSÃO", título "Inteligência
   Artificial na Prática", CTA "Toquem saiba mais" em laranja.

Paleta: ORANGE `(231,111,0)` `#E76F00`, CHIP_RED `(193,18,31)` `#C1121F`, LIGHT_BG `#F7F6F4`,
LIGHT_TEXT `#2B2118`, DARK_BG `#161210`, DARK_TEXT creme `#FFF8F0`.

## AS 4 VERSÕES DE CADA VÍDEO

Tudo sai nos DOIS temas (claro e escuro). REGRA ABSOLUTA: nunca misturar tema; escuro só usa
cenas e faixas do tema escuro.

1. **Completo** 1080x1920 (com a camada 4 de CTA).
2. **Sem CTA** 1080x1598: crop exato dos 322px de baixo (`crop=1080:1598:0:0`).
3. **Animado**: igual ao completo ou sem CTA, mas a camada 1 vira vídeo Veo (abaixo).
4. **Quadro (a versão final pra Meta)**: qualquer uma das acima emoldurada (abaixo).

## A MOLDURA (proporção exata, inegociável)

Medida do modelo montado à mão pelo Chefe (09_escuro_animado_sem_cta):

- Canvas final **1080x1920**.
- O vídeo sem CTA (1080x1598) é escalado para **926x1370** e **centralizado**: margens de ~77px
  nas laterais e ~275px no topo e na base.
- Filtro ffmpeg: `scale=926:-2:flags=lanczos,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=<COR>,fps=30`.
- **A cor do fundo é UMA SÓ, fixa do primeiro ao último frame de cada vídeo.** A variação é de
  vídeo pra vídeo, nunca dentro do mesmo vídeo.
- **Criativos claros: fundo escuro `#161210`.**
- **Criativos escuros: cores quentes e vivas, uma por vídeo.** Paleta aprovada:
  01 `#E76F00`, 02 `#C1121F`, 03 `#F59E0B`, 04 `#DC2626`, 05 `#EA580C`, 06 `#D97706`,
  07 `#B91C1C`, 08 `#F97316`, 09 `#F44936` (cor do modelo feito por ele), 10 `#E11D48`.
  Em vídeos novos, sortear dessa família (vermelhos, laranjas, âmbares vivos).
- Convenção de nome: sufixo `_quadro.mp4`. Script pronto no pipeline de referência: `quadro.py`.

## AS CENAS ANIMADAS (Veo 3.1 fast)

Quando ele pedir "anima as imagens" / "versão animada":

- Modelo `veo-3.1-fast-generate-preview` (o mais barato), image-to-video, 720p, 16:9, 8s por cena.
- Preparar a imagem 3:2 de 1536x1024 para o Veo redimensionando para 1296x864 e completando
  120px em cada lateral até 1536x864. Isso preserva a composição útil no centro do 16:9.
- Cada clipe de 8s é acelerado para os 5s exatos do chunk: `setpts=0.625*PTS,fps=30`.
- O Veo entrega 1280x720 com a imagem 3:2 letterboxada: CORTAR as barras com
  `crop=1080:720:(iw-1080)/2:0` ANTES de usar. Em 1280x720 isso equivale a
  `crop=1080:720:100:0`. Barra preta lateral no criativo final é reprovação.
- Prompt trava TUDO: câmera COMPLETAMENTE ESTÁTICA (sem zoom, pan ou dolly de nenhum tipo) e
  identidade do OpenClaw como lagosta chibi humanoide. Descrever cabeça oval alta e brilhante
  vermelho-cereja, exatamente quatro antenas, olhos redondos enormes e duas garras de lagosta
  grandes, arredondadas e sempre visíveis. O corpo é largo, nunca magro ou de inseto. Uniforme:
  moletom preto Avalanche, jogger preta com listra vermelha lateral, meias e tênis brancos, sem
  troca de roupa nem acessório novo.
- Negative prompt obrigatório: ant, ant head, insect, insect face, bug, beetle, tentacles,
  skinny arms, thin body, lobster tail, extra limbs, extra antennae, missing claws, tiny claws,
  duplicate character, deformed/melting/morphing face, character transforming into an insect,
  wardrobe change, different clothes, new outfit, color change on clothes, missing hoodie, bare
  legs, changing uniform.
- Chaves no cofre 1Password `Naia-sistemas`: item `Google-Gemini`, campos `veo_key_aq_1` a
  `veo_key_aq_4`. Injetar somente com `op run`; nunca imprimir ou gravar o valor.
- As quatro chaves `veo_key_aq_*` pertencem ao mesmo projeto Gemini e compartilham a mesma cota.
  Rotacionar ajuda em falha de chave/autenticação, mas NÃO contorna `429` de cota do projeto.
  Nesse caso, persistir o estado e retomar depois da janela de cota, ou usar somente outra chave
  de projeto faturado que esteja autorizada para este trabalho.
- Persistir o nome de cada operação antes de iniciar o polling. Assim o job pode retomar sem gerar
  a mesma cena de novo. Se a operação terminar sem vídeo, marcar como falha e abrir uma operação
  nova no retry, sem ficar retomando uma resposta vazia.
- Em `503 Unable to process input image`, repetir somente a cena que falhou. Se a mesma imagem
  falhar de novo, tentar sem o último frame de referência. O primeiro e o último frame iguais
  ajudam a conter drift, mas algumas cenas só processam sem `last_frame`.
- **Antes de gastar cota, verificar se outro agente da frota já gerou Veo das mesmas cenas** e
  aproveitar, com checagem de frame antes (OpenClaw lagosta, uniforme certo, sem barras, 5s).
- Imagens aprovadas pelo Chefe ANTES de animar (regra 11 da skill: checkpoint de imagem).

### QA e recuperação de take Veo

- Cada bruto aceito precisa medir 1280x720, 24fps e aproximadamente 8s no `ffprobe`.
- Extrair quadros em 1s, 4s e 7s e conferir OpenClaw, uniforme, número de personagens, garras,
  ausência de morphing e de barras. Uma amostra só do primeiro frame não aprova o take.
- Reprovar OpenClaw como formiga/inseto, personagem duplicado, garra ausente ou pequena, troca de
  roupa, deformação e transformação de qualquer integrante do quinteto.
- Se a cota acabar e o próprio take Veo tiver um intervalo temporal limpo, é permitido recuperar
  esse mesmo take localmente: recortar apenas o intervalo aprovado, montar loop ping-pong
  (ida/volta) até 8s e então acelerar para 5s. Conferir novamente em 1s, 4s e 7s. Não fabricar
  recuperação a partir de take que nunca teve trecho visualmente aprovado.

## FLUXO COMPLETO (ele manda só o vídeo)

1. Cortar o bruto em takes por bloco de assunto (transcrição Whisper com timestamp por palavra).
2. Escrever a copy das cenas e da faixa a partir da transcrição (cena = metáfora visual da fala,
   faixa = infográfico do dado). Zero travessão em tudo que aparece na tela.
3. Gerar as cenas (1 por chunk de 5s) nos dois temas. Abrir pra ele aprovar.
4. Buildar as faixas HyperFrames (1080x270) nos dois temas. SEM barra de progresso.
5. Queimar completo + cortar sem CTA, nos dois temas.
6. Se animado: gerar clipes Veo, acelerar pra 5s, cortar barras, requeimar (completo e sem CTA).
7. Emoldurar todos os sem CTA na proporção Meta, cor por regra acima.
8. Validar com ffprobe: completo 1080x1920, sem CTA 1080x1598, 30fps, áudio AAC, duração certa e
   decode integral sem erro. Extrair frames do resultado final para conferir barras, tema e a
   presença ou ausência correta do CTA.
9. Entregar abrindo os arquivos no Mac.

## REGRAS INVIOLÁVEIS DESTE MODELO

1. Nunca misturar tema claro/escuro (cenas, HF, CTA e fundo do quadro).
2. Faixa ilustra a fala pro espectador: zero meta interno ("na fala", "cena ao vivo", dump do whisper).
3. Zero overlap de elementos na faixa (sistema de zonas; sem `data-layout-allow-overlap` pra mascarar).
4. SEM barra de progresso na faixa.
5. Sem CTA = crop `1080:1598:0:0`. Quadro Meta parte do sem CTA, não do completo.
6. Fundo do quadro: uma cor só por arquivo; claro → `#161210`; escuro → cor quente da paleta.
7. Veo só depois do checkpoint de imagem; crop lateral `1080:720:100:0` obrigatório.
