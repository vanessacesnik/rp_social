#!/usr/bin/env python3
"""
arte.py · o motor de prompt das artes do youtube-1. Módulo único, usado por todos os vídeos.

REESCRITO EM 05/08/2026, depois de o Chefe ver a imagem do WhatsApp do vídeo 07: um celular
na mão, e dentro da tela BARRAS CINZAS no lugar da mensagem que ele estava lendo em voz
alta. Palavras dele: "o mockup feio do caralho com telefone com imagem com nada na tela".

A CULPA ERA DE UMA REGRA MINHA. O bloco `SEM_API` proibia "tela de produto, campo de
formulário, botão, URL, caminho, JSON", para impedir interface inventada e vazamento de
credencial. Aplicado a uma FOTO cujo assunto É uma conversa de WhatsApp, ele apagou
justamente o conteúdo. O modelo obedeceu e devolveu tarja.

A REGRA NOVA separa duas coisas que eu tinha juntado:
  · PROIBIDO continua tudo que é marca alheia, endereço, credencial e dado real de sistema.
  · OBRIGATÓRIO passa a ser o TEXTO DA FALA. Se ele lê uma mensagem em voz alta, a mensagem
    aparece escrita, legível, palavra por palavra. Se ele mostra um número, o número está lá.
    Uma tela vazia não ilustra nada e reprova a peça.

E a direção de arte subiu de patamar. O gpt-image-2 é o melhor modelo de imagem que existe
hoje e estava recebendo prompt de três linhas: câmera, lente, luz, material, profundidade e
composição agora vão especificados, porque é isso que separa foto de verdade de "imagem de
IA de 2024".
"""

# ============================================================ paleta e tipografia
PALETA = (
    "STRICT PALETTE, no other colour anywhere: background solid #0F172A (very dark navy, almost black), "
    "cards and data strips solid #1B2438, primary text #F7F5F0 (warm off-white), secondary text #94A3B8 "
    "(cool grey), cold accent #4FD8EF (light cyan) for numbers, rules and active items, hot accent "
    "#F5402E (coral red) for what hurts, positive accent #24D869 (green) for gains. "
    "ABSOLUTELY NO GRADIENT of any kind (no linear, no radial, no conic, no fade), NO glow, NO bloom, "
    "NO soft drop shadow, NO vignette, NO glassmorphism, NO neon halo, NO texture, NO emoji, NO brand logo. "
    "FLAT SOLID COLOUR ONLY, hard edges, crisp vector look. "
)

TIPO = (
    "TYPOGRAPHY: heavy geometric sans-serif, uppercase for titles and labels, tight tracking, strong "
    "hierarchy. The text must be PERFECTLY LEGIBLE ON A MOBILE PHONE SCREEN: big, thick, high contrast, "
    "no thin hairline type, no text smaller than roughly 2 percent of the image height. Text is rendered "
    "sharp and correctly spelled, never blurry, never doubled, never gibberish. "
)

CONTENCAO = (
    "TEXT CONTAINMENT RULE: every letter of every label and every supporting line lives strictly INSIDE "
    "its own card or block, with a clear inner padding of empty card colour on all four sides. No word "
    "ever touches, crosses or sticks out of the card outline, on any side. If a label is too long for the "
    "card width, break it over two or three shorter lines and set it smaller, never let it spill past the "
    "edge of the card. A label that starts before the left edge of its card or ends after the right edge "
    "of its card is a rejected image. "
)

PONTUACAO = (
    "PUNCTUATION RULE: no title, no label and no supporting line ends with a full stop, and none of them "
    "carries a colon, a semicolon, an ellipsis, a hyphen, a minus sign, a slash, a plus sign, an equals "
    "sign or an em dash. The only punctuation allowed is the comma and the MIDDLE DOT character, and the "
    "middle dot only where it is explicitly written below. The middle dot is a single small round dot at "
    "the vertical middle of the line with equal blank space on each side: NEVER a hyphen, NEVER a dash, "
    "NEVER a bullet square, NEVER a slash, NEVER a full stop on the baseline. "
)

SEM_DATA = (
    "FORBIDDEN CONTENT: never write a month name or a calendar date that was not explicitly requested "
    "below. Never draw a calendar page, never draw a calendar grid, never draw a week of marked days. "
)

