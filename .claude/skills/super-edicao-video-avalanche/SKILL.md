---
name: super-edicao-video-avalanche
description: "SKILL ÚNICA DE EDIÇÃO DE VÍDEO do Denderson. Use SEMPRE que ele mandar um vídeo (ou um lote) pra editar, pedir 'edita esse vídeo', 'skill de edição de vídeo', 'super edição', 'põe b-roll', 'edita no formato gennaro', 'faz o sanduíche', 'sanduíche 1 econômico', 'sanduíche 2', 'criativo pra meta', 'b-roll tela cheia', 'faixa de hyperframe', 'queima o hyperframe em cima do meu video', 'faz um video pro youtube', 'edita a VSL', 'corta o silêncio', 'põe legenda', 'põe gancho', 'tria esses cortes', ou mandar vídeo de talking-head, reels, corte de live, VSL ou vídeo de YouTube. Ao ser acionada apresenta o CARDÁPIO de modelos treinados (gennaro, b-roll no rodapé, b-roll tela cheia, b-roll imagem GPT, hyperframe queimado, faixa hyperframe, sanduíche, sanduíche 1 econômico, sanduíche 2 meta, VSL longa, YouTube 1) e SEMPRE pergunta três coisas: qual modelo, para qual plataforma (Reels, TikTok, Shorts ou YouTube 16:9) e se mantém o gancho do vídeo ou puxa um gancho do miolo."
---

# SUPER EDIÇÃO DE VÍDEO AVALANCHE

> **Gatilhos extras** (saíram do `description` por limite de 1024 caracteres, valem igual):
> 'sanduíche sem veo', 'modelo da imersão', 'monta a apresentacao animada do lado'.
> Esta skill substitui e aposenta as antigas `edicao-video-avalanche`, `edicao-video-gennaro`,
> `broll-fullscreen`, `broll-faixa-hyperframe`, `edicao-vsl-avalanche` e `triagem-cortes-live`.

Skill única de edição. Todo modelo que o Chefe treinou vive aqui, o miolo que se repete existe uma
vez só, e o conserto feito no núcleo vale para todos os formatos no mesmo instante.

## AO SER ACIONADA, NESTA ORDEM

Leia `nucleo/abertura.md` e resolva as três perguntas antes de tocar em qualquer arquivo:

1. **Qual modelo** (mostrar o cardápio se ele não disse).
2. **Para qual plataforma**: Reels, TikTok, Shorts ou YouTube 16:9.
3. **O gancho**: mantém o do vídeo ou puxa um do miolo.

O que ele já disse na mensagem não se pergunta de novo. Lote de vídeos não entra por aqui: vai para
`lote/triagem.md` primeiro.

## O CARDÁPIO

| modelo | o que é | arquivo |
|---|---|---|
| **Gennaro** | talking-head com elemento gráfico entrando na palavra exata, legenda gigante e fecho COMENTA / EU QUERO | `modelos/gennaro.md` |
| **B-roll no rodapé** | pipeline clássico: b-roll Veo 16:9 no rodapé, Chefe em cima, CTA e música | `modelos/broll-veo-rodape.md` |
| **B-roll tela cheia** | b-roll cobre a tela a cada ~3s, voz contínua por baixo, rosto no máximo 3s por vez | `modelos/broll-fullscreen.md` |
| **B-roll imagem GPT** | igual ao de cima, com imagem estática em Ken Burns em vez de Veo (econômico) | `modelos/broll-imagem-gpt.md` |
| **Hyperframe queimado** | gravação em TELA CHEIA 1080x1920 e faixa sobreposta por cima embaixo, legenda colada nela | `modelos/hyperframe-queimado.md` |
| **Faixa Hyperframe** | quadrado em cima, faixa ilustrada embaixo, meio a meio por `vstack` | `modelos/broll-faixa-hyperframe.md` (⚠ ver aviso abaixo) |
| **Sanduíche** | quadrado 1080 + strip Hyperframe 232 + b-roll Veo 608, as três camadas | `modelos/broll-faixa-hyperframe.md` (seção SANDUÍCHE) |
| **Sanduíche 1 econômico** | o sanduíche sem Veo: b-roll de imagem estática gpt-image-2 pela rota OAuth, Ken Burns com crossfade 0,7s, vídeo em 1.3x | `modelos/sanduiche-1-economico.md` |
| **Sanduíche 2 Meta** | criativo da Imersão pra Meta (aprovado 09/08/2026): anatomia 720+608+270+322, completo 1080x1920 e sem CTA 1080x1598, faixa SEM barra, quadro Meta 926x1370 em canvas 1080x1920 (claro fundo `#161210`, escuro cor quente por vídeo), opcional Veo nas cenas | `modelos/sanduiche-2-meta.md` |
| **VSL longa** | 10 a 15 min, multi-versão, faixa 16:9, trilha em 2 atos, sincronia labial por índice | `modelos/vsl-longa.md` |
| **YouTube 1** | horizontal 1920x1080: gravação vertical na coluna direita e apresentação animada em HyperFrames ancorada na fala, com imagens, infográficos e arte de encerramento | `modelos/youtube-1.md` |

