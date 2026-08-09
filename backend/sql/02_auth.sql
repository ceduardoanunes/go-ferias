-- ============================================================================
-- 02_auth.sql — autenticação: assinatura de JWT (HS256) + login()
-- Usa apenas pgcrypto (hmac/crypt), sem a extensão pgjwt.
-- O segredo do JWT vem do GUC `app.jwt_secret`, setado por 00_init.sh a partir
-- da variável de ambiente JWT_SECRET (a MESMA passada ao PostgREST).
-- ============================================================================

-- ---------- roles do PostgREST ----------
-- `anon`          → requisições sem token (pré-login)
-- `authenticated` → requisições com JWT válido (role vem do claim "role")
-- O role de conexão do PostgREST (`authenticator`) é criado em 00_init.sh e
-- recebe estes dois via GRANT em 03_grants.sql.
do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'anon') then
    create role anon nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'authenticated') then
    create role authenticated nologin;
  end if;
end $$;

-- ---------- base64url ----------
create or replace function api.b64url(data bytea)
returns text language sql immutable as $$
  -- base64 padrão → base64url: troca +/ por -_, remove '=' e quebras de linha
  select translate(
           replace(replace(replace(encode(data,'base64'), E'\n',''), E'\r',''), '=', ''),
           '+/', '-_'
         );
$$;

-- ---------- assina um JWT HS256 ----------
create or replace function api.sign_jwt(payload jsonb, secret text)
returns text language sql as $$
  select signing || '.' || api.b64url(hmac(signing, secret, 'sha256'))
  from (
    select api.b64url(convert_to('{"alg":"HS256","typ":"JWT"}', 'utf8'))
        || '.' || api.b64url(convert_to(payload::text, 'utf8')) as signing
  ) s;
$$;

-- ---------- login(email, senha) → { token, nome, email, papel } ----------
-- Chamada pelo frontend em POST /rpc/login. SECURITY DEFINER para poder ler
-- api.usuarios mesmo sendo invocada pelo role `anon`.
create or replace function api.login(email text, senha text)
returns json
language plpgsql
security definer
set search_path = api, public
as $$
declare
  u        api.usuarios;
  tok      text;
  payload  jsonb;
begin
  select * into u from api.usuarios where usuarios.email = lower(login.email);

  if not found or u.senha_hash <> crypt(login.senha, u.senha_hash) then
    insert into api.auditoria(acao, detalhe)
      values ('login_falhou', 'Credenciais inválidas para ' || coalesce(login.email, ''));
    -- SQLSTATE 'PT401' → PostgREST responde HTTP 401 com { message }
    raise exception 'E-mail ou senha inválidos' using errcode = 'PT401';
  end if;

  payload := jsonb_build_object(
    'role',  'authenticated',
    'papel', u.papel,
    'email', u.email,
    'nome',  u.nome,
    'exp',   (extract(epoch from now() + interval '12 hours'))::int
  );

  tok := api.sign_jwt(payload, current_setting('app.jwt_secret'));

  insert into api.auditoria(usuario_nome, usuario_email, acao, detalhe)
    values (u.nome, u.email, 'login', 'Acesso ao sistema');

  return json_build_object('token', tok, 'nome', u.nome, 'email', u.email, 'papel', u.papel);
end;
$$;

-- ---------- criar_usuario(...) → cria conta com senha já em hash ----------
-- O frontend não deve mandar senha em texto para uma tabela; passa por esta RPC.
-- (A checagem de "só admin cria usuário" será feita por RLS no passo de hardening.)
create or replace function api.criar_usuario(nome text, email text, senha text, papel api.papel, foto text default null)
returns api.usuarios
language plpgsql
security definer
set search_path = api, public
as $$
declare novo api.usuarios;
begin
  if (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'papel') is distinct from 'admin' then
    raise exception 'Apenas administradores criam usuários' using errcode = 'PT403';
  end if;
  insert into api.usuarios(nome, email, senha_hash, papel, foto)
    values (nome, lower(email), crypt(senha, gen_salt('bf')), papel, foto)
    returning * into novo;
  novo.senha_hash := null;   -- nunca devolve o hash
  return novo;
end;
$$;

-- ---------- alterar_senha(usuario_id, nova_senha) ----------
create or replace function api.alterar_senha(usuario_id uuid, nova_senha text)
returns void
language plpgsql
security definer
set search_path = api, public
as $$
begin
  if (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'papel') is distinct from 'admin' then
    raise exception 'Apenas administradores alteram senhas' using errcode = 'PT403';
  end if;
  update api.usuarios set senha_hash = crypt(nova_senha, gen_salt('bf')) where id = usuario_id;
end;
$$;
