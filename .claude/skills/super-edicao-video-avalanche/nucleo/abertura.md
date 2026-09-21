# NÚCLEO: ABERTURA (o cardápio e as três perguntas)

Toda vez que a skill é acionada, antes de tocar em qualquer arquivo, ela resolve três coisas. Se o
Chefe já disse alguma delas na mensagem, **não pergunta de novo**: usa o que ele falou e pergunta só
o que falta.

## 1. QUAL MODELO

Se ele não disse o formato, mostrar o cardápio, sem numeração, do jeito que ele prefere:

```
Qual formato você quer?

  Gennaro              talking-head com elemento gráfico entrando na palavra exata
  B-roll no rodapé     pipeline clássico, b-roll Veo 16:9 embaixo, CTA e música
  B-roll tela cheia    b-roll cobre a tela a cada ~3s, sua voz corre por baixo
  B-roll imagem GPT    igual ao de cima, com imagem estática em Ken Burns (econômico)
  Faixa Hyperframe     quadrado em cima, faixa ilustrada embaixo o vídeo inteiro
  Sanduíche            quadrado + faixinha Hyperframe + b-roll Veo embaixo
  Sanduíche 1 econômico  igual, sem Veo: imagem estática em Ken Burns e vídeo em 1.3x
  Sanduíche 2 Meta     criativo da Imersão pra Meta (cenas + take + faixa + CTA/quadro)
  VSL longa            10 a 15 min, multi-versão, faixa 16:9 e trilha em 2 atos
  YouTube 1            horizontal 16:9 com apresentação animada ao lado
```

Se ele disser o formato na própria frase ("edita no gennaro", "faz o sanduíche", "sanduíche econômico", "sanduíche 2",
"modelo da imersão", "criativo pra meta", "b-roll tela cheia", "põe a faixa de hyper"), pular
direto para a pergunta 2.

Cada modelo vive em `modelos/<nome>.md` e só é carregado quando escolhido.

## 2. PARA QUAL PLATAFORMA

Pergunta obrigatória, nunca inferir: **Reels, TikTok, Shorts ou YouTube 16:9.** Muda enquadramento,
duração alvo, safe area e posição de legenda. Detalhes em `nucleo/plataformas.md`.

Se ele responder mais de uma (por exemplo Reels e TikTok), montar pela régua mais restritiva das
escolhidas e avisar que a master serve às duas.

## 3. O GANCHO

Pergunta obrigatória: **manter o gancho que já está no vídeo, ou puxar um gancho de dentro do
miolo?** Se ele mandar escolher, a skill escolhe sozinha pela hierarquia de `nucleo/gancho-viral.md`
e informa qual frase pegou e por quê.

## COMO PERGUNTAR

Tudo numa mensagem só, curta, em prosa, sem numerar as opções. Ele responde por partes: travar cada
resposta recebida e seguir, sem repetir o que já foi respondido.

## DEPOIS DAS TRÊS RESPOSTAS

1. **Confirmar o arquivo certo** antes de editar: nome, `mtime`, duração, resolução por `ffprobe`, e
   uma amostra da transcrição para casar o tema com o pedido. Não bateu, para e confirma.
2. Transcrever word-level (whisper). O arquivo sai com o nome do vídeo, então renomear faz parte do
   passo.
3. Rodar o corte fino do `nucleo/corte-fino.md`, com a prova de palavras.
4. Seguir o `modelos/<escolhido>.md` para o vocabulário visual e a montagem.
5. Fechar pelo `nucleo/qa-e-entrega.md`.

## SE O CHEFE MANDAR UM LOTE

Vários vídeos de uma vez não entram por aqui: entram pelo `lote/triagem.md`, que transcreve todos,
avalia e classifica antes de qualquer edição. Só depois da triagem os aprovados voltam para este
fluxo, já com o formato e a plataforma definidos uma vez para o lote inteiro.
