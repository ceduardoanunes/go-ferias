#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2a leva de reconciliacao do RH (planilha `docs/colaboradores_por_departamento-alterado.xlsx`).
NAO mexe em admissao (ja foi feito pelo atualizar_admissao.py).

Faz 3 coisas contra o estado VIVO da API, casando por `ID (sistema)`:
  1) CAMPOS: atualiza funcao / unidade / regime onde a planilha difere.
  2) NOME: padroniza "Victor Bosich Rezende" -> "Victor Bosich".
  3) CNPJ: canoniza POR NUMERO em TODOS os colaboradores (idempotente):
        07.273.928/0001-99 -> Go! Editoracao
        37.406.102/0001-11 -> Go! Rec
        05.565.646/0001-30 -> Go! Midia
        61.734.337/0001-17 -> Digital ON   (conserta "ON/On Digital" e a anomalia
                                             "Go&Rec - 61.734.337" da Kim)
        "Sem CNPJ especificado" -> "Nao vinculado"
     (Em branco/None fica intacto. cnpj_desde: so grava se a planilha trouxer data;
      nunca limpa.)
  4) CRIA os colaboradores NOVOS (linhas sem ID), pulando quem ja existe pelo nome
     e a lista EXCLUIR_CRIAR (Julia/Nathalia/Mariana Dabes -> ja existem com ID).

Uso (dry-run):
  py atualizar_dados.py --url https://goferias.onrender.com --senha demo
Para gravar:
  py atualizar_dados.py --url https://goferias.onrender.com --senha demo --apply
Opcoes: --xlsx <caminho>  --email  --senha  --inseguro (TLS)
"""
import os, re, json, argparse, ssl, unicodedata, urllib.request, urllib.error

try:
    import openpyxl
except ImportError:
    raise SystemExit("Falta openpyxl. Instale com:  py -m pip install openpyxl")

ABAS_IGNORAR = {"Colaboradores", "Planilha1"}
COL = {"nome": "Nome", "email": "E-mail", "funcao": "Função", "departamento": "Departamento",
       "unidade": "Unidade", "regime": "Regime", "admissao": "Admissão",
       "desligamento": "Desligamento", "ativo": "Ativo", "cnpj": "CNPJ",
       "cnpj_desde": "CNPJ desde", "id": "ID (sistema)"}

# CNPJ canonico por numero
CNPJ_NOME = {
    "07.273.928/0001-99": "Go! Editoração",
    "37.406.102/0001-11": "Go! Rec",
    "05.565.646/0001-30": "Go! Mídia",
    "61.734.337/0001-17": "Digital ON",
}
NAO_VINCULADO = "Não vinculado"

# nomes que NAO devem ser criados como novos (ja existem com ID no sistema,
# mas vieram sem ID na planilha -> criar duplicaria)
EXCLUIR_CRIAR = {"julia mendes caria", "nathalia de souza ferreira", "mariana dabes"}

# padronizacoes de nome pontuais: normalizado -> nome final desejado.
# (Vazio: o nome INTEIRO fica no cadastro/perfil; abreviacao e so de EXIBICAO no app.)
RENOMEAR = {}


def norm(s):
    if s is None:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().lower()


def txt(v):
    if v is None:
        return None
    s = re.sub(r"\s+", " ", str(v)).strip()
    return s or None


def dia(v):
    if v is None:
        return None
    if hasattr(v, "date"):
        return v.date().isoformat()
    s = str(v).strip()
    return s or None


def boolat(v):
    if v is None:
        return None
    return norm(v).startswith("s")   # Sim -> True, Nao -> False


def canon_cnpj(raw):
    """Retorna o CNPJ canonico, ou None p/ 'nao mexer' (em branco)."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    low = norm(s)
    if "sem cnpj" in low or "nao vinc" in low or low == "nao vinculado":
        return NAO_VINCULADO
    m = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", s)
    if m:
        num = m.group(0)
        nome = CNPJ_NOME.get(num)
        return f"{nome} — {num}" if nome else s  # em-dash (U+2014), padrao do banco
    return NAO_VINCULADO


def http(url, token=None, method="GET", body=None, ctx=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, context=ctx) as r:
            t = r.read().decode("utf-8")
            return (r.status, json.loads(t) if t else None)
    except urllib.error.HTTPError as e:
        t = e.read().decode("utf-8", "ignore")
        try:
            msg = json.loads(t).get("message", t)
        except Exception:
            msg = t
        raise SystemExit(f"Erro HTTP {e.code} em {method} {url}: {msg}")
    except urllib.error.URLError as e:
        raise SystemExit(f"Nao consegui conectar em {url}: {e.reason}")


