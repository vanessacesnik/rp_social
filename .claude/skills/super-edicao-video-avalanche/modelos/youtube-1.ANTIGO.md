# Modelo YOUTUBE 1 · apresentação animada ao lado da gravação

> Treinado em 04/08/2026 no vídeo T1 ("o time que quase me quebrou", 12 min). Formato inspirado no
> vídeo da Gabi que o Chefe mandou: ela gravou só na vertical, e o Claude dela montou toda a
> apresentação animada em HyperFrames ao lado. Este arquivo é a receita completa, do insumo à entrega,
> com as armadilhas que custaram caro na primeira montagem.

## O QUE É

Vídeo horizontal 1920x1080 para o canal do YouTube. A gravação vertical do Chefe ocupa uma **coluna
à direita** e todo o resto da tela é uma **apresentação animada em HyperFrames** que acompanha a fala
segundo a segundo, alternando tipografia com dados, imagens ultra realistas e infográficos do
quinteto Avalanche. Fecha com a arte de encerramento por 10 segundos.

O insumo é um corte já pronto. O Chefe corta a live antes e aciona a skill com o arquivo na mão;
triagem de live não faz parte deste modelo.

## O LAYOUT

Canvas 1920x1080. Dois blocos sólidos, sem gradiente em lugar nenhum.

**O lado da gravação ALTERNA a cada vídeo da série.** Ordem do Chefe de 04/08/2026, ao começar o
lote da segunda live: "um quero o vídeo de um lado e no próximo inverte". Vídeo de número ímpar usa
a montagem A (gravação à direita, que é a dos quatro primeiros), vídeo par usa a montagem B
(gravação à esquerda). Só as duas coordenadas de `left` mudam; a régua vertical, os tamanhos e todas
as regras de conteúdo são idênticos nas duas.

| bloco | montagem A (ímpar) | montagem B (par) | tamanho |
|---|---|---|---|
| painel da apresentação | left 32 | left 636 | 1252x1016 |
| coluna da gravação | left 1316 | left 32 | 572x1016 |

Painel com **fundo escuro** e canto arredondado, gravação em `object-fit: cover`, os dois com
top 32. As contas fecham nos dois casos: 32 + 1252 + 32 + 572 + 32 = 1920.

### A paleta escura

Ordem do Chefe de 04/08/2026, no lote da segunda live: "quero o hyperframe com background escuro".
O painel bege `#F7F5F0` dos quatro primeiros vídeos foi aposentado.

| papel | cor | onde usa |
|---|---|---|
| fundo do painel | `#0F172A` | sólido, sem gradiente, sem textura |
| texto principal | `#F7F5F0` | headline, KPI, rótulo de destaque |
| texto secundário | `#94A3B8` | legenda, apoio, unidade |
| destaque frio | `#4FD8EF` | número, barra, item ativo |
| destaque quente | `#F5402E` | o número que dói, perda, custo |
| positivo | `#24D869` | ganho, economia, resultado |
| faixa de dados | `#1B2438` | um degrau acima do fundo, sólido |

O cyan `#0E7490` sai de cena, ele só servia sobre fundo claro. A separação entre faixa e fundo passa
a ser por tom sólido, nunca por sombra ou borda esbatida.

**A pegadinha que essa mudança cria:** os infográficos e as imagens de `gpt-image-2` dos quatro
primeiros vídeos nasceram com fundo claro. Colados num painel escuro eles viram um retângulo branco
gritando no meio da tela, e a moldura piora em vez de resolver. Todo infográfico deste lote em
diante é gerado **já com fundo `#0F172A`**, com o pedido explícito de fundo escuro sólido no prompt,
e a moldura vira uma borda de 1px em `#1B2438` só para dar aresta. Foto realista continua sangrando
até a borda da área, sem moldura, com overlay de opacidade única quando precisar segurar o texto.

Na montagem B, confira duas coisas que a A não exige: nenhuma cena pode ter texto ancorado por
`right` sem o par correspondente, e a folha de contato precisa ser revista inteira, porque elemento
posicionado por engano em coordenada absoluta de tela (e não relativa ao painel) só aparece torto
depois da inversão.

Dentro do painel, a régua vertical que vale para toda cena:

| elemento | posição |
|---|---|
| `.beat` (número + rótulo do capítulo) | top 34 |
| `.headline` em cena de texto | top 92, fonte de 40 a 56px |
| `.headline` em cena de imagem | top 70, UMA linha só, termina antes de 140 |
| área de imagem ou infográfico | top 146, altura 690, largura cheia |
| faixa de dados embaixo da imagem | top 850, altura 152 |
| limite inferior de tudo | 1000 |

A marca (logo, régua e rodapé) aparece **só na cena 1** e some. O gancho é limpo e o resto do vídeo
usa a tela inteira. Isso é ordem do Chefe de 04/08/2026: "a logo pode aparecer no começo, mas depois
prefiro que toda a tela seja utilizada pelo hyperframe, imagens e infográficos".

## O PASSO A PASSO

### 1. Transcrever o corte com tempo por palavra

