#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apaga TODOS os colaboradores de um backend remoto (via API), pra limpar uma
carga parcial antes de recarregar do zero. Cascata (periodos/ferias/folgas/
notas ligados a cada colaborador) fica a cargo do banco/API.

Uso:
  py limpar_colaboradores_remoto.py --url http://192.172.116.2:3000 \
     --email admin@goegrow.com.br --senha demo
"""
import argparse, json, urllib.request, urllib.error

def http(url, token=None, method="GET", body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req) as r:
        txt = r.read().decode("utf-8")
        return (r.status, json.loads(txt) if txt else None)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--email", default="admin@goegrow.com.br")
    ap.add_argument("--senha", default="demo")
    a = ap.parse_args()
    base = a.url.rstrip("/")

    _, login = http(f"{base}/auth/login", method="POST", body={"email": a.email, "senha": a.senha})
    token = login["token"]
    print(f"Login OK como {login['nome']} ({login['papel']}).")

    _, colabs = http(f"{base}/colaboradores", token=token)
    print(f"Encontrados {len(colabs)} colaboradores. Apagando...")
    ok = 0
    for c in colabs:
        try:
            http(f"{base}/colaboradores/{c['id']}", token=token, method="DELETE")
            ok += 1
        except urllib.error.HTTPError as e:
            print(f"  falha id={c['id']} ({c.get('nome')}): {e.code}")
    print(f"Apagados: {ok}/{len(colabs)}")

if __name__ == "__main__":
    main()
