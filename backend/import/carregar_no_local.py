#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carrega o snapshot do Render (gerado por baixar_do_render.py) num backend
Node/Prisma LOCAL, PELA API. Recria colaboradores/periodos/ferias/folgas/notas
remapeando os UUIDs (os IDs novos sao gerados pelo banco local).

NAO migra: usuarios (eram demo -> recrie os logins reais no app) nem auditoria
(historico). Solicitacoes ficam de fora por padrao (a unica era um TESTE);
use --com-solicitacoes se quiser traze-las como 'pendente'.

Uso (com a stack local no ar em http://localhost:3000):
  py carregar_no_local.py --url http://localhost:3000 \\
     --email admin@goegrow.com.br --senha demo

  --entrada   pasta com o snapshot (padrao: saida_render)
  --dry-run   mostra o que faria, sem enviar
  --com-solicitacoes  tambem cria as solicitacoes (status vira 'pendente')
"""
import os, json, argparse, ssl, urllib.request, urllib.error

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

def carrega(pasta, nome):
    caminho = os.path.join(pasta, f"{nome}.json")
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="base do backend local, ex.: http://localhost:3000")
    ap.add_argument("--email", default="admin@goegrow.com.br")
    ap.add_argument("--senha", default="demo")
    ap.add_argument("--entrada", default="saida_render")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--com-solicitacoes", action="store_true")
    ap.add_argument("--inseguro", action="store_true")
    a = ap.parse_args()

    base = a.url.rstrip("/")
    ctx = ssl._create_unverified_context() if a.inseguro else None

    colabs  = carrega(a.entrada, "colaboradores")
    periodos = carrega(a.entrada, "periodos_aquisitivos")
    ferias  = carrega(a.entrada, "ferias_oficiais")
    folgas  = carrega(a.entrada, "folgas")
    notas   = carrega(a.entrada, "notas")
    solic   = carrega(a.entrada, "solicitacoes") if a.com_solicitacoes else []

    print(f"Snapshot: {len(colabs)} colaboradores, {len(periodos)} periodos, "
          f"{len(ferias)} ferias, {len(folgas)} folgas, {len(notas)} notas.")

    if a.dry_run:
        print("[dry-run] nada foi enviado.")
        return

    # login local
    _, login = http(f"{base}/auth/login", method="POST",
                    body={"email": a.email, "senha": a.senha}, ctx=ctx)
    token = login["token"]
    print(f"Login OK como {login['nome']} ({login['papel']}).")

    # base ja tem colaboradores? avisa (evita duplicar numa re-execucao)
    _, atuais = http(f"{base}/colaboradores", token=token, ctx=ctx)
    if atuais:
        nomes = {c["nome"].strip().upper() for c in atuais}
        # remove os de exemplo do seed pra nao atrapalhar a contagem
        if len(atuais) > 2:
            raise SystemExit(
                f"A base local ja tem {len(atuais)} colaboradores. Este script e "
                f"para uma base VAZIA (so o seed). Zere o banco antes de recarregar "
                f"(docker compose down -v && up -d) para nao duplicar.")

    def post(rota, payload):
        _, r = http(f"{base}/{rota}", token=token, method="POST", body=payload, ctx=ctx)
        return r

    map_colab = {}   # id antigo -> id novo
    map_per   = {}

    # 1) colaboradores
    for c in colabs:
        novo = post("colaboradores", {
            "nome": c["nome"], "email": c.get("email"),
            "funcao": c["funcao"], "departamento": c["departamento"],
            "unidade": c["unidade"], "regime": c["regime"],
            "admissao": c["admissao"], "foto": c.get("foto"),
            "ativo": c.get("ativo", True),
        })
        map_colab[c["id"]] = novo["id"]
    print(f"  colaboradores: {len(map_colab)} criados")

    # 2) periodos
    for p in periodos:
        cid = map_colab.get(p["colaborador_id"])
        if not cid:
            continue
        novo = post("periodos_aquisitivos", {
            "colaborador_id": cid, "inicio": p["inicio"], "fim": p["fim"],
            "situacao": p.get("situacao", "acumulando"), "pago_em": p.get("pago_em"),
        })
        map_per[p["id"]] = novo["id"]
    print(f"  periodos: {len(map_per)} criados")

    # 3) ferias
    nf = 0
    for x in ferias:
        pid = map_per.get(x["periodo_id"])
        if not pid:
            continue
        post("ferias_oficiais", {
            "periodo_id": pid, "inicio": x["inicio"], "fim": x["fim"],
            "dias": x["dias"], "obs": x.get("obs", ""),
        }); nf += 1
    print(f"  ferias_oficiais: {nf} criados")

    # 4) folgas
    ng = 0
    for x in folgas:
        pid = map_per.get(x["periodo_id"])
        if not pid:
            continue
        post("folgas", {
            "periodo_id": pid, "inicio": x["inicio"], "fim": x["fim"],
            "dias": x["dias"], "obs": x.get("obs", ""),
        }); ng += 1
    print(f"  folgas: {ng} criadas")

    # 5) notas
    nn = 0
    for n in notas:
        cid = map_colab.get(n["colaborador_id"])
        if not cid:
            continue
        post("notas", {
            "colaborador_id": cid, "periodo_id": map_per.get(n.get("periodo_id")),
            "categoria": n.get("categoria", "outro"), "texto": n.get("texto", ""),
            "data": n.get("data"),
        }); nn += 1
    print(f"  notas: {nn} criadas")

    # 6) solicitacoes (opcional)
    ns = 0
    for s in solic:
        post("solicitacoes", {
            "colaborador_id": map_colab.get(s.get("colaborador_id")),
            "nome": s.get("nome", ""), "tipo": s.get("tipo", "folga"),
            "inicio": s["inicio"], "fim": s["fim"], "dias": s["dias"],
            "motivo": s.get("motivo", ""), "aval_coordenador": s.get("aval_coordenador", False),
        }); ns += 1
    if a.com_solicitacoes:
        print(f"  solicitacoes: {ns} criadas")

    print("\nPronto. Dados reais carregados no backend local.")
    print("Usuarios/senhas NAO vieram (eram demo) - crie os logins reais no app.")

if __name__ == "__main__":
    main()