Transcreva **o áudio exato que vai para o projeto**, nunca uma transcrição anterior de outra versão
do arquivo. Esse é o erro que gerou o retrabalho de 04/08.

```
ffmpeg -y -i corte.mp4 -ac 1 -ar 16000 audio16k.wav
whisper-cli -m ~/.local/share/whisper-models/ggml-large-v3-turbo-q5_0.bin \
  -l pt -ml 1 -oj -of palavras -f audio16k.wav
```

`-ml 1` força um segmento por palavra, e o JSON sai com `offsets.from` em milissegundos.

### 2. Montar o gancho

Ache na transcrição a frase mais forte do vídeo, normalmente onde ele crava o número e a promessa.
Corte esse trecho e coloque **na frente** do corte, gerando um master novo:

```
ffmpeg -y -ss <ini> -to <fim> -i corte.mp4 -c:v libx264 -crf 17 -r 30 -c:a aac gancho.mp4
ffmpeg -y -f concat -safe 0 -i lista.txt -c copy master.mp4
```

Atenção: se o vídeo do projeto não tiver trilha de áudio (é o caso quando o áudio vive num `.m4a`
separado), monte o áudio do master pelo mesmo caminho, senão o corte sai mudo.

A partir daí, todo tempo da timeline é **tempo do master**, ou seja, tempo original mais a duração do
gancho.

### 3. Ancorar as cenas NA FALA

Este é o coração do modelo e onde a primeira montagem errou feio.

**Não divida a duração em fatias iguais.** Leia a transcrição com os tempos e marque, para cada
assunto que ele desenvolve, o instante exato em que a frase começa. Cada cena nasce colada nesse
instante e termina onde a próxima começa. Uma cena pode durar 9 segundos e a vizinha 51.

Se um assunto da fala não tem cena, crie uma. Se um slide não tem fala correspondente, ele não existe.
No T1 sobraram duas falas órfãs (o Opus atendendo cliente e a jornada do lead) e um slide adiantado
em 71 segundos em relação à própria frase. O Chefe percebeu na hora: "o que representa a fala sobre
cadência de follow up apareceu muito antes da fala dele, tá desconectado".

Guarde o mapa num JSON com id, início, duração e a fala âncora de cada cena. Ele é o contrato de
tudo que vem depois.

### 4. Gerar as imagens e os infográficos

Imagens ultra realistas que ilustram a fala e infográficos do quinteto, os dois com **gpt-image-2**
pelo caminho da skill `infograficos` (`gen_infografico.py`, images.edit com os recortes canon). Regra
do Chefe: quando entra imagem, ela fica pelo menos 10 segundos na tela e leva uma faixa de dados
embaixo.

Infográfico é diferente de foto. Foto aceita `cover` e recorte; infográfico **precisa aparecer
inteiro**, então vai em `contain`, dentro de uma moldura, e nunca recebe zoom.

**O motor de prompt é um só e mora em `scripts/youtube-1/arte.py`.** Nenhum vídeo escreve o seu
próprio motor: o `gen_artes.py` do projeto só declara as peças e importa de lá. Isso existe porque
cada cópia editada divergia, e a divergência custou caro.

### O PADRÃO É PIXEL ART 3D COM O QUINTETO (aprovado em 05/08/2026)

Toda arte do youtube-1 sai em **pixel art 3D voxel com os cinco personagens Avalanche agindo dentro
da cena**, via `arte.base_pixel()`. Foto realista foi tentada, o Chefe disse "melhorou mas pode ser
muito melhor" e mudou a direção. O padrão aprovado é este e vale para os 14 vídeos e os dois CTAs.

Quatro coisas fazem esse padrão funcionar, e nenhuma é opcional:

- **O bloco de estilo é cópia VERBATIM da skill `quinteto-pixel-art-3d-voxel`.** A própria skill
  manda isso, porque prompt improvisado com "voxel render", "Minecraft" ou "cubos" puxa direto para
  o LEGO de plástico frio que ele reprovou em 17/07/2026.
- **Toda peça ancora nos cinco PNGs canon** (`~/naia-agent/.claude/skills/quinteto-pixel-art-3d-voxel/assets/`)
  por `images.edit`. É o que segura a calça do OpenClaw, a cabeça menor do Codexzinho e a Naia
  pixelada de blazer em vez de anime.
- **O fundo é `#0F172A`, não o off-white da skill.** A arte é colada num painel escuro e retângulo
  claro no meio dele é o que as regras de design do Chefe proíbem.
- **A tipografia NÃO é pixelada.** Texto em pixel art não se lê no celular e a peça existe para ser
  lida. Cena pixelada, interface limpa por cima, que é o que jogo HD-2D faz.

E o que muda de verdade em relação ao infográfico plano: **os personagens são atores, não adesivo de
margem**. Eles apontam, seguram, carregam, sobem, caminham. A escada de plataformas com a multidão
encolhendo ensina o funil antes de qualquer número ser lido; a torre gigante com o Claudinho
minúsculo ao pé é o que faz sentir 750 mil; a casa em corte com a sala alta e a sala baixa mostra a
diferença entre as duas imersões sem adjetivo nenhum.

