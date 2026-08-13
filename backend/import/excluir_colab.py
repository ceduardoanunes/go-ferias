#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exclui colaboradores por NOME, via API — para limpar demo/teste.
(O app só tem "inativar"; excluir de vez é só por aqui.)

Uso:
  py excluir_colab.py --url https://goferias.onrender.com \
     --email admin@goegrow.com.br --senha demo \
     "Carlos Eduardo Nunes" "Amanda Guerra de Castro Pires"

  # ver o que faria, sem excluir:
  py excluir_colab.py ... --dry-run "Nome"

⚠️ Exclui em CASCATA os períodos/férias/folgas do colaborador. Irreversível.
   Casamento por nome é exato (ignora acento/caixa/espaços nas pontas).
"""
import sys, json, argparse, unicodedata, urllib.request, urllib.error

def norm(s):
    s = unicodedata.normalize('NFD', str(s)).encode('ascii', 'ignore').decode()
    return s.strip().upper()

def http(url, token=None, method="GET", body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            t = r.read().decode("utf-8")
            return r.status, (json.loads(t) if t else None)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code} em {method} {url}: {e.read().decode('utf-8','ignore')[:200]}")
    except urllib.error.URLError as e:
        raise SystemExit(f"Não consegui conectar em {url}: {e.reason}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nomes", nargs="+", help="nomes exatos a excluir")
    ap.add_argument("--url", required=True)
    ap.add_argument("--email", default="admin@goegrow.com.br")
    ap.add_argument("--senha", default="demo")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    base = a.url.rstrip("/")

    _, login = http(f"{base}/auth/login", method="POST", body={"email": a.email, "senha": a.senha})
    tok = login["token"]
    print(f"Login OK como {login['nome']} ({login['papel']}).")

    _, cols = http(f"{base}/colaboradores", token=tok)
    alvo = {norm(n) for n in a.nomes}
    achados = [c for c in cols if norm(c["nome"]) in alvo]
    if not achados:
        print("Nenhum dos nomes informados foi encontrado.")
        return
    for c in achados:
        if a.dry_run:
            print(f"[dry-run] excluiria: {c['nome']}  (id={c['id']})")
        else:
            st, _ = http(f"{base}/colaboradores/{c['id']}", token=tok, method="DELETE")
            print(f"excluído: {c['nome']}  ->  HTTP {st}")
    nao = alvo - {norm(c["nome"]) for c in achados}
    if nao:
        print("Não encontrados:", ", ".join(sorted(nao)))

if __name__ == "__main__":
    main()
