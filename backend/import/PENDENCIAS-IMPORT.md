# Migração FORM 18 — status e pendências

Migração dos dados reais do RH (`FORM 18 - CONTROLE DE FÉRIAS ...xlsx`) para o app no Render, feita **aba por aba** (cada aba = 1 setor), conferindo no app antes de seguir. Status da **1ª inserção** (aba VÍDEO).

> ⚠️ A planilha `.xlsx` tem dados pessoais e **não é versionada** (gitignore).
> Detalhe com **nomes** fica em `PENDENCIAS-DETALHE.local.md` (local, gitignorado). Os nomes das pendências também saem nos `REVISAR.txt` / `PENDENTES.txt` gerados a cada import.

Ambiente: Render `https://goferias.onrender.com` · admin `admin@goegrow.com.br` / `demo`.

---

## ✅ Concluído

### 4ª inserção — aba INBOUND (8 colaboradores)
- Todos → setor **Inbound**: Ana Carolina Oliveira Mendes, Darlan, Francine da Silva Vieira, Leony de Paula, Vitor de Souza Rodrigues, Gabriel Campos, ~~Bruna Assis~~, Luan Oliveira. Gravados: **32 períodos, 20 férias, 117 folgas**. 0 pulados.
- **Bruna Assis EXCLUÍDA** (`excluir_colab.py`): era **ex-funcionária** numa linha de resquício na aba de ativos (função "GOOGLE", único período de 2022, sem situação/gozo). Restam **7 ativos** do Inbound. ⚠️ Ficar de olho em outras linhas de ex-funcionário perdidas nas abas de ativos das próximas levas.
- **Decisão RH: manter TODO o histórico** — os 5 que **trocaram de CNPJ** (Darlan, Francine, Leony, Vitor, Gabriel · empresa "RCT - DIGITAL ON") entraram com os períodos antigos (2021→2024) preservados.
- **Reconciliar à mão no app** nesses 5: a **admissão** ficou como a data do CNPJ novo (ex.: Francine 25/11/2025) enquanto os períodos vêm de ~2021 → ajustar p/ o tempo de casa refletir o histórico; remover o **período-stub de 1 dia** da readmissão.
- Períodos/folgas com data inválida (fim < início, stub) foram **rejeitados pela API** (já estavam no REVISAR) — 36→32 períodos, 120→117 folgas.
- **72 folgas** no REVISAR (Francine 20, Leony 18, Darlan 12, Vitor 10, Gabriel 9, Ana 2, Bruna 1). Nome **"Darlan"** sem sobrenome → conferir.

### 3ª inserção — aba REDAÇÃO-REVISÃO (5 colaboradores)
- Split por função funcionou: **Matheus Pereira Soares**, **Maryane Almeida**, **Vitória Beatriz** → **Redação**; **Flávia Revisora**, **Michele Fabiene** → **Revisão**. Total: 25 períodos, 15 férias, 56 folgas, 2 notas (Flávia — banco de horas). 0 pulados.
- **30 folgas** ficaram no `REVISAR.txt` (fim antes do início, contagem incompatível, "VER BH", "8 DIAS FDS") — lançar à mão no app.
- **Nome "Flávia Revisora"** = nome + cargo grudados na planilha → **corrigir no app** (sobrenome faltando).

### 2ª inserção — aba ATENDIMENTO OFF (3 colaboradores)
- **Amanda Guerra de Castro Pires**, **Mateus Jose Guedes Oliveira (Bahamas)**, **Andre Tuchtler Soares** → setor **Atendimento OFF**. Total: 20 períodos, 19 férias, 34 folgas.
- **André** era descartado pelo parser (a célula do nome tinha a nota "TEM 51 DIAS P TIRAR" colada, >60 chars → tratado como nota). Corrigido no envio: nome limpo + **admissão 05/12/2017** (a planilha trazia 02/02/2026 na 1ª linha). Períodos dele têm lacuna de **readmissão/troca de CNPJ** (2022→2023) — **reconciliar à mão no app**.
- **Mateus:** "(Bahamas)" (empresa/CNPJ) ficou no nome — **remover depois** (pendência de campo CNPJ).
- SSL do Python 3.14 no Mac: rodar o envio com `SSL_CERT_FILE=$(python3 -m certifi)` (ou instalar certificados).

### 1ª inserção
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

## ⏳ Abas ainda NÃO importadas (6)

| Aba | Setor do app | A enviar | Períodos | Férias | Folgas | Revisar |
|---|---|--:|--:|--:|--:|--:|
| ADM | Administrativo | 9 | 25 | 12 | 88 | 4 |
| ATENDIMENTO CORPORATIVO | Corporativo | 9 | 34 | 31 | 123 | 7 |
| SUPERVISÃO | Coordenação | 8 | 42 | 32 | 149 | 21 |
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
  - **Folga coincidente com férias** → MANTIDA. Férias contábeis e folga são independentes (na férias contábil a pessoa trabalha normal, sem bater ponto); não é dupla contagem.

---

## ⏳ Decisões pendentes do RH (não implementar até definir)

1. ~~**Saldo de folga multiciclo**~~ — ✅ **DECIDIDO:** só o **período atual** tem folga disponível (`22 − usadas do atual`). Períodos anteriores são completos/histórico (aparecem no hint "Período Anterior", mas não somam). Base fixa 22.
2. ~~**Meter na acumulação**~~ — ✅ **RESOLVIDO:** barra de férias começa vazia e reflete só o gozo do período gozável; período aquisitivo já vencido deixa de ser "em aquisição" (vira saldo a usufruir). Termo padronizado "Em aquisição".
3. **Empresa/CNPJ** (EDITORAÇÃO, GO&REC, BAHAMAS…) — não tem campo no cadastro hoje. Decidir se guarda em algum lugar (ex.: "unidade") ou ignora. (Ex. vivo: Mateus com "(Bahamas)" no nome, a remover.)

---

## Próximo passo
Escolher a próxima aba entre as 6 restantes (ADM, Atendimento Corporativo, Supervisão,
Criação, Estagiários, Social Mídia). Fluxo: gerar `dados.json` da aba → conferir
REVISAR → enviar → conferir no app. Deixar **Social Mídia (→ Digital)** por último (troca de CNPJ).

> Lembrete: rodar o envio com `SSL_CERT_FILE=$(python3 -m certifi) python3 enviar_para_api.py saida/dados.json --url https://goferias.onrender.com --senha demo`.