Carregue só o arquivo do modelo escolhido.

> ⚠️ **Empilhar meio a meio reduz a gravação dele, e isso foi reprovado em 29/07/2026.** Quando o
> pedido for "queima o hyperframe em cima do meu vídeo", o modelo é o **Hyperframe queimado**: a
> gravação ocupa os 1080x1920 inteiros e quem encolhe é a faixa. Só use o meio a meio se ele pedir
> esse layout com todas as letras.

## O NÚCLEO (vale para todos)

- `nucleo/abertura.md`: o cardápio, as três perguntas, o que fazer depois delas.
- `nucleo/plataformas.md`: Reels, TikTok, Shorts e YouTube 16:9: canvas, duração, safe area.
- `nucleo/corte-fino.md`: o corte de silêncio seguro e o corte de roteiro com aprovação.
- `nucleo/gancho-viral.md`: como escolher e montar o gancho, com o que a base de 110 virais mostra.
- `nucleo/faixa-hyperframe.md`: a faixa como organismo vivo e a biblioteca de mecanismos.
- `nucleo/qa-e-entrega.md`: o que reprova, as provas e a entrega.

## AS REGRAS QUE NÃO SE NEGOCIAM

1. **Corte não encosta na fala, e o silêncio se corta com RECUO DE 0,5s.** Padrão desde
   02/09/2026 em qualquer vídeo: corte seco em cada pausa e o trecho seguinte puxado 0,5s pra
   trás por cima da cauda do anterior, áudio do anterior por baixo, sem aparar sílaba
   (`scripts/nucleo/corte_recuo.py`, skill `corte-seco-recuo-05`). Retake sai antes (primeira
   tomada fora, segunda fica). Método em `nucleo/corte-fino.md` e a prova é o
   `verifica_recuo.py` terminando em `VERIFICACAO_OK`. Sem essa saída, não entrega.
2. **Procure a quebra da quarta parede ANTES de cortar.** Ele fala com o editor no meio da
   gravação ("errei, corta as duas falas anteriores"). Rode
   `scripts/nucleo/detecta_instrucoes.py` em toda transcrição e leve os achados para ele aprovar.
   Sem isso, a instrução vira conteúdo e o erro vai pro ar.
3. **Conteúdo só sai com aprovação.** Silêncio se corta sozinho; trecho de fala, nunca. Em vídeo
   longo, propor os trechos com timestamp e motivo e esperar o sim item a item.
4. **Na dúvida, mantém.** Vale para muleta, anáfora de estilo, pausa dramática antes de número.
5. **A legenda é queimada SEMPRE, colada acima da faixa, FRASE POR FRASE.** Ordem do Chefe em
   14/09/2026: "eu prefiro a legenda frase por frase e não palavra por palavra". Blocos de até 6
   palavras numa linha só, fechados na pausa da fala (gap > 0,45s) ou quando a linha estoura 90%
   da largura, cada bloco na tela do início da primeira palavra ao fim da última. Bricolage
   Grotesque ExtraBold, caixa original da fala, creme com as palavras-chave em VERMELHO ALARANJADO
   (#f5411f) dentro da frase, 15 a 20% das palavras (lista em `--destaques`, obrigatória: sem ela
   só número fica colorido e o Chefe cobra),
   base do texto a 26px do topo da faixa. `scripts/nucleo/legenda_queimada.py` (padrão
   `--modo frase`; `--modo palavra` só se ele pedir uma palavra por vez). Vale para todo modelo
   vertical. Em vídeo com imagem em cima e Chefe embaixo, "rodapé da imagem de cima" = `--faixa-y`
   na linha medida onde a imagem termina (ex.: 1075).
6. **Todo overlay é um organismo vivo, nunca texto.** Vale para a FAIXA (sanduíche, VSL) e para o
   CARD (Gennaro): infográfico que desenha o que ele está falando, preenchendo a área inteira, com
   `scripts/nucleo/faixa_hyperframe.py` ou `scripts/nucleo/infografico.py` (fluxo, barras, painel,
   confronto, medidor, acumulo, imagem_dados), nunca o mesmo arquétipo em janelas seguidas. Pode e
   deve **mesclar imagem com elementos** na mesma cena, em zonas exclusivas. Kicker mais headline
   mais um número é proibido: isso é legenda com outra fonte. Regra em `nucleo/faixa-hyperframe.md`.
   **Princípio corrigido num modelo vale imediatamente para todos os outros.**
7. **Elemento persiste até faltar 0,5s para o próximo.** A janela de cada elemento vai do offset
   dele até o offset do seguinte menos meio segundo, e a saída acontece exatamente nesse intervalo.
   Elemento que entra e sai deixando a cabeça falante sozinha derruba retenção. `GAP_SAIDA` no
   `cut_plan.py`.
8. **Zero travessão em tudo que aparece na tela.** Legenda, card, chip, toast. O `qa_final.py`
   reprova se achar.