As três armadilhas que a skill avisa e que já apareceram aqui: OpenClaw saindo com cara de formiga
ou sem calça, Codexzinho de cabeça grande demais, e Naia saindo anime em vez de pixelada. Confira as
três em toda peça antes de aceitar.

Três blocos são obrigatórios em TODA peça, foto ou infográfico:

- `CONTEUDO_OBRIGATORIO` · o que ele lê em voz alta tem que estar ESCRITO e legível na imagem,
  palavra por palavra. Tarja cinza, barra de placeholder, lorem ipsum, texto borrado, rabisco no
  lugar de letra e tela vazia **reprovam a peça e queimam a geração**. Foi exatamente o defeito da
  imagem do WhatsApp do vídeo 07, que o Chefe descreveu como "o mockup feio do caralho com telefone
  com imagem com nada na tela".
- `BASE_FOTO` · direção de arte de verdade. Câmera full-frame, lente prima, um foco prático
  dominante mais fill fraco, profundidade ótica crível, poro de pele, reflexo de vidro, realce
  anisotrópico em metal escovado. E a lista explícita do que denuncia imagem de IA: pele de cera,
  rosto simétrico de boneco, dedo a mais ou fundido, objeto flutuando, reflexo impossível, linha
  reta torta, tipografia derretida, borda brilhando, franja cromática, halo de HDR, nitidez
  exagerada. Tudo proibido.
- `SEGURANCA` · proibido continua tudo que é marca alheia, logo, endereço, endpoint, token, IP,
  telefone e e-mail reais. **A regra antiga proibia tela, campo e botão e foi ela que esvaziou a
  imagem do 07**: agora o que é proibido é o dado real, não a interface.

Para cena cujo assunto É uma tela, entra também `TELA_NA_FOTO`, que manda a interface vir completa,
em modo escuro, com balões de verdade e o texto da fala dentro, legível, com acento certo.

E `PROFUNDIDADE`, nos infográficos: três níveis de leitura obrigatórios (o de cinco segundos, o de
trinta e o do detalhe), relação entre blocos DESENHADA e não sugerida, e nada de elemento sem
função. O Chefe está pagando o melhor modelo de imagem que existe e não aceita saída de 2024.

### 5. Escrever as cenas em HyperFrames

Escreva um `CONTRATO.md` com a régua de layout, as classes prontas, as regras que reprovam e a fala
de cada cena. Quebre as cenas em blocos e **despache um agente por bloco em paralelo**, cada um
escrevendo só o seu arquivo em `blocos/<letra>.html`, no formato de duas seções:

```
<!--HTML-->
... as divs das cenas ...
<!--JS-->
... as linhas de timeline GSAP ...
```

Depois um merge só, feito por você, insere o HTML na ordem dos tempos e o JS no fim da timeline.
O contrato de referência está em `referencia/contrato-youtube-1.md`.

**A régua de animação vive em `referencia/componentes-painel.md` e o código pronto em
`referencia/componentes-painel.html`.** Sete componentes: fluxo, contador, barras, antes e depois,
lista viva, linha do tempo e destaque migrante. O agente ESCOLHE o componente pelo raciocínio do
trecho e copia o código, não reinventa.

A regra que manda, e que reprovou o primeiro lote inteiro: **nenhuma cena de conteúdo é feita só de
texto entrando**. Toda cena tem uma estrutura que se MONTA na frente do espectador, e o que se
monta é o raciocínio dele. Headline mais três linhas com fade continua existindo, mas só para a
frase de efeito, uma por vídeo, não sete. Palavras do Chefe em 05/08/2026: "quero animação bonita,
profunda, com complexidade, com didática, que ilustre de verdade o que está sendo dito no vídeo".

As regras que o contrato precisa carregar:

1. Toda cena é `<div id="cNN" class="clip livre" data-start data-duration data-track-index="2">` com
   os tempos exatos do mapa.
2. Animação só por `transform` e `opacity`, ou por `width` de barra de dados. Animar `top`, `left`,
   `fontSize`, `padding` ou `margin` faz o motor de captura tremer.
3. A tela nunca passa 2 segundos sem movimento, e o movimento vem do CONTEÚDO: número contando,
   barra crescendo, item entrando, destaque migrando. Proibido barra de progresso, varredura,
   partícula e brilho decorativo. O Chefe reprovou isso com todas as letras: "quando eu disse que
   não quero a tela 2 segundos sem movimento não foi pra vc encher de palhaçada, foi para a animação
   feita com hyperframe ser eficiente".
4. Zero travessão em texto de tela.
5. Nada colide, nada passa de 1000.
6. O texto sai da fala daquele momento. Headline curta, afirmativa, em minúsculas. Nunca inventar
   número que ele não disse.
7. IDs e variáveis JS prefixados pela cena.

### 6. Verificar ANTES de renderizar

Render de 12 minutos custa 9 minutos de relógio. Não gaste um render para descobrir defeito de
layout: o CLI tira frame direto da composição.

```
npx hyperframes snapshot --at "12.4,33.1,55.5,..." --no-end -o snaps --describe false
```

