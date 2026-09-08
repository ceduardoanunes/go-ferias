# Ferramentas de dados — Go Férias!

Scripts Python que falam com a API do backend (não mexem direto no Postgres).
Servem pra **migrar entre servidores** e pra **auditar/corrigir dado real**.

## O que tem aqui hoje

| Script | Pra quê |
|---|---|
| `baixar_do_render.py` | Baixa TODO o banco (pela API, só leitura) pra `saida_render/*.json`. |
| `carregar_no_local.py` | Lê `saida_render/` e recria tudo num servidor novo (remapeia IDs). |
| `auditar_desligamento_periodo.py` | Acha (e opcionalmente corrige) colaboradores desligados cujo período aquisitivo não fechou na data certa. |

Ver **`../../PARA-O-TI.md`** pro passo a passo completo de migração (esse é
o motivo desses dois primeiros scripts existirem: tirar os dados do Render
antes dele expirar e recriar no servidor da empresa).

## `historico-importacao-form18/`

A importação **original** dos ~120 colaboradores, a partir da planilha do RH
(`OFF/MODELO PLANILHA FÉRIAS.xlsx` e as abas por setor) — já **concluída**,
os dados já estão no sistema. Fica guardado só de referência (scripts de
reconciliação pontual: admissão, CNPJ/setor, exclusão de duplicata). Não é
preciso mexer aqui de novo, a menos que apareça uma divergência parecida.

## ⚠️ Privacidade

`saida_render/` e qualquer coisa em `historico-importacao-form18/saida_*`
contêm **dados pessoais reais** de colaboradores. O `.gitignore` já bloqueia
essas pastas, `*.xlsx`, `*.pdf` e `*.local.*` — **nunca force o commit
delas**. Pra levar esses dados pra outra máquina (ex.: mandar pro TI), copie
a pasta por fora do git (zip, pendrive, etc.), nunca pelo GitHub.
