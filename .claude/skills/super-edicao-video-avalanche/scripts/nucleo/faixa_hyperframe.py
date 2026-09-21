#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STRIP HYPERFRAME v3: o infografico OCUPA A FAIXA INTEIRA.

Correcao do Chefe em 25/07/2026: "duas frases, nenhum infografico, e principalmente o espaco
disponivel muito mal aproveitado, preencha o espaco todo. E nao so nesse trecho, em todos."

O que estava errado na v2: um terco da largura era um rotulo quase vazio, o desenho vivia so na
metade de cima e sobrava buraco embaixo. Aqui o rotulo vira um CHIP pequeno no canto e o desenho
usa 808x150, mais do que o dobro da area anterior, com camada de fundo (grid, eixo, marcacoes)
para nao existir vazio morto.

GEOMETRIA (dentro de [130,950], que e o que o celular mostra)
  chip     x 142, y 12, altura 26      rotulo curto, uma linha
  desenho  x 142..950, y 46..196       808 x 150, area util do infografico
  barra    y 206..212                  temporizador global
Nada se sobrepoe: o chip fica acima do desenho, com 8px de folga.
"""
import os

X0, X1 = 142, 950
LARG = X1 - X0
DY0, DH = 46, 150
FW, FH = 1080, 232        # dimensao da faixa


def configura(largura, altura, margem=None):
    """Adapta a geometria para outra faixa (ex: 1920x180 num video 16:9 de landing page).
    A margem lateral padrao e 5% da largura, que e a zona segura de qualquer player."""
    global X0, X1, LARG, DY0, DH, FW, FH
    FW, FH = largura, altura
    m = margem if margem is not None else int(largura * 0.052)
    X0, X1 = m, largura - m
    LARG = X1 - X0
    DY0 = int(altura * 0.20)
    DH = int(altura * 0.62)

BASE = """<!doctype html><html><head><meta charset="utf-8">
<style>
@font-face{{font-family:'Mont';src:url('../fonts/Montserrat-Black.ttf');font-weight:900;}}
@font-face{{font-family:'MontX';src:url('../fonts/Montserrat-ExtraBold.ttf');font-weight:800;}}
@font-face{{font-family:'MontB';src:url('../fonts/Montserrat-Bold.ttf');font-weight:700;}}
*{{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased;}}
html,body{{width:{fw}px;height:{fh}px;background:#080A0E;overflow:hidden;}}
#stage{{position:absolute;inset:0;background:
  radial-gradient(900px 260px at 50% 45%, rgba(62,200,255,.06), transparent 72%),
  linear-gradient(120deg,#0C1016 0%,#080A0E 55%,#0F141C 100%);}}
#grid{{position:absolute;left:{x0}px;top:{dy}px;width:{lw}px;height:{dh}px;opacity:.5;
  background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);
  background-size:44px 38px;}}
#chip{{position:absolute;left:{x0}px;top:{ct}px;height:30px;padding:0 14px;display:inline-flex;
  align-items:center;gap:9px;border-radius:14px;background:rgba(255,255,255,.06);
  border:1px solid {ac}55;font-family:'MontX';font-size:16px;letter-spacing:3px;color:{ac};
  text-transform:uppercase;white-space:nowrap;}}
#chip b{{width:7px;height:7px;border-radius:50%;background:{ac};box-shadow:0 0 8px {ac};}}
#des{{position:absolute;left:{x0}px;top:{dy}px;width:{lw}px;height:{dh}px;}}
#bar{{position:absolute;left:{x0}px;bottom:{bb}px;width:{lw}px;height:6px;
  background:rgba(255,255,255,.09);border-radius:3px;overflow:hidden;}}
#fill{{height:100%;width:100%;background:{ac};transform-origin:left center;border-radius:3px;
  box-shadow:0 0 14px {glow};}}
{css}
</style></head><body><div id="stage">
  <div id="grid"></div>
  <div id="chip"><b></b>{chip}</div>
  <div id="des">{body}</div>
  <div id="bar"><div id="fill"></div></div>
