#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INFOGRAFICO EM CARD (vertical 1080x1920) para o modelo Gennaro e qualquer overlay de tela cheia.

Ordem do Chefe em 25/07/2026, depois de eu repetir o erro em dois modelos seguidos:
"a gente esta usando o hyperframe so pra colocar texto na tela, sendo que ja tem a legenda. Pega o
texto do trecho, transforma em um prompt que gere uma animacao, um infografico, que DESENHE
literalmente o que eu estou falando naquele trecho. Pode ter texto? Pode, quando for relevante,
mas nao e pra fazer um video inteiro so com texto."

Este modulo e a versao em CARD da biblioteca de `faixa_hyperframe.py` (que e a versao em faixa
1080x232). Mesmo principio, geometria diferente: aqui o card vive na metade de baixo do quadro,
com 760x720 de area util, abaixo da legenda queimada.

GEOMETRIA
  card     x 160..920 (760), y 1040..1760 (720)   dentro da regua de texto largo
  titulo   linha curta de contexto no topo do card, opcional
  desenho  o resto do card, que e onde mora o mecanismo
Tudo animado por window.__seek(t), sem @keyframes CSS (o render usa animations:'disabled').
"""
import os

# Area DOBRADA por ordem do Chefe (25/07/2026): "quero a area feita com hyperframe + imagem maior
# do que o tamanho atual, o dobro do tamanho". 760x360 = 273.600px -> 760x720 = 547.200px.
# A largura fica em 760 porque e o teto da regua de texto largo [160,920]; o dobro vem da altura.
# A legenda queimada sobe junto (o caption_track do Gennaro passa a ancorar acima de y=1040).
CX, CW = 160, 760
CY, CH = 1040, 720

COR = {"cyan": ("#3EC8FF", "rgba(62,200,255,.45)"), "coral": ("#F5402E", "rgba(245,64,46,.45)"),
       "green": ("#24D869", "rgba(36,216,105,.45)"), "gold": ("#FFC53D", "rgba(255,197,61,.45)"),
       "violet": ("#9B6BFF", "rgba(155,107,255,.45)")}

BASE = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="_base.css">
<style>
#card{{position:absolute;left:{cx}px;top:{cy}px;width:{cw}px;height:{ch}px;border-radius:30px;
  background:linear-gradient(180deg,rgba(20,24,32,.95),rgba(9,11,16,.97));
  border:3px solid {glow};box-shadow:0 40px 90px rgba(0,0,0,.6);padding:22px 26px;overflow:hidden;}}
#card::before{{content:'';position:absolute;inset:0;opacity:.5;
  background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);
  background-size:52px 46px;}}
#tit{{position:relative;font-family:'MontX';font-size:30px;letter-spacing:3px;color:{ac};
  text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
#des{{position:absolute;left:26px;top:{dy}px;width:{dw}px;height:{dh}px;}}
{css}
</style></head><body><div id="stage">
  <div id="card"><div id="tit">{titulo}</div><div id="des">{body}</div></div>
</div>
<script src="_lib.js"></script>
<script>
const {{seg,E,clamp,count,lerp}}=window.__lib;
const DUR=parseFloat(new URLSearchParams(location.search).get('dur')||'{dur}');
const cl=clamp, oc=E.outCubic, oq=E.outQuint, ob=E.outBack;
const $=i=>document.getElementById(i);
{js}
window.__seek=function(t){{
  const card=$('card');
  const inS=ob(seg(t,0.05,0.5),1.4), rise=(1-oc(seg(t,0.05,0.5)))*46;
  card.style.opacity=cl(seg(t,0.05,0.32)*1.6)*cl(1-E.inOutCubic(seg(t,DUR-0.5,0.5)));
  card.style.transform=`translateY(${{rise}}px) scale(${{lerp(0.93,1,cl(inS))}})`;
  $('tit').style.opacity=oc(seg(t,0.18,0.4));
  desenho(t);
}};
window.__seek(0);
</script></body></html>
"""

