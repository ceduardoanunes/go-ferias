-- ============================================================================
-- 04_seed.sql — dados mínimos para o sistema subir utilizável.
-- Roda ANTES dos triggers de auditoria (05), então não gera ruído de auditoria.
-- Senhas de demonstração: "demo" (troque em produção!).
-- ============================================================================

-- ---------- usuários de acesso ----------
insert into api.usuarios (nome, email, senha_hash, papel) values
  ('Administrador',  'admin@goegrow.com.br',    crypt('demo', gen_salt('bf')), 'admin'),
  ('RH Go & Grow',   'rh@goegrow.com.br',       crypt('demo', gen_salt('bf')), 'rh'),
  ('Consulta Geral', 'consulta@goegrow.com.br', crypt('demo', gen_salt('bf')), 'leitura');

-- ---------- dois colaboradores reais do modelo, com período aquisitivo ----------
with c as (
  insert into api.colaboradores (nome, funcao, departamento, unidade, regime, admissao)
  values ('Carlos Eduardo Nunes', 'Designer Gráfico', 'Criação', 'Granbery', 'CLT', '2018-05-14')
  returning id
)
insert into api.periodos_aquisitivos (colaborador_id, inicio, fim, situacao)
  select id, '2025-07-30', '2026-07-29', 'acumulando' from c;

with c as (
  insert into api.colaboradores (nome, funcao, departamento, unidade, regime, admissao)
  values ('Amanda Guerra de Castro Pires', 'Coordenadora de Criação', 'Corporativo', 'Quintas da Avenida', 'CLT', '2019-06-03')
  returning id
)
insert into api.periodos_aquisitivos (colaborador_id, inicio, fim, situacao)
  select id, '2025-06-03', '2026-06-02', 'acumulando' from c;

-- Dica: para popular a base fictícia inteira que a UI usa em modo local, exporte
-- o Store.data do navegador (JSON) e faça um import — ou rode um script de carga.
-- Ver README → "Popular com dados de demonstração".
