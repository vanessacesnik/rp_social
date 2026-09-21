export const meta = {
  name: 'vsl-hf-brolls-p1',
  description: 'Gera os 22 b-rolls Hyperframe da Parte 1 da VSL (um subagente por b-roll: autora + valida + renderiza)',
  phases: [{ title: 'Gerar+Render', detail: 'um agente por b-roll Hyperframe' }],
}

const SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    id: { type: 'number' },
    status: { type: 'string', enum: ['ok', 'erro'] },
    output_path: { type: 'string' },
    dur_real: { type: 'number' },
    lint_inspect: { type: 'string', description: 'resumo do lint/validate/inspect (erros restantes ou 0)' },
    notes: { type: 'string' },
  },
  required: ['id', 'status', 'output_path', 'notes'],
}

const SHARED = `Você é um motion designer gerando UM b-roll de VSL com HyperFrames (vídeo programático via HTML+GSAP). Formato vertical 9:16, 1080x1920.

## CONTEXTO
É um b-roll que cobre a tela inteira por cima de uma VSL de vendas (a voz do Denderson — CEO da Avalanche, vende um agente de IA) toca por baixo. O b-roll é motion-graphics, SEM narração própria, SEM áudio. Estilo "dado/manchete editorial premium", igual ao exemplo de referência.

## ESTILO AVALANCHE (OBRIGATÓRIO — siga o arquivo de referência)
LEIA PRIMEIRO o arquivo de referência que JÁ renderiza certo: /Users/naiarodrigues/naia-agent/entregas/broll11-hf/index.html — copie a linguagem visual dele.
- Fundo escuro premium: #07090d com radial sutil (radial-gradient(120% 80% at 50% 0%, #11161f 0%, #07090d 60%)).
- Texto principal: #f4f7fb. Acento POSITIVO/marca: verde esmeralda #19e08a. Acento de DOR/CUSTO: vermelho #ff4747. Apoio/mudo: #8a93a3.
- Tipografia: "Helvetica Neue", Arial — PESADA (font-weight 800), CAIXA ALTA, letter-spacing apertado (-1 a -4px nos títulos), linhas curtas.
- Guias verticais bem sutis ao fundo (linear-gradient 90deg rgba(255,255,255,0.04) 1px, opacity ~0.5) pra dar cara de dado/editorial.
- Um "kicker": label pequeno em CAIXA ALTA, letter-spacing largo (~5px), na cor do acento, no topo — com um ponto/bolinha brilhante OU uma linha fina.
- Movimento cinético mas SUAVE: entradas com gsap.fromTo (power3.out, back.out, expo.out), números que contam, barras que crescem/colapsam (scaleY com transform-origin), carimbos que estouram (back.out), setas/elementos que entram. NADA de exagero kitsch.
- PROIBIDO: gradiente berrante de fundo, emoji, fonte externa via CDN (sem webfont — só system font, pois o render não pode fazer rede), card com borda-esquerda colorida, "AI slop". Menos é mais.

## CONTRATO TÉCNICO HYPERFRAMES (quebrar = render falha ou bug silencioso)
- index.html STANDALONE: <div id="root" data-composition-id="<ID_UNICO>" data-width="1080" data-height="1920" data-start="0" data-duration="<DUR>"> direto no body. SEM <template>.
- Root TEM que ter tamanho explícito (width:1080px;height:1920px;position:relative;overflow:hidden) senão o conteúdo colapsa no canto.
- Tudo dentro de UMA <section class="scene clip" data-start="0" data-duration="<DUR>" data-track-index="1" style="position:absolute;inset:0">. Padding interno >=80px (margem de segurança).
- GSAP via <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script> no <head>.
- UMA timeline: const tl = gsap.timeline({ paused: true }); ... ; window.__timelines["<ID_UNICO>"] = tl;  (a chave = data-composition-id exatamente). Construir SÍNCRONO (sem setTimeout/async/Promise).
- Duração do render vem do data-duration, NÃO do tamanho da timeline.
- Estado inicial escondido via CSS (opacity:0) e animar com fromTo. NÃO usar gsap.set em elementos de cenas futuras. NÃO animar display/visibility (use opacity/transform). NÃO repeat:-1. NADA de Date.now()/Math.random().
- Elemento transformado (scaleX/scaleY) precisa ser block + ter width/height reais. Para contador numérico use um objeto proxy {v:...} com onUpdate atualizando textContent (determinístico).
- Texto: nada de <br> em corpo longo; deixe quebrar por max-width. Garanta que o texto CABE (use font-size compatível com largura ~900px e rode inspect).

## FLUXO DE TRABALHO (execute exatamente)
1. cd /Users/naiarodrigues/naia-agent/entregas/vsl-broll && cp -r _tpl b<ID> && cd b<ID>
2. Leia /Users/naiarodrigues/naia-agent/entregas/broll11-hf/index.html pra absorver a estrutura/estilo.
3. Escreva o index.html do SEU b-roll (use data-composition-id único tipo "hf<ID>", data-duration = a sua duração). Texto COM acento correto em PT-BR.
4. Valide: npx --yes hyperframes@0.6.110 lint  ;  npx --yes hyperframes@0.6.110 validate  ;  npx --yes hyperframes@0.6.110 inspect
   - Corrija até lint=0 erros e inspect=0 erros (warnings de "studio_*" e overlaps intencionais podem ficar; marque overlap intencional com data-layout-allow-overlap e suba z-index pra resolver oclusão real). Use "npx --yes hyperframes@0.6.110 snapshot --at <t>" se quiser conferir um frame.
5. Renderize: npx --yes hyperframes@0.6.110 render --quality high --output /Users/naiarodrigues/naia-agent/entregas/vsl-broll/brolls/hf/hf-<ID>.mp4
6. Verifique: /opt/homebrew/bin/ffprobe no arquivo de saída (tem que ser 1080x1920 e duração ~= sua dur). 
Retorne o status estruturado (id, status ok/erro, output_path, dur_real, lint_inspect, notes). NÃO invente sucesso: se o arquivo não existir ou der erro, status="erro" e explique em notes.`

const items = (typeof args === 'string') ? JSON.parse(args) : args
log(`gerando ${items.length} b-rolls Hyperframe em paralelo`)
const results = await parallel(
  items.map((c) => () =>
    agent(
      `${SHARED}\n\n## SEU B-ROLL (id ${c.id})\nDUR = ${c.dur} segundos (use exatamente esse data-duration)\nKICKER (label pequeno topo): "${c.kicker}"\nTEXTO PRINCIPAL (frase âncora): "${c.text}"\nCONCEITO / IDEIA DE MOVIMENTO: ${c.concept}\n\nUse ID_UNICO = "hf${c.id}". Saída: /Users/naiarodrigues/naia-agent/entregas/vsl-broll/brolls/hf/hf-${c.id}.mp4`,
      { label: `hf-${c.id}`, phase: 'Gerar+Render', schema: SCHEMA }
    )
  )
)

return results.filter(Boolean)
