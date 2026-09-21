# Referencia do metodo Gennaro

Esta skill NAO duplica o dossie. O metodo completo, os dois formatos, o vocabulario dos 8 elementos
grafricos, as formulas de gancho, a estrutura narrativa e a tabela dos 25 reels analisados vivem no
dossie canonico. Leia ele quando precisar do "porque" por tras de cada regra desta skill.

## Dossie (metodo completo)

`/Users/naiarodrigues/naia-agent/knowledge/metodo-edicao-gennaroautomates.md`

Secoes uteis: secao 1 (o algoritmo de edicao dele: cadencia, legenda, os 8 elementos, bookends,
ganchos, estrutura narrativa), secao 3 (mapa de cada elemento para a nossa ferramenta) e secao 5
(as regras de producao que viraram esta skill: safe area, imagens gpt-image-2, logos, corte fino
word-level, punch-in, fecho assinatura).

## Frames de referencia visual (8 exemplares)

`/Users/naiarodrigues/naia-agent/knowledge/frames-gennaro/`

- `01_ganchoA_titlecard_ai-agency.jpg`. Card de titulo do gancho.
- `02_formatA_listbuild_pills.jpg`. Chips empilhando em lista.
- `03_formatA_floating_device_mockup.jpg`. Mockup de aparelho flutuando.
- `04_formatA_iconrow_mcp_flow.jpg`. Fileira de icones / fluxo.
- `05_formatA_roi_number_counter.jpg`. Contador de numero / ROI.
- `06_formatA_cta_instagram_dm_toast.jpg`. CTA "comente a palavra" + toast de DM.
- `07_formatB_split_listicle_5plugins.jpg`. Tela dividida do formato de listicle.
- `08_formatB_robe_keyword_pills.jpg`. Cabeca falante com chips de keyword.

> Para OLHAR um frame, quem abre e um subagente (contexto descartavel) ou o proprio Chefe via outbox
> do Telegram. Nao leia imagem no thread principal.

## Workspaces provados (exemplares do pipeline real)

- `/Users/naiarodrigues/naia-agent/entregas/teste-gennaro/`. "Faca 1 Milhao" (a versao mais completa).
- `/Users/naiarodrigues/naia-agent/entregas/gennaro-video2/`. "IA Salva Vendas".
- `/Users/naiarodrigues/naia-agent/entregas/gennaro-video3/`. "Dedo 100k" (traz `captions_curated.py`,
  o molde de curadoria manual de legenda, e a pasta `logos/` com svg oficiais ja baixados).

Os scripts desta skill sao a versao generalizada (sem caminho hardcoded) desses workspaces. Quando
precisar de um exemplar concreto de um elemento ou de um plano preenchido, olhe o `render/plan.json`
e os `elements/` desses tres.
