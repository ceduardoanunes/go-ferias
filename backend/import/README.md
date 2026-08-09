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

Depois de revisar, há duas formas:
1. **Junto com a subida do backend:** copie o `inserts.sql` (renomeado, ex.
   `07_dados_reais.sql`) para `backend/sql/` — ele roda na primeira inicialização.
   (Remova/ajuste o `04_seed.sql` para não misturar demo com dado real.)
2. **Com o backend já no ar:** rode o `inserts.sql` via `psql` no container do
   Postgres.

## ⚠️ Privacidade

A planilha dos 120 e as saídas contêm **dados pessoais reais**. O `.gitignore`
desta pasta já bloqueia `*.xlsx` e a pasta `saida/` — **não force o commit deles**.
