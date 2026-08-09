-- ============================================================================
-- 03_grants.sql — permissões por role.
-- MILESTONE 1: papel-based ainda NÃO é forçado no banco (será via RLS no passo
-- de hardening). Aqui damos o CRUD necessário para a UI atual funcionar, com o
-- anon reduzido ao mínimo do formulário público. Ver README → "Próximos passos".
-- ============================================================================

-- authenticator (role de conexão do PostgREST) pode assumir anon/authenticated
grant anon to authenticator;
grant authenticated to authenticator;

grant usage on schema api to anon, authenticated;

-- ---------- anon (pré-login) ----------
grant execute on function api.login(text, text) to anon;
-- autocomplete do formulário público: só as colunas necessárias
grant select (id, nome, funcao, departamento, ativo) on api.colaboradores to anon;
-- envio de solicitação pública
grant insert on api.solicitacoes to anon;

-- ---------- authenticated (pós-login) ----------
grant select, insert, update, delete on
  api.colaboradores,
  api.periodos_aquisitivos,
  api.ferias_oficiais,
  api.folgas,
  api.solicitacoes
to authenticated;

-- usuarios: leitura/edição via RLS depois; senha só muda via RPC
grant select (id, nome, email, papel, foto, criado_em), insert, update, delete
  on api.usuarios to authenticated;

grant select on api.v_auditoria to authenticated;
grant select, insert on api.auditoria to authenticated;

grant execute on function api.login(text, text)                       to authenticated;
grant execute on function api.criar_usuario(text, text, text, api.papel, text) to authenticated;
grant execute on function api.alterar_senha(uuid, text)               to authenticated;

-- sequences não são necessárias (PKs são uuid com default gen_random_uuid()).