# ============================================================ a regra reescrita
# Antes isto proibia QUALQUER tela, campo e botao, e foi o que esvaziou a imagem do 07.
SEGURANCA = (
    "SECURITY AND NAMING RULE, still absolute: the artwork must NEVER show a real web address, a domain "
    "name, an API endpoint, a key, a token, a password, an account identifier, an IP address, a server "
    "name, a hosting provider, a file path, a real phone number, a real e-mail address or any credential. "
    "It must NEVER carry the logo, the wordmark, the monogram, the app icon or the exact brand colour of "
    "any real company, product, social network, messaging app, bank or payment provider, and must never "
    "invent a product name. Any name that appears is PLAIN TYPED TEXT in the artwork's own typeface. "
)

CONTEUDO_OBRIGATORIO = (
    "\n\nTHE CONTENT RULE, THE ONE THAT MATTERS MOST, READ IT TWICE: this image exists to SHOW what the "
    "speaker is saying out loud at this exact second of the video. Whatever he reads aloud must be "
    "READABLE IN THE IMAGE, spelled out, word for word, at a size a person can read on a phone. "
    "An interface drawn with grey placeholder bars, redacted blocks, lorem ipsum, blurred lines, "
    "squiggles standing in for letters or an empty screen is a REJECTED IMAGE and a wasted generation. "
    "If the scene is a conversation, the messages carry the real sentences. If the scene is a screen, "
    "the screen is filled with the real content. If the scene is a number, the number is written. "
    "Nothing on the surface that the viewer looks at is left blank, generic or suggested. "
)

# ============================================================ foto
# QUEM APARECE NA FOTO É ELE (05/08/2026). A primeira leva saiu com mão genérica e, na peça do
# formulário, com um sujeito de cabelo visto por trás. O Chefe é careca, negro, barba curta
# grisalha: ver outra pessoa na tela quebra a ilusão de que aquilo é a mesa dele. As palavras
# dele foram "quero que eu olhe e fale, caralho, essa imagem realmente parece EU com o celular
# na mão". Rosto continua fora de quadro, sempre: nuca, ombro, mãos e antebraço.
ELE = (
    "\n\nWHO IS IN THE PHOTOGRAPH: the man in this frame is the speaker himself, and everything "
    "visible of him must match, because a stranger's hands break the illusion that this is his own "
    "desk. He is a Brazilian Black man in his forties, with a SHAVED BALD HEAD and a SHORT "
    "SALT-AND-PEPPER BEARD, medium-dark brown skin with real texture, pores and a natural sheen "
    "where the light grazes it. His hands are adult male hands, medium-dark brown, with visible "
    "knuckle creases, tendons under the skin, short clean nails and correct anatomy: exactly five "
    "fingers, no fusion, no extra digit, no rubbery smoothing. He wears either a plain black "
    "t-shirt or a plain coral-red hoodie, with real fabric weave and natural folds, no logo, no "
    "print, no wordmark.\n"
    "HIS FACE IS NEVER IN FRAME. Show him from behind, over the shoulder, from the side of the "
    "head, or crop to hands and forearms only. The back of a bald head, the line of an ear, the "
    "edge of a bearded jaw in profile are all fine. A full face, a recognisable portrait or eyes "
    "looking at the camera reject the image. "
)

# O AMBIENTE CONTA HISTÓRIA. O que separa foto de verdade de render limpo é a sujeira certa:
# fio que existe, poeira na luz, marca de dedo no vidro, mesa usada. Sem isso a imagem lê como
# maquete, e foi por isso que a primeira leva ainda parecia montagem.
AMBIENTE = (
    "\n\nTHE ROOM IS REAL, NOT A STUDIO SET. This is a working home office at night, lived in and "
    "used: the desk surface shows fine scuffs and a faint smudge, a cable runs off the edge of the "
    "frame and disappears, another is coiled loosely behind the machine, the monitor glass carries "
    "one soft fingerprint catching the light, a mug ring or a scrap of paper sits at the edge of "
    "the composition. The air has the faintest haze so the light source has volume. "
    "Everything present has a reason to be there: no styled props, no plant placed for balance, no "
    "empty notebook and pen, no headphones arranged at an angle, no stack of hardback books. "
    "The framing is a photographer's frame, not a product shot: slightly off axis, the subject not "
    "dead centre, something cropped by the edge, one plane sharp and the rest falling away. "
)

