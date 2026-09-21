# SANDUÍCHE 1 ECONÔMICO (imagem estática, sem Veo, 1.3x)

> Criado em 18/08/2026 por ordem do Chefe. É o **Sanduíche 1** (`modelos/broll-faixa-hyperframe.md`,
> seção SANDUÍCHE) com três trocas fixas: b-roll de **imagem estática** em vez de Veo, imagem gerada
> pela rota **OAuth da assinatura** (nunca API paga) e velocidade **1.3x**.
> Base validada: LOTE 49 (18/07/2026, 21 finais entregues no sanduíche econômico).

Gatilhos: "sanduíche 1 econômico", "sanduíche econômico", "sanduíche sem Veo", "sanduíche só imagem",
"faz o sanduíche barato".

## A ANATOMIA (1080x1920, vstack de três camadas)

1. **TOPO 1080x1080** · talking-head em quadrado, rosto BEM centralizado, legenda queimada palavra a
   palavra (Bricolage Grotesque ExtraBold, caixa original da fala, creme com impacto em vermelho),
   base do texto colada acima da strip, nunca invadindo y=1080.
2. **MEIO 1080x232** · strip HyperFrames: pill de kicker à esquerda, headline de 1 linha caixa alta
   (56-72px, max-width ~760px) e 1 elemento visual animado à direita (x:820-1016), padding 64px.
   Ilustra a IDEIA do trecho, nunca repete a frase falada.
3. **BAIXO 1080x608** · b-roll de **imagem estática gpt-image-2 com Ken Burns**, uma imagem por
   janela, crossfade de 0,7s entre elas. **Zero Veo neste modelo.**

Sem linha de separação: a strip clara já separa.

## AS TRÊS TROCAS QUE DEFINEM ESTE MODELO

### 1. Velocidade 1.3x

Corte de silêncio primeiro, **depois 1.3x**, e só então transcrever. A ordem importa: o whisper roda
no arquivo já acelerado, senão todo timestamp de strip, imagem e legenda nasce errado.

```
ffmpeg -i corte.mp4 -filter_complex "[0:v]setpts=PTS/1.3[v];[0:a]atempo=1.3[a]" -map "[v]" -map "[a]" \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k fast.mp4
```

`atempo` aceita 1.3 direto (só acima de 2.0 precisa encadear). Conferir no `ffprobe` que a duração
caiu para `original/1.3` e que áudio e vídeo terminam juntos (diferença acima de 0,1s reprova).

### 2. Imagem, e imagem só

- **Uma imagem por janela de 10s** (o Veo usava 8s; aqui a janela é maior de propósito, menos arte
  por vídeo). A mesma janela vale para a strip, para a imagem e para a barra de progresso.
- **Ken Burns discreto:** zoom 1,00 → 1,06 na permanência inteira, alternando o movimento entre
  imagens vizinhas (push, pan à esquerda, pan à direita). Duas seguidas com o mesmo movimento reprova.
- **Crossfade de 0,7s** entre imagens (o corte seco só serve no b-roll de 3s do modelo tela cheia).

```
ffmpeg -loop 1 -i cena.png -t <DUR> -vf \
 "scale=2160:-2,zoompan=z='min(1.06,1+0.0004*on)':d=<DUR*30>:s=1080x608:fps=30,setsar=1" \
 -c:v libx264 -crf 18 -pix_fmt yuv420p cena.mp4
```

`-t` explícito sempre; `d=` solto gera centenas de segundos de vídeo.

### 3. Imagem pela rota OAuth (nunca crédito pago)

Motor único: `~/naia-agent/scripts/naia_image.py`, modelo `gpt-image-2`, rota OAuth da assinatura
ChatGPT do Chefe.

```
python3 ~/naia-agent/scripts/naia_image.py --check          # rota_padrao tem que dizer "oauth"
python3 ~/naia-agent/scripts/naia_image.py --prompt "..." --out cena_01.png \
        --size 1536x1024 --no-paid-fallback --json
```

Em código: `from naia_image import gerar; gerar(prompt, out, size="1536x1024", allow_paid_fallback=False)`.

- **`allow_paid_fallback=False` é obrigatório neste modelo.** Ele é o modelo econômico: cair na API
  paga sem ordem do Chefe anula a razão de existir. Conferir `r["rota"] == "oauth"` em toda geração e
  registrar isso no reporte.
- **Tamanhos cravados da rota:** `1536x1024`, `1024x1536`, `1254x1254`. Pedir outra coisa volta
  reescalado. Para a faixa 16:9, gerar sempre **1536x1024** e recortar na montagem.
- Se o OAuth estiver expirado (`--check` com `oauth_disponivel: false`), **para e avisa**. Não trocar
  para chave paga por conta própria.
- Nunca exportar `OPENAI_API_KEY` no ambiente do job só para "garantir": ambiente com chave paga
  disponível já queimou crédito do Chefe sem ninguém pedir.

## PROMPT DE CENA

- Safe-area: conteúdo no centro 70%, topo e base 18% só ambiente, porque o crop para 608 come as
  bordas.
- **Sem texto legível dentro da imagem.** Só formas de UI, ícones e rótulos minúsculos.
- Conteúdo do Denderson usa o squad Avalanche quando o assunto é IA e agentes, e cena realista
  cinematográfica quando é história pessoal. **Conteúdo de cliente nunca leva os personagens
  Avalanche.** Canon em `referencia/broll-veo-rodape/personagens-canon.md` (OpenClaw é lagosta de
  cabeça vermelho-cereja com corpo de criança e moletom Avalanche, nunca inseto).

