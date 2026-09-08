# Migração FORM 18 — status e pendências

Migração dos dados reais do RH (`FORM 18 - CONTROLE DE FÉRIAS ...xlsx`) para o app no Render, feita **aba por aba** (cada aba = 1 setor), conferindo no app antes de seguir. Status da **1ª inserção** (aba VÍDEO).

> ⚠️ A planilha `.xlsx` tem dados pessoais e **não é versionada** (gitignore).
> Detalhe com **nomes** fica em `PENDENCIAS-DETALHE.local.md` (local, gitignorado). Os nomes das pendências também saem nos `REVISAR.txt` / `PENDENTES.txt` gerados a cada import.

Ambiente: Render `https://goferias.onrender.com` · admin `admin@goegrow.com.br` / `demo`.

---

## ✅ Concluído

### 8ª–10ª inserção — CORPORATIVO, ADM, CRIAÇÃO (últimas 3 abas) → migração de abas COMPLETA
Sistema **72 → 96** colaboradores. Todas as abas de setor ativo foram importadas.

**Corporativo → Coordenação/Corporativo (8 criados, 1 pulado):** Adrielly Dandara Silva Leao, Alice Teixeira Oliveira, Ana Carolina Mendes Martins Maia, Clara Freguglia Roque, Clarice Abreu, Darlene Christiny Santos Moura, Júlia Fernandes Baptista Oliveira, Sarah Daibert Couri. 33 períodos, 31 férias, 90 folgas.
- **Eric Oliviera Quintella PULADO** — já existia como **estagiário efetivado** (ver abaixo).
- Reconciliar: **Sarah Daibert Couri** (CNPJ, hist desde 2021-08-17 / adm 2026-03-24). Sem função: **Darlene** e **Júlia** (ambas sem empresa também). **Júlia** tem 2 períodos **sobrepostos** (2023-07-14 e 2023-09-13) — conferir/apagar espúrio.

**ADM → Administrativo (9 criados):** Amanda Lima, Augusto Pires, Clara Teixeira Evangelista, Fabiana Morais, Valéria Leão Marins, Victoria Camarinha, Clarisse da Silva de Oliveira, Danielle de Souza Resende, Renata Marcon. 24 períodos, 12 férias, 71 folgas.
- **Amanda Lima** tinha stub 0/1 dia (2026-07-24) rejeitado (7→6 períodos). Reconciliar CNPJ: **Victoria Camarinha** (2025-11-24) e **Danielle de Souza Resende** (2023-03-03).

**Criação → Criação (24 criados, 1 pulado):** Bruna Labanca, Caio Alves, Carlos Eduardo Nunes, Carlos Eduardo Fregulia, Caik de Souza Sene, Edimar da Costa Silva, Gabriel Fernandes Delarue, Guilherme Pereira, Gustavo Martins Esteves, Maria Carolina Miranda e Silva, Maria Vitoria Freitas Lima, Nathalia Garcia Rodrigues, Oliver Baio, Rafael Cardoso Dias Silva, Roberto Martins Gonçalves, Victor Bosich Rezende, Daniel Marcos de Assis e Oliveira, Felipe Antonio Rodrigues, Gustavo Augusto Alves, Jordan Christian Portes Martins de Melo, Júlio Cesar de Sousa Vieira, Melissa Gilberto Marques, Osmar Parma Junior, Paola Fidelis Freitas. 75 períodos, 65 férias, 214 folgas, **3 notas** (Fregulia 2× venda MP, Jordan banco de horas).
- **Nathalia de Sousa Ferreira PULADA** — estagiária efetivada (ver abaixo). ⚠️ Distinta de **Nathalia Garcia Rodrigues** (entrou normal).
- **Paola Fidelis Freitas**: parser quebrou em 2 linhas (2 aquisitivos) → **mescladas à mão** no dados.json antes do envio (1 pessoa, 2 períodos). Sem função/empresa.
- Reconciliar CNPJ: **Carlos Eduardo Fregulia** (2019-01-28), **Victor Bosich Rezende** (2020-02-23), **Jordan Christian Portes** (2022-04-06), **Felipe Antonio Rodrigues** (2023-04-05). Sem função: **Guilherme Pereira**.
- **Denis Fernando de Oliveira Ribeiro (Bahamas)** e **Sara Efigenia de Oliveira Magalhaes** NÃO entraram (sem admissão) → lançar à mão.
- 124 folgas no REVISAR.

