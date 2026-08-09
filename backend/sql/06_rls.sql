-- ============================================================================
-- 06_rls.sql — Row Level Security por papel (admin / rh / leitura).
-- Força no BANCO as regras que hoje só existem no cliente (e eram burláveis).
-- O papel vem do claim `papel` do JWT (request.jwt.claims), setado por login().
--
-- Mapa (espelha Auth.pode* do frontend):
--   leitura → só SELECT
--   rh      → SELECT tudo + edita lançamentos (períodos/férias/folgas) e decide solicitações
--   admin   → tudo, inclusive colaboradores e usuários
--
-- Funções SECURITY DEFINER (login, criar_usuario, triggers de auditoria) são
-- donas = superusuário e IGNORAM RLS — então continuam funcionando.
-- ============================================================================

-- papel do usuário logado (null p/ anon)
create or replace function api.jwt_papel()
returns text language sql stable as $$
  select nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'papel';
$$;

-- ---------------------------------------------------------------------------
-- colaboradores: todos leem; só admin escreve
-- ---------------------------------------------------------------------------
alter table api.colaboradores enable row level security;

create policy colab_sel on api.colaboradores for select
  to anon, authenticated using (true);
create policy colab_ins on api.colaboradores for insert
  to authenticated with check (api.jwt_papel() = 'admin');
create policy colab_upd on api.colaboradores for update
  to authenticated using (api.jwt_papel() = 'admin') with check (api.jwt_papel() = 'admin');
create policy colab_del on api.colaboradores for delete
  to authenticated using (api.jwt_papel() = 'admin');

-- ---------------------------------------------------------------------------
-- periodos / ferias / folgas: todos leem; rh e admin escrevem
-- ---------------------------------------------------------------------------
alter table api.periodos_aquisitivos enable row level security;
create policy per_sel on api.periodos_aquisitivos for select
  to authenticated using (true);
create policy per_wri on api.periodos_aquisitivos for all
  to authenticated using (api.jwt_papel() in ('admin','rh')) with check (api.jwt_papel() in ('admin','rh'));

alter table api.ferias_oficiais enable row level security;
create policy fer_sel on api.ferias_oficiais for select
  to authenticated using (true);
create policy fer_wri on api.ferias_oficiais for all
  to authenticated using (api.jwt_papel() in ('admin','rh')) with check (api.jwt_papel() in ('admin','rh'));

alter table api.folgas enable row level security;
create policy fol_sel on api.folgas for select
  to authenticated using (true);
create policy fol_wri on api.folgas for all
  to authenticated using (api.jwt_papel() in ('admin','rh')) with check (api.jwt_papel() in ('admin','rh'));

-- ---------------------------------------------------------------------------
-- solicitacoes: anon insere (form público); rh/admin leem e decidem
-- ---------------------------------------------------------------------------
alter table api.solicitacoes enable row level security;
create policy sol_ins_anon on api.solicitacoes for insert
  to anon, authenticated with check (true);
create policy sol_sel on api.solicitacoes for select
  to authenticated using (api.jwt_papel() in ('admin','rh'));
create policy sol_upd on api.solicitacoes for update
  to authenticated using (api.jwt_papel() in ('admin','rh')) with check (api.jwt_papel() in ('admin','rh'));
create policy sol_del on api.solicitacoes for delete
  to authenticated using (api.jwt_papel() = 'admin');

-- ---------------------------------------------------------------------------
-- usuarios: só admin (criação/senha via RPC SECURITY DEFINER, que ignora RLS)
-- ---------------------------------------------------------------------------
alter table api.usuarios enable row level security;
create policy usr_sel on api.usuarios for select
  to authenticated using (api.jwt_papel() = 'admin');
create policy usr_upd on api.usuarios for update
  to authenticated using (api.jwt_papel() = 'admin') with check (api.jwt_papel() = 'admin');
create policy usr_del on api.usuarios for delete
  to authenticated using (api.jwt_papel() = 'admin');
-- (INSERT direto fica bloqueado de propósito: use api.criar_usuario())

-- ---------------------------------------------------------------------------
-- auditoria: rh/admin leem; escrita só via triggers/login (definer, ignora RLS)
-- ---------------------------------------------------------------------------
alter table api.auditoria enable row level security;
create policy aud_sel on api.auditoria for select
  to authenticated using (api.jwt_papel() in ('admin','rh'));

-- a view precisa avaliar o RLS de QUEM consulta (senão o dono=postgres o ignora
-- e um usuário "leitura" veria a auditoria). security_invoker exige PG15+ (temos 16).
alter view api.v_auditoria set (security_invoker = true);
