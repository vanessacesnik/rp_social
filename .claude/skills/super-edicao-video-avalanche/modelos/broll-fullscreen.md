# MODELO: B-ROLL TELA CHEIA a cada ~3s

> Migrado VERBATIM da skill `broll-fullscreen` em 2026-07-25, na unificação da
> `super-edicao-video-avalanche`. Nada foi resumido: o que estava escrito continua escrito.
> Acervo deste modelo: `assets/broll-fullscreen` (os caminhos `scripts/`, `assets/`, `references/`
> citados no texto abaixo agora vivem sob essas pastas).
> O que e COMUM a todos os modelos (perguntas de abertura, plataforma, corte fino,
> gancho e QA) mora em `nucleo/` e vale aqui tambem.

---

# B-ROLL FULL-SCREEN (b-roll cobre a tela a cada ~3s — reels e vídeos talking-head)

Formato: vídeo talking-head vertical 9:16 do Chefe. O b-roll cobre a tela inteira por cima, a **voz do
Chefe continua contínua por baixo** o tempo todo. **Regra de ouro: o rosto dele aparece no máximo 3
segundos por vez** — a cada ~3s entra um b-roll. Serve pra reels (o caso mais comum) e pra VSL.

## REGRAS INEGOCIÁVEIS (o Chefe brigou por cada uma)
1. **Rosto ≤3s por vez.** Garantido pelo MODELO JANELADO (abaixo). O vídeo ABRE no t=0 já com b-roll (sem rosto na abertura).
2. **B-roll pinado no timestamp EXATO da fala** (transcrição). Se entrar adiantado/atrasado, fica "deslocado" e o Chefe percebe na hora.
3. **Personagens só com aprovação:** Veo é caro. SEMPRE gera a IMAGEM primeiro (gpt-image-2) → abre pro Chefe aprovar → SÓ ENTÃO anima no Veo. NUNCA anima sem aprovar (já queimou R$50 fazendo isso).
4. **Personagens fiéis ao canon:** ancorar a geração de imagem nas refs de b-rolls aprovados (`images.edit` com frames de referência), e seguir `knowledge/personagens/SQUAD-AVALANCHE-CLAUDINHO.md` (Naia ruiva circuitos cyan; Denderson careca+barba; OpenClaw lagosta cherry speckled — NUNCA Siri Cangrejo/bola lisa; Claudinho cubo laranja `>‹`).
5. **Velocidade na timeline:** clipe de personagem (Veo + aproveitados) entra a **2x** (`setpts=0.5*PTS`, 8s→4s). Hyperframe a **1x**, **90% de opacidade** (rosto aparece de leve por trás). 9:16 sem faixa preta.
6. **Sem faixa preta no Veo:** clipe do Veo vem com letterbox embutido → `cropdetect` + crop + `scale=...:force_original_aspect_ratio=increase,crop=1080:1920` → salvar `*-fill.mp4`. Montar SEMPRE com os `-fill`.
7. **Preço (se houver oferta):** mostrar "12x R$30,00 / R$297 à vista", NUNCA centavos quebrados (27,25/29,90).

## GANCHO VIRAL (obrigatório desde 2026-07-19)
Todo reels editado ABRE com o gancho, no padrão da skill **`edicao-video-avalanche`** (seção GANCHO VIRAL lá, regras completas): frase-gancho autossuficiente de 3-8s tirada de DENTRO do vídeo, escolhida pela hierarquia (1º número chocante, 2º afirmação contraintuitiva/polêmica, 3º implicação do "você", 4º open loop, 5º pico emocional; nunca abrir em saudação), recortada do arquivo final e colada NA FRENTE (a frase repete no lugar original, cold open). Corte ~0.15s antes da 1ª palavra, fim em 0.3-0.4s de silêncio ou boundary (whisper word-level, nunca cortar palavra); transição `xfade=fade:0.4` + `acrossfade=d=0.4:c1=tri:c2=nofade`. No formato TELA CHEIA (sem faixa), a headline em 2 LINHAS caixa alta vai num **card vermelho `#D32F2F` na base do quadro**, mesma fonte Bricolage Grotesque weight 800 branca e mesmas regras de auto-fit/margens da edicao-video-avalanche.