> ⚠️ **NOVO — Estagiários efetivados (nome colidiu → PULADOS pelo envio):** **Eric Oliviera Quintella** (→ Corporativo, adm 2026-02-02, 1 período) e **Nathalia de Sousa Ferreira** (→ Criação, adm 2026-06-25, 1 período) já existiam como estagiários (0 períodos). O cadastro CLT novo **não** foi criado. **Converter à mão no app:** mudar setor de Estagiários → Corporativo/Criação, ajustar admissão e lançar o período aquisitivo.

### 7ª inserção — aba ATEND. SOCIAL MÍDIA (17 colaboradores → Digital) 💣 troca de CNPJ
- Maria Eduarda Oliveira Agreli, Ana Clara Souza David, Eliton de Jesus Souza, Ester dos Anjos Rocha, Fabrício Alves Correa, Gabriel Almeida de Oliveira, João Francisco Beghelli, Larissa Costa Cardoso e Silva, Maria Eduarda Robusti Barbosa, Mariana Marcato Oliveira, Matheus Pereira Pires, Pablo Amaro Reis da Silva, Pedro Guimarães, Pedro Henrique Portes, Raphaela Morena Borges, Tamiris Toroa Procopio, Victor Saggioro de Oliveira. Gravados: **46 períodos, 21 férias, 129 folgas**. 0 pulados. Sistema 38 → 55.
- **6 períodos-stub de 0/1 dia** (Eliton, Gabriel, Mariana, Matheus P. Pires, Pablo, Pedro H. Portes) rejeitados pela API → 52 → 46 períodos. Esperado.
- **Decisão RH (igual Inbound): manter TODO o histórico.** ~11 pessoas migraram de CNPJ (RCT-DIGITAL / REC) em 2025/2026 → `admissão` ficou como a data do CNPJ novo, mas com períodos vindos de 2022-2024. **Reconciliar a admissão à mão** p/ o tempo de casa refletir o histórico. Mais antigos: **João Francisco Beghelli** e **Victor Saggioro** (desde 2022), **Maria Eduarda Robusti Barbosa** (desde 2020).
- ⚠️ **Maria Eduarda Robusti Barbosa**: função + empresa **em branco** na planilha e **buraco no histórico** (2020→2022, pula p/ 2025 — faltam 2023/2024). Provável saída+readmissão. Conferir tudo à mão.
- ⚠️ **Gabriel Almeida**: dois períodos com **mesmo início** (2025-02-03) — duplicata do corte de CNPJ (parser flagou "conferir no app").
- ⚠️ **Duas Marias Eduardas distintas**: Agreli (Atendimento/EDITORAÇÃO) e Robusti Barbosa. Ambas entraram.
- **59 folgas no REVISAR** (padrões conhecidos: listas de dias, datas viradas, "direito a X dias").

### 6ª inserção — aba SUPERVISÃO (8 colaboradores → Coordenação)
- Brênio Peters Ribeiro, Cintia de Freitas Guimaraes, Luzya Marxiellen Montan Oliveira, Danilo dos Santos Bispo, Dhafni Esteves Maciel, Eduardo Moreira Valente Junior, Kim Menini Arimathea, Maria Eduarda Mendonça. Gravados: **40 períodos, 32 férias, 106 folgas**. 0 pulados. Sistema 30 → 38 colaboradores.
- Parser atual mais conservador que a estimativa antiga do doc (era 149 folgas/21 revisar → ficou 106 folgas + **66 no REVISAR**). Padrões conhecidos: venda MP ("10/30 DIAS VENDIDOS MP", "direito a X dias"), listas de dias não fatiadas ("20,23/02 (2)"), ranges com "fim antes do início" (viradas de ano).
- **2 períodos-stub de 0/1 dia** (readmissão de Eduardo e Kim) rejeitados pela API → 42 → 40 períodos. Esperado.
- **Reconciliar à mão no app:** Danilo dos Santos Bispo tem **"Bahamas"** (empresa/CNPJ) grudado na função → limpar (mesma pendência do Mateus/Bahamas). Maria Eduarda Mendonça está **sem função** na planilha.