DW, DH = CW - 52, CH - 52 - 40   # descontando padding e o titulo

# --------------------------------------------------------------------- auto-fit de texto
_FONTE = os.path.expanduser("~/.claude/skills/super-edicao-video-avalanche/"
                            "assets/gennaro/fonts/Montserrat-Black.ttf")
_DR = None


def fit(texto, larg, teto=64, piso=20, tracking=0.0):
    """Maior tamanho em que `texto` cabe em `larg` px, medido na fonte REAL.
    Estimar por caractere foi o que fez 'RESOLVIDO' virar 'RESOLVID' cortado na borda."""
    global _DR
    if _DR is None:
        from PIL import Image, ImageDraw
        _DR = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    from PIL import ImageFont
    limpo = texto.replace("<b>", "").replace("</b>", "").replace("<br>", " ")
    px = teto
    while px > piso:
        try:
            f = ImageFont.truetype(_FONTE, px)
        except Exception:
            return int(teto * 0.7)
        if _DR.textlength(limpo, font=f) + tracking * len(limpo) <= larg:
            return px
        px -= 2
    return piso



def escreve(work, nome, titulo, cor, css, body, js, dur):
    ac, glow = COR[cor]
    html = BASE.format(cx=CX, cy=CY, cw=CW, ch=CH, dy=52 + 18, dw=DW, dh=DH,
                       ac=ac, glow=glow, titulo=titulo, css=css, body=body, js=js, dur=dur)
    open(os.path.join(work, "elements", nome + ".html"), "w", encoding="utf-8").write(html)


def barras(work, nome, titulo, cor, dados, dur):
    """Colunas altas com valor em cima e rotulo embaixo. dados=[(label, frac, valor, destaque)]"""
    ac, glow = COR[cor]
    n = len(dados)
    lg = int((DW - (n - 1) * 26) / n)
    fvl = min(fit(str(d[2]), lg - 8, 56, 22) for d in dados)
    flb = min(fit(d[0], lg - 6, 32, 15) for d in dados)
    cols = "".join(
        f'<div class="col" style="left:{i*(lg+26)}px;width:{lg}px;">'
        f'<div class="vl" id="v{i}">{d[2]}</div>'
        f'<div class="bw"><div class="bb" id="b{i}" style="height:{int(d[1]*100)}%;'
        f'background:{ac if d[3] else "rgba(255,255,255,.20)"};'
        f'box-shadow:{"0 0 30px "+glow if d[3] else "none"};"></div></div>'
        f'<div class="lb" style="color:{"#fff" if d[3] else "rgba(255,255,255,.45)"};">{d[0]}</div>'
        f'</div>' for i, d in enumerate(dados))
    css = """
.col{position:absolute;top:8px;height:calc(100% - 16px);}
.vl{position:absolute;top:0;left:0;right:0;text-align:center;font-family:'Mont';font-size:FVLpx;
  color:#fff;opacity:0;white-space:nowrap;}
.bw{position:absolute;left:0;right:0;top:74px;bottom:64px;display:flex;align-items:flex-end;}
.bb{width:100%;border-radius:12px 12px 5px 5px;transform-origin:bottom center;transform:scaleY(0);}
.lb{position:absolute;bottom:0;left:0;right:0;text-align:center;font-family:'MontB';font-size:FLBpx;
  letter-spacing:1px;text-transform:uppercase;white-space:nowrap;}
#eixo{position:absolute;left:0;right:0;bottom:58px;height:3px;background:rgba(255,255,255,.14);}
"""
    js = ("const N=" + str(n) + ";\nfunction desenho(t){for(let i=0;i<N;i++){"
          "const p=oq(seg(t,0.30+i*0.18,0.6));$('b'+i).style.transform='scaleY('+p+')';"
          "$('v'+i).style.opacity=cl(seg(t,0.5+i*0.18,0.3));}}")
    css = css.replace("FVL", str(fvl)).replace("FLB", str(flb))
    escreve(work, nome, titulo, cor, css, '<div id="eixo"></div>' + cols, js, dur)


