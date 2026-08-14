# Importador da planilha do RH → backend

Converte a planilha de férias (formato do `OFF/MODELO PLANILHA FÉRIAS.xlsx`) nos
dados do sistema. Foi **testado contra o modelo de 2 pessoas** e reproduz o
Carlos e a Amanda exatamente como já estão no sistema (parte estruturada).

## Como rodar

```bash
cd backend/import
pip3 install openpyxl          # uma vez
python3 importar_planilha.py "caminho/para/PLANILHA-DOS-120.xlsx" saida
```

Gera na pasta `saida/`:
- **`dados.json`** — tudo que foi extraído (para conferência).
- **`inserts.sql`** — comandos SQL prontos para carregar no banco.
- **`REVISAR.txt`** — a lista curta de folgas que precisam de olho humano.

## O que confiar × o que revisar

| Parte | Confiança | Observação |
|-------|-----------|------------|
| Nome, empresa, função, admissão | ✅ Alta | direto das colunas |
| Períodos aquisitivos + situação | ✅ Alta | `FÉRIAS NÃO VENCIDAS`→acumulando, `PAGO`→pago, `PAGTO PROGRAMADO`→programado |
| Férias contábeis (gozos de 30 dias) | ✅ Alta | datas e nº de dias conferem com o feito à mão |
| **Folgas (coluna de texto livre)** | ⚠️ **Best-effort** | pega as datas simples; **marca para revisão** os casos de negócio (venda pela MP, licença, banco de horas) |

> **Regra de ouro:** abra o `REVISAR.txt` e resolva cada item antes de considerar
> a migração pronta. No modelo, os itens marcados foram coisas como
> "8 DIAS VENDEU PELA MP", "LICENÇA MATERNIDADE", "banco 4 horas — descontar…" —
> decisões que só o RH sabe tomar.

## Carregar no banco

### ✅ Backend Node/Prisma (o que está no Render) — use este
Envie o `dados.json` **pela API** com o `enviar_para_api.py`. Não precisa de Node,
psql nem Prisma na sua máquina — só Python (que o parser já usa):

```bash
py enviar_para_api.py saida/dados.json \
   --url https://SEU-APP.onrender.com \
   --email admin@goegrow.com.br --senha demo
```

- `--dry-run` mostra o que faria sem enviar nada (teste antes).
- É **seguro re-rodar**: colaboradores cujo nome já existe são **pulados** (não duplica).
- `empresa` (setor da planilha) vira `departamento`; `unidade`/`regime` usam padrões
  ajustáveis no topo do script.

> **Notas de RH** (venda pela MP, licença, pandemia/banco de horas) são extraídas
> automaticamente do texto livre e **enviadas** como Notas do colaborador (aba Notas
> na ficha, vinculadas ao período). Editáveis/excluíveis no app. Os demais itens do
> **REVISAR.txt** (inconsistências de data, casos ambíguos) seguem para revisão à mão.

### Backend legado (PostgREST em `backend/sql/`) — só se ainda usar aquele
O `inserts.sql` gerado é para o schema `api.` do PostgREST **antigo**, e **não**
funciona no backend Node/Prisma. Se ainda usar o legado: copie o `inserts.sql`
(renomeado, ex. `07_dados_reais.sql`) para `backend/sql/`, ou rode via `psql`.

## ⚠️ Privacidade

A planilha dos 120 e as saídas contêm **dados pessoais reais**. O `.gitignore`
desta pasta já bloqueia `*.xlsx` e a pasta `saida/` — **não force o commit deles**.