Tire um frame perto do FIM de cada cena, que é quando todo o conteúdo já entrou e é onde a colisão
aparece, monte uma folha de contato e revise as cenas uma a uma. Rode também `npm run check`.

### 7. Renderizar e auditar

```
npm run render
```

Depois do arquivo pronto, rode a auditoria dos 2 segundos, que é a prova que o Chefe pediu:
`scripts/youtube-1/audita_2s.py`. Ela amostra o painel a 2 quadros por segundo ao longo do vídeo
inteiro e acusa qualquer janela de 2 segundos sem movimento perceptível, com o tempo exato.

Rode também a conferência de sincronia: escolha uns dez instantes em que você sabe pela transcrição
o que ele está falando, extraia o frame e confirme que o slide na tela é o daquela frase.

### 8. Cortar o silêncio

O corte vai no arquivo **já renderizado**, não no áudio de origem, e é a última coisa antes do
encerramento. Assim você não precisa refazer a timeline inteira.

O `silencedetect` do ffmpeg pode não achar nada quando o piso de ruído é alto, e foi o que aconteceu
no T1: zero pausas a -32dB, e na verdade havia 166 pausas somando 69 segundos. Meça pelo envelope
RMS em janelas de 50ms (`scripts/youtube-1/corta_silencio.py`), com limiar em torno de -40dB,
pausa mínima de 0,30s e guarda de 90ms de cada lado para não comer o começo nem o fim das palavras.

O corte é uma passada só de `trim`/`atrim` mais `concat` no filter_complex. Avise o Chefe do efeito
colateral: como o corte é no vídeo já queimado, a animação dá pequenos saltos nos pontos de corte.
Nas pausas curtas passa despercebido; se incomodar, o conserto é aplicar o mesmo plano no áudio de
origem e re-renderizar a apresentação já na timeline cortada.

### 9. Fechar o pacote de publicação

O vídeo sozinho não é a entrega. O modelo YouTube 1 só termina com o pacote completo, e o passo a
passo dos quatro itens está em `nucleo/encerramento-youtube.md`:

1. **Arte de encerramento** colada por 10 segundos no fim, de `assets/encerramento-youtube.png`.
2. **Thumbnail** própria do vídeo, gerada por `scripts/youtube-1/gen_thumb.py`.
3. **Documento da legenda**, que abre com três opções de título com estudo de SEO e a recomendada
   marcada, e segue com a legenda em três partes: CTA com o link https://denderson.ai na primeira
   linha, o convite do Instagram com o link clicável, e a legenda do conteúdo escrita a partir do
   que ele fala no vídeo.
4. **Pasta na Desktop**, em `~/Desktop/conteudo youtube/<NN> - <titulo>/`, com `video.mp4`,
   `thumbnail.png` e `legenda.txt`.

A regra que vale para as duas artes: **o texto é escrito pelo próprio gpt-image-2**, nunca composto
por cima. O modelo acerta acentuação em português quando o prompt soletra os acentos e diz que a peça
é uma thumbnail ou um card de fim de vídeo que precisa ser legível no celular.

## AS ARMADILHAS QUE JÁ CUSTARAM CARO

Todas foram encontradas na montagem do T1, em 04/08/2026. Confira uma a uma antes de entregar.

**A duração do `<video>` e do `<audio>`.** Quando você troca o master (por exemplo para colocar o
gancho na frente), atualize o `data-duration` de TODOS os elementos, não só o do root: o
`<video id="video-chefe">` e o `<audio id="audio-chefe">` têm duração própria. Ficaram com o valor
antigo e, a partir daquele segundo, a coluna da gravação apagou e o áudio parou, comendo treze
segundos de fala no meio de uma frase. O Chefe viu na tela: "os últimos segundos o meu video do lado
direito sumiu e ficou só hyperframe".

**Os eventos escritos em várias linhas.** Contador com `onUpdate` termina numa linha que começa com
`} },` e não com `tl.`. Qualquer script que remapeie tempos procurando linhas iniciadas por `tl.`
deixa esses eventos para trás, com o tempo antigo, e eles disparam fora da própria cena. No T1 isso
abriu buracos de até 16 segundos com a tela parada.

**Reescalar a duração junto com o início.** Ao mover uma cena para uma janela mais curta ou mais
longa, o início de cada evento muda, mas a `duration` dos eventos longos (contadores, barras, zoom)
também precisa ser reescalada, senão transborda a cena ou deixa cauda morta.

**Zoom corta infográfico.** O movimento lento de escala nas imagens é bom em foto e péssimo em
infográfico: mesmo com `contain`, qualquer escala acima de 1 corta as bordas. Em cena de infográfico
a imagem entra com um reveal que termina em escala 1 e fica parada; o movimento vem da faixa e dos
ticks.

**Elemento sobre o infográfico.** Etiqueta posicionada em cima da arte cobre justamente o que o
Chefe quer ver. Se precisar de rótulo, ele vai na faixa, não sobre a imagem.