def fluxo(work, nome, titulo, cor, etapas, dur):
    """Etapas em cards com icone, ligadas por conexao que pulsa."""
    ac, glow = COR[cor]
    n = len(etapas)
    bw = int((DW - (n - 1) * 22) / n)
    flb = min(fit(e[0], bw - 28, 48, 20) for e in etapas)
    fsb = min(fit(e[2], bw - 30, 30, 15) for e in etapas)
    nos = "".join(
        f'<div class="no" id="n{i}" style="left:{i*(bw+22)}px;width:{bw}px;">'
        f'<div class="ic">{e[1]}</div><div class="lb">{e[0]}</div>'
        f'<div class="sb">{e[2]}</div></div>' for i, e in enumerate(etapas))
    lns = "".join(f'<div class="ln" style="left:{i*(bw+22)+bw}px;width:22px;"><i id="li{i}"></i></div>'
                  for i in range(n - 1))
    css = f"""
.no{{position:absolute;top:8px;height:calc(100% - 16px);border-radius:18px;background:rgba(255,255,255,.04);
  border:2px solid rgba(255,255,255,.10);display:flex;flex-direction:column;align-items:center;
  justify-content:space-evenly;padding:26px 10px;opacity:0;}}
.no .ic svg{{width:118px;height:118px;}}
.no .lb{{font-family:'Mont';font-size:{flb}px;color:#fff;text-transform:uppercase;text-align:center;
  line-height:1.05;padding:0 8px;}}
.no .sb{{font-family:'MontB';font-size:{fsb}px;max-width:92%;letter-spacing:1px;color:rgba(255,255,255,.5);
  text-transform:uppercase;text-align:center;padding:0 6px;line-height:1.1;}}
.ln{{position:absolute;top:50%;height:4px;margin-top:-2px;background:rgba(255,255,255,.12);overflow:hidden;}}
.ln i{{display:block;height:100%;width:100%;background:{ac};transform-origin:left;transform:scaleX(0);
  box-shadow:0 0 14px {glow};}}
"""
    js = f"""const N={n};
function desenho(t){{
  for(let i=0;i<N;i++){{
    const p=ob(seg(t,0.22+i*0.32,0.5),1.5), el=$('n'+i);
    el.style.opacity=cl(seg(t,0.22+i*0.32,0.3)*1.6);
    el.style.transform=`scale(${{lerp(0.88,1,cl(p))}})`;
    el.style.borderColor = t>0.22+i*0.32+0.3 ? '{ac}66' : 'rgba(255,255,255,.10)';
  }}
  for(let i=0;i<N-1;i++){{const li=$('li'+i);
    if(li) li.style.transform=`scaleX(${{oq(seg(t,0.45+i*0.32,0.4))}})`;}}
}}"""
    escreve(work, nome, titulo, cor, css, lns + nos, js, dur)


