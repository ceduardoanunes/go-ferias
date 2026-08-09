# Backend — Go Férias!

Backend do sistema, na stack que o próprio frontend já pressupõe:
**PostgreSQL + PostgREST + JWT + triggers + (RLS a seguir)**.

> Marco atual: **schema + auth + CRUD + RLS por papel**, e a **camada de dados do
> frontend já integrada** (modo `postgrest`). Falta o essencial: **testar de ponta a
> ponta com o Docker no ar** (foi tudo escrito sem um backend rodando) e o
> endurecimento fino do acesso público (ver o fim deste arquivo).

---

## Arquitetura

```
navegador ──HTTP──▶  nginx (web)          :8080
                     ├── /            → serve index.html (o frontend)
                     └── /api/*       → proxy p/ PostgREST (remove o /api)
                                          │
                                          ▼
                                     PostgREST (postgrest) :3000
                                          │  valida JWT, troca de role
                                          ▼
                                     PostgreSQL (db)       :5432
                                       schema `api`: tabelas, login(), triggers
```

- O frontend fala com `Store.pgUrl = '/api'`; o nginx repassa para o PostgREST.
- Autenticação: `POST /api/rpc/login` → JWT HS256 assinado no banco (pgcrypto),
  validado pelo PostgREST com o **mesmo** segredo (`JWT_SECRET`).
- CRUD: gerado automaticamente pelo PostgREST a partir do schema `api`.
- Auditoria: triggers gravam INSERT/UPDATE/DELETE lendo o usuário do JWT.

## Estrutura

```
backend/
  docker-compose.yml         # db + postgrest + web(nginx)
  nginx.conf                 # serve o front e faz proxy /api
  .env.example               # segredos (copie p/ .env)
  sql/                       # rodam em ordem alfabética no primeiro init
    00_init.sh               # cria role `authenticator` e grava o segredo JWT
    01_schema.sql            # schema api, enums, tabelas, view de auditoria
    02_auth.sql              # sign_jwt, login(), criar_usuario(), roles
    03_grants.sql            # permissões anon/authenticated
    04_seed.sql              # usuários demo + 2 colaboradores
    05_auditoria_triggers.sql# auditoria automática por trigger
    06_rls.sql               # Row Level Security por papel (admin/rh/leitura)
```

## Pré-requisitos

- Docker + Docker Compose (Docker Desktop no Mac/Windows).
- Nada mais: o Postgres e o PostgREST vêm nas imagens.

## Como subir (local)

```bash
cd backend
cp .env.example .env          # edite as senhas e o JWT_SECRET
docker compose up -d          # sobe db + postgrest + web
docker compose logs -f db     # acompanhe o init (só na 1ª vez)
```

- Frontend: <http://localhost:8080>
- API direta (sem proxy): <http://localhost:3000>

Para usar o backend, aponte o frontend para ele — em `index.html`, no objeto
`Store`, troque `driver: 'local'` por `driver: 'postgrest'`. O `pgUrl` já é `/api`.

> Reaplicar o SQL depois de editar algo em `sql/`:
> `docker compose down -v && docker compose up -d` (o `-v` apaga o volume, o
> init roda de novo). Sem `-v`, os scripts de init **não** rodam de novo.

## Testes rápidos (smoke test)

```bash
# 1) login → deve devolver { token, nome, email, papel }
curl -s http://localhost:3000/rpc/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@goegrow.com.br","senha":"demo"}'

# 2) guarde o token e liste colaboradores (autenticado)
TOKEN=$(curl -s http://localhost:3000/rpc/login -H 'Content-Type: application/json' \
  -d '{"email":"admin@goegrow.com.br","senha":"demo"}' | sed -E 's/.*"token":"([^"]+)".*/\1/')

curl -s http://localhost:3000/colaboradores -H "Authorization: Bearer $TOKEN"

# 3) inserir um colaborador
curl -s http://localhost:3000/colaboradores \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -H 'Prefer: return=representation' \
  -d '{"nome":"Teste","funcao":"QA","departamento":"TI","unidade":"Granbery","regime":"CLT","admissao":"2024-01-10"}'

# 4) auditoria (a inserção acima deve aparecer)
curl -s "http://localhost:3000/v_auditoria?limit=5" -H "Authorization: Bearer $TOKEN"
```

## Popular com dados de demonstração (opcional)

O seed traz só 2 colaboradores. Para carregar a base fictícia grande que a UI
usa em modo local: abra o app em modo local, no console do navegador rode
`copy(JSON.stringify(Store.data))`, e escreva um pequeno script de import (POST
para cada tabela). Posso gerar esse script quando quiser.

---

## ✅ Já feito (segurança e integração)

- **RLS por papel** (`06_rls.sql`): as regras `admin`/`rh`/`leitura` agora são
  forçadas **no banco**, não mais só no cliente. `leitura` só lê; `rh` edita
  lançamentos e decide solicitações; só `admin` mexe em colaboradores e usuários.
- **Senhas em bcrypt**, JWT assinado no banco, auditoria por trigger.
- **Frontend integrado** (modo `postgrest`, tudo atrás de `driver==='postgrest'`):
  `pgUpdate`/`update`/`pgRpc`, sincronização de memória em insert/update/remove,
  `pgLoad` carregando também `usuarios` e `solicitacoes`, dados carregados
  **após o login**, mutações (`editarColab`, `toggleAtivoColab`, `marcarPago`,
  `reabrirPeriodo`, `salvarLanc`/`salvarEdicaoLanc`, `salvarUsuario`,
  `delUsuario`, `decidirSolic`) e o formulário público ligados à API.
  Usuários criados via `rpc/criar_usuario` e senha via `rpc/alterar_senha`.
  → O modo `local` foi mantido intacto (verificado por render headless).

## ⚠️ Ainda falta

1. **Testar de ponta a ponta.** Tudo acima foi escrito **sem um backend rodando**.
   Suba o Docker, rode os smoke tests, troque `Store.driver` para `'postgrest'`
   e valide os fluxos reais (login, listar, editar, aprovar solicitação, etc.).
2. **Acesso público mais restrito.** O `anon` lê o diretório (colunas mínimas)
   para o autocomplete e insere solicitações. Vale expor menos (uma view enxuta)
   e pôr rate-limit no proxy.
3. **Segredos.** Troque `JWT_SECRET` e as senhas do `.env`; nunca comite o `.env`
   (já está no `.gitignore`).
4. **TLS/produção.** Em produção, proxy (Traefik/nginx) com HTTPS e PostgREST/DB
   em rede interna, não expostos.
