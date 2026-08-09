-- ============================================================================
-- 01_schema.sql — modelo de dados do Go Férias!
-- Reflete 1:1 as entidades que o frontend (index.html) já envia/consome.
-- Tudo vive no schema `api`, que é o único exposto pelo PostgREST.
-- ============================================================================

create schema if not exists api;
create extension if not exists pgcrypto;   -- gen_random_uuid(), crypt(), hmac()

-- ---------- enums (valores exatos usados no frontend) ----------
create type api.papel                as enum ('admin','rh','leitura');
create type api.periodo_situacao     as enum ('acumulando','programado','aberto','pago');
create type api.solicitacao_status   as enum ('pendente','aprovada','recusada');
create type api.ausencia_tipo        as enum ('ferias','folga');   -- solicitacao.tipo (hoje só 'folga')

-- ---------- usuarios (contas de acesso ao sistema) ----------
create table api.usuarios (
  id          uuid primary key default gen_random_uuid(),
  nome        text not null,
  email       text not null unique,
  senha_hash  text not null,               -- bcrypt (pgcrypto), NUNCA texto puro
  papel       api.papel not null default 'leitura',
  foto        text,                         -- data URL (base64) ou null
  criado_em   timestamptz not null default now()
);

-- ---------- colaboradores ----------
create table api.colaboradores (
  id            uuid primary key default gen_random_uuid(),
  nome          text not null,
  funcao        text not null,
  departamento  text not null,
  unidade       text not null,
  regime        text not null,
  admissao      date not null,
  foto          text,
  ativo         boolean not null default true
);

-- ---------- periodos_aquisitivos ----------
create table api.periodos_aquisitivos (
  id              uuid primary key default gen_random_uuid(),
  colaborador_id  uuid not null references api.colaboradores(id) on delete cascade,
  inicio          date not null,
  fim             date not null,
  situacao        api.periodo_situacao not null default 'acumulando',
  pago_em         date
);

-- ---------- ferias_oficiais (gozo de férias contábeis) ----------
create table api.ferias_oficiais (
  id          uuid primary key default gen_random_uuid(),
  periodo_id  uuid not null references api.periodos_aquisitivos(id) on delete cascade,
  inicio      date not null,
  fim         date not null,
  dias        integer not null check (dias >= 1),
  obs         text default ''
);

-- ---------- folgas ----------
create table api.folgas (
  id          uuid primary key default gen_random_uuid(),
  periodo_id  uuid not null references api.periodos_aquisitivos(id) on delete cascade,
  inicio      date not null,
  fim         date not null,
  dias        integer not null check (dias >= 1),
  obs         text default ''
);

-- ---------- solicitacoes (pedidos, inclusive anônimos pré-login) ----------
create table api.solicitacoes (
  id                uuid primary key default gen_random_uuid(),
  colaborador_id    uuid references api.colaboradores(id) on delete set null,
  nome              text not null default '',
  tipo              api.ausencia_tipo not null default 'folga',
  inicio            date not null,
  fim               date not null,
  dias              integer not null check (dias >= 1),
  motivo            text default '',
  aval_coordenador  boolean not null default false,
  status            api.solicitacao_status not null default 'pendente',
  criado_em         timestamptz not null default now(),
  decidido_em       timestamptz,
  decidido_por      text
);

-- ---------- auditoria ----------
-- Populada pelos triggers (05_auditoria_triggers.sql) e pela função login().
create table api.auditoria (
  id             uuid primary key default gen_random_uuid(),
  ts             timestamptz not null default now(),
  usuario_nome   text,
  usuario_email  text,
  acao           text not null,   -- inserir|atualizar|excluir|login|logout|login_falhou
  tabela         text,
  registro_id    text,
  detalhe        text,
  dados_antes    jsonb,
  dados_depois   jsonb
);

-- ---------- índices ----------
create index on api.periodos_aquisitivos (colaborador_id);
create index on api.ferias_oficiais (periodo_id);
create index on api.folgas (periodo_id);
create index on api.solicitacoes (status);
create index on api.auditoria (ts desc);

-- ---------- view de auditoria (frontend lê /v_auditoria?limit=500) ----------
create or replace view api.v_auditoria as
  select id, ts, usuario_nome, usuario_email, acao, tabela, registro_id, detalhe, dados_antes, dados_depois
  from api.auditoria
  order by ts desc;