def confronto(work, nome, titulo, cor, esq, dir_, dur):
    """Dois paineis lado a lado com barra propria e seta no meio."""
    ac, glow = COR[cor]
    pw = int((DW - 76) / 2)
    fe = fit(esq[1], pw - 48, 92, 30)
    fd = fit(dir_[1], pw - 48, 92, 30)
    fv = min(fe, fd)                      # mesmo corpo nos dois lados, e nenhum estoura
    css = f"""
.pn{{position:absolute;top:8px;width:{pw}px;height:calc(100% - 16px);border-radius:18px;padding:22px;
  display:flex;flex-direction:column;
  border:2px solid rgba(255,255,255,.12);background:rgba(255,255,255,.035);opacity:0;}}
.pn .t{{font-family:'MontB';font-size:24px;letter-spacing:2px;color:rgba(255,255,255,.45);
  text-transform:uppercase;flex:0 0 auto;}}
.pn .ico{{flex:0 0 auto;margin-top:14px;}}
.pn .ico svg{{width:74px;height:74px;}}
.pn .v{{font-family:'Mont';font-size:{fv}px;line-height:1.06;text-transform:uppercase;flex:1 1 auto;
  display:flex;align-items:center;justify-content:flex-start;}}
.pn .tr{{flex:0 0 auto;height:34px;border-radius:17px;
  background:rgba(255,255,255,.08);overflow:hidden;}}
.pn .tr i{{display:block;height:100%;transform-origin:left;transform:scaleX(0);border-radius:11px;}}
#p1{{left:0;}} #p2{{right:0;border-color:{ac}77;}}
#sx{{position:absolute;left:{pw+8}px;top:50%;margin-top:-26px;width:60px;height:52px;}}
"""
    ICO_ESQ = ('<svg viewBox="0 0 48 48" fill="none"><circle cx="24" cy="24" r="20" stroke="rgba(255,255,255,.5)" '
               'stroke-width="3"/><path d="M16 30c2-6 6-9 8-9s6 3 8 9" stroke="rgba(255,255,255,.5)" stroke-width="3" '
               'stroke-linecap="round"/><path d="M17 18l4 4M31 18l-4 4" stroke="rgba(255,255,255,.5)" stroke-width="3" '
               'stroke-linecap="round"/></svg>')
    ICO_DIR = ('<svg viewBox="0 0 48 48" fill="none"><circle cx="24" cy="24" r="20" stroke="' + ac + '" '
               'stroke-width="3"/><path d="M15 24l6 6 12-13" stroke="' + ac + '" stroke-width="4" '
               'stroke-linecap="round" stroke-linejoin="round"/></svg>')
    body = f"""<div class="pn" id="p1"><div class="t">{esq[0]}</div><div class="ico">{ICO_ESQ}</div>
      <div class="v" style="color:rgba(255,255,255,.72);">{esq[1]}</div>
      <div class="tr"><i id="f1" style="width:{int(esq[2]*100)}%;background:rgba(255,255,255,.3);"></i></div></div>
    <div id="sx"><svg viewBox="0 0 60 52"><path id="sp" d="M4 26 H40" stroke="{ac}" stroke-width="5"
      fill="none" stroke-linecap="round" stroke-dasharray="40" stroke-dashoffset="40"/>
      <path id="sh" d="M33 15 L50 26 L33 37" stroke="{ac}" stroke-width="5" fill="none"
      stroke-linecap="round" stroke-linejoin="round" opacity="0"/></svg></div>
    <div class="pn" id="p2"><div class="t">{dir_[0]}</div><div class="ico">{ICO_DIR}</div>
      <div class="v" style="color:{ac};">{dir_[1]}</div>
      <div class="tr"><i id="f2" style="width:{int(dir_[2]*100)}%;background:{ac};box-shadow:0 0 18px {glow};"></i></div></div>"""
    js = """function desenho(t){
  const a=ob(seg(t,0.18,0.45),1.4), e1=$('p1');
  e1.style.opacity=cl(seg(t,0.18,0.3)*1.6); e1.style.transform=`scale(${lerp(0.92,1,cl(a))})`;
  $('f1').style.transform=`scaleX(${oq(seg(t,0.38,0.5))})`;
  $('sp').setAttribute('stroke-dashoffset', 40-40*oq(seg(t,0.65,0.4)));
  $('sh').setAttribute('opacity', cl(seg(t,0.92,0.22)));
  const b=ob(seg(t,1.05,0.5),1.6), e2=$('p2');
  e2.style.opacity=cl(seg(t,1.05,0.3)*1.6); e2.style.transform=`scale(${lerp(0.88,1,cl(b))})`;
  $('f2').style.transform=`scaleX(${oq(seg(t,1.25,0.55))})`;
}"""
    escreve(work, nome, titulo, cor, css, body, js, dur)


