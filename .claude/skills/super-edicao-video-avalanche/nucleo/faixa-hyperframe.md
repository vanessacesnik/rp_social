# NÚCLEO: TODO OVERLAY É UM ORGANISMO VIVO (faixa E card)

**Regra estabelecida pelo Chefe em 25/07/2026, depois de TRÊS rodadas de retrabalho.** Vale para
todo overlay de todo modelo: a faixa do sanduíche e da VSL, e também o CARD do Gennaro.

A terceira rodada aconteceu porque eu corrigi a faixa e não levei o princípio para o card do
Gennaro, que tinha exatamente a mesma doença. Nas palavras dele: *"eu falei isso no outro modelo,
você em vez de adaptar para esse, fez a mesma cagada."* **Princípio corrigido num modelo vale
imediatamente para todos.**

As palavras dele: *"essa faixa tem que ser um organismo vivo e não só texto. Texto por texto já tem
a legenda. É pra ilustrar, trazer desenho, infográfico, mecanismo, desenhar o que eu tô falando."*
E depois: *"duas frases, nenhum infográfico, e principalmente o espaço disponível muito mal
aproveitado, preencha o espaço todo. E não só nesse trecho, em todos."*

## O QUE ESTÁ PROIBIDO

- **Kicker mais headline mais um número.** Isso é legenda com outra fonte. A legenda queimada já
  está na tela, colada logo acima da faixa.
- **Frase dentro de retângulo.** Duas caixas com texto não são infográfico.
- **Sobrar vazio.** Desenhar só na metade de cima, ou reservar um terço da largura para um rótulo
  quase vazio, é desperdício do único espaço que a faixa tem.
- **Repetir o mesmo arquétipo em janelas seguidas.** Dezoito faixas iguais é o mesmo erro em série.

## A GEOMETRIA (`scripts/nucleo/faixa_hyperframe.py`)

Faixa de 1080x232, dentro de [130, 950] que é o que o celular mostra:

```
chip      x 142, y 12, altura 26     rótulo curto, uma linha, no canto
desenho   x 142..950, y 46..196      808 x 150, a área do infográfico
barra     y 206..212                 temporizador global contínuo
```

O chip fica acima do desenho com 8px de folga, então nada se sobrepõe por construção. O fundo leva
uma grade sutil para não existir vazio morto.

## AS DUAS BIBLIOTECAS

- `scripts/nucleo/faixa_hyperframe.py` para a FAIXA de 1080x232 (sanduíche, faixa, VSL).
- `scripts/nucleo/infografico.py` para o CARD de 760x360 do Gennaro e overlays de tela cheia.

Mesmos arquétipos, geometrias diferentes. O card tem um a mais, `imagem_dados`.

## IMAGEM MESCLADA COM ELEMENTO (ordem do Chefe, 25/07/2026)

*"O Gennaro não é só hyperframe, pode e deve incluir imagens. Você pode inclusive mesclar imagens
com elementos do hyperframe na mesma animação, ao mesmo tempo na tela, desde que um não sobrescreva
o outro e não fique feio."*

`imagem_dados` faz isso com zonas exclusivas: imagem de 330px à esquerda com moldura, legenda e Ken
Burns leve, corredor de 24px, e o bloco de dados à direita com barras animadas e valores. As duas
zonas nunca se cruzam. As imagens do gpt-image-2 já geradas para um modelo servem para o outro:
reaproveite em vez de gerar de novo.

## A BIBLIOTECA DE MECANISMOS

Cada função desenha e anima por `window.__seek`, preenchendo os 808x150:

| arquétipo | quando usar | o que desenha |
|---|---|---|
| `fluxo` | processo, cadeia, implementação, "faz isso e vira aquilo" | cards altos com ícone, título e subtítulo, ligados por conexão que pulsa |
| `barras` | comparação de grandeza, evolução, quanto cada coisa pesa | colunas com valor em cima, eixo e rótulo embaixo |
| `painel` | um número é o assunto (preço, salário, faturamento) | número gigante com trilho, mais barras satélite de contexto |
| `confronto` | antes contra depois, paradoxo, promessa contra realidade | dois painéis do tamanho da faixa, cada um com sua barra, seta no meio |
| `medidor` | proporção, percentual, "a maioria" | anel grande com valor, mais lista de itens marcando ao lado |
| `acumulo` | uma coisa ruim somando na outra, atrito acumulado | cards de carga entrando com sinal de mais, e uma barra despencando a cada carga |

Assinatura e parâmetros no cabeçalho de cada função do módulo.

## COMO ESCOLHER

Pela **fala daquela janela**, não pelo que sobrou. Números viram `painel` ou `barras`. Contradição
vira `confronto`. Processo vira `fluxo`. Proporção vira `medidor`. Atrito somando vira `acumulo`.
Se duas janelas seguidas pedirem o mesmo arquétipo, mude o ângulo de uma delas ou troque a cor de
acento e o conjunto de dados, nunca entregue duas iguais coladas.

## O TEXTO NA FAIXA

Curto e de apoio, sempre. O chip é um rótulo de duas ou três palavras. Dentro do desenho, o texto é
rótulo de eixo, nome de etapa, unidade. **Nunca a frase falada**, que é trabalho da legenda.

## VERIFICAÇÃO

1. Renderize um frame a 85% da janela (com a animação já assentada) de cada faixa.
2. Meça a tinta: precisa ficar dentro de [130, 950]. Sobra grande de um lado é sinal de espaço
   desperdiçado, não só de segurança.
3. Olhe as 18 juntas numa tira: se duas seguidas parecem irmãs, refaça uma.
4. Confira que nenhum elemento encosta em outro, principalmente rótulo de extremidade de `fluxo`,
   que alinha para dentro justamente para não vazar.
