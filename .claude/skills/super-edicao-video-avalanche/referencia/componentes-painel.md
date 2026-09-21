# Os componentes do painel escuro · a régua de animação do youtube-1

**Por que este arquivo existe (05/08/2026).** O Chefe assistiu o lote e a sentença foi: "toda a
animação feita por HyperFrames tem que ser mais detalhada, mais complexa, mais visualmente bonita
e mais completa. Não quero economia, não quero animação de merda. Quero animação bonita, profunda,
com complexidade, com didática, que ilustre de verdade o que está sendo dito no vídeo."

O defeito era estrutural, não de esforço. As cenas tinham quase todas a mesma forma: uma headline,
três linhas grandes que entram por opacidade, uma faixa embaixo. Isso é uma legenda animada, não é
didática. Uma cena didática **constrói** alguma coisa na frente do espectador enquanto ele fala.

## A regra

> Nenhuma cena de conteúdo é feita só de texto entrando. Toda cena tem uma ESTRUTURA que se monta,
> e o que se monta é o raciocínio dele naquele trecho.

Três linhas grandes com fade continuam existindo, mas só para a cena de virada, a frase de efeito,
o momento em que a tela deve calar e deixar a fala mandar. Uma dessas por vídeo, não sete.

## Os sete componentes

Cada um está implementado, com CSS e GSAP, em `componentes-painel.html`. Copie de lá, não reescreva.

### 1. fluxo · a corrente de etapas
Uma sequência de blocos numerados atravessando o painel, ligados por conectores sólidos. Cada bloco
tem número, título e uma linha de explicação. Os blocos **acendem um por um** no instante em que
ele cita a etapa, e o conector entre dois blocos cresce da esquerda para a direita antes do próximo
acender. É o componente certo para "primeiro isso, depois aquilo, e aí acontece isso".

### 2. contador · o número que se forma

> **Armadilha que mata o script inteiro.** O contador vai em `tl.to({v:0}, {v:N, onUpdate...}, T)`,
> nunca em `tl.fromTo`. Com `fromTo` o GSAP lê a assinatura como `(target, from, to)`, estoura
> `Cannot create property 'parent' on number` e **nenhuma cena do vídeo anima**, não só a do
> contador. Custou um render inteiro para aparecer.
Um número enorme que **conta** de zero até o valor que ele diz, com um rótulo em cima e a unidade
embaixo. Nunca aparece pronto. Quando ele diz dois números que se relacionam, os dois contam ao
mesmo tempo e o segundo termina depois, para o olho comparar.

### 3. barras · a comparação que cresce
Duas a cinco barras horizontais que crescem por `width` a partir da esquerda, cada uma com rótulo
à esquerda e valor à direita que conta junto com a barra. A barra que representa o problema é
`#F5402E`, a que representa o ganho é `#24D869`, o neutro é `#4FD8EF`. É o componente certo para
"era assim e passou a ser assim".

### 4. antes e depois · as duas colunas
Duas colunas do mesmo tamanho. A da esquerda se monta primeiro, item por item, enquanto ele
descreve o problema. Quando ele vira a frase, a coluna esquerda **perde saturação** e a direita se
monta por cima do mesmo eixo. Nunca as duas ao mesmo tempo.

### 5. lista viva · o inventário que soma
Itens que entram um a um com um marcador de conferido, e um contador no canto que sobe a cada item.
É o componente certo para "ela faz isso, isso, isso e isso".

### 6. linha do tempo · o que acontece quando
Um eixo horizontal com marcas de tempo e eventos pendurados nelas. O eixo se desenha, depois cada
evento entra na sua marca. É o componente certo para "às 9 da manhã acontece isso, às 11 aquilo".

### 7. destaque migrante · o foco que anda
Uma grade de itens já visível, e uma moldura sólida `#4FD8EF` que **anda** de um item para o outro
conforme ele fala de cada um. O item ativo fica em `#F7F5F0`, os demais em `#94A3B8`. É o
componente certo para percorrer um menu, uma tela ou uma lista que já está na tela.

## A régua de movimento, herdada da skill `impeccable`

O Chefe perguntou em 05/08/2026 se dava para casar o HyperFrames com a `/impeccable`. Dá, e a
resposta veio cara: as leis de movimento dela **reprovaram quatro coisas escritas nesta mesma
biblioteca**, todas já corrigidas aqui.

Metade da `/impeccable` é interação (hover, foco, formulário, `prefers-reduced-motion`) e num vídeo
renderizado quadro a quadro nada disso existe, então não se roda `/impeccable animate` em cima da
composição e aceita a saída. O que se herda é a régua:

- **Curva exponencial, nunca bounce.** `expo.out` para entrada, `quart.inOut` para ida e volta,
  `quart.out` para número contando e barra crescendo. Bounce e elastic estão na lista de "tacky e
  amadorista" dela, e o `back.out(1.4)` que eu tinha escrito no fluxo era exatamente isso.
- **Saída é mais rápida que entrada**, cerca de 75% da duração.
- **Duração pela régua 100/300/500.** 100 a 150 ms para acender um item, 200 a 300 ms para troca de
  estado, 300 a 500 ms para mudança de layout, 500 a 800 ms para entrada de cena.
- **Proibições absolutas**, que valem também para os infográficos gerados: borda lateral colorida
  como acento, texto com gradiente, glass como padrão, o molde do número gigante com rótulo pequeno
  e estatística de apoio, e **grade de cards idênticos com ícone, título e texto repetida sem fim**.
- **Transform e opacidade são o piso, não o teto.** A régua libera `blur`, `filter`, `clip-path` e
  máscara como material de animação, e como o HyperFrames captura por screenshot os três funcionam.
  Um bloco que recua com `blur(3px)` em vez de só perder opacidade lê como profundidade de verdade,
  e uma revelação por `clip-path` lê como peça cara. Use onde o efeito significa alguma coisa.

## O que continua valendo

- Animação só por `transform`, `opacity` e `width` de barra. `top`, `left`, `fontSize`, `padding` e
  `margin` fazem o motor de captura tremer.
- A tela nunca passa 2 segundos sem movimento, e o movimento vem do CONTEÚDO. Proibido barra de
  progresso decorativa, varredura, partícula e brilho.
- Cada passo da estrutura é ancorado no tempo REAL da palavra, medido na transcrição. Fatiar a cena
  em partes iguais é o erro que fez a tela mostrar a etapa 2 enquanto ele falava da 4.
- Zero travessão, nada colide, nada passa de 1000, IDs prefixados pela cena.
- O texto sai da fala daquele momento e nunca inventa número que ele não disse.

## O que reprova a cena

- Cena de conteúdo que é só headline mais três linhas com fade.
- Estrutura que aparece pronta em vez de se montar.
- Etapa acesa antes ou depois da frase que a nomeia.
- Componente escolhido que não tem relação com o raciocínio (fluxo para uma comparação, barras para
  uma sequência).
- Número que aparece sem contar.