## CHECKPOINT DE IMAGEM

Gerar todas as imagens do vídeo (ou do lote inteiro), montar uma galeria, **abrir no Mac e esperar o
sim do Chefe**, e só então queimar num passe só. Vale mesmo sem custo de Veo: imagem fora do canon
queima o vídeo inteiro.

## GANCHO

Padrão de `nucleo/gancho-viral.md`. No sanduíche, a headline em 2 linhas caixa alta vai na faixa
vermelha `#D32F2F` cobrindo **só a região do strip** (232px), Bricolage Grotesque 800 branca com
auto-fit; quadrado e b-roll seguem com o conteúdo original durante o gancho. Corte 0,15s antes da
primeira palavra, fim em 0,3-0,4s de silêncio, transição `xfade=fade:0.4` +
`acrossfade=d=0.4:c1=tri:c2=nofade`.

## TEMPORIZADOR GLOBAL DA STRIP (INEGOCIÁVEL)

A barra de progresso da strip nunca vai de 0 a 100% dentro do próprio take. Anima linear
(`ease:'none'`, duração igual ao `data-duration`, origem à esquerda) da fração inicial à fração final
daquela janela no vídeo todo (fração = fronteira / duração total **já em 1.3x**). Verificar nos dois
lados de uma fronteira: preenchimento contínuo, sem reset.

## ENQUADRAMENTO DO QUADRADO (o Chefe brigou)

Crop `1080:1080:0:<offset>` com o rosto centralizado o vídeo inteiro: extrair ~8 frames espalhados,
escolher o offset que elimina o teto morto sem nunca cortar a cabeça (nem quando ele se inclina),
gerar preview e conferir com Read antes de montar.

## MONTAGEM

1. `crop=1080:1080:0:<offset>` do canvas, com áudio (`-map 0:a`, `-c:a copy`).
2. Concat das strips na ordem, trim na duração exata.
3. Concat das imagens já animadas, `scale=1080:608,fps=30`, crossfade 0,7s entre elas.
4. `vstack` das três camadas. `tpad=stop_mode=clone` em toda camada de mesma duração do base.
5. `-frames:v` nunca entra no comando que muxa áudio.

## LOTE

- CTA único no fim de todos: imagem 9:16 do quinteto, animada **uma vez** e reaproveitada no lote
  inteiro (o CTA é a única exceção ao "sem Veo", e só se já existir asset pronto ou se ele mandar).
- Música de suspense canônica em ~-42dB.
- Entrega em pasta única na Desktop, nomes `V{n}_SANDUICHE-ECON.mp4`, sem abrir um por um no Mac
  quando for lote grande.
- Lote de cortes de live entra antes por `lote/triagem.md`.

## DICIONÁRIO WHISPER → LEGENDA (fala do Chefe)

Naya/Maia/Maya/Anaya → Naia · Cloud/Open Cloud → Claude/OpenClaw · Feibo → Fable ·
copila/depilóia → compila/deploya · Antropox/Antrópica → Anthropic · Sask → SaaS · TOTUS → TOTVS ·
NPJs → CNPJs · Reigen → HeyGen · **"Cláudio" fica** (apelido canônico).
O whisper alucina "Legendas pela comunidade Amara.org" no fim: nunca virar legenda.

## O QUE REPROVA AQUI

- Rota diferente de `oauth` em qualquer imagem sem ordem escrita do Chefe.
- Qualquer take de Veo no b-roll deste modelo.
- Velocidade que não seja 1.3x, ou timestamps tirados do arquivo antes da aceleração.
- Imagem com texto legível, ou duas imagens vizinhas com o mesmo movimento de câmera.
- Strip repetindo a frase falada, barra de progresso resetando na fronteira, atropelo de zonas.
- Legenda invadindo a strip (y=1080) e travessão em qualquer camada.
- Mais o que já reprova em `nucleo/qa-e-entrega.md`.

## GOTCHAS DA PRIMEIRA PRODUÇÃO (18/08/2026, vídeo IMG_3137)

- **O ffmpeg 8.1.1 do Homebrew não tem `zscale` nem `drawtext`** (sem libzimg e sem libfreetype). O
  tonemap HLG→BT.709 sai pelo swscale novo: `scale=1080:-2:out_color_matrix=bt709:out_primaries=bt709:out_transfer=bt709:out_range=tv,format=yuv420p`.
  Texto queimado é sempre Pillow mais overlay, nunca `drawtext`.
- **Painel da strip atropelava as mini barras** quando o apoio ou a unidade era longo: o auto-fit do
  `faixa_hyperframe.py` mede o rect do apoio **com o número já no valor final** (no primeiro seek ele
  ainda vale 0 e tudo parece caber) e encolhe. Corrigido no núcleo em 18/08/2026, vale para todos os
  modelos. Regra prática: apoio de painel com no máximo 10 caracteres, unidade com 1 ou 2.
- **`while read` em shell com node/ffmpeg dentro come o stdin** e o loop pula linhas (uma strip foi
  renderizada com o número errado). Orquestrar em Python com `stdin=subprocess.DEVNULL`, e nada de
  `mapfile` (o bash do macOS é 3.2).
- **`nohup cmd &` dentro da ferramenta Bash morre** quando a chamada termina: usar o modo background
  da própria ferramenta.
- Envio pelo chat tem teto de 30 MB: master fica na pasta e a cópia de conferência sai em CRF 31.