def medidor(work, nome, titulo, cor, frac, centro, legenda, itens, dur):
    """Anel grande com valor + lista marcando ao lado."""
    ac, glow = COR[cor]
    fit_it = min(fit(x, DW - 340 - 40, 30, 15) for x in itens) if itens else 24
    fct = fit(centro, DW - 340, 54, 24)
    lis = "".join(f'<div class="it" id="i{i}"><span class="dot"></span>{x}</div>'
                  for i, x in enumerate(itens))
    css = f"""
#g{{position:absolute;left:0;top:50%;margin-top:-150px;width:300px;height:300px;}}
#g svg{{width:300px;height:300px;transform:rotate(-90deg);}}
#gc{{position:absolute;left:0;top:50%;margin-top:-150px;width:300px;height:300px;display:flex;align-items:center;
  justify-content:center;flex-direction:column;}}
#gv{{font-family:'Mont';font-size:82px;color:{ac};line-height:1;text-shadow:0 0 30px {glow};}}
#gl{{font-family:'MontB';font-size:16px;letter-spacing:2px;color:rgba(255,255,255,.5);
  text-transform:uppercase;margin-top:6px;white-space:nowrap;}}
#ct{{position:absolute;left:340px;top:0;width:{DW-340}px;font-family:'Mont';font-size:{fct}px;
  line-height:1.1;color:#fff;text-transform:uppercase;}}
#ct b{{color:{ac};}}
#lista{{position:absolute;left:340px;top:110px;bottom:0;width:{DW-340}px;
  display:flex;flex-direction:column;justify-content:space-evenly;}}
.it{{width:100%;display:flex;align-items:center;gap:16px;
  font-family:'MontB';font-size:{fit_it}px;letter-spacing:.6px;color:rgba(255,255,255,.72);
  text-transform:uppercase;white-space:nowrap;opacity:0;}}
.dot{{width:11px;height:11px;border-radius:50%;background:{ac};box-shadow:0 0 12px {ac};flex:0 0 auto;}}
"""
    body = f"""<div id="g"><svg viewBox="0 0 300 300">
      <circle cx="150" cy="150" r="126" fill="none" stroke="rgba(255,255,255,.09)" stroke-width="26"/>
      <circle id="arc" cx="150" cy="150" r="126" fill="none" stroke="{ac}" stroke-width="26"
        stroke-linecap="round" stroke-dasharray="792" stroke-dashoffset="792"/></svg></div>
    <div id="gc"><div id="gv">0%</div><div id="gl">{legenda}</div></div>
    <div id="ct">{centro}</div><div id="lista">{lis}</div>"""
    js = f"""const FR={frac}, NI={len(itens)};
function desenho(t){{
  const p=oq(seg(t,0.28,1.0));
  $('arc').setAttribute('stroke-dashoffset', 792-792*FR*p);
  $('gv').textContent=Math.round(FR*p*100)+'%';
  const q=oc(seg(t,0.5,0.45)); $('ct').style.opacity=q;
  $('ct').style.transform=`translateY(${{(1-q)*14}}px)`;
  for(let i=0;i<NI;i++){{const el=$('i'+i); if(!el) continue;
    const r=oc(seg(t,0.8+i*0.24,0.4));
    el.style.opacity=r; el.style.transform=`translateX(${{(1-r)*20}}px)`;}}
}}"""
    escreve(work, nome, titulo, cor, css, body, js, dur)


