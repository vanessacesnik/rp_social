# NÚCLEO: PLATAFORMA DE DESTINO

**Pergunta obrigatória em toda edição, antes de qualquer corte.** O destino muda enquadramento,
duração alvo, safe area, posição de legenda e como o gancho é montado. Editar sem saber para onde
vai é retrabalho garantido.

| destino | canvas | duração alvo | o que mais muda |
|---|---|---|---|
| **Reels (Instagram)** | 1080x1920 (9:16) | 30 a 90s, teto 3min | UI cobre topo e base; legenda na faixa central-baixa |
| **TikTok** | 1080x1920 (9:16) | 21 a 60s, teto 10min | UI lateral direita é larga; texto foge da direita |
| **Shorts (YouTube)** | 1080x1920 (9:16) | até 3min | título sobreposto no topo; base com barra de progresso |
| **YouTube 16:9** | 1920x1080 | livre, 5 a 20min | sem UI cobrindo; legenda opcional; miniatura à parte |

## SAFE AREA POR PLATAFORMA (vertical)

A régua que a skill usa por padrão é a mais restritiva das três verticais, medida na tela real de
celular: **a faixa visível é de x=97 a x=983** (886px centrais dos 1080). Dentro disso, com respiro:

- **Texto largo** (cards, big numbers, contadores, recap): faixa `[160, 920]`, até ~760px.
- **Legendas**: faixa `[170, 910]`, até ~740px.
- **Elementos pequenos** (chips, badges, pills, toasts, stamps): faixa `[130, 950]`, até ~820px.

Vertical: manter conteúdo essencial entre y=250 e y=1650. O topo leva nome de perfil e o rodapé leva
legenda da postagem, botões e barra de progresso, que variam por app.

**TikTok pede um cuidado a mais:** a coluna de ações da direita é larga. Elemento que vive à direita
some atrás dela. Quando o destino for TikTok, puxar o conteúdo para o centro-esquerda e nunca
ancorar informação essencial na borda direita.

**Shorts** desenha o título por cima do topo do vídeo nos primeiros segundos. Cold open com card no
topo perde legibilidade; nesse destino, o card do gancho desce para a faixa central.

## YOUTUBE 16:9 (horizontal)

Muda o jogo: não há UI cobrindo, o espectador está sentado e o vídeo é longo. Consequências práticas:

- **Formato empilhado 8:9 não se aplica.** Para material horizontal existe a variante documentada em
  `modelos/vsl-longa.md` (canvas 1920x2160 com faixa Hyperframe em cima e vídeo original embaixo),
  usada quando o vídeo vai para página de vendas e não para o YouTube.
- Legenda é opcional e menor. Queimar legenda gigante em 16:9 é vício de vertical.
- A régua de safe area vertical não vale. Use margens de 5% em cada lado.
- **Corte de roteiro entra em cena** (ver `nucleo/corte-fino.md`): vídeo longo pede proposta de
  trechos para abrir mão, com sua aprovação item a item.
- Densidade de elemento cai: em vertical entra um estado visual a cada 1,5 a 2,5s; em 16:9 longo, o
  ritmo é bem mais espaçado, senão cansa.

## REAPROVEITAMENTO ENTRE PLATAFORMAS

Um vídeo vertical serve aos três destinos verticais com a mesma master, desde que respeitada a régua
mais restritiva. Vertical para 16:9 **não** se resolve com reenquadramento: ou se monta o formato
empilhado, ou se regrava. Avisar isso antes de editar, nunca depois.