**Animar filho antes do pai aparecer.** Um evento em cima de um elemento cujo container ainda está
invisível não existe para quem assiste: o tempo passa, o script marca movimento, e a tela está
parada. No T1 os três rótulos da faixa da cena 6 animavam segundos antes de a faixa entrar, e isso
abriu a única janela morta que sobrou na entrega. Antes de fechar uma cena, confira que **todo
elemento animado já entrou em cena no instante em que o evento dispara**, e que o pai dele também.
Em cena de infográfico, onde a imagem fica parada de propósito, esse é o erro mais fácil de cometer,
porque o movimento inteiro depende da faixa.

**Barra sem `width` e preenchimento sem `background`.** `.barra-tubo` sem largura inline colapsa e a
barra simplesmente não existe na tela; `.barra-fill` sem cor fica invisível; `.barra-val` sem `left`
cai colado na borda esquerda do painel. Varra o HTML final procurando os três casos.

**Rótulo comprido na faixa.** Tick com texto longo quebra em duas linhas e vaza para fora da faixa
escura, virando texto claro sobre fundo bege. Máximo de 6 ticks, cada um com no máximo 15
caracteres, e `white-space: nowrap` no CSS.

**Headline de duas linhas em cena de imagem.** A imagem começa em 146; headline de duas linhas de
56px passa disso e fica cortada atrás da foto. Em cena de imagem, headline sempre em uma linha.

**Texto encavalado.** Subtítulo de duas linhas sobre um bloco que começa logo abaixo, dois rótulos
adjacentes que se tocam, valor de barra atrás do preenchimento. Só a varredura de frames pega isso;
o `check` não reprova.

## ARMADILHAS DO SEGUNDO LOTE (T2, T3 e T4, 04/08/2026)

Estas apareceram ao produzir três vídeos em série reaproveitando o projeto do primeiro. Todas
custaram pelo menos um render de nove minutos.

**O `</div>` do painel some quando você reaproveita o esqueleto.** Ao recortar o `index.html` de um
vídeo pronto para virar molde, o fechamento do `#painel` mora entre a última cena e o
`<div id="coluna">`. Cortar na linha da coluna deixa esse fechamento de fora, a coluna nasce DENTRO
do painel e **a gravação do Chefe some do vídeo inteiro**. O `check` não reprova, porque o HTML
segue válido, e a auditoria dos 2 segundos também não, porque ela mede o painel. Depois de cada
merge, confira duas coisas: o saldo de `<div>` contra `</div>` no corpo tem que ser zero, e a
profundidade de aninhamento no ponto da coluna tem que ser 1, não 2. E meça o brilho da coluna num
frame do render antes de seguir.

**HTML solto dentro de `proj/` vira uma segunda composição.** Arquivos de esqueleto ou de teste
deixados na pasta são descobertos pelo motor como outro ponto de entrada, o que duplica o áudio.
Guarde molde e teste fora de `proj/`, e mande os agentes fazerem o mesmo.

**`transform` inline briga com o GSAP.** Elemento com `transform: scaleX(0)` no style e um tween de
`scaleX` faz o motor avisar que vai sobrescrever o transform inteiro. O estado inicial mora só no
`fromTo`.

**Número gigante com `line-height: 1` invade o rótulo de cima.** O glifo sobe acima da caixa, e o
detector de colisão só acusa depois que o texto final está aplicado. Deixe pelo menos 24px a mais
entre o rótulo e um KPI de 150px, e confira a legenda de baixo também.

**Movimento que não move pixel não conta.** Pulso de escala em tick de 16px aparece na timeline e
não aparece na tela: a auditoria reprova mesmo com evento registrado. Em cena de infográfico, onde a
imagem fica parada de propósito, o movimento tem que vir do **texto grande da faixa**, deslizando ou
trocando. Isso apareceu em quatro cenas diferentes ao longo dos três vídeos.

**O prompt da thumb repete o texto em dois lugares.** A lista das três linhas e o bloco
`SPELLING IS CRITICAL` dizem o mesmo texto, e o bloco de soletração é mais enfático. Trocar só um
faz a arte sair com o valor do vídeo anterior. Troque nos dois ou parametrize.

**O corte da thumb para 16:9 se divide entre topo e rodapé.** A arte sai em 3:2 e sobram 160px de
altura. Cortar tudo pelo rodapé come a última linha do texto, tudo pelo topo come a testa. Meça onde
a última linha termina e reparta, tipicamente 60 em cima e 100 embaixo.

**`rm -f` com curinga vazio aborta a cadeia no zsh.** `rm -f renders/*.mp4 && npm run render` não
renderiza quando a pasta está vazia. Remova o diretório inteiro e recrie.

**`fromTo` com `opacity: 1` no estado inicial empilha texto na tela.** O GSAP aplica o estado
inicial de um `fromTo` no quadro ZERO (`immediateRender`), então um fade de saída escrito como
`fromTo(alvo, { opacity: 1 }, { opacity: 0 })` acende o elemento desde o começo do vídeo. Numa faixa
com sete frases que se revezam, as sete nascem visíveis e viram um borrão ilegível. O `check` não
acusa, a auditoria dos 2 segundos não acusa, e só se vê assistindo. Duas regras: fade de saída é
sempre `to`, nunca `fromTo`; e quando várias frases ocupam o mesmo lugar, use **um elemento só**
trocando `textContent` no `onComplete`, nunca vários empilhados. Esse é o padrão do T1 e do T3.