def painel(work, nome, titulo, cor, big, unidade, apoio, satelites, dur):
    """Numero gigante com trilho + barras satelite de contexto."""
    ac, glow = COR[cor]
    fml = min(fit(m[0], 290, 30, 15) for m in satelites) if satelites else 22
    fap = fit(apoio, 380, 34, 16)
    # o numero e a unidade dividem 380px: mede-se o conjunto, nao so o numero
    fbig = fit(str(big), 372, 230, 90)          # so o numero: a unidade vai na linha de baixo
    funi = int(fbig * 0.30)
    minis = "".join(
        f'<div class="mi"><span class="ml">{m[0]}</span>'
        f'<span class="mt"><i id="mf{i}" style="width:{int(m[1]*100)}%;"></i></span></div>'
        for i, m in enumerate(satelites))
    css = f"""
#esq{{position:absolute;left:0;top:16px;width:380px;overflow:hidden;height:calc(100% - 32px);display:flex;flex-direction:column;
  justify-content:space-between;}}
#big{{font-family:'Mont';font-size:{fbig}px;line-height:.92;color:{ac};text-shadow:0 0 46px {glow};
  font-variant-numeric:tabular-nums;white-space:nowrap;overflow:hidden;}}
#uni{{font-family:'Mont';font-size:{funi}px;color:{ac};opacity:.9;text-transform:uppercase;
  letter-spacing:2px;line-height:1;margin-top:-6px;}}
#apo{{font-family:'MontB';font-size:{fap}px;letter-spacing:1.2px;color:rgba(255,255,255,.62);
  text-transform:uppercase;line-height:1.2;}}
#trilho{{width:100%;height:26px;border-radius:13px;background:rgba(255,255,255,.08);overflow:hidden;}}
#trilho i{{display:block;height:100%;width:100%;background:linear-gradient(90deg,{ac},rgba(255,255,255,.22));
  transform-origin:left;transform:scaleX(0);}}
#dir{{position:absolute;right:0;top:16px;width:302px;height:calc(100% - 32px);display:flex;flex-direction:column;
  justify-content:space-evenly;}}
.mi{{width:100%;display:flex;flex-direction:column;gap:10px;}}
.ml{{font-family:'MontB';font-size:{fml}px;letter-spacing:1.4px;color:rgba(255,255,255,.6);
  text-transform:uppercase;white-space:nowrap;}}
.mt{{width:100%;height:26px;border-radius:13px;background:rgba(255,255,255,.07);overflow:hidden;}}
.mt i{{display:block;height:100%;background:{ac};transform-origin:left;transform:scaleX(0);border-radius:13px;}}
"""
    unidade_txt = unidade.replace("<small>", "").replace("</small>", "").strip()
    body = f"""<div id="esq"><div id="big"><span id="bv">0</span></div>
      <div id="uni">{unidade_txt}</div>
      <div id="apo">{apoio}</div><div id="trilho"><i id="tf"></i></div></div>
    <div id="dir">{minis}</div>"""
    js = f"""const ALVO={big}, NM={len(satelites)};
function desenho(t){{
  const p=oq(seg(t,0.25,1.1));
  $('bv').textContent=Math.round(ALVO*p);
  $('tf').style.transform=`scaleX(${{p}})`;
  $('apo').style.opacity=oc(seg(t,0.5,0.45));
  for(let i=0;i<NM;i++){{const f=$('mf'+i);
    if(f) f.style.transform=`scaleX(${{oq(seg(t,0.5+i*0.18,0.55))}})`;}}
}}"""
    escreve(work, nome, titulo, cor, css, body, js, dur)


