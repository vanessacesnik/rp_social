# rp_social

Repositório de serviços do Realizando Potenciais.

## Serviços disponíveis

| serviço | como é entregue | onde vive |
|---|---|---|
| **Edição de vídeo** | skill do Claude Code, acionada em linguagem natural | `.claude/skills/super-edicao-video-avalanche/` |

---

## Edição de vídeo — `super-edicao-video-avalanche`

Skill única de edição de vídeo. Unifica os seis fluxos antigos (`edicao-video-avalanche`,
`edicao-video-gennaro`, `broll-fullscreen`, `broll-faixa-hyperframe`, `edicao-vsl-avalanche` e
`triagem-cortes-live`) num só acervo: o miolo que se repete existe uma vez só, em `nucleo/`, e o
conserto feito lá vale na hora para todos os modelos.

### Como acionar

Basta pedir em português dentro de uma sessão do Claude Code neste repositório: *"edita esse
vídeo"*, *"super edição"*, *"põe b-roll"*, *"faz o sanduíche"*, *"queima o hyperframe em cima do
meu vídeo"*, *"faz um vídeo pro YouTube"*, *"corta o silêncio"*, *"põe legenda"*, *"tria esses
cortes"* — ou simplesmente mandar um vídeo (ou um lote) para editar.

Ao ser acionada, a skill mostra o cardápio e resolve três perguntas antes de tocar em qualquer
arquivo: **qual modelo**, **para qual plataforma** (Reels, TikTok, Shorts ou YouTube 16:9) e
**o gancho** (mantém o do vídeo ou puxa um do miolo).

### O cardápio de modelos

Gennaro · B-roll no rodapé · B-roll tela cheia · B-roll imagem GPT · Hyperframe queimado ·
Faixa Hyperframe · Sanduíche · Sanduíche 1 econômico · Sanduíche 2 Meta · VSL longa · YouTube 1.

Cada um está em `.claude/skills/super-edicao-video-avalanche/modelos/`. O detalhe de cada modelo e
as 21 regras que não se negociam estão no `SKILL.md`.

### Estrutura

```
.claude/skills/super-edicao-video-avalanche/
├── SKILL.md              ponto de entrada: cardápio, as 3 perguntas, as regras
├── nucleo/               o que vale para todos os modelos (abertura, plataformas,
│                         corte fino, gancho viral, faixa hyperframe, QA e entrega)
├── modelos/              um arquivo por modelo treinado
├── scripts/nucleo/       corte com recuo 0,5s, legenda queimada, faixa, infográfico
├── scripts/gennaro/      planejador, pipeline, medidores e os 4 verificadores
├── scripts/broll-veo-rodape/   geração de imagem, Veo, montagem, gancho, legenda
├── scripts/youtube-1/    pipeline do formato horizontal 1920x1080
├── elements/gennaro/     design system e elementos HTML (contrato window.__seek)
├── assets/               fontes, SFX, refs de personagem, templates e workflows
├── referencia/           método completo, canon dos personagens, 110 transcrições
│                         de cortes virais, dossiês de processo
└── lote/triagem.md       modo lote: transcreve, avalia, dá nota e decide o que editar
```

### Requisitos da máquina que roda a edição

Os scripts são chamados pela skill e esperam encontrar:

- **ffmpeg** e **ffprobe** (composição, corte, encode);
- **whisper** (transcrição e timestamps por palavra, base de toda legenda e de todo corte);
- **Python 3** com **Pillow** e **numpy**;
- **Node** / **npx** com **Playwright** (render dos elementos HTML e das faixas Hyperframe);
- `naia_image` — módulo próprio de geração de imagem pela rota OAuth da assinatura,
  importado por `scripts/broll-veo-rodape/01_gen_images.py`, `scripts/youtube-1/gen_thumb.py`,
  `scripts/youtube-1/gen_encerramento.py` e `assets/broll-fullscreen/gen_imgs_personagens.py`.
  Precisa estar no `PYTHONPATH` da máquina; não vem neste repositório.
- acesso ao **Veo** para os modelos que animam b-roll (os modelos econômicos dispensam).

Alguns scripts trazem caminhos absolutos do Mac do Chefe (`/Users/...`) e comandos de macOS
(`osascript`, `say`). Em outra máquina, ajuste o caminho na hora de usar.

### Regras que a skill não negocia (resumo)

O `SKILL.md` lista 21. As que mais reprovam entrega:

1. Corte não encosta na fala: silêncio se corta com **recuo de 0,5s**, e a prova é o
   `verifica_recuo.py` terminando em `VERIFICACAO_OK`.
2. **Quebra da quarta parede antes de cortar**: rodar `detecta_instrucoes.py` em toda transcrição.
3. **Conteúdo só sai com aprovação**, item a item. Na dúvida, mantém.
4. Legenda **queimada sempre, frase por frase**, com a lista de `--destaques`.
5. Todo overlay é **organismo vivo** (infográfico), nunca texto solto.
6. **A gravação do Chefe é intocável**: quem encolhe é o overlay.
7. Nada de pronto sem as provas de `nucleo/qa-e-entrega.md`.