## FLUXO
1. **Transcrever** o áudio com a API OpenAI `whisper-1` (NÃO whisper local — erra). Copiar o áudio pra caminho ASCII (acento/vírgula quebram o `-F @` do curl). `verbose_json` + `timestamp_granularities[]=segment,word`.
2. **Mapear cada b-roll** pinado no timestamp da frase. Momentos de IA/agentes/o-que-os-agentes-fazem → **personagens**; resto → **Hyperframe**. Seja generoso com personagem onde fala de IA. (Não precisa quebrar o vídeo em partes — monta o vídeo inteiro de uma vez. Pra vídeo MUITO longo dá pra fatiar pra trabalhar por pedaço, mas é opcional, não regra.)
3. **Hyperframe (grátis, paralelo):** dispara um Workflow (1 subagente por b-roll) com `assets/workflow-hf-portrait.js` (args = lista de conceitos `{id,dur,text,kicker,concept}`; o script faz `JSON.parse(args)`). Cada agente copia um `_tpl` (clone de `assets/template-hf-portrait.html`, que renderiza limpo) e autora um motion-graphic 9:16 estilo Avalanche, valida e renderiza.
4. **Personagens:** `assets/gen_imgs_personagens.py` (gpt-image-2 `images.edit` com refs) → abre pro Chefe aprovar → `assets/anima_veo_chave2.py` (Veo 3.1 fast, **GOOGLE_AI_API_KEY_2** porque a chave 1 estoura cota 429) → gera `-fill` (tira faixa preta).
5. **Montar:** `assets/montar_parte.py` — define os inserts `(kind,file,start_abs)` numa única faixa cobrindo o vídeo. MODELO JANELADO: cada b-roll exibe de `start` até `(próximo_start - 2.5s)`, `overlay=eof_action=repeat` segura o último frame → **rosto fixo 2,5s garantido**. hf = 90% opacidade 1x; char = 2x cobrindo 100%. Mantém `[0:a]` (voz). Salvar e abrir pro Chefe ver. (Se tiver fatiado um vídeo longo: `ffmpeg -f concat -c copy` no fim.)

## GOTCHAS (caros, aprendidos na marra)
- **Veo cota 429** na chave 1 → usar `GOOGLE_AI_API_KEY_2`. Veo volta vazio às vezes (instável) → retry; fallback Ken Burns (`zoompan z='min(1.12,1+0.0005*on)':d=1`, `-t 8`, `-frames:v 240` — NUNCA `d=120` que gera 400s).
- **`eof_action=clone` NÃO existe** no overlay → é `repeat`.
- **Verificar frame de b-roll:** sampleie no MEIO da janela (start+1.5s), nunca no `start` exato (lá o b-roll está em opacity:0 entrando → parece preto/rosto).
- **Subagentes do workflow + hook RTK:** o hook reescreve `npx hyperframes@x` e quebra. Rodar via `npm run` (dentro do projeto) ou caminho absoluto do npx do nvm.
- Chaves em `~/naia-agent/.env` (Mac) / `/opt/naia-agent/.env` (Hetzner): OPENAI_API_KEY, GOOGLE_AI_API_KEY(+_2). Precisa de venv com `openai google-genai pillow`.
- Hyperframe: `npx hyperframes@0.6.110`. Render `--quality high`. Verificar SEMPRE com ffprobe (1080x1920 + duração) — não confiar no "ok" do agente.

## ASSETS
- `montar_parte.py` — montador (modelo janelado, hf 90% / char 2x). Editar os inserts pro seu vídeo.
- `template-hf-portrait.html` — composição Hyperframe 9:16 de referência (renderiza limpo).
- `workflow-hf-portrait.js` — workflow que autora N b-rolls Hyperframe em paralelo (1 agente cada).
- `gen_imgs_personagens.py` — gera imagens dos 4 personagens (gpt-image-2 + refs aprovadas).
- `anima_veo_chave2.py` — anima imagem aprovada no Veo 3.1 fast (chave 2) + fill (tira faixa preta).