BASE_FOTO = (
    "PHOTOREALISTIC EDITORIAL PHOTOGRAPH, horizontal 3:2, indistinguishable from a real photograph taken "
    "by a professional. Shot on a full-frame camera with a fast prime lens, natural optical depth of "
    "field with a believable focal plane, true-to-life micro-contrast, visible fine surface detail, "
    "authentic material response: skin has pores and fine texture, glass has real reflections and "
    "fingerprints, brushed metal has anisotropic highlights, matte plastic scatters light softly, fabric "
    "has weave. Colour is graded like a magazine feature, not saturated, not plastic, not airbrushed. "
    "\n\nLIGHT: a dim room at night lit by ONE dominant practical source plus a weak fill, so the frame "
    "reads dark overall and sits on a dark presentation panel without looking like a bright rectangle. "
    "Deep near-black navy shadows that still hold detail, gentle falloff, a single crisp specular "
    "highlight where the material deserves it. NO bright white walls, NO daylight, NO blown-out window, "
    "NO ceiling fluorescent, NO ring light, NO coloured gel wash, NO lens flare, NO bokeh balls, NO "
    "artificial glow around anything. "
    "\n\nCOMPOSITION: one clear subject that fills the frame with intent, shot from a considered angle "
    "(over the shoulder, low three-quarter, or straight-on macro), with foreground and background layers "
    "that give real depth. The frame is quiet: no clutter, no random props, no stock-photo staging, no "
    "person smiling at the camera. "
    "\n\nFORBIDDEN, because it is what makes an image look machine-made: waxy plastic skin, symmetrical "
    "doll faces, extra or fused fingers, floating objects, impossible reflections, warped straight lines, "
    "duplicated hardware, melted typography, glowing edges, rainbow chromatic fringing, HDR halo, "
    "over-sharpened micro-contrast, cartoon proportions and any watermark. "
    "NO recognisable face of a real person and no public figure: if a person appears, only hands, "
    "forearms or a shoulder, never a full face. "
    + SEGURANCA + CONTEUDO_OBRIGATORIO
)

# Tela dentro de foto (celular, monitor, tablet). Foi aqui que a peça do 07 morreu.
TELA_NA_FOTO = (
    "\n\nTHE SCREEN IS THE SUBJECT OF THIS PHOTOGRAPH, so it is rendered with the same care as the "
    "hardware around it. The display is sharp, correctly exposed against the dark room, slightly brighter "
    "than the surroundings but never blown out, with a believable anti-reflective sheen and a faint hint "
    "of the room reflected in the glass at a grazing angle. The interface inside it is CLEAN, MODERN and "
    "GENERIC, dark mode, with real rounded message bubbles, real spacing, a real top bar and a real "
    "bottom input area, and it is COMPLETELY FILLED with the exact Brazilian Portuguese text written at "
    "the end of this prompt, set in a normal readable interface typeface, correct accents, correct line "
    "breaks, left aligned inside each bubble. The text is large enough to read comfortably. "
    "Do NOT draw grey bars, do NOT draw redacted blocks, do NOT draw placeholder lines, do NOT blur the "
    "text, do NOT crop the message out of frame, do NOT tilt the screen so far that the text becomes "
    "unreadable. The screen must never carry a company logo, a real phone number, a profile photograph "
    "of a real person or a verified badge. "
)

# ============================================================ pixel art 3D voxel
# ORDEM DO CHEFE, 05/08/2026: as artes do vídeo saem com o QUINTETO em pixel art 3D, e não
# como fotografia. O bloco de estilo abaixo é copiado VERBATIM da skill
# `quinteto-pixel-art-3d-voxel`, e a própria skill manda colar verbatim: prompt improvisado
# com as palavras "voxel render", "Minecraft" ou "cubos" puxa direto para o LEGO de plástico
# frio que ele reprovou em 17/07/2026.
ESTILO_PIXEL = (
    "ART STYLE: a CUTE RETRO VIDEO-GAME CHARACTER, looks like an adorable mascot that just STEPPED "
    "OUT OF A CLASSIC 16-bit / 32-bit VIDEO GAME and gained gentle 3D depth. HAND-CRAFTED COZY "
    "SPRITE with SOFT ROUNDED PIXELS, NOT hard cubes. Charming, warm, expressive, lovable, full of "
    "personality. VISIBLE CHUNKY PIXELS on the surface (clear pixel-art texture / dithering, like a "
    "hi-res game sprite) BUT with ROUNDED, FRIENDLY, SOFT forms and soft 3D volume — pixel shading "
    "is WARM and SOFT, cozy game-art lighting, gentle highlights and soft shadows, slightly glowing. "
    "Think Crossy Road / Octopath-style HD-2D sprite charm and Funko cuteness, hand-crafted and "
    "inviting. STRICTLY AVOID: MagicaVoxel render, LEGO bricks, hard plastic toy, cold sharp "
    "identical cubes, stiff blocky robot, glossy product photo, sterile CGI, Minecraft-style voxel "
    "blocks. It must look CUTE and HUGGABLE and WARM, not like a cold plastic toy on a shelf. "
)