def ler_planilha(caminho):
    wb = openpyxl.load_workbook(caminho, read_only=True, data_only=True)
    com_id, sem_id = {}, []
    for aba in wb.sheetnames:
        if aba in ABAS_IGNORAR:
            continue
        ws = wb[aba]
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            continue
        idx = {h: i for i, h in enumerate(rows[0])}
        if COL["id"] not in idx:
            continue
        for r in rows[1:]:
            if not any(x is not None for x in r):
                continue
            g = lambda k: (r[idx[COL[k]]] if COL[k] in idx else None)
            reg = {"nome": txt(g("nome")), "email": txt(g("email")), "funcao": txt(g("funcao")),
                   "departamento": txt(g("departamento")) or aba, "unidade": txt(g("unidade")),
                   "regime": txt(g("regime")), "admissao": dia(g("admissao")),
                   "desligamento": dia(g("desligamento")), "ativo": boolat(g("ativo")),
                   "cnpj": txt(g("cnpj")), "cnpj_desde": dia(g("cnpj_desde")), "aba": aba}
            rid = g("id")
            if rid:
                com_id[rid] = reg
            else:
                sem_id.append(reg)
    return com_id, sem_id


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", default=os.path.join(here, "..", "..", "docs",
                    "colaboradores_por_departamento-alterado.xlsx"))
    ap.add_argument("--url", required=True)
    ap.add_argument("--email", default="admin@goegrow.com.br")
    ap.add_argument("--senha", default="demo")
    ap.add_argument("--apply", action="store_true", help="grava. Sem isso: dry-run.")
    ap.add_argument("--inseguro", action="store_true")
    a = ap.parse_args()

    if not os.path.exists(a.xlsx):
        raise SystemExit(f"Planilha nao encontrada: {a.xlsx}")
    base = a.url.rstrip("/")
    ctx = ssl._create_unverified_context() if a.inseguro else None

    com_id, sem_id = ler_planilha(a.xlsx)
    print(f"Planilha: {len(com_id)} com ID | {len(sem_id)} sem ID (candidatos a novos).\n")

    _, login = http(f"{base}/auth/login", method="POST",
                    body={"email": a.email, "senha": a.senha}, ctx=ctx)
    token = login["token"]
    print(f"Login OK como {login['nome']} ({login['papel']}) em {base}.")
    _, atuais = http(f"{base}/colaboradores", token=token, ctx=ctx)
    vivo = {c["id"]: c for c in (atuais or [])}
    por_nome = {norm(c["nome"]): c for c in (atuais or [])}
    print(f"{len(vivo)} colaborador(es) no sistema.\n")

    # ---- 1/2/3) updates por ID (campos + nome + cnpj/cnpj_desde) ----
    CAMPOS = ["funcao", "unidade", "regime"]
    updates = []   # (id, nome, {campo: (de, para)})
    for cid, c in vivo.items():
        s = com_id.get(cid)                      # linha da planilha (pode nao existir)
        mud = {}
        for campo in CAMPOS:
            if s and s.get(campo) and s[campo] != (txt(c.get(campo))):
                mud[campo] = (c.get(campo), s[campo])
        # nome: padronizacao pontual
        alvo_nome = RENOMEAR.get(norm(c["nome"]))
        if alvo_nome and alvo_nome != c["nome"]:
            mud["nome"] = (c["nome"], alvo_nome)
        # cnpj: canoniza por numero (planilha manda; senao usa o vivo). "em tudo".
        base_cnpj = (s["cnpj"] if (s and s.get("cnpj")) else c.get("cnpj"))
        novo_cnpj = canon_cnpj(base_cnpj)
        if novo_cnpj is not None and novo_cnpj != (txt(c.get("cnpj"))):
            mud["cnpj"] = (c.get("cnpj"), novo_cnpj)
        # cnpj_desde: so grava se planilha trouxer data; nunca limpa
        if s and s.get("cnpj_desde") and s["cnpj_desde"] != (c.get("cnpj_desde")):
            mud["cnpj_desde"] = (c.get("cnpj_desde"), s["cnpj_desde"])
        if mud:
            updates.append((cid, c["nome"], mud))

    # ---- 4) novos ----
    criar, pular_novos = [], []
    for reg in sem_id:
        n = norm(reg["nome"])
        if n in EXCLUIR_CRIAR or n in por_nome:
            pular_novos.append((reg["nome"], reg["aba"],
                                "ja existe/duplicata" if n in por_nome else "excluir_criar"))
            continue
        criar.append(reg)

    modo = "APLICANDO" if a.apply else "DRY-RUN (nada sera gravado)"
    print(f"=== {modo} ===")
    print(f"{len(updates)} colaborador(es) com update de campo/cnpj | "
          f"{len(criar)} novo(s) a criar | {len(pular_novos)} novo(s) pulado(s).\n")

    print("--- UPDATES ---")
    for cid, nome, mud in sorted(updates, key=lambda x: x[1]):
        partes = "; ".join(f"{k}: [{d}]->[{p}]" for k, (d, p) in mud.items())
        print(f"  {nome:42s} {partes}")
        if a.apply:
            body = {k: p for k, (d, p) in mud.items()}
            http(f"{base}/colaboradores/{cid}", token=token, method="PATCH", body=body, ctx=ctx)

    print("\n--- NOVOS ---")
    for reg in sorted(criar, key=lambda x: x["nome"]):
        print(f"  + {reg['nome']:38s} {reg['aba']:14s} adm={reg['admissao']} "
              f"regime={reg['regime']} cnpj={canon_cnpj(reg['cnpj'])}")
        if a.apply:
            if not reg["admissao"]:
                print(f"    ! sem admissao -> PULADO (API exige). Lancar a mao.")
                continue
            body = {"nome": reg["nome"], "email": reg["email"], "funcao": reg["funcao"] or "",
                    "departamento": reg["departamento"], "unidade": reg["unidade"] or "",
                    "regime": reg["regime"] or "CLT", "admissao": reg["admissao"],
                    "cnpj": canon_cnpj(reg["cnpj"]),
                    "ativo": True if reg["ativo"] is None else reg["ativo"]}
            http(f"{base}/colaboradores", token=token, method="POST", body=body, ctx=ctx)

    if pular_novos:
        print("\n--- NOVOS PULADOS (nao criados) ---")
        for nome, aba, motivo in pular_novos:
            print(f"  - {nome} ({aba}) [{motivo}]")

    if not a.apply and (updates or criar):
        print("\n>>> DRY-RUN. Para gravar: rode de novo com --apply")
    print("\nOk.")


if __name__ == "__main__":
    main()