</div>
<script>
const P0={p0}, P1={p1}, DUR={dur}, W={lw}, H={dh};
const cl=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const seg=(t,t0,d)=>cl((t-t0)/d);
const oc=p=>1-Math.pow(1-p,3);
const oq=p=>1-Math.pow(1-p,5);
const ob=(p,s=1.5)=>{{const c3=s+1;return 1+c3*Math.pow(p-1,3)+s*Math.pow(p-1,2);}};
const lerp=(a,b,p)=>a+(b-a)*p;
const $=i=>document.getElementById(i);
{js}
window.__seek=function(t){{
  const a=oc(seg(t,0.05,0.4));
  $('chip').style.opacity=a; $('chip').style.transform=`translateY(${{(1-a)*-8}}px)`;
  $('fill').style.transform=`scaleX(${{P0+(P1-P0)*cl(t/DUR)}})`;
  desenho(t);
}};
window.__seek(0);
</script></body></html>
"""

COR = {"cyan": ("#3EC8FF", "rgba(62,200,255,.5)"), "coral": ("#F5402E", "rgba(245,64,46,.5)"),
       "green": ("#24D869", "rgba(36,216,105,.5)"), "gold": ("#FFC53D", "rgba(255,197,61,.5)"),
       "violet": ("#9B6BFF", "rgba(155,107,255,.5)")}


def escreve(work, nome, chip, cor, css, body, js, p0, p1, dur):
    ac, glow = COR[cor]
    html = BASE.format(x0=X0, lw=LARG, dy=DY0, dh=DH, ac=ac, glow=glow, chip=chip,
                       css=css, body=body, js=js, p0=round(p0, 4), p1=round(p1, 4),
                       dur=round(dur, 2), fw=FW, fh=FH, bb=max(10, int(FH * 0.06)),
                       ct=max(8, int(FH * 0.055)))
    open(os.path.join(work, "elements", f"strip_{nome}.html"), "w", encoding="utf-8").write(html)


# ---------------------------------------------------------------------- arquetipos densos

def barras(work, nome, chip, cor, dados, p0, p1, dur):
    """Colunas ocupando toda a altura, com valor em cima, eixo e rotulo embaixo."""
    ac, glow = COR[cor]
    n = len(dados)
    larg = int((LARG - (n - 1) * 26) / n)
    cols = "".join(
        f'<div class="col" style="left:{i*(larg+26)}px;width:{larg}px;">'
        f'<div class="vl" id="v{i}">{d[2]}</div>'
        f'<div class="bw"><div class="bb" id="b{i}" style="height:{int(d[1]*100)}%;'
        f'background:{ac if d[3] else "rgba(255,255,255,.20)"};'
        f'box-shadow:{"0 0 26px "+glow if d[3] else "none"};"></div></div>'
        f'<div class="lb" style="color:{"#fff" if d[3] else "rgba(255,255,255,.42)"};">{d[0]}</div>'
        f'</div>' for i, d in enumerate(dados))
    css = """
