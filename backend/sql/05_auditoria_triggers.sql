-- ============================================================================
-- 05_auditoria_triggers.sql — auditoria automática por trigger.
-- Captura INSERT/UPDATE/DELETE nas tabelas de negócio, lendo nome/email do
-- usuário a partir dos claims do JWT (request.jwt.claims, populado pelo PostgREST).
-- Substitui, no modo backend, o logAudit() que o frontend faz em modo local.
--
-- OBS: o `detalhe` textual amigável (ex.: "Férias de 5 dias — Fulano") é gerado
-- no frontend em modo local; aqui guardamos os diffs estruturados em
-- dados_antes/dados_depois. Um detalhe amigável pode ser adicionado depois.
-- ============================================================================

create or replace function api.fn_auditoria()
returns trigger
language plpgsql
security definer
set search_path = api, public
as $$
declare
  claims  jsonb := coalesce(nullif(current_setting('request.jwt.claims', true), '')::jsonb, '{}'::jsonb);
  v_acao  text := lower(
                    case tg_op when 'INSERT' then 'inserir'
                               when 'UPDATE' then 'atualizar'
                               when 'DELETE' then 'excluir' end);
  v_id    text := case tg_op when 'DELETE' then (old).id::text else (new).id::text end;
begin
  insert into api.auditoria(usuario_nome, usuario_email, acao, tabela, registro_id, dados_antes, dados_depois)
  values (
    claims->>'nome',
    claims->>'email',
    v_acao,
    tg_table_name,
    v_id,
    case when tg_op <> 'INSERT' then to_jsonb(old) end,
    case when tg_op <> 'DELETE' then to_jsonb(new) end
  );
  return case tg_op when 'DELETE' then old else new end;
end;
$$;

create trigger aud after insert or update or delete on api.colaboradores
  for each row execute function api.fn_auditoria();
create trigger aud after insert or update or delete on api.periodos_aquisitivos
  for each row execute function api.fn_auditoria();
create trigger aud after insert or update or delete on api.ferias_oficiais
  for each row execute function api.fn_auditoria();
create trigger aud after insert or update or delete on api.folgas
  for each row execute function api.fn_auditoria();
create trigger aud after insert or update or delete on api.solicitacoes
  for each row execute function api.fn_auditoria();
create trigger aud after insert or update or delete on api.usuarios
  for each row execute function api.fn_auditoria();
