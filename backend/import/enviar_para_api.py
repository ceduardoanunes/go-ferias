#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carrega o dados.json (gerado por importar_planilha.py) no backend Node/Prisma
ENVIANDO PELA API — sem precisar de Node, psql ou Prisma na sua máquina.

Fluxo:
  1) importar_planilha.py  → gera dados.json (parte estruturada, tabela CONFIÁVEL)
  2) revise o REVISAR.txt   → resolva os casos de negócio (MP, licença, banco de horas)
  3) este script            → faz login e cria colaboradores/períodos/férias/folgas

Uso:
  py enviar_para_api.py <dados.json> --url https://SEU-APP.onrender.com \\
     --email admin@goegrow.com.br --senha demo

Opções:
  --dry-run   Só mostra o que faria, sem enviar nada.
  --url       Base do backend (ex.: https://goferias.onrender.com). Obrigatório.
  --email     Login de admin (padrão: admin@goegrow.com.br).
  --senha     Senha do admin (padrão: demo).

Segurança: é SEGURO re-rodar — colaboradores cujo NOME já existe são PULADOS,
então não duplica. (A planilha real tem dados pessoais: não suba o .xlsx no Git.)
"""
import sys, os, json, argparse, urllib.request, urllib.error

# empresa (coluna da planilha) é o SETOR → vira "departamento".
# A planilha não traz unidade nem regime; usamos padrões (ajustáveis abaixo).
UNIDADE_PADRAO = ""       # a planilha não informa; preencha depois no app se precisar
REGIME_PADRAO = "CLT"

def http(url, token=None, method="GET", body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req) as r:
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
        raise SystemExit(f"Não consegui conectar em {url}: {e.reason}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dados", help="caminho do dados.json")
    ap.add_argument("--url", required=True, help="base do backend, ex.: https://goferias.onrender.com")
    ap.add_argument("--email", default="admin@goegrow.com.br")
    ap.add_argument("--senha", default="demo")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    base = a.url.rstrip("/")
    with open(a.dados, encoding="utf-8") as f:
        pessoas = json.load(f)

    print(f"{len(pessoas)} colaborador(es) no arquivo.")

    if a.dry_run:
        token, existentes = None, set()
        print("[dry-run] sem login, sem envio.")
    else:
        _, login = http(f"{base}/auth/login", method="POST",
                        body={"email": a.email, "senha": a.senha})
        token = login["token"]
        print(f"Login OK como {login['nome']} ({login['papel']}).")
        _, atuais = http(f"{base}/colaboradores", token=token)
        existentes = {c["nome"].strip().upper() for c in (atuais or [])}
        print(f"{len(existentes)} colaborador(es) já no sistema (serão pulados se repetirem).")

    criados = pulados = nper = nfer = nfol = 0
    for p in pessoas:
        nome = p["nome"].strip()
        if nome.upper() in existentes:
            pulados += 1
            print(f"  - pula (ja existe): {nome}")
            continue

        payload_colab = {
            "nome": nome,
            "email": None,
            "funcao": p.get("funcao") or "",
            "departamento": p.get("empresa") or "",   # empresa = setor → departamento
            "unidade": UNIDADE_PADRAO,
            "regime": REGIME_PADRAO,
            "admissao": p.get("admissao"),
            "ativo": True,
        }
        if a.dry_run:
            tot_f = sum(len(x["ferias"]) for x in p["periodos"])
            tot_g = sum(len(x["folgas"]) for x in p["periodos"])
            print(f"  + {nome}  (períodos:{len(p['periodos'])} férias:{tot_f} folgas:{tot_g})")
            criados += 1
            continue

        _, colab = http(f"{base}/colaboradores", token=token, method="POST", body=payload_colab)
        cid = colab["id"]
        criados += 1
        for per in p["periodos"]:
            _, pr = http(f"{base}/periodos_aquisitivos", token=token, method="POST", body={
                "colaborador_id": cid,
                "inicio": per["inicio"], "fim": per["fim"],
                "situacao": per.get("situacao") or "acumulando",
            })
            pid = pr["id"]; nper += 1
            for fx in per["ferias"]:
                http(f"{base}/ferias_oficiais", token=token, method="POST", body={
                    "periodo_id": pid, "inicio": fx["inicio"], "fim": fx["fim"],
                    "dias": fx["dias"], "obs": "",
                }); nfer += 1
            for fg in per["folgas"]:
                http(f"{base}/folgas", token=token, method="POST", body={
                    "periodo_id": pid, "inicio": fg["inicio"], "fim": fg["fim"],
                    "dias": fg["dias"], "obs": fg.get("obs", ""),
                }); nfol += 1
        print(f"  OK {nome}  ->  periodos:{len(p['periodos'])}")

    print("\nResumo:")
    print(f"  colaboradores criados: {criados}   pulados: {pulados}")
    if not a.dry_run:
        print(f"  periodos: {nper}   ferias: {nfer}   folgas: {nfol}")
    print("\ni) Folgas com regra de negocio ficaram no REVISAR.txt - lancar a mao no app.")

if __name__ == "__main__":
    main()
