#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
So leitura: investiga por que colaboradores somem do servidor.
Mostra quem existe hoje, desde quando o banco tem historico (auditoria mais
antiga) e toda exclusao de colaborador registrada.

  py diagnostico_sumico.py --url http://192.172.116.2:3000 --email ... --senha ...
"""
import argparse, json, urllib.request
from collections import Counter

def http(url, token=None, method="GET", body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req) as r:
        txt = r.read().decode("utf-8")
        return json.loads(txt) if txt else None

ap = argparse.ArgumentParser()
ap.add_argument("--url", required=True)
ap.add_argument("--email", required=True)
ap.add_argument("--senha", required=True)
a = ap.parse_args()
base = a.url.rstrip("/")

token = http(f"{base}/auth/login", method="POST", body={"email": a.email, "senha": a.senha})["token"]

colabs = http(f"{base}/colaboradores", token=token)
print(f"== Colaboradores hoje: {len(colabs)}")
for c in colabs:
    print(f"   - {c['nome']} ({c.get('departamento')}, unidade {c.get('unidade')}) ativo={c.get('ativo')} desligamento={c.get('desligamento')}")

aud = http(f"{base}/auditoria?limit=2000", token=token)
print(f"\n== Auditoria: {len(aud)} registros")
if aud:
    ts = sorted(x.get("ts") or "" for x in aud)
    print(f"   mais antigo: {ts[0]}   mais recente: {ts[-1]}")
    print("   acoes:", dict(Counter((x.get("acao"), x.get("tabela")) for x in aud)))

    print("\n== Exclusoes de colaborador:")
    exc = [x for x in aud if x.get("acao") == "excluir" and x.get("tabela") == "colaboradores"]
    for x in sorted(exc, key=lambda x: x.get("ts") or ""):
        nome = (x.get("dados_antes") or {}).get("nome", "?")
        print(f"   {x.get('ts')}  {nome}  por {x.get('usuario_nome')}")
    if not exc:
        print("   nenhuma")

    print("\n== Cadastros de colaborador:")
    for x in sorted((x for x in aud if x.get("acao") == "inserir" and x.get("tabela") == "colaboradores"),
                    key=lambda x: x.get("ts") or ""):
        nome = (x.get("dados_depois") or {}).get("nome", "?")
        print(f"   {x.get('ts')}  {nome}  por {x.get('usuario_nome')}")

    print("\n== Edicoes de colaborador:")
    for x in sorted((x for x in aud if x.get("acao") == "atualizar" and x.get("tabela") == "colaboradores"),
                    key=lambda x: x.get("ts") or ""):
        antes, depois = x.get("dados_antes") or {}, x.get("dados_depois") or {}
        mud = {k: (antes.get(k), depois.get(k)) for k in depois if antes.get(k) != depois.get(k)}
        print(f"   {x.get('ts')}  {depois.get('nome', '?')}  por {x.get('usuario_nome')}: {mud}")

    print("\n== Ultimos logins:")
    for x in [x for x in aud if x.get("acao") == "login"][:10]:
        print(f"   {x.get('ts')}  {x.get('usuario_nome')}")