.col{position:absolute;top:0;height:100%;}
.vl{position:absolute;top:0;left:0;right:0;text-align:center;font-family:'Mont';font-size:26px;
  color:#fff;opacity:0;white-space:nowrap;}
.bw{position:absolute;left:0;right:0;top:34px;bottom:30px;display:flex;align-items:flex-end;}
.bb{width:100%;border-radius:9px 9px 4px 4px;transform-origin:bottom center;transform:scaleY(0);}
.lb{position:absolute;bottom:0;left:0;right:0;text-align:center;font-family:'MontB';font-size:17px;
  letter-spacing:1.2px;text-transform:uppercase;white-space:nowrap;}
#eixo{position:absolute;left:0;right:0;bottom:28px;height:2px;background:rgba(255,255,255,.14);}
"""
    js = ("const N=" + str(n) + ";\nfunction desenho(t){for(let i=0;i<N;i++){"
          "const p=oq(seg(t,0.28+i*0.18,0.62));"
          "$('b'+i).style.transform='scaleY('+p+')';"
          "$('v'+i).style.opacity=cl(seg(t,0.45+i*0.18,0.3));}}")
    escreve(work, nome, chip, cor, css, '<div id="eixo"></div>' + cols, js, p0, p1, dur)


def fluxo(work, nome, chip, cor, etapas, p0, p1, dur):
    """Cadeia de etapas com icone grande, conexao pulsante e legenda, ocupando toda a faixa."""
    ac, glow = COR[cor]
    n = len(etapas)
    box = int((LARG - (n - 1) * 30) / n)
    nos = "".join(
        f'<div class="no" id="n{i}" style="left:{i*(box+30)}px;width:{box}px;">'
        f'<div class="ic">{e[1]}</div><div class="lb">{e[0]}</div>'
        f'<div class="sb">{e[2]}</div></div>' for i, e in enumerate(etapas))
    linhas = "".join(
        f'<div class="ln" style="left:{i*(box+30)+box}px;width:30px;"><i id="li{i}"></i></div>'
        for i in range(n - 1))
    css = f"""
.no{{position:absolute;top:0;height:100%;border-radius:16px;background:rgba(255,255,255,.035);
  border:2px solid rgba(255,255,255,.10);display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:6px;opacity:0;}}
.no .ic{{width:56px;height:56px;display:flex;align-items:center;justify-content:center;}}
.no .ic svg{{width:52px;height:52px;}}
.no .lb{{font-family:'Mont';font-size:22px;color:#fff;text-transform:uppercase;letter-spacing:.4px;
  text-align:center;line-height:1.06;padding:0 8px;}}
.no .sb{{font-family:'MontB';font-size:14px;letter-spacing:1.4px;color:rgba(255,255,255,.45);
  text-transform:uppercase;text-align:center;padding:0 8px;line-height:1.1;}}
.ln{{position:absolute;top:50%;height:3px;margin-top:-1px;background:rgba(255,255,255,.12);overflow:hidden;}}
.ln i{{display:block;height:100%;width:100%;background:{ac};transform-origin:left;transform:scaleX(0);
  box-shadow:0 0 12px {glow};}}
"""
    js = f"""const N={n};
function desenho(t){{
  for(let i=0;i<N;i++){{
    const p=ob(seg(t,0.18+i*0.30,0.5),1.5), el=$('n'+i);
    el.style.opacity=cl(seg(t,0.18+i*0.30,0.3)*1.6);
    el.style.transform=`scale(${{lerp(0.88,1,cl(p))}})`;
    el.style.borderColor = t>0.18+i*0.30+0.28 ? '{ac}66' : 'rgba(255,255,255,.10)';
  }}
  for(let i=0;i<N-1;i++){{ const li=$('li'+i);
    if(li) li.style.transform=`scaleX(${{oq(seg(t,0.40+i*0.30,0.4))}})`; }}
}}"""
    escreve(work, nome, chip, cor, css, linhas + nos, js, p0, p1, dur)


def painel(work, nome, chip, cor, titulo, big, unidade, apoio, barras_lat, p0, p1, dur):
    """Numero gigante + apoio + mini barras. Em faixa BAIXA (altura util < 130px) o layout vira
    HORIZONTAL: numero e apoio lado a lado, sem trilho, senao o texto de apoio fica cortado."""
    ac, glow = COR[cor]
    baixa = DH < 155
    minis = "".join(
        f'<div class="mi"><span class="ml">{m[0]}</span>'
        f'<span class="mt"><i id="mf{i}" style="width:{int(m[1]*100)}%;"></i></span></div>'
        for i, m in enumerate(barras_lat))
    lesq = int(LARG * (0.62 if baixa else 0.55))
    dir_esq = "row" if baixa else "column"
    ali = "baseline" if baixa else "flex-start"
    gap = 18 if baixa else 4
    tit_extra = "align-self:center;" if baixa else ""
    fbig = int(DH * (0.72 if baixa else 0.58))
    funi = int(fbig * 0.40)
    show_tr = "none" if baixa else "block"
    css = f"""
#esq{{position:absolute;left:0;top:0;width:{lesq}px;height:100%;
  display:flex;flex-direction:{dir_esq};align-items:{ali};gap:{gap}px;}}