def acumulo(work, nome, titulo, cor, cargas, resultado, dur):
    """A + B = C com cards e uma barra que despenca a cada carga."""
    ac, glow = COR[cor]
    n = len(cargas)
    # largura: n cargas + resultado + (n) operadores de 44px. Nada se sobrepoe por construcao.
    op_w = 44
    cw = int((DW - n * op_w) / (n + 1)) - 16
    ch_card = int(DH * 0.58)          # cards ocupam 74% da altura; o resto e a barra de paciencia
    fcarga = min(fit(c[0], cw - 24, 54, 22) for c in cargas)
    fres = fit(resultado[0], cw - 24, 50, 20)
    cards = "".join(
        f'<div class="cg" id="c{i}" style="left:{i*(cw+op_w)}px;width:{cw}px;">'
        f'<div class="n">{c[0]}</div><div class="t">{c[1]}</div></div>' for i, c in enumerate(cargas))
    ops = "".join(f'<div class="op" style="left:{i*(cw+op_w)+cw}px;width:{op_w}px;" id="o{i}">+</div>'
                  for i in range(n))
    css = f"""
.cg{{position:absolute;top:0;height:{ch_card}px;border-radius:16px;border:2px solid rgba(255,255,255,.14);
  background:rgba(255,255,255,.04);display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:14px;opacity:0;padding:20px 10px;}}
.cg .n{{font-family:'Mont';font-size:{fcarga}px;color:#fff;line-height:1;text-transform:uppercase;}}
.cg .t{{font-family:'MontB';font-size:21px;letter-spacing:1.2px;color:rgba(255,255,255,.5);
  text-transform:uppercase;text-align:center;line-height:1.15;}}
.op{{position:absolute;top:{int(ch_card/2)-24}px;text-align:center;font-family:'Mont';font-size:44px;
  color:rgba(255,255,255,.45);opacity:0;}}
#eq{{position:absolute;left:{(n-1)*(cw+op_w)+cw}px;top:{int(ch_card/2)-24}px;width:{op_w}px;
  text-align:center;font-family:'Mont';font-size:44px;color:rgba(255,255,255,.45);opacity:0;}}
#res{{position:absolute;right:0;top:0;width:{cw}px;height:{ch_card}px;border-radius:16px;
  border:2px solid {ac};background:rgba(255,255,255,.05);box-shadow:0 0 36px {glow};
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;opacity:0;padding:0 8px;}}
#res .n{{font-family:'Mont';font-size:{fres}px;color:{ac};line-height:1.05;text-transform:uppercase;text-align:center;}}
#res .t{{font-family:'MontB';font-size:16px;letter-spacing:1.2px;color:rgba(255,255,255,.5);
  text-transform:uppercase;text-align:center;}}
#pl{{position:absolute;left:16px;bottom:86px;font-family:'MontB';font-size:26px;letter-spacing:2px;
  color:rgba(255,255,255,.42);text-transform:uppercase;}}
#pt{{position:absolute;left:16px;bottom:14px;width:calc(100% - 32px);height:54px;border-radius:10px;
  background:rgba(255,255,255,.08);overflow:hidden;}}
#pf{{height:100%;width:100%;background:linear-gradient(90deg,{ac},rgba(255,255,255,.2));
  transform-origin:left;transform:scaleX(1);}}
"""
    body = (cards + ops + '<div id="eq">=</div>'
            f'<div id="res"><div class="n">{resultado[0]}</div><div class="t">{resultado[1]}</div></div>'
            '<div id="pl">O QUE SOBRA DE PACIÊNCIA</div><div id="pt"><div id="pf"></div></div>')
    js = f"""const N={n};
function desenho(t){{
  for(let i=0;i<N;i++){{
    const p=ob(seg(t,0.2+i*0.42,0.45),1.5), el=$('c'+i);
    el.style.opacity=cl(seg(t,0.2+i*0.42,0.3)*1.6);
    el.style.transform=`scale(${{lerp(0.86,1,cl(p))}})`;
    const o=$('o'+i); if(o) o.style.opacity=cl(seg(t,0.55+i*0.42,0.22));
  }}
  $('eq').style.opacity=cl(seg(t,1.08,0.22));
  const r=ob(seg(t,1.2,0.5),1.7), el=$('res');
  el.style.opacity=cl(seg(t,1.2,0.3)*1.6); el.style.transform=`scale(${{lerp(0.82,1,cl(r))}})`;
  const d1=oq(seg(t,0.42,0.5))*0.45, d2=oq(seg(t,0.95,0.6))*0.48;
  $('pf').style.transform=`scaleX(${{Math.max(0.06,1-d1-d2)}})`;
}}"""
    escreve(work, nome, titulo, cor, css, body, js, dur)


