#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baixa TODO o banco do backend Node/Prisma (o que está no Render) PELA API,
sem precisar da senha do Postgres nem de psql/pg_dump. Espelho do
enviar_para_api.py, mas no sentido inverso (puxa em vez de enviar).

Uso:
  py baixar_do_render.py --url https://goferias.onrender.com \\
     --email admin@goegrow.com.br --senha demo

Gera na pasta saida_render/ (já ignorada pelo .gitignore):
  - banco_render.json      -> tudo junto (1 objeto com todas as tabelas)
  - <tabela>.json          -> um arquivo por tabela (colaboradores, folgas, ...)

Observações:
  * A API NÃO devolve o hash das senhas dos usuários (por segurança). O arquivo
    usuarios.json traz nome/email/papel, mas sem senha — logins têm de ser
    recriados no destino (ou use pg_dump se precisar das senhas exatas).
  * É só leitura: não altera nada no Render.
  * Se der erro de certificado SSL no Windows, rode com o certifi:
      set SSL_CERT_FILE=  &&  py -m certifi   (pega o caminho)
    ou:  py baixar_do_render.py ... --inseguro   (ignora verificação TLS)
"""
import sys, os, json, argparse, ssl, urllib.request, urllib.error

# Tabelas expostas pela API (ver server/src/index.js). Ordem = dependência
# (colaboradores antes de períodos, etc.), útil para recarregar depois.
TABELAS = [
    "colaboradores",
    "periodos_aquisitivos",
    "ferias_oficiais",
    "folgas",
    "notas",
    "solicitacoes",
    "usuarios",
    "auditoria",
]

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
    ap.add_argument("--saida", default="saida_render", help="pasta de saida")
    ap.add_argument("--inseguro", action="store_true", help="ignora verificacao do certificado TLS")
    a = ap.parse_args()

    base = a.url.rstrip("/")
    ctx = ssl._create_unverified_context() if a.inseguro else None
    os.makedirs(a.saida, exist_ok=True)

    # 1) login -> token
    _, login = http(f"{base}/auth/login", method="POST",
                    body={"email": a.email, "senha": a.senha}, ctx=ctx)
    token = login["token"]
    print(f"Login OK como {login['nome']} ({login['papel']}).")

    # 2) baixa cada tabela
    banco = {}
    for t in TABELAS:
        rota = f"{base}/{t}"
        if t == "auditoria":
            rota += "?limit=100000"   # a rota de auditoria pagina por limit
        _, linhas = http(rota, token=token, ctx=ctx)
        linhas = linhas or []
        banco[t] = linhas
        caminho = os.path.join(a.saida, f"{t}.json")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(linhas, f, ensure_ascii=False, indent=2)
        print(f"  {t:22s} {len(linhas):6d} registro(s) -> {caminho}")

    # 3) tudo junto
    tudo = os.path.join(a.saida, "banco_render.json")
    with open(tudo, "w", encoding="utf-8") as f:
        json.dump(banco, f, ensure_ascii=False, indent=2)
    print(f"\nSnapshot completo em {tudo}")
    print("Pronto. (Somente leitura: nada foi alterado no Render.)")

if __name__ == "__main__":
    main()