#tit{{font-family:'MontB';font-size:16px;letter-spacing:2.4px;color:rgba(255,255,255,.5);
  text-transform:uppercase;white-space:nowrap;{tit_extra}}}
#big{{font-family:'Mont';font-size:{fbig}px;line-height:1;color:{ac};text-shadow:0 0 34px {glow};
  font-variant-numeric:tabular-nums;white-space:nowrap;}}
#big small{{font-size:{funi}px;opacity:.85;}}
#apo{{font-family:'MontB';font-size:19px;letter-spacing:1.2px;color:rgba(255,255,255,.62);
  text-transform:uppercase;white-space:nowrap;line-height:1.2;}}
#dir{{position:absolute;right:0;top:6px;width:{int(LARG*0.34)}px;height:100%;
  display:flex;flex-direction:column;justify-content:space-evenly;}}
.mi{{width:100%;display:flex;align-items:center;gap:12px;}}
.ml{{width:{140 if baixa else 210}px;font-family:'MontB';font-size:14px;letter-spacing:1.2px;
  color:rgba(255,255,255,.5);
  text-transform:uppercase;text-align:right;white-space:nowrap;}}
.mt{{flex:1;height:12px;border-radius:7px;background:rgba(255,255,255,.07);overflow:hidden;}}
.mt i{{display:block;height:100%;background:{ac};transform-origin:left;transform:scaleX(0);border-radius:7px;}}
#trilho{{position:absolute;left:0;bottom:0;width:{lesq}px;height:10px;border-radius:6px;
  display:{show_tr};
  background:rgba(255,255,255,.08);overflow:hidden;}}
#trilho i{{display:block;height:100%;width:100%;background:linear-gradient(90deg,{ac},rgba(255,255,255,.22));
  transform-origin:left;transform:scaleX(0);}}
"""
    lesq = int(LARG * (0.62 if baixa else 0.55))
    body = f"""<div id="esq"><div id="tit">{titulo}</div>
      <div id="big"><span id="bv">0</span><small>{unidade}</small></div>
      <div id="apo">{apoio}</div></div>
    <div id="trilho"><i id="tf"></i></div>
    <div id="dir">{minis}</div>"""
    js = f"""const ALVO={big}, NM={len(barras_lat)};
// AUTO-FIT (correcao 18/08/2026): em faixa BAIXA o bloco da esquerda e horizontal e com texto de
// apoio ou unidade longa ele transbordava POR CIMA das mini barras da direita. Encolhe apoio e
// numero ate caber de verdade, medido no proprio layout, em vez de cortar ou deixar atropelar.
let _fit=false;
function fit(){{
  const esq=$('esq'), apo=$('apo'), big=$('big');
  // medir com o numero JA no valor final: no primeiro seek ele ainda vale 0 e tudo 'cabe',
  // e o atropelo aparecia depois, quando a contagem terminava.
  $('bv').textContent=Math.round(ALVO).toLocaleString('pt-BR');
  // scrollWidth mente em flex container com overflow visible: medir o RECT do ultimo filho
  // contra o rect do proprio bloco e a borda esquerda das mini barras.
  const lim=()=>{{const d=document.getElementById('dir');
    const a=d?d.getBoundingClientRect().left-10:esq.getBoundingClientRect().right;
    return Math.min(a, esq.getBoundingClientRect().right);}};
  const cabe=()=>apo.getBoundingClientRect().right<=lim();
  let fa=19; while(!cabe() && fa>11){{ fa-=1; apo.style.fontSize=fa+'px'; }}
  let fb={fbig}; while(!cabe() && fb>26){{ fb-=2; big.style.fontSize=fb+'px'; }}
}}
function desenho(t){{
  if(!_fit){{ _fit=true; fit(); }}
  const p=oq(seg(t,0.22,1.1));
  $('bv').textContent=Math.round(ALVO*p).toLocaleString('pt-BR');
  $('tf').style.transform=`scaleX(${{p}})`;
  const q=oc(seg(t,0.5,0.45)); $('apo').style.opacity=q;
  for(let i=0;i<NM;i++){{ const f=$('mf'+i);
    if(f) f.style.transform=`scaleX(${{oq(seg(t,0.45+i*0.16,0.55))}})`; }}
}}"""
    escreve(work, nome, chip, cor, css, body, js, p0, p1, dur)


def confronto(work, nome, chip, cor, esq, dir_, p0, p1, dur):
    """Dois paineis do tamanho da faixa, com barra propria e seta no meio."""
    ac, glow = COR[cor]
    css = f"""