**Falso positivo conhecido do `check`.** Dois textos na mesma coordenada com o de cima sobre fundo
opaco (um cartão que troca de estado, por exemplo) são acusados como sobreposição ilegível. Confira
com snapshot antes de mexer: se a tela está limpa, é falso positivo.


## ARMADILHAS DO TERCEIRO LOTE (vídeo 05, painel escuro, 04/08/2026)

Seis renders neste vídeo, todos por defeito real. Estas cinco são as que custaram render.

**A faixa narrativa fatiada em intervalos iguais.** O agente de bloco divide a duração da cena
pelo número de etapas e distribui. A fala não anda assim: ele recita cinco etapas em nove segundos
e depois gasta oito numa só. Medido no 05: quando ele dizia "esse link leva pra um site" (etapa 4),
a tela mostrava "02 direct automático". **Toda troca de faixa é ancorada no instante em que aquela
etapa é falada**, medido na transcrição por palavra, igual às cenas. Isso vale para contador
também: no 05 o contador chegou a 3 plataformas cinco segundos antes de ele dizer "três".

**Script que anexa linha no fim da lista joga o evento para fora do `<script>`.** O
`reancora_faixa.py` fez `linhas.append(...)` sobre o arquivo inteiro, e sete eventos foram parar
depois do `</html>`. Código morto: o `check` não acusa porque o HTML segue válido, e a auditoria
dos 2 segundos só diz "parado", sem dizer por quê. **Toda edição de timeline entra ANTES de
`window.__timelines["main"] = tl;`**, e o build audita que não existe nenhum `tl.` depois do
fechamento do script.

**Empurrão que manda o elemento para onde ele já está não move pixel.** Ao preencher vão longo,
clonar o mesmo `tl.to({x: 26})` várias vezes faz só o primeiro mover. E alternar por índice par e
ímpar não basta, porque a entrada da batida pousa o elemento em `x: 0` e o alternar pode calhar de
mandar para 0 de novo. A regra que se prova sozinha: percorra a linha do tempo guardando onde o
elemento está, e cada empurrão sai obrigatoriamente para o outro lado.

**Fade de saída que termina antes do fim da cena deixa painel preto.** No 05 eram quatorze pontos,
o pior com 0,84s de painel vazio antes da cartela final. O build atrasa toda saída para terminar no
instante exato do corte.

**Buraco no começo de cena de infográfico depois da reancoragem.** Ao colar as batidas na fala, o
começo da cena pode ficar sem faixa. Não preencha com enfeite: procure o que ele está dizendo
naqueles segundos e transforme em batida. No 05 o buraco virou "e isso com o site já pronto", que
é literalmente a frase dele ali.

**O `check` também pega o HTML solto dentro de `proj/`.** O backup do index deixado ao lado vira
uma segunda composição e duplica o áudio. Guarde backup fora de `proj/`.

## A INVERSÃO DO LADO (montagem B)

Vídeo par usa a gravação à esquerda. Só as duas coordenadas de `left` mudam. Depois do merge,
confira que nenhuma cena posiciona por `right` sem par, e revise a folha de contato inteira: elemento
posicionado por engano em coordenada de tela, e não relativa ao painel, só aparece torto depois de
inverter.


## O CORTE FINO (método reescrito em 05/08/2026, depois de o Chefe reprovar o lote)

O Chefe assistiu o 05 entregue e reprovou: "tem bastante silêncios, bastante repetições,
e frases que podem ser eliminadas", "teve momento que vazou áudio de alguém que me
atrapalhou e eu fiquei parado até mutar o áudio do invasor". Ele estava certo. Medido
nos catorze entregues, o silêncio ia de 3,9% a 26,7% do vídeo, com pausa de até 9
segundos dentro do conteúdo.

### Passo 1 · o silêncio sai por ENERGIA, o whisper não opina

O `corta_silencio.py` antigo perguntava ao whisper onde cada palavra começa e acaba, e
vetava corte que encostasse nesse intervalo. Não funciona, porque **o whisper estica o
tempo da palavra por cima da pausa**: no 05 ele jurava que "para" durava 4,93 segundos e
que "ou" durava 4,48. Cada palavra dessas blindava vários segundos de silêncio, e 88% do
arquivo ficava protegido.

A verdade que destrava é uma frase: **se um trecho não tem energia, não pode haver
palavra nele.** Então o silêncio é decidido só pela energia. Use `corta_fino.py`.

Dois limiares, e é isso que impede comer sílaba:

| limiar | serve para |
|---|---|
| `-45 dB` | achar o silêncio, ou seja, o que dá para cortar |
| `-58 dB` | achar a CAUDA da palavra, o que não se pode tocar |