# O canon de cada um, resumido da skill. As três armadilhas que já reprovaram peça vão em CAPS.
QUINTETO_CANON = (
    "\n\nTHE FIVE AVALANCHE CHARACTERS, exact canon, never improvise them:\n"
    "  DENDERSON, the CEO: a Black Brazilian man, completely BALD shaved head, short dark beard, "
    "broad friendly shoulders, all-BLACK tech outfit with a small GOLDEN chevron letter A on the "
    "chest, warm confident leader smile. Clearly a friendly human guy.\n"
    "  NAIA, the AI executive: a woman with long voluminous COPPER-RED ginger hair, fair skin "
    "showing SUBTLE thin glowing CYAN circuit lines on her neck and forearms, fitted BLACK "
    "executive blazer, small orange-red letter N pin, warm elegant smile. She wears the EXECUTIVE "
    "look, never the mascots' tracksuit, and she is PIXELATED like the others, never anime.\n"
    "  OPENCLAW: a CHIBI HUMANOID kid with a big cherry-RED LOBSTER HEAD (round friendly lobster "
    "face, two huge round black eyes, small happy mouth, two long red antennae), hands are red "
    "lobster CLAWS shaped like soft boxing-glove pincers. He wears a COMPLETE MATCHING BLACK "
    "TRACKSUIT: black hoodie with GOLDEN chevron A and a gold chain, AND BLACK JOGGER SWEATPANTS "
    "with a RED side stripe FULLY COVERING BOTH LEGS, and chunky WHITE sneakers. "
    "ABSOLUTELY NO LOBSTER TAIL AND NEVER BARE LEGS. Never an ant, never an insect.\n"
    "  CLAUDINHO: a CHIBI kid with a BIG rounded CUBE head in matte ORANGE, a minimalist face of "
    "two thick black BRACKET eyes, a '>' on the left and a '<' on the right, two small orange side "
    "blocks, NO nose and NO mouth. Complete black Avalanche tracksuit, golden A, gold chain, black "
    "jogger with red stripe, white chunky sneakers. Never a lobster, never a speaker.\n"
    "  CODEXZINHO: a CHIBI kid whose head is a soft CLOUD shaped like a FLOWER with rounded puffy "
    "lobes, going from LAVENDER-PURPLE at the top to BLUE at the bottom, and whose only facial "
    "feature is a clean WHITE terminal prompt, a white '>' plus a clearly marked bold white "
    "underscore. HIS HEAD IS SMALL AND PROPORTIONAL TO HIS BODY, never oversized. Complete black "
    "Avalanche tracksuit, golden A, chain, black jogger with red stripe, white sneakers.\n"
    # As três armadilhas que a própria skill avisa e que já apareceram nas peças do 07.
    "THE THREE MISTAKES THAT KEEP HAPPENING, check each one before finishing:\n"
    "  1. OPENCLAW COMES OUT LOOKING LIKE AN ANT, and it has now happened four times. Build his head SHAPE FIRST, before any colour: it is a TALL ROUNDED OVAL, wider than it is deep, like a big friendly egg standing upright, with a SMOOTH continuous outline and NO segmentation, NO waist, NO pinch between head and body, NO mandibles and NO jaw plates. On that oval sit TWO ENORMOUS ROUND BLACK EYES placed FAR APART and LOW, taking up a third of the face, plus one small curved happy mouth. Two thin antennae rise from the TOP of the oval and curl at the tip. If the head reads as a small pointed insect skull with eyes close together, IT IS WRONG and must be redrawn as the big round oval. He is a LOBSTER: a big round cherry-red lobster "
    "head, wide and rounded, with two huge round black eyes set far apart, a small happy mouth and "
    "TWO THICK RED ANTENNAE. He is NEVER an ant, never a beetle, never a bug, has NO segmented "
    "thorax, NO narrow waist, NO six legs and NO feelers on the face. His hands are big soft "
    "boxing-glove pincers, and his legs are FULLY COVERED by black jogger sweatpants with a red "
    "side stripe. NO TAIL, ever.\n"
    "  2. CODEXZINHO comes out with an oversized head. His flower-cloud head is SMALL and "
    "proportional to his little body.\n"
    "  3. NAIA comes out ANIME instead of pixelated. She is a SPRITE like the others: her copper "
    "hair is built of visible chunky pixels with hard stepped edges, not smooth painted anime hair, "
    "and her face is a simple sprite face, not a rendered illustration.\n"
    "COUNT THEM BEFORE FINISHING: every character that appears must be one of these five, correct "
    "in every detail, and never duplicated in the same frame."
)