.pn{{position:absolute;top:0;width:368px;height:100%;border-radius:16px;padding:14px 18px;
  border:2px solid rgba(255,255,255,.12);background:rgba(255,255,255,.035);opacity:0;}}
.pn .t{{font-family:'MontB';font-size:15px;letter-spacing:2px;color:rgba(255,255,255,.45);
  text-transform:uppercase;}}
.pn .v{{font-family:'Mont';font-size:40px;line-height:1.02;margin-top:6px;text-transform:uppercase;
  white-space:nowrap;}}
.pn .tr{{position:absolute;left:18px;right:18px;bottom:16px;height:11px;border-radius:6px;
  background:rgba(255,255,255,.08);overflow:hidden;}}
.pn .tr i{{display:block;height:100%;transform-origin:left;transform:scaleX(0);border-radius:6px;}}
#p1{{left:0;}} #p2{{right:0;border-color:{ac}77;box-shadow:0 0 30px rgba(0,0,0,.45);}}
#sx{{position:absolute;left:380px;top:50%;margin-top:-22px;width:48px;height:44px;}}
"""
    body = f"""<div class="pn" id="p1"><div class="t">{esq[0]}</div>
      <div class="v" style="color:rgba(255,255,255,.72);">{esq[1]}</div>
      <div class="tr"><i id="f1" style="width:{int(esq[2]*100)}%;background:rgba(255,255,255,.3);"></i></div></div>
    <div id="sx"><svg viewBox="0 0 48 44"><path id="sp" d="M2 22 H32" stroke="{ac}" stroke-width="4"
      fill="none" stroke-linecap="round" stroke-dasharray="34" stroke-dashoffset="34"/>
      <path id="sh" d="M26 13 L40 22 L26 31" stroke="{ac}" stroke-width="4" fill="none"
      stroke-linecap="round" stroke-linejoin="round" opacity="0"/></svg></div>
    <div class="pn" id="p2"><div class="t">{dir_[0]}</div>
      <div class="v" style="color:{ac};">{dir_[1]}</div>
      <div class="tr"><i id="f2" style="width:{int(dir_[2]*100)}%;background:{ac};box-shadow:0 0 16px {glow};"></i></div></div>"""
    js = """function desenho(t){
  const a=ob(seg(t,0.15,0.45),1.4), e1=$('p1');
  e1.style.opacity=cl(seg(t,0.15,0.3)*1.6); e1.style.transform=`scale(${lerp(0.92,1,cl(a))})`;
  $('f1').style.transform=`scaleX(${oq(seg(t,0.35,0.5))})`;
  $('sp').setAttribute('stroke-dashoffset', 34-34*oq(seg(t,0.62,0.4)));
  $('sh').setAttribute('opacity', cl(seg(t,0.88,0.22)));
  const b=ob(seg(t,1.00,0.5),1.6), e2=$('p2');
  e2.style.opacity=cl(seg(t,1.00,0.3)*1.6); e2.style.transform=`scale(${lerp(0.88,1,cl(b))})`;
  $('f2').style.transform=`scaleX(${oq(seg(t,1.20,0.55))})`;
}"""
    escreve(work, nome, chip, cor, css, body, js, p0, p1, dur)


def medidor(work, nome, chip, cor, frac, centro, legenda, itens, p0, p1, dur):
    """Anel grande + lista de itens marcando ao lado, preenchendo a faixa."""
    ac, glow = COR[cor]
    lis = "".join(
        f'<div class="it" id="i{i}" style="top:{i*40}px;"><span class="dot"></span>{x}</div>'
        for i, x in enumerate(itens))
    css = f"""
