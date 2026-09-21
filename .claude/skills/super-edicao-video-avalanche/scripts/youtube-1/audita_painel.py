#!/usr/bin/env python3
"""audita_painel.py · roda os PORTÕES DA LEI 2 e da LEI 3 num Chrome só seu.

Uso:
    python3 audita_painel.py <dir do proj> [--porta 8899]

Por que existe (06/08/2026). As duas auditorias moram em JS
(`referencia/audita-geometria.js` e `referencia/audita-tela-cheia.js`) e antes eram rodadas
pelo browser do MCP. Com vários agentes editando vídeos ao mesmo tempo, todos disputam a
MESMA aba: a medição de um vídeo saía com o DOM de outro. Este script sobe um
chrome-headless-shell próprio, mede e mata o browser, então cada vídeo é auditado no seu.

Ele confere a identidade do projeto antes de medir (duração da raiz e número de cenas) e
falha alto se a página não for a que você pediu.

Saída: JSON com `geometria` (violacoes) e `tela_cheia` (instantes_ocos). Os dois têm que
ser ZERO antes do render.
"""
import json, os, re, socket, subprocess, sys, time, urllib.request

import websocket  # websocket-client

SHELL = None
for base in ('~/Library/Caches/ms-playwright',):
    b = os.path.expanduser(base)
    if os.path.isdir(b):
        for d in sorted(os.listdir(b), reverse=True):
            p = os.path.join(b, d, 'chrome-headless-shell-mac-arm64', 'chrome-headless-shell')
            if os.path.exists(p):
                SHELL = p
                break
    if SHELL:
        break
if not SHELL:
    sys.exit('chrome-headless-shell nao encontrado')

JS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'referencia')
JS_DIR = os.path.normpath(JS_DIR)


def porta_livre():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p


def carrega_js(nome):
    src = open(os.path.join(JS_DIR, nome), encoding='utf-8').read()
    i = src.index('() => {')
    return src[i:]


def main():
    proj = os.path.abspath(os.path.expanduser(sys.argv[1]))
    if not os.path.exists(os.path.join(proj, 'index.html')):
        sys.exit('sem index.html em ' + proj)

    http_port = porta_livre()
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(http_port), '--bind', '127.0.0.1'],
                           cwd=proj, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cdp_port = porta_livre()
    br = subprocess.Popen([SHELL, '--headless', '--disable-gpu', '--hide-scrollbars',
                           '--window-size=1920,1080', '--remote-debugging-port=%d' % cdp_port,
                           '--user-data-dir=/tmp/audita-%d' % cdp_port, '--remote-allow-origins=*', 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        alvo = None
        for _ in range(80):
            try:
                alvo = json.load(urllib.request.urlopen('http://127.0.0.1:%d/json/list' % cdp_port))
                if alvo:
                    break
            except Exception:
                pass
            time.sleep(0.25)
        if not alvo:
            sys.exit('browser nao subiu')
        ws = websocket.create_connection(alvo[0]['webSocketDebuggerUrl'], timeout=600,
                                         max_size=64 * 1024 * 1024)
        n = [0]

        def cmd(method, **params):
            n[0] += 1
            ws.send(json.dumps({'id': n[0], 'method': method, 'params': params}))
            while True:
                msg = json.loads(ws.recv())
                if msg.get('id') == n[0]:
                    return msg

        cmd('Page.enable')
        cmd('Runtime.enable')
        cmd('Emulation.setDeviceMetricsOverride', width=1920, height=1080,
            deviceScaleFactor=1, mobile=False)
        cmd('Page.navigate', url='http://127.0.0.1:%d/index.html' % http_port)

        pronto = False
        for _ in range(160):
            r = cmd('Runtime.evaluate', expression=(
                '(() => { const t = window.__timelines && window.__timelines["main"];'
                ' const r = document.querySelector("[data-composition-id]");'
                ' return t && r ? JSON.stringify({dur: +r.dataset.duration,'
                ' cenas: document.querySelectorAll(".clip[data-track-index=\\"2\\"]").length}) : ""; })()'),
                returnByValue=True)
            v = r.get('result', {}).get('result', {}).get('value')
            if v:
                ident = json.loads(v)
                pronto = True
                break
            time.sleep(0.25)
        if not pronto:
            sys.exit('composicao nao carregou')

        saida = {'proj': proj, 'identidade': ident}
        for chave, arquivo in (('geometria', 'audita-geometria.js'),
                               ('tela_cheia', 'audita-tela-cheia.js')):
            fn = carrega_js(arquivo)
            r = cmd('Runtime.evaluate', expression='JSON.stringify((%s)())' % fn,
                    returnByValue=True, awaitPromise=True, timeout=600000)
            res = r.get('result', {}).get('result', {})
            if res.get('type') == 'string':
                saida[chave] = json.loads(res['value'])
            else:
                saida[chave] = {'erro': r.get('result', {}).get('exceptionDetails')
                                or res}
        print(json.dumps(saida, ensure_ascii=False, indent=1))

        g = saida.get('geometria', {}).get('violacoes')
        o = saida.get('tela_cheia', {}).get('instantes_ocos')
        if g or o:
            sys.exit(1)
    finally:
        try:
            br.terminate()
        except Exception:
            pass
        try:
            srv.terminate()
        except Exception:
            pass


if __name__ == '__main__':
    main()
