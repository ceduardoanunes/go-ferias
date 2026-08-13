#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincroniza NOME, SETOR (departamento) e FUNÇÃO de colaboradores JÁ cadastrados
a partir de um dados.json (nome/função em Title Case, setor mapeado da aba).
Serve pra acertar quem entrou com texto em CAIXA ALTA ou departamento errado.

Casa por NOME normalizado (ignora acento/caixa/espaços), então "DAVI ALVES" no
banco casa com "Davi Alves" do arquivo. Só faz PATCH nos campos que diferem —
os demais não são tocados (PATCH parcial).

Uso:
  py corrigir_setor.py <dados.json> --url https://goferias.onrender.com \
     --email admin@goegrow.com.br --senha demo
  # ver o que mudaria, sem gravar:
  py corrigir_setor.py <dados.json> ... --dry-run
"""
import json, argparse, unicodedata, urllib.request, urllib.error

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
    ap.add_argument("dados", help="caminho do dados.json (com 'nome' e 'setor')")
    ap.add_argument("--url", required=True)
    ap.add_argument("--email", default="admin@goegrow.com.br")
    ap.add_argument("--senha", default="demo")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    base = a.url.rstrip("/")

    pessoas = json.load(open(a.dados, encoding="utf-8"))
    alvo = {norm(p["nome"]): {"nome": p["nome"], "departamento": p.get("setor"), "funcao": p.get("funcao")}
            for p in pessoas}

    _, login = http(f"{base}/auth/login", method="POST", body={"email": a.email, "senha": a.senha})
    tok = login["token"]
    print(f"Login OK como {login['nome']} ({login['papel']}).")

    _, cols = http(f"{base}/colaboradores", token=tok)
    mudou = 0
    for c in cols:
        d = alvo.get(norm(c["nome"]))
        if not d:
            continue
        patch, quais = {}, []
        if d["nome"] and d["nome"] != c.get("nome"):
            patch["nome"] = d["nome"]; quais.append(f"nome '{c.get('nome')}' -> '{d['nome']}'")
        if d["departamento"] and d["departamento"] != c.get("departamento"):
            patch["departamento"] = d["departamento"]; quais.append(f"setor '{c.get('departamento')}' -> '{d['departamento']}'")
        if d["funcao"] and d["funcao"] != c.get("funcao"):
            patch["funcao"] = d["funcao"]; quais.append(f"função '{c.get('funcao')}' -> '{d['funcao']}'")
        if not patch:
            continue
        if a.dry_run:
            print(f"[dry-run] {c['nome']}: " + "; ".join(quais))
        else:
            http(f"{base}/colaboradores/{c['id']}", token=tok, method="PATCH", body=patch)
            print(f"OK {c['nome']}: " + "; ".join(quais))
        mudou += 1
    verbo = "seriam" if a.dry_run else "foram"
    print(f"\n{mudou} colaborador(es) {verbo} atualizados.")

if __name__ == "__main__":
    main()