#g{{position:absolute;left:6px;top:-4px;width:158px;height:158px;}}
#g svg{{width:158px;height:158px;transform:rotate(-90deg);}}
#gc{{position:absolute;left:6px;top:-4px;width:158px;height:158px;display:flex;align-items:center;
  justify-content:center;flex-direction:column;}}
#gv{{font-family:'Mont';font-size:44px;color:{ac};line-height:1;text-shadow:0 0 24px {glow};}}
#gl{{font-family:'MontB';font-size:13px;letter-spacing:2px;color:rgba(255,255,255,.5);
  text-transform:uppercase;margin-top:4px;white-space:nowrap;}}
#ct{{position:absolute;left:196px;top:8px;width:280px;font-family:'Mont';font-size:32px;
  line-height:1.12;color:#fff;text-transform:uppercase;}}
#ct b{{color:{ac};}}
#lista{{position:absolute;right:0;top:6px;width:300px;height:100%;}}
.it{{position:absolute;left:0;width:100%;height:32px;display:flex;align-items:center;gap:12px;
  font-family:'MontB';font-size:17px;letter-spacing:.8px;color:rgba(255,255,255,.72);
  text-transform:uppercase;white-space:nowrap;opacity:0;}}
.dot{{width:9px;height:9px;border-radius:50%;background:{ac};box-shadow:0 0 10px {ac};flex:0 0 auto;}}
"""
    body = f"""<div id="g"><svg viewBox="0 0 158 158">
      <circle cx="79" cy="79" r="66" fill="none" stroke="rgba(255,255,255,.09)" stroke-width="15"/>
      <circle id="arc" cx="79" cy="79" r="66" fill="none" stroke="{ac}" stroke-width="15"
        stroke-linecap="round" stroke-dasharray="415" stroke-dashoffset="415"/></svg></div>
    <div id="gc"><div id="gv">0%</div><div id="gl">{legenda}</div></div>
    <div id="ct">{centro}</div><div id="lista">{lis}</div>"""
    js = f"""const FR={frac}, NI={len(itens)};
function desenho(t){{
  const p=oq(seg(t,0.25,1.0));
  $('arc').setAttribute('stroke-dashoffset', 415-415*FR*p);
  $('gv').textContent=Math.round(FR*p*100)+'%';
  const q=oc(seg(t,0.45,0.45)); $('ct').style.opacity=q;
  $('ct').style.transform=`translateY(${{(1-q)*12}}px)`;
  for(let i=0;i<NI;i++){{ const el=$('i'+i); if(!el) continue;
    const r=oc(seg(t,0.70+i*0.22,0.4));
    el.style.opacity=r; el.style.transform=`translateX(${{(1-r)*18}}px)`; }}
}}"""
    escreve(work, nome, chip, cor, css, body, js, p0, p1, dur)


def acumulo(work, nome, chip, cor, cargas, resultado, p0, p1, dur, barra="PACIÊNCIA DE QUEM COMPRA"):
    """A + B = C com cards da altura da faixa e uma barra que despenca a cada carga."""
    ac, glow = COR[cor]
    n = len(cargas)
    cw = 190
    cards = "".join(
        f'<div class="cg" id="c{i}" style="left:{i*(cw+56)}px;width:{cw}px;">'
        f'<div class="n">{c[0]}</div><div class="t">{c[1]}</div></div>' for i, c in enumerate(cargas))
    ops = "".join(
        f'<div class="op" id="o{i}" style="left:{i*(cw+56)+cw+14}px;">+</div>' for i in range(n - 1))
    css = f"""
