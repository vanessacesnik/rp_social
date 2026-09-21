export const meta = {
  name: 'vsl-bar-ilustrado',
  description: 'Cria 130 b-rolls Hyperframe de barra (1080x844) que ILUSTRAM a fala de cada take (kicker+headline+elementos), nao legenda',
  phases: [{ title: 'Desenhar+Render', detail: 'lotes de takes por subagente' }],
}
const SCHEMA = { type:'object', additionalProperties:false, properties:{
  rendered:{type:'array',items:{type:'number'}}, failed:{type:'array',items:{type:'number'}}, notes:{type:'string'} },
  required:['rendered','failed','notes'] }

const NPX='/Users/naiarodrigues/.nvm/versions/node/v22.22.0/bin/npx'
const ROOT='/Users/naiarodrigues/naia-agent/entregas/vsl-broll'
const N=130, BATCH=4, batches=[]
for(let i=0;i<N;i+=BATCH){const g=[];for(let j=i;j<Math.min(i+BATCH,N);j++)g.push(j);batches.push(g)}
log(`desenhando ${N} barras em ${batches.length} lotes`)

const BRIEF=`Você é motion designer da Avalanche. Vai criar b-rolls Hyperframe de BARRA HORIZONTAL (1080x844) que vão preencher a faixa preta de baixo de uma VSL. Cada barra ILUSTRA o que o Denderson fala naquele trecho.

## O MAIS IMPORTANTE (o chefe ODIOU a versao anterior que so queimava a frase)
- NUNCA escreva a frase falada inteira como legenda. PROIBIDO.
- Em vez disso: ENTENDA a ideia da fala e crie um b-roll com KICKER curto (label de acento) + HEADLINE PUNCHY (resuma a ideia em 3-7 palavras, CAIXA ALTA) + ELEMENTOS VISUAIS que ILUSTRAM: numero contando, barra crescendo/encolhendo, icones, comparacao lado a lado, carimbo (back.out), seta, checklist, gauge. Igual aos b-rolls de um VSL profissional.
- Ex: fala "demitiu 4 mil pessoas" -> headline "−4.000 POSTOS" + numero gigante contando + barra de equipe encolhendo. Fala "agente atende 24h" -> headline "ATENDE 24H SEM PARAR" + icones de canais + relogio. Use a fala SO como inspiracao do conceito.

## O MAIS IMPORTANTE 2 — FAIXA 100% LIMPA, ZERO ATROPELO (exigencia direta do chefe)
- Texto e elementos NUNCA podem se esbarrar nem um cobrir/sobrescrever o outro. Use o SISTEMA DE ZONAS do exemplo:
  - ZONA ESQUERDA (x:64 ate ~664, largura travada ~600px): kicker (topo) + headline + sub opcional (rodape esquerdo).
  - ZONA DIREITA (x:712 ate ~1016, largura ~304px): o visual (numero gigante / gauge / barras / icone CSS).
  - CORREDOR de 48px entre as zonas (x:664->712) que NINGUEM invade.
  - RODAPE: barra de progresso (left:64, width:952, bottom:~48).
- Headline largura MAX ~600px e MAX 2 LINHAS. Nao coube em 2? Reduz a fonte (range ~64-88px) ou encurta. Nada vaza os limites da faixa nem encosta na barra de progresso.
- Rode o inspect e SO renderize com inspect=0 layout issues. NAO use data-layout-allow-overlap pra mascarar atropelo real (so pra camada de fundo decorativa de proposito: guias/glow).

## ESTILO AVALANCHE + ZONAS (leia o arquivo de referencia)
LEIA /Users/naiarodrigues/.claude/skills/broll-faixa-hyperframe/assets/template-bar-ZONAS-1080x742.html pra absorver o estilo E O SISTEMA DE ZONAS (copie a estrutura de zonas dele; ajuste so as dimensoes/posicoes y pra altura da SUA faixa). Fundo #07090d com radial sutil; texto #f4f7fb; acento verde #19e08a (positivo/marca) e vermelho #ff4747 (dor/custo); apoio #8a93a3. Helvetica Neue 800 caixa alta, letter-spacing apertado. Guias verticais sutis. Movimento suave (power3.out/back.out/expo). Sem gradiente berrante, sem emoji, sem webfont (system font), sem audio.

## FORMATO BARRA (1080x844 — landscape, NAO portrait)
Composicao standalone 1080x844. Aproveite o espaco horizontal: kicker em cima/esquerda, headline grande (~80-104px, pode 2 linhas, max-width ~940), elementos (numeros/barras/icones) ao lado ou abaixo. Padding >=64px. O texto e os elementos tem que CABER em 1080x844 (rode inspect).

## CONTRATO HYPERFRAMES (quebrar = falha)
- index.html standalone: <div id="root" data-composition-id="barNNN" data-width="1080" data-height="844" data-start="0" data-duration="DUR"> direto no body, sem <template>. Root com width:1080px;height:844px;position:relative;overflow:hidden.
- Tudo numa <section class="scene clip" data-start="0" data-duration="DUR" data-track-index="1" style="position:absolute;inset:0">.
- GSAP via cdn.jsdelivr no head. UMA timeline paused, window.__timelines["barNNN"]=tl, construida sincrona. Estados iniciais via opacity:0 + fromTo. Sem Date.now/Math.random/repeat:-1. Numero contando = objeto proxy {v} com onUpdate. data-duration manda na duracao.

## FLUXO (por take)
1. cd ${ROOT}/barproj && cp -r ../broll11-hf bN (onde N=id) ... na verdade: mkdir -p ${ROOT}/barproj/d{id} && cp ${ROOT}/barproj/hyperframes.json ${ROOT}/barproj/d{id}/hyperframes.json
2. Escreva ${ROOT}/barproj/d{id}/index.html (1080x844, ilustrando a fala). data-composition-id="bar{id3}" (id com 3 digitos, ex bar007).
3. Valide e renderize (o hook quebra 'npx' — use o caminho absoluto e dangerouslyDisableSandbox=true):
   cd ${ROOT}/barproj/d{id} && ${NPX} --yes hyperframes@0.6.110 lint ; ... validate ; ... inspect ; ... render --quality high --output ${ROOT}/brolls/bar/bar-{id3}.mp4
   (corrija ate lint=0 e inspect=0; marque overlap intencional com data-layout-allow-overlap)
4. ffprobe confirma 1080x844 e a duracao. 
Retorne rendered (ids ok) e failed.`

const results=await parallel(batches.map((b)=>()=>{
  const id3=b.map(i=>String(i).padStart(3,'0')).join(', ')
  return agent(`${BRIEF}\n\n## SEUS TAKES: ids ${b.join(', ')} (id3 = ${id3}).\nLeia o arquivo ${ROOT}/barproj/specs130.json (array de {id,dur,fala}) e pegue a fala e a dur de CADA um dos SEUS ids. Para cada take, ILUSTRE a ideia da fala (NAO copie a frase). Saida: ${ROOT}/brolls/bar/bar-<id3>.mp4 pra cada um.`,
    { label:`barras ${b[0]}-${b[b.length-1]}`, phase:'Desenhar+Render', schema:SCHEMA, effort:'medium' })
}))
const rendered=results.filter(Boolean).flatMap(r=>r.rendered||[])
const failed=results.filter(Boolean).flatMap(r=>r.failed||[])
log(`render: ${rendered.length} ok, ${failed.length} falhas`)
return { rendered:rendered.length, failed }
