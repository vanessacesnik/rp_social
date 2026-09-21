# NÚCLEO: GANCHO

Vale para todos os modelos. Todo vídeo editado abre com um gancho, e a skill **sempre pergunta**
antes de escolher: manter o gancho que já está no vídeo, ou puxar um gancho de dentro do miolo.

## AS DUAS OPÇÕES QUE SE PERGUNTA

**Manter o começo original.** Quando o vídeo já abre quente, mexer só piora. É o caso de material
gravado com abertura pensada.

**Puxar gancho do miolo (cold open).** A frase mais forte de dentro do vídeo é copiada para a frente.
Ela **continua no lugar original**: é cópia, não recorte, exatamente como os cortes virais fazem.
Autossuficiente, 3 a 8 segundos, frase completa, nunca cortada pela metade.

## O QUE A BASE DE 110 CORTES VIRAIS MOSTRA

`referencia/cortes-virais-110-transcricoes.txt` traz 110 cortes de podcast e live com 1,96M a 42,2M
de views (média 5,6M, mediana 4,1M), transcritos em 19/07/2026. Medindo a **primeira frase** de cada
um contra o desempenho:

| padrão na primeira frase | frequência | média de views |
|---|---|---|
| termina em **pergunta** | 24,5% | **8,1M** (+45% vs média) |
| contém **você / tu / teu / seu** | 21,8% | **7,0M** (+25%) |
| **frase seca**, até 6 palavras | 25,5% | **6,6M** (+18%) |
| abre negando (não, nunca, nada) | 6,4% | 5,9M (na média) |
| contém **número** | 8,2% | **3,2M** (43% abaixo) |
| contém dinheiro (R$, mil, milhão) | 3,6% | 4,4M (abaixo) |

A abertura dos 20 mais vistos tem **mediana de 8 palavras**; a dos 20 menos vistos, 11.

**Isso corrige a hierarquia antiga.** As skills anteriores mandavam colocar "número específico
chocante" em primeiro lugar. Na base real, número na abertura é o padrão **menos frequente e de pior
média**. Número convence no meio do argumento, não na porta de entrada: ele pede contexto que o
espectador ainda não tem.

**Ressalva honesta:** views dependem muito de autor e assunto, e a base é de podcast e polêmica
geral, não do nicho de negócios e IA. Isso é correlação, não prova de causa. E o recorte de
"abertura com saudação" tem só 4 casos, amostra pequena demais para virar regra. Use a tabela como
ordem de preferência, não como lei.

## HIERARQUIA DE ESCOLHA (revisada em 25/07/2026 com os dados acima)

1. **Pergunta curta que já é confronto.** "Vagabundo?", "Não tem branco pobre?", "Ela supera a
   biologia?". Abre um loop que só fecha assistindo.
2. **Implicação direta do espectador.** A frase que tem "você" e acusa, provoca ou promete algo a
   quem está do outro lado.
3. **Afirmação contraintuitiva ou polêmica**, dita seca, sem preâmbulo.
4. **Open loop**, promessa de revelação que o vídeo cumpre.
5. **Pico emocional** ou aforismo forte.
6. **Número chocante**, que continua valendo quando o número é o assunto do vídeo (o caso do vídeo
   dos 12,5 milhões de empresas), mas deixou de ser a primeira escolha por padrão.

**Regra transversal:** a primeira frase nunca é saudação nem contexto. Prefira a frase mais curta que
ainda se sustenta sozinha: entre duas boas, ganha a de menos palavras.

## COMO CORTAR O GANCHO

- Whisper word-level para os timestamps. **Nunca cortar palavra pela metade.**
- Começar ~0,15s antes da primeira palavra; terminar em 0,3 a 0,4s de silêncio ou em boundary natural.
- Frase **completa**, mesmo que passe um pouco dos 8s.
- Transição para o corpo: `xfade=transition=fade:duration=0.4:offset=(dur_gancho−0.4)` no vídeo e
  `acrossfade=d=0.4:c1=tri:c2=nofade` no áudio. O `c2=nofade` evita engolir a primeira palavra
  quando o corpo abre falando.
- `settb=AVTB` nos dois lados, senão o xfade recusa por timebase diferente.

## O VISUAL DO GANCHO, POR MODELO

- **Sanduíche e faixa Hyperframe:** faixa vermelha sólida `#D32F2F` cobrindo SOMENTE a região do
  strip (232px em 1080p, 464px em 4K), headline em 2 linhas, caixa alta, Bricolage Grotesque weight
  800 branca, auto-fit com teto de 175px em 4K, margens laterais de pelo menos 150px. O quadrado do
  talking-head e a área de baixo ficam com o conteúdo original durante o gancho.
- **Tela cheia e b-roll no rodapé:** headline em 2 linhas, caixa alta, em card vermelho `#D32F2F` na
  base do quadro, mesma fonte e mesmas regras de auto-fit.
- **Gennaro:** o cold open já é o card de gancho do próprio modelo, com o número ou a promessa nos 2
  primeiros segundos.

A headline é **derivada** da frase, não a transcrição dela: caixa alta, curta, com R$ e números
literais quando existirem.

## VERIFICAÇÃO

Por vídeo: duração final igual a original mais gancho menos 0,4s; frame do meio do gancho conferindo
que a headline é a certa **e** que o vídeo por baixo é o certo (já houve bug real de input trocado);
frame do meio do xfade; e whisper de ~2,5s na emenda mostrando que nenhuma palavra foi cortada.