.cg{{position:absolute;top:0;height:96px;border-radius:14px;border:2px solid rgba(255,255,255,.14);
  background:rgba(255,255,255,.04);display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:4px;opacity:0;}}
.cg .n{{font-family:'Mont';font-size:34px;color:#fff;line-height:1;text-transform:uppercase;white-space:nowrap;}}
.cg .t{{font-family:'MontB';font-size:13px;letter-spacing:1.4px;color:rgba(255,255,255,.5);
  text-transform:uppercase;white-space:nowrap;}}
.op{{position:absolute;top:26px;width:28px;text-align:center;font-family:'Mont';font-size:34px;
  color:rgba(255,255,255,.45);opacity:0;}}
#eq{{position:absolute;left:{2*(cw+56)-42}px;top:26px;width:28px;text-align:center;font-family:'Mont';
  font-size:34px;color:rgba(255,255,255,.45);opacity:0;}}
#res{{position:absolute;right:0;top:0;width:{LARG-2*(cw+56)}px;height:96px;border-radius:14px;
  border:2px solid {ac};background:rgba(255,255,255,.05);box-shadow:0 0 34px {glow};
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;opacity:0;}}
#res .n{{font-family:'Mont';font-size:36px;color:{ac};line-height:1;text-transform:uppercase;white-space:nowrap;}}
#res .t{{font-family:'MontB';font-size:13px;letter-spacing:1.4px;color:rgba(255,255,255,.5);
  text-transform:uppercase;white-space:nowrap;}}
#pl{{position:absolute;left:0;bottom:22px;font-family:'MontB';font-size:14px;letter-spacing:2px;
  color:rgba(255,255,255,.42);text-transform:uppercase;}}
#pt{{position:absolute;left:0;bottom:0;width:100%;height:14px;border-radius:8px;
  background:rgba(255,255,255,.08);overflow:hidden;}}
#pf{{height:100%;width:100%;background:linear-gradient(90deg,{ac},rgba(255,255,255,.2));
  transform-origin:left;transform:scaleX(1);}}
"""
    body = (cards + ops + '<div id="eq">=</div>'
            f'<div id="res"><div class="n">{resultado[0]}</div><div class="t">{resultado[1]}</div></div>'
            f'<div id="pl">{barra}</div><div id="pt"><div id="pf"></div></div>')
    js = f"""const N={n};
function desenho(t){{
  for(let i=0;i<N;i++){{
    const p=ob(seg(t,0.18+i*0.42,0.45),1.5), el=$('c'+i);
    el.style.opacity=cl(seg(t,0.18+i*0.42,0.3)*1.6);
    el.style.transform=`scale(${{lerp(0.86,1,cl(p))}})`;
    const o=$('o'+i); if(o) o.style.opacity=cl(seg(t,0.52+i*0.42,0.22));
  }}
  $('eq').style.opacity=cl(seg(t,1.05,0.22));
  const r=ob(seg(t,1.15,0.5),1.7), el=$('res');
  el.style.opacity=cl(seg(t,1.15,0.3)*1.6); el.style.transform=`scale(${{lerp(0.82,1,cl(r))}})`;
  const d1=oq(seg(t,0.40,0.5))*0.45, d2=oq(seg(t,0.90,0.6))*0.48;
  $('pf').style.transform=`scaleX(${{Math.max(0.06,1-d1-d2)}})`;
}}"""
    escreve(work, nome, chip, cor, css, body, js, p0, p1, dur)
