# MODELO: B-ROLL COM IMAGEM GPT (estática, sem Veo)

> Consolidado em 2026-07-25 na unificação. O conteúdo vinha espalhado entre o "sanduíche econômico"
> da `edicao-video-avalanche` (validado no LOTE 49) e a camada de imagens estáticas da
> `edicao-vsl-avalanche`. Vira modelo próprio porque o Chefe o trata como um dos tipos do cardápio.
>
> Acervo: `scripts/broll-veo-rodape` (o `01_gen_images.py` gera as imagens),
> `referencia/broll-veo-rodape` (canon dos personagens).

É o irmão econômico do b-roll animado: mesma escolha de cena, mesma régua visual, mas a imagem do
`gpt-image-2` entra **estática com Ken Burns** em vez de virar clipe no Veo. Serve quando o lote é
grande, quando o orçamento pesa ou quando o movimento do Veo não acrescenta nada à cena.

## QUANDO ESCOLHER ESTE EM VEZ DO VEO

- **Lote grande.** Um take de Veo custa ~US$0,80 (8s a 720p) mais ~US$0,165 da imagem. Vinte vídeos
  com seis takes cada passam de US$100 só de animação. Com imagem estática, fica o custo da imagem.
- **Cena de conceito**, painel, gráfico, tela de sistema: movimento de câmera não ajuda e às vezes
  atrapalha a leitura.
- **Prazo curto.** Não há polling de job nem risco de o Veo voltar vazio.
- **Público que precisa ler** algo na imagem: estática com 5s na tela lê melhor que clipe de 8s.

Quando a cena tem ação (personagem fazendo algo, movimento que ilustra a fala), o Veo continua sendo
melhor. Ver `modelos/broll-veo-rodape.md`.

## COMO ENTRA NA TELA

- **Duração:** 3,0s por imagem no ritmo padrão. **Exceção: tela de sistema ou portal fica 5,0s**,
  porque o público precisa ler o que está ali.
- **Ken Burns discreto:** zoom 1,00 → 1,06 ao longo da permanência. Nada de zoom agressivo.
  `zoompan z='min(1.06,1+0.0004*on)':d=<frames>` com `-t` explícito. Nunca `d=120` solto, que gera
  centenas de segundos.
- **Entrada e saída secas** no ritmo de reels; crossfade curto (0,3s) quando o vídeo é longo e o
  corte seco ficaria abrupto.
- **Duas imagens seguidas nunca com o mesmo movimento.** Alterna push, pan à esquerda, pan à direita.
- **Legenda por cima da imagem**, re-renderizada com as palavras da janela, quando a imagem cobre o
  bloco inteiro. A faixa e o áudio continuam intactos.

## GERAÇÃO

`scripts/broll-veo-rodape/01_gen_images.py`, gpt-image-2, 1536x1024 quality high para b-roll 16:9 e
1024x1536 para cobertura vertical, dimensão divisível por 16, resposta em `data[0].b64_json` salva
via arquivo (o terminal trunca base64).

- **Safe-area no prompt:** conteúdo no centro 70%, topo e base 18% só ambiente, para o crop nunca
  comer conteúdo.
- **Sem texto legível dentro da imagem.** Texto gerado por modelo de imagem sai errado. Só formas de
  UI, ícones e rótulos minúsculos.
- **Regra editorial por público:** conteúdo do Denderson usa o squad Avalanche quando fala de IA e
  agentes, e cena realista cinematográfica para história pessoal. **Conteúdo de cliente nunca leva os
  personagens Avalanche**, nem quando o assunto é IA: vira cena realista (atendimento respondendo
  sozinho no celular, consultório cheio, tela real do sistema).
- **Canon dos personagens** em `referencia/broll-veo-rodape/personagens-canon.md`. OpenClaw é lagosta
  cabeça vermelho-cereja texturizada com corpo de criança e moletom Avalanche, nunca inseto nem bola
  lisa.

## CHECKPOINT

Gerar as imagens, **abrir no Mac e esperar a aprovação do Chefe** antes de queimar no vídeo. Vale
para este modelo também, mesmo sem o custo do Veo: imagem fora do canon queima o vídeo inteiro.

Fluxo econômico validado no LOTE 49: gerar tudo, montar uma galeria, aprovar de uma vez, e só então
queimar em um passe só. CTA animado uma vez e reaproveitado em todos os vídeos do lote.
