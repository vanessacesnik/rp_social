# NÚCLEO: QA E ENTREGA

Vale para todos os modelos. Cada item abaixo **reprova** e bloqueia a entrega. Aviso não é item de
QA: ou passa, ou volta para a bancada.

## 1. A FALA SAIU INTEIRA (sempre)

```bash
python3 scripts/nucleo/verifica_palavras.py --orig audio16k.json --cortado build/corpo.mp4
```
Precisa terminar em `VERIFICACAO_OK`. Ele re-transcreve o vídeo cortado e compara palavra a palavra
com o original, acusando palavra sumida e palavra picotada (letra inicial comida). Tokens de moeda
ficam fora da conta porque o whisper troca "30 mil reais" por "R$ 30 mil" entre duas passadas do
mesmo áudio, e isso não é erro de corte.

## 2. A RÉGUA DE MARGEM, MEDIDA PELA TINTA

Vale para todo modelo que desenha overlay (Gennaro, faixa, sanduíche, strips, cards de gancho):

```bash
python3 scripts/gennaro/measure_ink.py     # 0 item furando é o único valor aceitável
```
A medição que vale é a **tinta renderizada** (alpha > 150) dos PNGs, nunca a caixa do layout: texto
com `white-space:nowrap` transborda a própria caixa e o `getBoundingClientRect` mente. Rodar **antes
do build**, assim que os PNGs existirem: furou, conserta e re-renderiza só o elemento afetado.

Sintoma útil: `cx` longe de 540 quer dizer texto transbordando para a direita, não card descentrado.

## 3. OS OVERLAYS APARECERAM MESMO

```bash
python3 scripts/gennaro/verify_overlays.py   # compara o final com a base pré-overlay
python3 scripts/gennaro/verify_motion.py     # nenhum overlay congelado
```
É o único par de checagens que pega índice deslocado no `filter_complex` e `.mov` que não renderizou,
os dois erros que entregam um mp4 perfeito e sem o elemento.

## 4. ÁUDIO

```bash
python3 scripts/gennaro/verify_audio.py      # voz contínua nas emendas, SFX presentes
```
Mais o click check dentro do `qa_final.py`: o maior salto de amostra numa janela de ±25ms ao redor de
cada emenda tem que ficar abaixo do p99.9 global. Zero cliques é o alvo.

## 5. QA FINAL

```bash
python3 scripts/gennaro/qa_final.py          # sai 1 quando reprova
```
Duração contra o plano, A/V sync (limite 120ms), decode limpo, cliques nas emendas e o guard de
travessão em legenda **e** em todo HTML que foi para a tela.

## 6. A PROVA QUE NENHUM SCRIPT SUBSTITUI

```bash
python3 scripts/gennaro/proof_celular.py FINAL.mp4 t1 t2 t3 t4 t5 t6
```
Crop na proporção da tela de celular, aberto e conferido **a olho**. Foi assim, e só assim, que se
pegou card escrito sem acento ao lado de legenda acentuada em 25/07. Medição numérica não vê erro de
português, hierarquia feia nem elemento que colide com a legenda.

Em vídeo para YouTube 16:9, a prova equivalente é abrir em tela cheia e conferir três pontos.

## 7. SINCRONIA LABIAL (VSL e qualquer vídeo com muitos cortes)

Auditoria não amostral: três pontos por versão, whisper no próprio arquivo final, palavra plosiva,
frames ±3 do onset lidos, fechamento labial a no máximo 1 frame. Detalhe completo em
`modelos/vsl-longa.md`. A carga de prova é nossa; o Chefe não vai assistir caçando lábio torto.

## ENTREGA

- Arquivo final no workspace da entrega, nome `FINAL_<slug>_<modelo>.mp4`.
- Provas em `proof/celular/`.
- Matar o servidor estático se algum modelo tiver subido um.
- Reportar: caminho, duração, o que cada elemento cobre, e as provas dos itens acima.
- Cópia para os bancos em `Desktop/EDIÇÃO DE VÍDEO/` com prefixo `PROJETO_DATA_` quando for entrega
  de produção.
- **Nunca limpar o workspace antes da aprovação:** os PNGs e ProRes são insumo dos verificadores. Um
  workspace de vídeo de 80s fecha em torno de 1,3 GB.

## REGRA DE CARGA (inegociável, custou um Mac travado)

Encode pesado, principalmente 4K, sobe **um de cada vez**, com 60s entre lançamentos e portão de
`load < 45` antes do próximo. Fan-out cego de 12 ffmpeg já levou o Mac a load 177 com 37GB de swap.