# A skill manda fundo claro off-white, que serve para o card solto. AQUI a arte é colada num
# painel #0F172A, e retângulo claro no meio do painel escuro é justamente o que as regras de
# design do Chefe proíbem. Então o fundo vira o próprio painel e a luz do sprite compensa.
CENA_PIXEL = (
    "\n\nTHE SCENE IS A WIDE PIXEL-ART DIORAMA, horizontal 3:2, in the same cozy 16/32-bit HD-2D "
    "style as the characters, so the props, the furniture, the screens and the room are ALSO made "
    "of soft rounded visible pixels with warm soft shading.\n"
    "THE BACKGROUND IS SOLID DARK #0F172A edge to edge, a very dark navy, because this art is "
    "pasted onto a dark presentation panel and a light background would read as a white box in the "
    "middle of the screen. Against that dark, the sprites carry a warm rim light and a soft cast "
    "shadow so they pop without any glow, bloom or halo. There is no light off-white background "
    "anywhere in this piece.\n"
    "DEPTH: build the diorama in three planes, a foreground element cropped by the frame edge, the "
    "characters and the data in the middle, and a suggestion of the room falling away behind, so "
    "the scene has real space instead of a flat sticker row.\n"
    "SCALE: the characters are ACTORS IN THE SCENE, not margin decoration. They are big enough to "
    "read their expression, they interact with the data (pointing at it, holding it, standing on "
    "it, carrying it), and they never cover, overlap or block a single letter or figure."
)

# O TEXTO NÃO É PIXELADO. Texto em pixel art fica ilegível no celular, e a peça existe para o
# espectador LER o que ele está dizendo. HD-2D de verdade faz exatamente esta mistura.
TEXTO_LIMPO = (
    "\n\nTHE TYPOGRAPHY IS NOT PIXELATED, and this is deliberate. Every word, label and figure is "
    "set in a CLEAN, HEAVY, GEOMETRIC SANS-SERIF, sharp and perfectly legible on a phone, exactly "
    "as a modern HD-2D game renders its interface over a pixel-art world. Pixelated or dotted or "
    "8-bit lettering is a rejected image, because the viewer has to READ this. The data panels, "
    "cards, bars and rules that carry the text are also clean flat solid shapes with hard edges, "
    "sitting over the pixel-art scene like a modern overlay. "
)


def base_pixel(extra=''):
    """Prompt base de uma cena de vídeo em pixel art 3D com o quinteto."""
    return (ESTILO_PIXEL + PALETA + TIPO + CONTENCAO + SEM_DATA + PONTUACAO + SEGURANCA
            + CONTEUDO_OBRIGATORIO + CENA_PIXEL + TEXTO_LIMPO + QUINTETO_CANON + extra + SAFE)