9. **Texto de card se escreve com acento.** A legenda do whisper já vem acentuada; card escrito em
   "MILHOES / SO NO BRASIL" grita erro de português do lado dela.
10. **Honestidade de citação.** Logo de marca só entra se a narração nomear a marca ou se ela estiver
   de fato na tela. Nunca inventar citação para enfeitar.
11. **Checkpoint de imagem antes de animar.** Gerar as imagens, abrir no Mac, esperar aprovação, só
   então gastar Veo. Já queimou dinheiro fazendo o contrário.
12. **Prova em crop de celular, conferida a olho, antes de entregar.** Medição numérica não vê erro de
   português nem hierarquia feia.
13. **Encode pesado um de cada vez**, com portão de carga. Fan-out cego já derrubou o Mac.
14. **A gravação dele é intocável.** Não reduzir, não emoldurar, não cortar o quadro dele pra
   caber apoio. Quem encolhe é o overlay. Se o overlay não couber, meça onde termina o rosto e
   reduza a faixa proporcionalmente, nunca corte a faixa nem espreme o vídeo.
15. **A medida decide, não o gosto.** Altura de faixa, posição de legenda e folga saem de medição no
   próprio material (onde termina a cabeça, qual o pixel mais baixo da legenda), com o número
   registrado no reporte.
16. **Áudio nunca se recodifica na composição** (`-c:a copy`), e **`-frames:v` nunca entra no comando
   que muxa áudio**: ele encerra o mux na contagem de quadros e trunca o som.
17. **Toda camada sobreposta com a mesma duração do vídeo base leva `tpad=stop_mode=clone`**, senão o
   último quadro fica descoberto.
18. **Gravação de iPhone é HLG BT.2020 com Dolby Vision e rotação por matriz.** Tonemap para BT.709
   no primeiro comando, sempre, senão a imagem sai lavada.
19. **O que ele mandou tirar se prova que sumiu, com controle positivo.** Varredura em todos os
   quadros usando o render antigo como controle: se o detector acha no antigo e não acha no novo,
   sumiu de verdade. Ler o código não é prova.
20. **Master grande fica salvo; para o Telegram vai cópia recomprimida** (limite de 50 MB), com o
   áudio copiado e o aviso de uma linha de que o master está guardado.
21. **Nunca reportar pronto sem as provas do `nucleo/qa-e-entrega.md`.**

## ACERVO

```
scripts/nucleo/          corte_recuo.py + verifica_recuo.py (PADRÃO de silêncio, recuo 0,5s),
                         corte_seguro.py, verifica_palavras.py (fallback sem recuo),
                         legenda_queimada.py, faixa_hyperframe.py     (comuns a todos)
scripts/gennaro/         planejador, pipeline, medidores e os 4 verificadores que reprovam
scripts/broll-veo-rodape/  geração de imagem, animação Veo, montagem, gancho, legenda Bricolage
elements/gennaro/        design system e elementos HTML com contrato window.__seek
assets/                  fontes, SFX, refs de personagem, templates de faixa e workflows
referencia/              método Gennaro, canon dos personagens, 110 transcrições de cortes virais,
                         processo-video-opus5-2026-07-29.md (dossiê completo do hyperframe queimado)
lote/triagem.md          modo lote: transcreve, avalia, dá nota e decide o que editar
```

## HISTÓRICO

Criada em 2026-07-25 por ordem do Chefe, unificando seis skills que dividiam o mesmo miolo com
pequenas divergências: `edicao-video-avalanche`, `edicao-video-gennaro`, `broll-fullscreen`,
`broll-faixa-hyperframe`, `edicao-vsl-avalanche` e `triagem-cortes-live`. Cada modelo entrou por
cópia integral, não por resumo. As seis foram aposentadas para não disputarem gatilho.

O motivo de existir: o QA que não reprovava viveu meses dentro de uma delas porque o conserto de uma
irmã não chegava nas outras.

Em 09/08/2026 entrou o modelo **Sanduíche 2 Meta** (`modelos/sanduiche-2-meta.md`), batizado na
produção dos criativos da Imersão (Kimi): anatomia 4 camadas, SEM_CTA, quadro Meta e Veo opcional.

Em 18/08/2026 entrou o modelo **Sanduíche 1 econômico** (`modelos/sanduiche-1-economico.md`), por
ordem do Chefe: mesma anatomia do sanduíche (1080 + 232 + 608), b-roll só de imagem estática gerada
pela rota OAuth da assinatura (`naia_image.py`, `allow_paid_fallback=False`), zero Veo, e velocidade
fixa de 1.3x. Base validada no LOTE 49 de 18/07/2026.

Em 02/09/2026 o corte de silêncio de TODOS os modelos passou a ser o **corte seco com recuo de
0,5s** (técnica do Chefe no CapCut, replicada em ffmpeg e aprovada por ele: "isso ficou
perfeito"). Skill própria `corte-seco-recuo-05`, scripts espelhados em `scripts/nucleo/`,
regra 1 e `nucleo/corte-fino.md` atualizados. O corte_seguro.py antigo virou fallback.
