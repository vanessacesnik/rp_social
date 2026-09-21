# O pacote de publicação do YouTube

Ordem do Chefe, 04/08/2026: **todo vídeo que a gente fizer para YouTube** sai com pacote completo:
vídeo com arte de encerramento colada, thumbnail e legenda, tudo numa pasta na Desktop dele.

---

## A REGRA QUE VALE PARA AS DUAS ARTES

**O TEXTO É ESCRITO PELO PRÓPRIO gpt-image-2.** Não componha texto por cima com PIL, com ffmpeg nem
com nada.

Isso foi decidido no dia em que eu errei. Achei que o modelo comeria os acentos de "IMPLEMENTAÇÃO" e
"SERVIÇOS", gerei as artes limpas e escrevi o texto por cima. O Chefe olhou e cravou: *"o GPT não
erra texto porra nenhuma, gera infográficos com muito texto e nunca erra"*. Ele estava certo. Pedindo
para o modelo escrever, saiu IMPLEMENTAÇÃO com cedilha e til, INTELIGÊNCIA com circunflexo, NEGÓCIOS
com agudo, DESCRIÇÃO com cedilha e til, SERVIÇOS com cedilha, e os pontos de milhar de R$ 1.000.000
no lugar. Além de correto, o texto sai integrado à arte, com peso e contorno próprios, muito melhor
do que colado por cima.

O que o prompt precisa carregar para o texto sair bom:

1. **Dizer o que a peça é.** "This image is a YOUTUBE VIDEO THUMBNAIL / CLOSING CARD", que vai ser
   vista no celular a uns 320 pixels de largura, disputando atenção num feed, e que o texto tem que
   ser grande, pesado e legível quando a imagem encolhe a um quinto do tamanho. Sem isso o modelo
   escreve pequeno e tímido.
2. **Soletrar caractere por caractere**, com uma linha só de "SPELLING IS CRITICAL", listando os
   acentos um a um: cedilha sob o C, til sobre o A, circunflexo sobre o E, agudo sobre o O.
3. **Reservar a zona do texto na composição**, dizendo que nada mais entra ali: nem rosto, nem mão,
   nem ícone, nem gráfico.
4. **Proibir texto fora dessa zona**: nada de marca d'água, assinatura, legenda ou escrita legível
   nos monitores do fundo.

---

## A ARTE DE ENCERRAMENTO

Uma imagem só, reaproveitada em todos os vídeos, colada por **10 segundos** no fim.

Arquivo aprovado: `assets/encerramento-youtube.png`. Gerador: `scripts/youtube-1/gen_encerramento.py`.

Conteúdo: o **quinteto Avalanche no estúdio, trabalhando**, e um banner embaixo com

```
CONSULTORIA DE IMPLEMENTAÇÃO DE
INTELIGÊNCIA ARTIFICIAL PARA NEGÓCIOS
LINK NA DESCRIÇÃO
```

### O que reprovou a primeira versão

**Cor chapada mata o anime.** Eu escrevi "flat solid colour, ZERO gradient" para toda a cena, achando
que aplicava a regra do Chefe. A regra de zero gradiente vale para **interface**; em ilustração o
canon do anime ultra realista pede o contrário: iluminação cinematográfica, textura rica de tecido,
acabamento premium. O resultado com tudo chapado foi reprovado na hora: *"background em cor dura,
horrível"*. O fundo certo é o **branco premium com textura sutil de circuito**, o mesmo da família B
dos infográficos aprovados.

**Os personagens saíram trocados, e eu não percebi.** Descrevi o Claudinho como criatura vermelha e o
OpenClaw como cubo laranja. É o inverso do canon:

- **Claudinho** tem cabeça de **CUBO LARANJA** fosco, olhos de colchete `>` e `<`, sem boca.
- **OpenClaw** é a **LAGOSTA cereja**: cabeça oval mais alta que larga, olhos enormes com íris âmbar,
  boca aberta com línguinha rosa, quatro antenas, pinças no lugar das mãos.

A skill `descricao-personagens-avalanche` avisa que virar formiga é a armadilha número um dele no
gpt-image-2, e manda gerar **ancorado em `openclaw-referencia-canonica.png`** mesmo em cena de grupo.
Leia o canon antes de escrever o prompt, sempre, e nunca de memória.

**Perguntar o look antes de gerar.** Quando a cena tem Denderson e/ou Naia, o canon obriga a
perguntar qual look, com as quatro combinações quando os dois aparecem. Nunca inferir. Nesta arte o
Chefe escolheu uniforme vermelho nos dois.

### Como ela entra no vídeo