# ============================================================ o padrão da skill `infograficos`
# 05/08/2026. Ordem do Chefe: "quero eles usando a skill de infográficos e mantendo os
# personagens em pixel art". A skill `infograficos` custou QUATRO tentativas até ele aprovar e
# tem o Estilo 2 (pixel art 3D voxel) já previsto, com o precedente dark do LS Club. O que
# vem de lá é a ESTRUTURA: header em pill, cards modulares com faixa de cor, elemento-herói,
# densidade alta e organizada, e o quinteto EM AÇÃO sem plaquinha de nome.
#
# Uma coisa da skill NÃO entra: ela pede borda de gradiente no header, e a regra global do
# Chefe é zero gradiente em qualquer peça. Vai borda sólida na cor de acento.
ESTRUTURA_INFO = (
    "\n\nTHE PAGE STRUCTURE, taken from the approved Avalanche infographic standard. This is a "
    "PAGE OF A TECHNICAL DECK, not a poster, and it has four fixed parts:\n"
    "  1. THE FRAME. A rounded outer frame in #1B2438, one pixel wide, with BRACKET CORNERS: four "
    "short right-angle marks in #2E3A4E at the four corners, like registration marks. In the top "
    "right corner, a small monospaced tag in #94A3B8.\n"
    "  2. THE HEADER. The title sits in a PILL, a rounded solid #1B2438 banner centred at the top "
    "with a 3px SOLID accent border (never a gradient border), and the title inside it is set in a "
    "HEAVY CONDENSED DISPLAY face, uppercase, tight tracking, in #F7F5F0.\n"
    "  3. THE BODY. Modular rounded cards, each with a SOLID COLOURED HEADER STRIP across its top "
    "carrying the card name in uppercase, and under it the card content. Each card gets its own "
    "accent from the palette, so the page is MULTI-ACCENT and the eye can tell the blocks apart at "
    "a glance. Cards are separated by clean gutters of empty dark background.\n"
    "  4. THE HERO ELEMENT. One block is the hero and is visibly bigger and louder than the rest, "
    "chosen to fit the content: a giant figure, a circular gauge, an isometric 3D stack, a 3D "
    "funnel, a numbered horizontal flow, or a grid of portraits.\n"
    "DENSITY IS HIGH BUT ORGANISED: a lot of information, never a mess, held together by a strong "
    "typographic hierarchy and generous gutters. An empty-looking page fails this standard just as "
    "much as a cluttered one.\n"
    "THE CHARACTERS ARE ALWAYS WORKING INSIDE THE SCENE, operating a dashboard, pointing at a card, "
    "carrying a block, climbing the hero element. NEVER standing in a row, NEVER posing, and NEVER "
    "with a name plate under them."
)


def base_info_pixel(extra=''):
    """Infográfico no padrão da skill `infograficos`, acabamento pixel art 3D, fundo escuro."""
    return (ESTILO_PIXEL + PALETA + TIPO + CONTENCAO + SEM_DATA + PONTUACAO + SEGURANCA
            + CONTEUDO_OBRIGATORIO + CENA_PIXEL + TEXTO_LIMPO + ESTRUTURA_INFO + PROFUNDIDADE
            + SEM_CLICHE + ICONE + QUINTETO_CANON + extra + SAFE)


# ============================================================ infográfico
def _colunas():
    return (
        "\n\nLAYOUT GRID, THE SINGLE MOST IMPORTANT INSTRUCTION, OBEY IT BEFORE ANYTHING ELSE: the frame "
        "is split into THREE VERTICAL COLUMNS. The LEFT column is a NARROW empty dark strip, about one "
        "tenth of the image width. The RIGHT column is a NARROW empty dark strip, about one tenth of the "
        "image width. The CENTRE column is everything in between, about eight tenths of the width, and it "
        "belongs ENTIRELY TO THE CONTENT. "
    )


_HERO = (
    "THE CONTENT IS THE HERO. Do NOT squeeze the content into the upper third. Do NOT leave the lower "
    "half to the characters. There is NO leftover empty dark band below the content. "
)

# Camadas de leitura: o que sobe a qualidade de um infografico nao e mais enfeite, e mais
# NIVEL DE INFORMACAO. O Chefe pediu profundidade e didatica, e didatica e hierarquia.
PROFUNDIDADE = (
    "\n\nDEPTH OF INFORMATION, this is what separates a real teaching diagram from a poster with words "
    "on it. The artwork carries THREE LEVELS OF READING and all three must be present:\n"
    "  1. the five-second read: one dominant element the eye lands on first, biggest and loudest;\n"
    "  2. the thirty-second read: the supporting blocks, each with a short heading AND a line of "
    "     explanation under it, so the viewer learns something by looking;\n"
    "  3. the detail read: a small precise element inside each block that proves the point, such as a "
    "     figure, a tiny labelled bar, a step number or a short comparison, drawn flat and solid.\n"
    "Relationships between blocks are DRAWN, not implied: when one thing leads to another, a flat solid "
    "connector or a numbered step order says so. Nothing is decoration: every icon, rule, number and "
    "connector carries meaning, and an element that carries no meaning is removed. "
)