Consoante final de "mais", "faz", "então" tem energia baixa e morreria com um limiar só.
A guarda não é fixa: ela anda para dentro do silêncio enquanto o sinal ainda está
decaindo acima do limiar de cauda, e é assimétrica (0,06s antes, 0,20s depois), porque o
problema é sempre na cauda.

Resultado no lote: silêncio de 19% para 7% no 05, e a maior pausa de cada vídeo caiu de
até 5,2 segundos para menos de 1.

### Passo 2 · o conteúdo sai por leitura, em BLOCOS entre silêncios

O detector automático (`acha_dispensavel.py`) acha repetição literal e pouco mais: no 05
propôs 15 segundos onde havia 80. Quem faz esse trabalho é um agente lendo o **mapa de
corte** (`mapa_corte.py`), que mostra o que a transcrição esconde: cada pausa marcada com
a duração, e o nível de voz de cada fala comparado com a mediana da voz dele.

Seis famílias: `REPETICAO`, `MULETA`, `INTERACAO`, `DIVAGACAO`, `INVASAO`, `BLOCO`. Para
cada trecho o agente escreve a `emenda`, ou seja, como a frase fica depois do corte. Se a
emenda ficar torta, o corte não é proposto.

**A unidade do corte é o BLOCO ENTRE DOIS SILÊNCIOS MEDIDOS, nunca um instante.** Isso
custou três tentativas:

1. cortar no instante proposto quebrou frase ("eu vou até *sequer saibam* o que é automação");
2. exigir que a borda proposta caísse perto de uma pausa rejeitou tudo, porque o agente
   estima o tempo lendo o mapa;