```
ffmpeg -y -loop 1 -t 10 -i assets/encerramento-youtube.png \
  -f lavfi -t 10 -i anullsrc=r=48000:cl=stereo \
  -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p" \
  -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 192k -shortest encerramento_10s.mp4

printf "file 'video.mp4'\nfile 'encerramento_10s.mp4'\n" > lista.txt
ffmpeg -y -f concat -safe 0 -i lista.txt -c copy final.mp4
```

Confira depois: a duração final é a do vídeo mais 10 segundos e o último frame é a arte, não preto.

---

## A THUMBNAIL

Uma por vídeo. Gerador: `scripts/youtube-1/gen_thumb.py`. Exemplar aprovado:
`referencia/exemplar-thumb-aprovada.png`.

O padrão aprovado em 04/08/2026:

- **Rosto do avatar do Chefe em close**, estilo **caricatura**, ocupando de 45% a 55% do quadro, fora
  do centro, na regra dos terços, ancorado no recorte canon `denderson_cut.png`.
- **Expressão** de acordo com o gancho. No exemplar, espanto exagerado.
- **Fundo de uma cor sólida forte** com um único elemento de acento sólido atrás da cabeça, contorno
  grosso em volta da silhueta para ele descolar do fundo. Aqui a cor chapada é certa, porque é
  pôster, não cena.
- **Olhar apontando para o lado do texto**, puxando o olho de quem vê.
- **Logos** do Claude (asterisco coral de doze pétalas) e do ChatGPT (nó branco), símbolos apenas,
  sem palavra, do lado do rosto, nunca sobre ele.
- **Texto grande na metade vazia**, escrito pelo modelo, número em cor de acento e o resto em
  off-white, com contorno escuro.

O que a pesquisa de CTR mostrou e vale considerar: entre as thumbnails campeãs analisadas pela vidIQ
em 500 vídeos de breakout, 69% traziam rosto humano e 80% entre as 50 maiores; a mediana de texto foi
de cinco palavras; e cara de espanto exagerada aparece em cerca de 1 a cada 20, com público de
negócios e tecnologia respondendo melhor a expressão determinada de boca fechada. O Chefe pediu
espanto e aprovou o resultado, então espanto é o padrão da casa, mas vale oferecer a variação contida
para teste A/B.

---

## O DOCUMENTO DA LEGENDA

O `legenda.txt` abre com o **TÍTULO do vídeo, com estudo de SEO**, e só depois vem a legenda.

### O título

Entregue **três opções de título**, com o raciocínio de SEO explícito em uma linha cada, e marque a
recomendada. O que cada título precisa carregar:

- **O termo que a pessoa realmente busca** na frente, nos primeiros 40 caracteres, porque é o que
  aparece no celular antes do corte. Pesquise o termo em vez de chutar: veja o que o YouTube sugere
  no autocomplete, o que os vídeos que já rankeiam para o assunto usam e como eles escrevem.
- **O número concreto** do vídeo, quando existir. Número no título é o que separa promessa vaga de
  promessa verificável.
- **Até 60 caracteres** no total, para não truncar em lugar nenhum.
- **Nenhuma palavra desperdiçada** com enfeite ("descubra", "incrível", "você não vai acreditar").

Registre no documento os termos pesquisados e de onde veio a informação, para o Chefe conferir e para
o próximo vídeo aproveitar o levantamento. Nunca inventar volume de busca.

### A legenda

Três partes, nesta ordem, e a primeira linha é sempre CTA:

1. **CTA**, na primeira linha: convite para a próxima imersão ou para saber da consultoria de
   implementação, com o link https://denderson.ai
2. **Instagram**, logo abaixo: convite para seguir, com o link clicável
   https://www.instagram.com/denderson.ai/
3. **A legenda do conteúdo**, escrita a partir do que ele fala no vídeo, não do título. Abre com a
   dor concreta, entrega os números reais que ele cita, marca em que minuto a chave vira, e fecha com
   o caminho prático. Tom de amigão que manja muito, o fenômeno como protagonista, zero travessão.
   Hashtags no fim.

Separe as três partes com uma linha de pontos, para o YouTube não colapsar o bloco.

---

## A PASTA DE ENTREGA

Na Desktop do Chefe:

```
~/Desktop/conteudo youtube/<NN> - <titulo do video>/
    video.mp4          o vídeo final, já com os 10 segundos de encerramento
    thumbnail.png      a thumb escolhida
    legenda.txt        a legenda pronta para colar
```

O nome da pasta começa com número sequencial, para a ordem de publicação ficar óbvia.
