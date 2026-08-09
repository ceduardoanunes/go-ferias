# Backend Node — Go Férias!

API do sistema em **Node.js + Express + Prisma (PostgreSQL)**, com autenticação
**JWT**, controle de acesso por papel e **envio de e-mail via SMTP** — a stack
escolhida pelo TI (que fará a manutenção).

> ⚠️ **Escrito, mas ainda não executado** (a máquina de desenvolvimento não tinha
> Node). Rode e revise antes de considerar pronto. É uma base idiomática,
> pensada para o time evoluir.
>
> Existe também uma alternativa em `../backend/` (PostgreSQL + PostgREST). Esta
> pasta (`server/`) é a **escolhida**.

## Stack

- **Express** — a API HTTP.
- **Prisma** — ORM (modelo em `prisma/schema.prisma`, tabelas em snake_case).
- **jsonwebtoken** — login por JWT (12h).
- **bcryptjs** — senhas em hash (nunca texto puro).
- **nodemailer** — envio de e-mail (SMTP).

## Estrutura

```
server/
  prisma/
    schema.prisma      # modelo de dados (+ campo email no colaborador)
    seed.js            # usuários demo + Carlos/Amanda p/ testar
  src/
    index.js           # sobe o Express e monta as rotas
    prisma.js          # cliente Prisma
    auth.js            # hash, JWT, middlewares requireAuth / requirePapel
    mailer.js          # SMTP (nodemailer) + modelos de e-mail
    audit.js           # gravação de auditoria
    serialize.js       # Prisma <-> formato JSON do frontend (snake_case, datas ISO)
    routes/
      crud.js          # fábrica de CRUD (list/create/patch/delete) com papel + auditoria
      auth.js          # POST /auth/login, GET /auth/me
      usuarios.js      # admin; senha com hash
      solicitacoes.js  # POST público + decidir (aprova/recusa → e-mail)
      auditoria.js     # GET /auditoria
  Dockerfile
  docker-compose.yml   # postgres + api
  .env.example
```

## Como rodar (Docker)

```bash
cd server
cp .env.example .env          # ajuste senha do banco, JWT_SECRET e (opcional) SMTP
docker compose up -d --build  # sobe Postgres + API (cria tabelas e roda o seed)
curl http://localhost:3000/health
```

Login de teste: `admin@goegrow.com.br` / `demo`.

### Sem Docker (Node local)
```bash
cd server
npm install
cp .env.example .env          # DATABASE_URL apontando p/ um Postgres acessível
npx prisma db push            # cria as tabelas
node prisma/seed.js
npm start
```

## Endpoints

| Método | Rota | Papel | Observação |
|--------|------|-------|------------|
| POST | `/auth/login` | público | `{email,senha}` → `{token,nome,email,papel}` |
| GET | `/colaboradores` | todos | |
| POST/PATCH/DELETE | `/colaboradores[/:id]` | **admin** | |
| GET | `/periodos_aquisitivos` `/ferias_oficiais` `/folgas` | todos | |
| POST/PATCH/DELETE | idem | admin, **rh** | |
| POST | `/solicitacoes` | **público** | pedido sem login |
| GET | `/solicitacoes` | admin, rh | |
| POST | `/solicitacoes/:id/decidir` | admin, rh | `{aprovar:true/false}` → lança folga + **e-mail** |
| GET/POST/PATCH/DELETE | `/usuarios[/:id]` | **admin** | senha sempre com hash |
| GET | `/auditoria?limit=500` | admin, rh | |

Autenticação: envie `Authorization: Bearer <token>` (menos nas rotas públicas).

## E-mail (SMTP)

Configure `SMTP_*` no `.env`. Se `SMTP_HOST` ficar vazio, o envio é **desligado**
(o sistema loga e segue — não quebra). Hoje o disparo ocorre ao **decidir uma
solicitação** (aprovada/recusada → e-mail ao colaborador, se ele tiver e-mail).
Modelos de mensagem em `src/mailer.js` — fácil adicionar outros (ex.: aviso de
férias vencendo).

## Conectar o frontend (index.html)

A API devolve o **mesmo formato** que o app já consome (snake_case, datas
`YYYY-MM-DD`). Falta apenas apontar o `Store` do `index.html` para estes
endpoints (as URLs mudam em relação ao modo PostgREST — ex.: `POST /auth/login`
no lugar de `/rpc/login`, `PATCH /colaboradores/:id` no lugar de `?id=eq.`).
Posso fazer esse adaptador quando a API estiver de pé para testar.

## Dados reais (120 colaboradores)

O importador em `../backend/import/` gera `dados.json` a partir da planilha do RH.
Para carregar aqui, o caminho mais direto é um script Prisma que lê esse JSON e
cria os registros (as tabelas têm os mesmos nomes). Posso escrever esse script
quando a planilha real chegar.

## Produção (antes de dados reais)

- Trocar `JWT_SECRET` e senhas; nunca comitar `.env` (já no `.gitignore`).
- Restringir `cors()` ao domínio do app.
- HTTPS no proxy; Postgres em rede interna.
- Rate-limit no `POST /solicitacoes` (rota pública).
