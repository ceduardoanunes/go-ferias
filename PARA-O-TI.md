# Handoff — Backend Go Férias! (para o TI)

Resumo técnico do que está pronto, como rodar e o que falta. Repositório:
`github.com/ceduardoanunes/go-ferias`.

## TL;DR

Backend em **Node + Express + Prisma (PostgreSQL)** na pasta **`server/`** — a
stack que vocês pediram. **Construído e testado de ponta a ponta** (não é só
esqueleto). Sobe com `docker compose up`. O frontend (`index.html`) já tem o
adaptador para consumi-lo. Falta: credenciais de SMTP, hardening de produção,
importar os ~120 colaboradores reais e uma decisão sobre o formulário público.

## O que já está pronto (e verificado rodando)

- **Modelo de dados** (`server/prisma/schema.prisma`): colaboradores, períodos
  aquisitivos, férias, folgas, usuários, solicitações, auditoria. Inclui o
  **campo `email` no colaborador**.
- **Auth**: `POST /auth/login` → JWT (12h). Senhas em **bcrypt**.
- **RBAC por papel** (middleware): `leitura` só lê; `rh` edita lançamentos e
  decide solicitações; **só `admin`** mexe em colaboradores e usuários.
  Verificado: `403`/`401` corretos.
- **CRUD** de todas as entidades (fábrica genérica em `src/routes/crud.js`).
- **Solicitações**: `POST /solicitacoes` público; `POST /solicitacoes/:id/decidir`
  aprova/recusa, **lança a folga** e **dispara e-mail** ao colaborador (nodemailer).
- **Auditoria** automática (insert/update/delete + login) via `src/audit.js`.
- **Frontend integrado**: `Store.driver = 'node'` no `index.html` liga tudo
  (login, carga, CRUD, decidir, auditoria). Testado headless: login → carrega do
  banco → cria → edita, sem erros.

> Nota: a base da imagem foi trocada de `node:20-alpine` para `node:20-slim`
> (+`openssl`) — o Prisma não inicializa no Alpine. Já corrigido no Dockerfile.

## Como rodar (local)

```bash
cd server
cp .env.example .env          # ajuste POSTGRES_PASSWORD, DATABASE_URL, JWT_SECRET
docker compose up -d --build  # sobe Postgres + API; cria tabelas (prisma db push) e seed
curl http://localhost:3000/health          # {"ok":true,"smtp":...}
```

Login de teste: `admin@goegrow.com.br` / `demo` (ver `prisma/seed.js`).
`API_PORT` no `.env` muda a porta do host (usei 3333 no dev por conflito com o 3000).

Sem Docker: `npm install && npx prisma db push && node prisma/seed.js && npm start`.

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

No `index.html`, objeto `Store`: `driver: 'node'` e `apiUrl` apontando para a API
(dev: `http://localhost:3333`; prod: sirva o front e proxie `/api` → API, e use
`apiUrl:'/api'`). Toda a lógica remota está atrás de `driver` — o modo `local`
(localStorage) segue intacto como fallback/demo.

## O que falta (decisões e produção)

1. **SMTP real** — preencher `SMTP_*` no `.env` para os e-mails saírem (hoje o
   envio é "no-op" logado se não configurado). Modelos em `src/mailer.js`.
2. **Hardening de produção**: trocar `JWT_SECRET`/senhas, restringir `cors()` ao
   domínio, HTTPS no proxy, Postgres em rede interna, **rate-limit** no
   `POST /solicitacoes` (rota pública).
3. **Importar os ~120 colaboradores** da planilha do RH. Há um parser em
   `backend/import/` (gera `dados.json`; parte estruturada confere 1:1 com o
   modelo, folgas em texto livre exigem revisão). Falta um pequeno script Prisma
   que leia esse JSON e crie os registros — posso escrever quando a planilha vier.
4. **Formulário público** (pedir folga sem login): hoje as rotas exigem auth,
   então o autocomplete do diretório não funciona anonimamente (mais seguro).
   Decidir o fluxo: exigir nome completo + confirmação, um dado extra, ou remover.

## Estrutura

```
server/
  prisma/schema.prisma  seed.js
  src/index.js  prisma.js  auth.js  mailer.js  audit.js  serialize.js
  src/routes/  crud.js auth.js usuarios.js solicitacoes.js auditoria.js
  Dockerfile  docker-compose.yml  .env.example  README.md
```

## Alternativa (preterida)

Há um backend equivalente em **PostgreSQL + PostgREST** em `backend/` (com RLS no
banco). Foi **preterido** em favor do Node/Express/Prisma, mas fica de referência
(schema, políticas de acesso, análise técnica). Ignorar salvo interesse.
