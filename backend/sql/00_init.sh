#!/bin/sh
# ============================================================================
# 00_init.sh — roda ANTES dos .sql (ordem alfabética no initdb).
# Cria o role de conexão do PostgREST (`authenticator`) com a senha do .env e
# grava o segredo do JWT no banco, para que login()/sign_jwt() assinem com a
# MESMA chave que o PostgREST usa para validar (PGRST_JWT_SECRET).
#
# Só executa na primeira inicialização (volume de dados vazio). Para reaplicar,
# use: docker compose down -v && docker compose up.
# ============================================================================
set -e

: "${AUTHENTICATOR_PASSWORD:?defina AUTHENTICATOR_PASSWORD no .env}"
: "${JWT_SECRET:?defina JWT_SECRET no .env}"

# Variáveis do psql (:'pw' etc.) são interpoladas fora de blocos dollar-quoted.
# Como o initdb roda só uma vez em volume vazio, CREATE ROLE direto basta.
psql -v ON_ERROR_STOP=1 \
     --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
     -v pw="$AUTHENTICATOR_PASSWORD" -v secret="$JWT_SECRET" -v db="$POSTGRES_DB" <<'SQL'
create role authenticator noinherit login password :'pw';
alter database :"db" set app.jwt_secret to :'secret';
SQL