### ⛔ REGRA: aba ESTAGIÁRIOS NÃO entra no controle CLT
- **Estagiário é regido pela Lei 11.788/2008, não pela CLT** → não tem férias/folgas CLT. A aba **ESTAGIÁRIOS não deve ser migrada** com períodos aquisitivos/férias/folgas.
- ⚠️ **Erro corrigido:** a 5ª inserção subiu os 11 por engano (19 períodos + 9 folgas). **Revertido** com `scratchpad/zerar_periodos.py --setor "Estagiários"` — os **11 cadastros foram MANTIDOS** (Ana Luiza Chaves Souza, Cassiano Fernandes Augusto Pires, Eric Oliviera Quintella, Jessica da Silva Xavier, Luan Carlos Esteves Oliveira, Luiz Fernando Assis Rangel, Mariana Paiva Dabés, Mateus Costa, Nathalia de Sousa Ferreira, Victoria Werneck, Vinicius Silva), mas **períodos/férias/folgas removidos** (9 folgas + 21 períodos apagados — 2 períodos extras eram auto-abertos pelo app). Conferido: 11 estagiários, 0 períodos.
- Se no futuro o RH quiser controlar **recesso de estagiário** (30 dias a cada 12 meses de estágio, Lei 11.788), é regra **à parte** do fluxo CLT — decidir modelagem antes.

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

## ✅ Abas — TODAS importadas
Todas as 12 abas de setor ativo foram migradas (Vídeo, Atendimento OFF, Redação-Revisão,
Inbound, Estagiários, Supervisão, Digital, Corporativo, ADM, Criação). `BAYER, NEXA E NISSAN`
estava vazia → ignorada. Restam só as pendências **por colaborador** abaixo (à mão no app).

---

## ⏳ Pendências de dados (padrões, sem nomes)

### 1. Pessoas sem admissão (NÃO entram — API exige admissão; lançar à mão)
- **Estagiários:** N/A — aba fora do escopo CLT (ver regra acima). Ainda por vir nas abas não importadas: **Criação ×2**. Nomes no `PENDENTES.txt` gerado a cada import.

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

## Próximo passo — reconciliação à mão no app (import de abas encerrado)
Migração automática das abas concluída (96 colaboradores). Falta o trabalho manual no app:
1. **Estagiários efetivados:** converter **Eric Oliviera Quintella** (→ Corporativo) e **Nathalia de Sousa Ferreira** (→ Criação) — setor, admissão e período.
2. **Reconciliar admissão (CNPJ):** Digital (~11), Inbound (5), Criação (4), ADM (2), Corporativo (1), Vídeo/Atend. OFF (Isaac, André). Ver seções por inserção.
3. **Lançar sem-admissão à mão:** Denis Fernando de Oliveira Ribeiro (Bahamas) e Sara Efigenia de Oliveira Magalhaes (Criação).
4. **Campos:** limpar "Bahamas" de nomes/funções; preencher funções vazias (Darlene, Júlia, Guilherme, Paola, Maria Eduarda Robusti/Mendonça); Flávia Revisora, Darlan (sobrenome).
5. **Períodos duplicados/sobrepostos:** Júlia (Corporativo), Gabriel Almeida (Digital), Isaac (Vídeo).
6. **Folgas do REVISAR** de cada aba (à mão).

> Lembrete: rodar o envio com `SSL_CERT_FILE=$(python3 -m certifi) python3 enviar_para_api.py saida/dados.json --url https://goferias.onrender.com --senha demo`.