3. usar o intervalo entre palavras do whisper como fronteira também quebrou ("*tiras na
   vida*", metade de "tirando quem já construiu um funil de vendas na vida"), porque o
   whisper separa palavra sem que exista silêncio no áudio.

O que funciona é definir os blocos pelo silêncio de energia e remover blocos inteiros.
Duas travas obrigatórias em cima disso: o bloco só entra se **70% dele** estiver dentro do
pedido, e o corte aplicado não pode passar de **1,35 vez o pedido mais 1,5s**. Sem a
segunda trava o corte fica guloso e chega a INVERTER sentido: no 05 comeu o "eu não estou
falando" de "eu não estou falando que você não vai mais usar plataformas".

### Passo 3 · a INVASÃO se identifica por TIMBRE, nunca por volume

A live inteira foi um Zoom com outras pessoas, então voz alheia é normal. Ordem do Chefe:
"vc deve sim identificar essas invasões mas sem cortar falas minhas importantes".

Volume não separa pessoa: no 08 havia 26 falas muito abaixo da mediana e **todas eram
ele**, com a lapela abafada depois que ele tirou a blusa aos 393s (de 403s ao fim o vídeo
inteiro está 5 a 15 dB mais baixo, e isso pede ganho, não corte).

Quem separa é o timbre. O `perfil_voz.py` mede por fala a altura da voz (f0 por
autocorrelação), o centroide e o rolloff do espectro, monta o perfil dele pela moda
ponderada pela duração, e dá a distância de cada fala até esse perfil. **Fala abaixo de
1,5s não é classificável**, porque não tem ciclos suficientes para medir altura de voz, e
vira `curto_demais`: aí decide-se pelo texto.

A regra editorial vale mais que a detecção:

- **pergunta de aluno que ele responde em seguida FICA**, senão a resposta fica órfã;
- só é invasão o que **não tem relação com a aula E atrapalha**, principalmente o trecho
  em que ele para e espera até mutar;
- a assinatura da invasão é voz estranha, pausa longa, e ele **retomando a frase
  interrompida do zero**.

No lote inteiro havia UMA invasão de verdade, no vídeo 07 em 134,84s, com f0 de 153 Hz
contra os 183 Hz dele, 2,13s de espera e a pergunta refeita pela terceira vez.

### Passo 4 · a prova, que agora é dupla

**Geométrica**, contra o plano do corte: nenhum intervalo removido pode cobrir 25% ou mais
de uma palavra. É determinística e não depende de reconhecedor.

**Da emenda** (`prova_emendas.py`): calcula onde cada corte caiu no arquivo NOVO, recorta
oito segundos em volta e transcreve isolado. O texto que sai é a costura como o
espectador vai ouvir. Reprova palavra dobrada em cima da emenda, mudança de assunto sem
conectivo, e sentido invertido. **Foi essa prova que pegou os três defeitos acima**, e
nenhum deles aparece no `check`, na auditoria dos 2 segundos ou na prova geométrica.


## OS DOIS CTAs, QUE SÃO PADRÃO EM TODO VÍDEO (05/08/2026)

Todo vídeo do canal leva um CTA no meio, sem exceção. São duas peças gravadas, já editadas e
prontas em `~/Desktop/conteudo youtube/CTAs/`, e os projetos vivem em `~/workspace/cta1-full` e
`~/workspace/cta2-full`.

| peça | duração | montagem | o que diz |
|---|---|---|---|
| `CTA1.mp4` | 1:18 | A, gravação à direita | um convite, se inscrever e ativar a notificação, a imersão mensal, a equipe da Naia, preço de pizza, dois formatos, o ingresso na descrição |
| `CTA2.mp4` | 1:23 | B, gravação à esquerda | dois pedidos, inscrição e notificações, os formatos da imersão, a equipe da Naia, "se acontece dentro de um computador a Naia consegue fazer", o link na descrição |

**A alternância.** CTA 1 nos vídeos de número ímpar, CTA 2 nos pares. Do vídeo 05 em diante isso
faz a montagem do CTA bater com a do próprio vídeo, porque os vídeos também alternam A e B, e a
inserção deixa de parecer um enxerto.

**O que o CTA tem de diferente do vídeo**, e por quê, está inteiro no cabeçalho do
`prepara_cta.py`: não tem gancho (gancho segura quem chega, e aqui já estamos no meio), o
cabeçalho da marca fica a peça inteira (é o sinal de que aquilo é recado do canal), não tem
rodapé nem carimbo de cena (a faixa cobre o rodapé e o carimbo cai dentro do cabeçalho, os dois
reprovam no `check`), e quem nomeia a cena é o rótulo de capítulo, que troca de texto. A geometria
sobe: o conteúdo nasce em 200 e não em 34, porque o cabeçalho permanente ocupa 54 a 175.

**O infográfico da equipe não sai da tela.** Ordem direta do Chefe. A arte entra uma vez e fica
até o corte da cena, 22,8s no CTA 1 e 26,5s no CTA 2, e quem se move é a faixa embaixo dela,
acendendo cada capacidade no instante exato da fala: sites, vídeos, imagens, atendimento nos
canais, vendas, CRM e as funções fora do marketing.

**O CTA é DETERMINÍSTICO.** Não se escreve bloco de CTA à mão e não se despacha agente para isso.
O conteúdo editorial mora em `blocos.json` e o `blocos_cta.py` gera a geometria e o tempo. Ele
sozinho já garante tipografia que cabe, faixa ancorada na fala, tela nunca parada, linha de cena
curta que não nasce durante o fade, e batida de faixa que não atropela a anterior (a troca inteira
leva 0,50s: duas batidas a menos de 0,55s uma da outra fazem a faixa piscar sem assentar, o que
aconteceu no CTA 2 quando ele lista cinco canais em dois segundos, e a saída é juntar os canais
numa linha só).

### Onde o CTA entra, que foi o que deu mais trabalho

`insere_cta.py` escolhe o ponto sozinho, e o método levou três tentativas até ficar honesto:

1. **pausa mais próxima do meio** · errado. Depois do corte fino todas as pausas viraram curtas e
   parecidas, então duração de silêncio não distingue respiro de fim de frase. No vídeo 07 o CTA
   entrou dentro de "só que aí, na semana seguinte".
2. **fim de segmento do whisper** · errado. O segmento é longo e quase nunca pontua: foram 14
   segmentos e um só terminava frase, e esse um era uma pergunta retórica seguida da resposta.
3. **fim de palavra com pontuação** · quase. Como o whisper adianta o fim da palavra, o casamento
   pegava o silêncio ANTERIOR a ela e o vídeo voltava com um "Certo?" solto.
4. **o VÃO entre a palavra que fecha e a que abre a próxima** · certo. O silêncio medido tem que
   COMEÇAR dentro desse vão, e o corte vai 60 ms antes de a fala voltar, o que joga tudo que veio
   antes garantidamente para a primeira metade. Ponto final vale mais que interrogação, porque
   pergunta quase sempre é seguida da própria resposta.

Depois de inserir, **sempre** transcreva os 8 segundos em volta das duas emendas e leia o que sai.
E rode o `reancora_cta.py`, que empurra em +78s (ou +83s) todo capítulo posterior à entrada,
cria um capítulo próprio para o recado e recalcula o contador de caracteres do cabeçalho contando
só o bloco entre a régua do "COLE DAQUI" e a do "FIM DO QUE VAI PARA O YOUTUBE".

## O QUE REPROVA A ENTREGA

- Vídeo publicado sem CTA no meio.
- CTA que entra no meio de uma frase, ou que devolve o vídeo com palavra órfã.
- Capítulo da legenda que não andou depois da inserção do CTA.
- Qualquer janela de 2 segundos sem movimento no painel, medida pelo `audita_2s.py`.
- Slide que aparece antes ou depois da frase que ele ilustra.
- Infográfico cortado.
- Corte que come o começo ou o fim de uma palavra.
- Vídeo ou áudio que param antes do fim da timeline.
- Travessão em texto de tela, gradiente, emoji na interface.
- Troca de faixa que não bate com a etapa que ele está falando.
- Evento de timeline fora do `<script>`.
- Pausa acima de 1 segundo dentro do conteúdo, ou silêncio acima de 8% do vídeo.
- Emenda que dobra palavra, quebra frase ou inverte sentido.
- Corte em fala de aluno cuja resposta dele fica órfã.

## A ENTREGA

Arquivo final, a folha de contato com um frame de cada cena e a saída do `audita_2s.py`. O Chefe não
precisa confiar, ele confere.
