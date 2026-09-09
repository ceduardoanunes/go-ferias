# Handoff — Go Férias! (para o TI)

Resumo técnico do que está pronto, como subir e como carregar os dados reais.
Repositório: `github.com/ceduardoanunes/go-ferias`.

## TL;DR

Backend em **Node + Express + Prisma (PostgreSQL)** na pasta **`server/`**.
**Construído, testado e rodando em produção** (estava no Render, gratuito —
expira e o serviço será desligado; por isso este handoff). O frontend
(`index.html`) já fala com ele. **Os dados reais dos colaboradores já
existem** — não é mais um sistema vazio, é uma migração de um servidor pro
outro. O snapshot completo está em `backend/import/saida_render/` (fora do
git — contém dados pessoais; foi enviado separadamente, não pelo GitHub).

## Passo a passo pra subir

```bash
cd server
cp .env.example .env          # ajuste POSTGRES_PASSWORD, DATABASE_URL, JWT_SECRET
docker compose up -d --build  # sobe Postgres + API; aplica as migrations (prisma migrate deploy) e roda o seed
curl http://localhost:3000/health          # {"ok":true,"smtp":...}
```

Isso sobe o sistema **vazio** (só os usuários demo do seed). O guia
`GUIA-WINDOWS.md` tem o passo a passo com mais detalhe (instalar Docker,
etc.) se for a primeira vez nessa máquina.

## Carregar os dados reais (depois do passo acima)

O snapshot em `backend/import/saida_render/*.json` foi baixado do Render em
**08/09/2026** via `backend/import/baixar_do_render.py` (é só ler a API,
não usa senha do Postgres). Pra recriar tudo no servidor novo:

```bash
cd backend/import
py carregar_no_local.py --url http://SEU-SERVIDOR:3000
```

Isso lê `saida_render/` e recria colaboradores → períodos → férias → folgas
→ notas na API do servidor novo, remapeando os IDs. **Não** carrega
`usuarios` nem `auditoria` (de propósito — ver abaixo). Passe
`--com-solicitacoes` se quiser levar a única solicitação pendente também.
É idempotente pra reexecução com `--url` diferente, mas **não** é seguro
rodar duas vezes contra o mesmo servidor (duplicaria tudo) — se precisar
refazer, apague as tabelas antes ou suba um Postgres limpo.

**Usuários (login) não migram com senha** — a API do Render nunca devolve o
hash da senha (por segurança), então `usuarios.json` só tem nome/e-mail/papel,
sem senha. É preciso **criar os acessos de novo** no servidor novo: admin
entra com o usuário do seed (`admin@goegrow.com.br` / `demo`, TROCAR a senha
assim que possível) e cadastra os usuários reais em Minha Conta → Usuários.

**Auditoria não migra** — histórico de "quem mexeu no quê" fica só como
registro histórico no Render (puxado em `saida_render/auditoria.json` se
precisar consultar depois); o servidor novo começa a auditoria dele do zero.

## O que já está pronto (testado, rodando)

- **Modelo de dados** (`server/prisma/schema.prisma`): colaboradores, períodos
  aquisitivos, férias, folgas, usuários, solicitações, auditoria.
- **Auth**: `POST /auth/login` → JWT (12h). Senhas em bcrypt.
- **RBAC por papel**: `leitura` só lê; `rh` edita lançamentos e decide
  solicitações; só `admin` mexe em colaboradores e usuários.
- **CRUD** de todas as entidades (fábrica genérica em `src/routes/crud.js`).
- **Solicitações**: `POST /solicitacoes` público; `POST /solicitacoes/:id/decidir`
  aprova/recusa, lança a folga e dispara e-mail (nodemailer, se SMTP configurado).
- **Auditoria** automática (insert/update/delete + login) via `src/audit.js`.
- **Frontend integrado**: `Store.driver = 'node'` no `index.html`.
- **Dados reais**: 111 colaboradores, ~360 períodos aquisitivos, ~230 férias,
  ~830 folgas, notas — todo o histórico do RH, migrado do Render.

## Endpoints

| Método | Rota | Papel |
|---|---|---|
| POST | `/auth/login` | público |
| GET | `/colaboradores` `/periodos_aquisitivos` `/ferias_oficiais` `/folgas` | qualquer logado |
| POST/PATCH/DELETE | `/colaboradores[/:id]` | admin |
| POST/PATCH/DELETE | `/periodos_aquisitivos` `/ferias_oficiais` `/folgas` | admin, rh |
| POST | `/solicitacoes` | público |
| GET | `/solicitacoes` | admin, rh |
| POST | `/solicitacoes/:id/decidir` `{aprovar}` | admin, rh |
| GET/POST/PATCH/DELETE | `/usuarios[/:id]` | admin |
| GET | `/auditoria?limit=` | admin, rh |

Header: `Authorization: Bearer <token>`. A serialização (`src/serialize.js`)
devolve snake_case + datas `YYYY-MM-DD` — o formato que o frontend consome.

## Como o frontend conecta

No `index.html`, objeto `Store`: detecta sozinho — servido por `http(s)` vira
`driver:'node'`, apontando `/` na mesma origem (o `server/src/index.js` serve
o `index.html` da raiz do repo e faz proxy da API). Não precisa editar nada
pra trocar de servidor, contanto que o Node sirva os dois juntos como já está.

## O que falta (decisões e produção)

1. **Hardening de produção**: trocar `JWT_SECRET`/senha do Postgres, restringir
   `cors()` ao domínio da empresa, HTTPS no proxy, Postgres em rede interna,
   rate-limit no `POST /solicitacoes` (rota pública, sem login).
2. **SMTP real** — preencher `SMTP_*` no `.env` pros e-mails de
   aprovação/recusa de solicitação saírem (hoje é "no-op" logado, se vazio).
3. **Usuários reais** — recriar os acessos de RH/admin (senhas não migram,
   ver acima).
4. **Backup** — definir rotina de backup do Postgres novo (o Render tinha
   backup próprio; o servidor da empresa precisa de um, `pg_dump` agendado
   ou equivalente).
5. **Formulário público** (pedir folga sem login): hoje as rotas exigem auth,
   então o autocomplete do diretório não funciona anonimamente (mais seguro,
   mas ainda em aberto se é o comportamento final desejado).

## Estrutura

```
index.html               frontend (arquivo único)
server/
  prisma/schema.prisma  seed.js
  src/index.js  prisma.js  auth.js  mailer.js  audit.js  serialize.js
  src/routes/  crud.js auth.js usuarios.js solicitacoes.js auditoria.js
  Dockerfile  docker-compose.yml  .env.example  README.md
backend/import/
  baixar_do_render.py    baixa tudo do Render pela API (só leitura)
  carregar_no_local.py   recria tudo num servidor novo, a partir do snapshot
  saida_render/           snapshot dos dados reais (08/09/2026) — NÃO vai pro git
```

## Alternativa (preterida)

Há um backend equivalente em **PostgreSQL + PostgREST** em `backend/` (com RLS
no banco). Foi **preterido** em favor do Node/Express/Prisma, mas fica de
referência (schema, políticas de acesso, análise técnica). Ignorar salvo
interesse.