# Vindo das proibicoes absolutas da skill `impeccable`, que reprovou a forma que eu vinha
# usando: seis cards do mesmo tamanho com icone, titulo e texto, repetidos sem fim.
SEM_CLICHE = (
    "\n\nCOMPOSITION BANS, absolute, rewrite the layout if you are about to draw one of these:\n"
    "  · A GRID OF IDENTICAL CARDS. Blocks of the same size carrying icon plus heading plus text, "
    "repeated four, six or eight times, is the most tired shape in this medium. The blocks in this "
    "artwork have DIFFERENT WEIGHTS: one is clearly dominant, the others support it, and their sizes "
    "say which is which before a single word is read.\n"
    "  · THE HERO METRIC TEMPLATE. One giant number with a small label under it and a row of "
    "supporting statistics is a cliché. A figure only earns that size when the artwork also shows "
    "WHAT IT IS COMPARED TO.\n"
    "  · A COLOURED STRIPE down the left edge of a block as an accent. Use a full outline, a solid "
    "background tint, a leading figure or nothing.\n"
    "  · TEXT FILLED WITH A GRADIENT, and any glass or blur panel used as decoration.\n"
    "  · SYMMETRY FOR ITS OWN SAKE. If two things are not equally important, they are not the same "
    "size and they do not sit on the same axis. "
)

ICONE = (
    "\n\nICONS: flat line icons only, uniform 3px stroke, no fill, no rounded tile behind them, drawn "
    "from the FUNCTION being described and never generic. They sit alone in a defined corner of their "
    "block and never overlap a letter. No emoji, no 3D icon, no gradient icon, no shadow. "
)


def base_info(grade, pontuacao=PONTUACAO, extra=''):
    """Prompt base de um infográfico de painel escuro."""
    return (
        "PREMIUM EDUCATIONAL INFOGRAPHIC, horizontal 3:2, flat vector design, razor sharp, highest "
        "quality, corporate tech aesthetic, generous dark negative space. "
        "THE BACKGROUND IS A SOLID DARK #0F172A FILL EDGE TO EDGE, a very dark navy, almost black. "
        "The whole artwork is BORN DARK: there is NO white background, NO light panel, NO bright "
        "rectangle anywhere, because this art is pasted onto a dark presentation panel. "
        + PALETA + TIPO + CONTENCAO + SEM_DATA + pontuacao + SEGURANCA
        + CONTEUDO_OBRIGATORIO + PROFUNDIDADE + SEM_CLICHE + ICONE + grade + extra + SAFE
    )


SAFE = (
    "\n\nSAFE AREA: the artwork is a WIDE HORIZONTAL BANNER. Every piece of text, every icon and every "
    "card must live inside the CENTRAL horizontal band of the frame. Leave the TOP 12 percent and the "
    "BOTTOM 12 percent as EMPTY solid #0F172A background with nothing in it, because the image will be "
    "cropped there. Do NOT put a title, a footer, a caption or a character in those strips. "
)

GRADE = _colunas() + (
    "The content FILLS THE WHOLE CENTRAL BAND FROM TOP TO BOTTOM: the title sits at the top of it and the "
    "cards start right under the title and reach down to the bottom of the band, so the cards are TALL "
    "and are BY FAR the biggest, loudest, most dominant object in the picture. "
    "Nothing is stacked under the cards. " + _HERO
)

GRADE_ZONAS = _colunas() + (
    "The content FILLS THE WHOLE CENTRAL BAND FROM TOP TO BOTTOM: a short title line at the very top of "
    "the central column and everything described below occupying ALL the remaining height, down to the "
    "bottom edge of the band, with no leftover empty dark band under it. " + _HERO
)

GRADE_ZONAS_FAIXA = _colunas() + (
    "The content FILLS THE WHOLE CENTRAL BAND FROM TOP TO BOTTOM in THREE stacked zones only: a short "
    "title line at the very top, then the MAIN AREA described below taking about three quarters of the "
    "remaining height, then ONE wide READING STRIP, a flat solid #1B2438 rectangle spanning the full "
    "width of the central column, at the very bottom of the band. " + _HERO
)

