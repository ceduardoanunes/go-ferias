# Migração FORM 18 — status e pendências

Migração dos dados reais do RH (`FORM 18 - CONTROLE DE FÉRIAS ...xlsx`) para o app no Render, feita **aba por aba** (cada aba = 1 setor), conferindo no app antes de seguir. Status da **1ª inserção** (aba VÍDEO).

> ⚠️ A planilha `.xlsx` tem dados pessoais e **não é versionada** (gitignore).
> Detalhe com **nomes** fica em `PENDENCIAS-DETALHE.local.md` (local, gitignorado). Os nomes das pendências também saem nos `REVISAR.txt` / `PENDENTES.txt` gerados a cada import.

Ambiente: Render `https://goferias.onrender.com` · admin `admin@goegrow.com.br` / `demo`.

---

## ✅ Concluído nesta 1ª inserção

- **Demo de teste apagada** (2 registros).
- **Aba VÍDEO importada 100%** → 4 colaboradores no setor **Vídeo**, com nome/função em Title Case, períodos/férias/folgas limpos.
- Pipeline de import maduro e validado (scripts abaixo).
- Bug do app corrigido: campo **Unidade** virou editável (datalist) + unidades padrão.
- Cards do dashboard passam a abrir a **aba certa** (folga/férias) no relatório e na agenda.

### Scripts (`backend/import/`, rodar com `py`; escritas em produção rodadas com `!`)
1. `importar_form18.py "<xlsx>" <saida> --aba "NOME"` → gera `dados.json` (+ `REVISAR.txt`, `PENDENTES.txt`).
2. `enviar_para_api.py <dados.json> --url ... --senha demo` → cria via API (pula nome já existente).
3. `corrigir_setor.py <dados.json> ...` → sincroniza nome/setor/função de quem já entrou.
4. `excluir_colab.py "Nome" ... --url ...` → exclui por nome (limpeza).

> Em casa: `git pull` traz app + scripts. **A planilha `.xlsx` NÃO vem pelo git** (gitignore) — use sua própria cópia (Drive/RH).

---

## ⏳ Abas ainda NÃO importadas (9)

| Aba | Setor do app | A enviar | Períodos | Férias | Folgas | Revisar |
|---|---|--:|--:|--:|--:|--:|
| ATENDIMENTO OFF | Atendimento OFF | 2 | 10 | 12 | 31 | 4 |
| ADM | Administrativo | 9 | 25 | 12 | 88 | 4 |
| ATENDIMENTO CORPORATIVO | Corporativo | 9 | 34 | 31 | 123 | 7 |
| SUPERVISÃO | Coordenação | 8 | 42 | 32 | 149 | 21 |
| INBOUND | Inbound | 8 | 36 | 20 | 171 | 17 |
| REDAÇÃO-REVISÃO | Redação + Revisão (por função) | 5 | 25 | 15 | 76 | 10 |
| CRIAÇÃO | Criação | 26 | 77 | 65 | 313 | 25 |
| ESTAGIÁRIOS | Estagiários | 11 | 19 | 0 | 15 | 4 |
| ATEND. SOCIAL MIDIA | Digital | 17 | 52 | 21 | 169 | 12 |

- **Sugestão de ordem:** começar pelas menores/limpas (**Atendimento OFF**, **ADM**) e deixar **SOCIAL MÍDIA (→ Digital)** por último — teve **migração de CNPJ em 2025**, então terá muitos períodos duplicados/readmissão pra reconciliar.
- `BAYER, NEXA E NISSAN` está vazia → **ignorada** (aba de cliente/nota).

---

## ⏳ Pendências de dados (padrões, sem nomes)

### 1. Pessoas sem admissão (NÃO entram — API exige admissão; lançar à mão)
- **3 pessoas** no arquivo completo: Criação ×2, Estagiários ×1. Nomes no `PENDENTES.txt` gerado no import.

### 2. Folgas a revisar (não entram no automático — ~106 no arquivo completo)
- **~59 recuperáveis**: têm dia/mês mas **falta o ano** (ex.: `20/04 (1)`). Dá pra deduzir o ano do período aquisitivo — **melhoria de parser ainda não feita**.
- **~30 regra de negócio**: "direito a X dias", "vendido pela MP", "licença maternidade", "FDS" → decisão humana.
- **~17 sem data**: texto sem data reconhecível.

### 3. Reconciliações por colaborador (troca de CNPJ etc.)
- Detalhe com nomes em `PENDENCIAS-DETALHE.local.md`. Padrões que aparecem:
  - **Troca de CNPJ / readmissão** → períodos duplicados ou com mesmo início → reconciliar no app.
  - **Datas invertidas** na planilha (fim antes do início) → folga vai pro REVISAR.
  - **Contagem incompatível** com o intervalo → vai pro REVISAR.
  - **Folga idêntica a uma férias** → removida (evita dupla contagem).

---

## ⏳ Decisões pendentes do RH (não implementar até definir)

1. **Saldo de folga multiciclo** — hoje o app mostra só o **período atual** (`22 − usadas`). Somar todos os ciclos aguarda decisão do RH. Fórmula proposta: `Σ max(0, 22 − usadas por período)`.
2. **Meter na acumulação** — durante o período `acumulando` (2+ ciclos) a barra de férias fica **cheia** e diz "0 disponíveis", parecendo que a pessoa tirou tudo (quando não tirou; só não venceu). Definir se muda a visualização.
3. **Empresa/CNPJ** (EDITORAÇÃO, GO&REC, BAHAMAS…) — não tem campo no cadastro hoje. Decidir se guarda em algum lugar (ex.: "unidade") ou ignora.

---

## Próximo passo
Retomar por **Atendimento OFF** ou **ADM**: gerar `dados.json` da aba → conferir REVISAR → enviar → conferir no app.