def imagem_dados(work, nome, titulo, cor, img, legenda_img, dados, dur, kb="push"):
    """IMAGEM + ELEMENTOS na mesma animacao, lado a lado, sem um cobrir o outro.

    Ordem do Chefe (25/07/2026): "o Gennaro nao e so hyperframe, pode e deve incluir imagens. Voce
    pode inclusive mesclar imagens com elementos do hyperframe na mesma animacao, ao mesmo tempo na
    tela, desde que um nao sobrescreva o outro e nao fique feio."

    Layout: imagem a esquerda com moldura e Ken Burns leve, corredor de 24px, e a direita o bloco de
    dados (numero, barras ou lista). As duas zonas sao exclusivas por construcao.
    `img` e o caminho servido (ex: '../img/t03.png'); `dados` = [(label, frac, valor)].
    """
    ac, glow = COR[cor]
    # Com a area dobrada, a imagem deixa de ser um selo lateral e vira o protagonista: ela ocupa a
    # largura toda em cima, e os dados desenhados ficam embaixo, em faixa propria. Zonas exclusivas.
    ih = int(DH * 0.56)
    dtop = ih + 22
    linhas = "".join(
        f'<div class="dd" style="top:{i*62}px;"><div class="dl">{d[0]}</div>'
        f'<div class="dt"><i id="df{i}" style="width:{int(d[1]*100)}%;"></i></div>'
        f'<div class="dv" id="dv{i}">{d[2]}</div></div>' for i, d in enumerate(dados))
    css = f"""
#img{{position:absolute;left:0;top:0;width:100%;height:{ih}px;border-radius:18px;overflow:hidden;
  border:2px solid {ac}55;box-shadow:0 0 34px rgba(0,0,0,.5);opacity:0;}}
#img img{{position:absolute;left:50%;top:50%;width:118%;transform:translate(-50%,-50%) scale(1);
  will-change:transform;}}
#imgleg{{position:absolute;left:0;right:0;bottom:0;padding:16px 18px;background:linear-gradient(
  180deg,transparent,rgba(0,0,0,.85));font-family:'Mont';font-size:28px;letter-spacing:.6px;
  color:#fff;text-transform:uppercase;text-align:center;}}
#dados{{position:absolute;left:0;top:{dtop}px;width:100%;}}
.dd{{position:absolute;left:0;width:100%;height:52px;}}
.dl{{font-family:'MontB';font-size:22px;letter-spacing:1.2px;color:rgba(255,255,255,.55);
  text-transform:uppercase;white-space:nowrap;}}
.dt{{margin-top:8px;height:22px;border-radius:12px;background:rgba(255,255,255,.08);overflow:hidden;}}
.dt i{{display:block;height:100%;background:{ac};transform-origin:left;transform:scaleX(0);
  border-radius:12px;box-shadow:0 0 16px {glow};}}
.dv{{position:absolute;right:0;top:-4px;font-family:'Mont';font-size:34px;color:{ac};
  white-space:nowrap;opacity:0;}}
"""
    body = f"""<div id="img"><img id="im" src="{img}"><div id="imgleg">{legenda_img}</div></div>
    <div id="dados">{linhas}</div>"""
    js = f"""const ND={len(dados)}, KB='{kb}';
function desenho(t){{
  const iv=$('img');
  iv.style.opacity=cl(seg(t,0.12,0.4)*1.5);
  const z=1+0.09*cl(t/Math.max(1,DUR));
  const px = KB==='panr' ? -18*cl(t/Math.max(1,DUR)) : (KB==='panl' ? 18*cl(t/Math.max(1,DUR)) : 0);
  $('im').style.transform=`translate(calc(-50% + ${{px}}px),-50%) scale(${{z}})`;
  for(let i=0;i<ND;i++){{
    const f=$('df'+i); if(f) f.style.transform=`scaleX(${{oq(seg(t,0.42+i*0.2,0.55))}})`;
    const v=$('dv'+i); if(v) v.style.opacity=cl(seg(t,0.62+i*0.2,0.3));
  }}
}}"""
    escreve(work, nome, titulo, cor, css, body, js, dur)