GRADE_DUAS_FAIXA = _colunas() + (
    "The content FILLS THE WHOLE CENTRAL BAND FROM TOP TO BOTTOM in THREE stacked zones only: a short "
    "title line at the very top, then TWO BIG COLUMNS side by side taking about three quarters of the "
    "remaining height, then ONE wide READING STRIP, a flat solid #1B2438 rectangle spanning the full "
    "width of the central column, at the very bottom of the band. " + _HERO
)

GRADE_FLUXO = _colunas() + (
    "The content FILLS THE WHOLE CENTRAL BAND as a LEFT TO RIGHT FLOW: a short title line at the top, "
    "then a horizontal sequence of steps across the full width of the central column, each step a flat "
    "solid #1B2438 block with a number, a heading and one explaining line, joined by flat solid #4FD8EF "
    "connectors that show the direction of the flow. The chain of steps is BY FAR the biggest, loudest, "
    "most dominant object in the picture. " + _HERO
)

QUINTETO_MARGEM = (
    "\n\nTHE AVALANCHE TEAM, DRAWN AS TINY MARGIN DECORATION: exactly FIVE characters TOTAL, one of each, "
    "no duplicates, no sixth character. They are DECORATION, not content. "
    "SIZE RULE: each character is TINY, roughly one fifth of the image height, and a whole character must "
    "be SHORTER THAN HALF OF ONE CARD. If a character looks as tall as a card, it is WRONG. "
    "PLACEMENT RULE: they stand ONLY inside the two NARROW dark margin strips at the extreme left and "
    "extreme right edges, TWO of them stacked in the LEFT strip and THREE stacked in the RIGHT strip, "
    "like small stickers glued in the margin. In the LEFT strip stand DENDERSON and NAIA. In the RIGHT "
    "strip stand the three mascots. "
    "They NEVER enter the central content column, NEVER stand in a horizontal row, NEVER line up along "
    "the bottom, NEVER sit under the cards, NEVER cover, overlap, touch or pass in front of any card, "
    "title, icon, number, label or letter. Every single word stays completely unobstructed. "
    "VERTICAL INSET RULE: in EACH margin strip the little stack is VERTICALLY INSET relative to the "
    "cards. The head of the TOPMOST character sits clearly BELOW the top edge of the cards, never level "
    "with the title. The shoes of the LOWEST character sit clearly ABOVE the bottom edge of the cards, "
    "leaving a gap at least one eighth of the image height. The whole stack is SHORTER than the row of "
    "cards and floats inside it, with visible empty dark background above the first head and below the "
    "last pair of shoes. NO shoe, NO leg and NO part of any character crosses that line downwards. "
    "BOTTOM EDGE RULE: no character touches, overlaps or is cut by the bottom or top edge of the frame. "
    "Every character is whole, head to shoes. "
    "They are anime ultra-realistic 3D characters, lit so they read clearly against the dark navy, and "
    "they carry NO name plate. DENDERSON is a bald Black Brazilian man with a short salt-and-pepper beard "
    "in a coral-red hoodie with a small upright gold letter A on the chest; NAIA is a red-haired woman "
    "with long wavy copper hair in a matching coral-red hoodie, elegant and confident; the three mascots "
    "wear full black Avalanche tracksuits with the upright gold letter A: CLAUDINHO has a matte ORANGE "
    "CUBE head with two thick black bracket eyes and no mouth, OPENCLAW has a tall oval CHERRY-RED "
    "LOBSTER head with huge round black eyes with amber irises, an open happy smile with a small pink "
    "tongue, four red antennae and big red claws for hands (NOT an ant), and CODEXZINHO has a soft purple "
    "flower-shaped CLOUD head whose only face is one white '>' plus one white '_'. "
    "FINAL CHECK, MEASURE IT BEFORE YOU FINISH: exactly five characters, each at most one third of the "
    "image height, all five inside the two narrow side strips, the lowest shoe well above the bottom of "
    "the content, and the whole central column unobstructed. They are small stickers in the margin, not "
    "people posing next to a poster."
)


def soletra(linhas):
    """Bloco final de ortografia. É o que garante acento certo e zero palavra inventada."""
    corpo = '\n'.join('  ' + l for l in linhas)
    return ("\n\nSPELLING IS CRITICAL. Render these Brazilian Portuguese strings letter by letter, with "
            "these exact accents, and write NOTHING ELSE anywhere in the image:\n" + corpo +
            "\nEvery one of these must be spelled exactly as written and be readable on a phone.")
