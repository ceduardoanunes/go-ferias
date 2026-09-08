#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audita colaboradores DESLIGADOS cujo período aquisitivo mais recente nao fecha
na data do desligamento -- o bug que fazia o período "continuar contando" e
travar a readmissao (corrigido no app em 08/09/2026, commit edeaa5a). Esse fix
so vale para desligamentos feitos DAQUI PRA FRENTE -- quem ja estava desligado
antes disso fica preso nesse estado ate alguem corrigir a mao.

Uso (dry-run, so lista quem esta quebrado):
  py auditar_desligamento_periodo.py --url https://goferias.onrender.com --senha demo

Para corrigir de verdade (fecha o período na data do desligamento, exatamente
o que o app faz sozinho hoje ao desligar alguem):
  py auditar_desligamento_periodo.py --url https://goferias.onrender.com --senha demo --apply

Opcoes:
  --url       base do backend (obrigatorio). Ex.: https://goferias.onrender.com
  --email     login admin (padrao: admin@goegrow.com.br)
  --senha     senha admin (padrao: demo)
  --apply     grava (PATCH). Sem isso, so lista (dry-run).
  --inseguro  ignora verificacao do certificado TLS (SSL do Python no Windows).

Seguro re-rodar: idempotente (so mexe em quem ainda esta divergente).
"""
import json, argparse, ssl, urllib.request, urllib.error


def http(url, token=None, method="GET", body=None, ctx=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, context=ctx) as r:
            txt = r.read().decode("utf-8")
            return (r.status, json.loads(txt) if txt else None)
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "ignore")
        try:
            msg = json.loads(txt).get("message", txt)
        except Exception:
            msg = txt
        raise SystemExit(f"Erro HTTP {e.code} em {method} {url}: {msg}")
    except urllib.error.URLError as e:
        raise SystemExit(f"Nao consegui conectar em {url}: {e.reason}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="base do backend, ex.: https://goferias.onrender.com")
    ap.add_argument("--email", default="admin@goegrow.com.br")
    ap.add_argument("--senha", default="demo")
    ap.add_argument("--apply", action="store_true", help="corrige (PATCH). Sem isso: so lista.")
    ap.add_argument("--inseguro", action="store_true", help="ignora verificacao do certificado TLS")
    a = ap.parse_args()

    base = a.url.rstrip("/")
    ctx = ssl._create_unverified_context() if a.inseguro else None

    _, login = http(f"{base}/auth/login", method="POST",
                     body={"email": a.email, "senha": a.senha}, ctx=ctx)
    token = login["token"]
    print(f"Login OK como {login['nome']} ({login['papel']}) em {base}.")

    _, colabs = http(f"{base}/colaboradores", token=token, ctx=ctx)
    _, pers = http(f"{base}/periodos_aquisitivos", token=token, ctx=ctx)
    print(f"{len(colabs)} colaborador(es), {len(pers)} periodo(s) aquisitivo(s).\n")

    por_colab = {}
    for p in pers:
        por_colab.setdefault(p["colaborador_id"], []).append(p)
    for lst in por_colab.values():
        lst.sort(key=lambda p: p["inicio"], reverse=True)

    desligados = [c for c in colabs if c.get("desligamento")]
    print(f"{len(desligados)} colaborador(es) desligado(s) no cadastro.\n")

    quebrados, sem_periodo, ok = [], [], 0
    for c in desligados:
        lst = por_colab.get(c["id"], [])
        if not lst:
            sem_periodo.append(c)
            continue
        atual = lst[0]
        if atual["fim"] != c["desligamento"]:
            quebrados.append((c, atual))
        else:
            ok += 1

    modo = "APLICANDO (corrigindo)" if a.apply else "DRY-RUN (nada sera gravado)"
    print(f"=== {modo} ===")
    print(f"{len(quebrados)} com periodo inconsistente | {ok} ja corretos | "
          f"{len(sem_periodo)} sem nenhum periodo\n")

    for c, p in sorted(quebrados, key=lambda x: x[0]["nome"]):
        print(f"  {c['nome']:42s} desligado {c['desligamento']}  ·  periodo vai ate {p['fim']} "
              f"(devia ir ate {c['desligamento']})")
        if a.apply:
            http(f"{base}/periodos_aquisitivos/{p['id']}", token=token, method="PATCH",
                 body={"fim": c["desligamento"]}, ctx=ctx)

    if sem_periodo:
        print("\nDesligados SEM nenhum periodo aquisitivo cadastrado (revisar a mao):")
        for c in sem_periodo:
            print(f"  - {c['nome']} (desligado em {c['desligamento']})")

    if not a.apply and quebrados:
        print("\n>>> Isto foi um DRY-RUN. Para corrigir de verdade, rode de novo com --apply")
    print("\nOk.")


if __name__ == "__main__":
    main()
