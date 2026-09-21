# MODO LOTE: TRIAGEM DE CORTES (separar o joio do trigo antes de editar)

> Migrado VERBATIM da skill `triagem-cortes-live` em 2026-07-25.
> Entra quando o Chefe manda um LOTE de videos em vez de um so.

---

# Triagem de Cortes de Live (separar o joio do trigo)

Recebe N cortes de live (talking-head), transcreve TODOS e classifica um a um. Saída: relatório com a classificação e o motivo de cada corte. Nada é editado nesta skill.

## PROCESSO
1. **Inventário:** ffprobe de todos os arquivos (duração, dims, áudio). Detectar duplicatas (mesmo título/duração) e vídeos já editados antes — não retrabalhar.
2. **Transcrição em paralelo:** lotes de ~10 por agente; whisper-1 API (verbose_json com words+segments; chave em `~/naia-bot/.env`; salvar resposta direto em arquivo — rtk trunca terminal). Extrair 4 frames por vídeo e LER: legenda queimada? enquadramento?
3. **Classificação (o orquestrador decide, lendo as transcrições inteiras):** aplicar os critérios abaixo, na ordem. Em dúvida entre editar e descartar, descartar — lote grande premia seletividade.
4. **Relatório final:** tabela id → classe → motivo curto; salvar `RELATORIO-TRIAGEM.md` junto da entrega. O Chefe audita pelos motivos.

## FRASE-GANCHO CANDIDATA (obrigatório desde 2026-07-19 — a triagem já entrega o gancho pronto pra edição)
Ao avaliar cada corte que vai pra EDITAR, identificar e reportar a **FRASE-GANCHO candidata**: a frase de dentro do próprio corte (autossuficiente, 3-8s) que abriria o vídeo em temperatura máxima. Escolher pela mesma hierarquia da skill `edicao-video-avalanche` (seção GANCHO VIRAL), nesta ordem: 1º número específico chocante (dinheiro, quantidade, prazo); 2º afirmação contraintuitiva ou polêmica; 3º implicação direta do espectador ("você"); 4º open loop, promessa de revelação; 5º pico emocional. Nunca uma saudação/contexto. Reportar a frase (texto + timestamp aproximado) no relatório, ao lado da classe. Assim a `edicao-video-avalanche` já recebe o gancho escolhido e só corta.

## CRITÉRIO-MESTRE: começo, meio e fim autossuficientes
O corte precisa se sustentar SOZINHO pra quem nunca viu a live: abre um assunto (mesmo que em 1 frase), desenvolve e FECHA. Teste rápido: um estranho entende do que se trata nos primeiros 10s? A última frase fecha um raciocínio (não corta no meio)?
- **Cauda com frase incompleta** ("...que se bem planejados um lançamento, uma distribuição...") = pode salvar com **TAIL-TRIM**: cortar a cauda no fim da última frase completa. Documentar o trim.
- **Abertura ruim mas recuperável** (ex. "Pode falar, Zaba" e em 3s entra no assunto) = aceitável. Abertura com voz de ALUNO/terceiro ou 15s de contexto interno = reprova.

## CLASSES
**ANÚNCIO** (criativo de tráfego — os melhores):
- Gancho forte nos primeiros segundos (número brutal, afirmação polêmica, história).
- Prova concreta (valores reais vendidos, casos com desfecho, matemática de mercado).
- Fala com PÚBLICO FRIO: entende sem conhecer comunidade/produtos internos.
- Sem palavrão pesado, sem promessa irreal explícita, sem tema sensível (hacking ofensivo, burla de plataforma) — compliance Meta.

**PERFIL** (conteúdo de Instagram):
- Ensina algo ou constrói autoridade; tolera jargão do nicho (loop, PRD, VPS) se a ideia central passa.
- História/opinião com arco fechado; palavrão leve ok.

**DESCARTE** (o joio) — qualquer um destes:
- **Fragmento de meio de conversa:** começa respondendo pergunta que não se ouve, ou termina em pergunta de aluno/nova pergunta.
- **Voz de terceiro dominando:** aluno/cliente falando mais que o Chefe, ou o Chefe só ouvindo (visual fica ele parado escutando).
- **Demo presa na tela:** "olha aqui, ó, tá vendo?" apontando pra tela que NÃO aparece no talking-head.
- **Redundância:** mesmo tema/história de outro corte mais forte do lote (ficar só com o melhor; cortes de live repetem MUITO — ex. a mesma história contada em 3 cortes). Escolher o de arco mais completo e emocional.
- **Conteúdo interno:** upsell de mentoria pra quem já é aluno, avisos de comunidade, produtos internos sem contexto.
- **Risco/compliance:** hacking ofensivo, tirar filtro de LLM, minerar cripto, violação de política de plataforma como INSTRUÇÃO (defensivo/pentest do próprio sistema = ok pra PERFIL).
- **Sem entrega:** "isso eu vou ensinar outro dia" / promete e não entrega no próprio corte.

## GOTCHAS (aprendidos no LOTE 49)
- Whisper grafa nomes foneticamente: Naya/Maia/Maya→Naia, Cloud→Claude/OpenClaw, Feibo→Fable, TOTUS→TOTVS, Antropox→Anthropic, Sask→SaaS, Reigen→HeyGen. "Cláudio" fica (apelido canônico). Isso NÃO reprova o corte — vira dicionário de correção na edição.
- Whisper alucina "Legendas pela comunidade Amara.org" em finais com silêncio — ignorar, nunca virar legenda.
- Cortes sequenciais da mesma live emendam um no outro (o fim de um é o começo do outro) — se os dois são metades de um raciocínio, nenhum se sustenta: descartar ambos ou achar o que fecha sozinho.
- Duplicata com # e sem # no nome do arquivo, e números repetidos (dois "#31") — conferir por duração/título antes de contar o lote.

## SAÍDA ESPERADA
- `RELATORIO-TRIAGEM.md` com: critérios usados, lista EDITAR (classe + slug sugerido + tail-trim se houver), lista DESCARTE (motivo curto por vídeo), duplicatas/já-editados.
- Handoff pra edição: a lista EDITAR alimenta a `edicao-video-avalanche` (1 vídeo, com Veo) ou o sanduíche econômico em lote (brief `~/Desktop/LOTE49-18-07/BRIEF-EDICAO.md`).
