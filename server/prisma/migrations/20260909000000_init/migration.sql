-- CreateEnum
CREATE TYPE "Papel" AS ENUM ('admin', 'rh', 'leitura');

-- CreateEnum
CREATE TYPE "PeriodoSituacao" AS ENUM ('acumulando', 'programado', 'aberto', 'pago');

-- CreateEnum
CREATE TYPE "SolicitacaoStatus" AS ENUM ('pendente', 'aprovada', 'recusada');

-- CreateEnum
CREATE TYPE "AusenciaTipo" AS ENUM ('ferias', 'folga');

-- CreateTable
CREATE TABLE "usuarios" (
    "id" TEXT NOT NULL,
    "nome" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "senha_hash" TEXT NOT NULL,
    "papel" "Papel" NOT NULL DEFAULT 'leitura',
    "foto" TEXT,
    "criado_em" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "usuarios_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "colaboradores" (
    "id" TEXT NOT NULL,
    "nome" TEXT NOT NULL,
    "email" TEXT,
    "funcao" TEXT NOT NULL,
    "departamento" TEXT NOT NULL,
    "unidade" TEXT NOT NULL,
    "regime" TEXT NOT NULL,
    "admissao" DATE NOT NULL,
    "desligamento" DATE,
    "foto" TEXT,
    "ativo" BOOLEAN NOT NULL DEFAULT true,
    "cnpj" TEXT,
    "cnpj_desde" DATE,

    CONSTRAINT "colaboradores_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "periodos_aquisitivos" (
    "id" TEXT NOT NULL,
    "colaborador_id" TEXT NOT NULL,
    "inicio" DATE NOT NULL,
    "fim" DATE NOT NULL,
    "situacao" "PeriodoSituacao" NOT NULL DEFAULT 'acumulando',
    "pago_em" DATE,

    CONSTRAINT "periodos_aquisitivos_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ferias_oficiais" (
    "id" TEXT NOT NULL,
    "periodo_id" TEXT NOT NULL,
    "inicio" DATE NOT NULL,
    "fim" DATE NOT NULL,
    "dias" INTEGER NOT NULL,
    "obs" TEXT NOT NULL DEFAULT '',

    CONSTRAINT "ferias_oficiais_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "folgas" (
    "id" TEXT NOT NULL,
    "periodo_id" TEXT NOT NULL,
    "inicio" DATE NOT NULL,
    "fim" DATE NOT NULL,
    "dias" INTEGER NOT NULL,
    "obs" TEXT NOT NULL DEFAULT '',

    CONSTRAINT "folgas_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "solicitacoes" (
    "id" TEXT NOT NULL,
    "colaborador_id" TEXT,
    "nome" TEXT NOT NULL DEFAULT '',
    "tipo" "AusenciaTipo" NOT NULL DEFAULT 'folga',
    "inicio" DATE NOT NULL,
    "fim" DATE NOT NULL,
    "dias" INTEGER NOT NULL,
    "motivo" TEXT NOT NULL DEFAULT '',
    "aval_coordenador" BOOLEAN NOT NULL DEFAULT false,
    "status" "SolicitacaoStatus" NOT NULL DEFAULT 'pendente',
    "criado_em" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "decidido_em" TIMESTAMP(3),
    "decidido_por" TEXT,

    CONSTRAINT "solicitacoes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "notas" (
    "id" TEXT NOT NULL,
    "colaborador_id" TEXT NOT NULL,
    "periodo_id" TEXT,
    "categoria" TEXT NOT NULL,
    "texto" TEXT NOT NULL,
    "data" DATE,
    "criado_em" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "notas_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auditoria" (
    "id" TEXT NOT NULL,
    "ts" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "usuario_nome" TEXT,
    "usuario_email" TEXT,
    "acao" TEXT NOT NULL,
    "tabela" TEXT,
    "registro_id" TEXT,
    "detalhe" TEXT,
    "dados_antes" JSONB,
    "dados_depois" JSONB,

    CONSTRAINT "auditoria_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "usuarios_email_key" ON "usuarios"("email");

-- CreateIndex
CREATE INDEX "periodos_aquisitivos_colaborador_id_idx" ON "periodos_aquisitivos"("colaborador_id");

-- CreateIndex
CREATE INDEX "ferias_oficiais_periodo_id_idx" ON "ferias_oficiais"("periodo_id");

-- CreateIndex
CREATE INDEX "folgas_periodo_id_idx" ON "folgas"("periodo_id");

-- CreateIndex
CREATE INDEX "solicitacoes_status_idx" ON "solicitacoes"("status");

-- CreateIndex
CREATE INDEX "notas_colaborador_id_idx" ON "notas"("colaborador_id");

-- CreateIndex
CREATE INDEX "auditoria_ts_idx" ON "auditoria"("ts");

-- AddForeignKey
ALTER TABLE "periodos_aquisitivos" ADD CONSTRAINT "periodos_aquisitivos_colaborador_id_fkey" FOREIGN KEY ("colaborador_id") REFERENCES "colaboradores"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ferias_oficiais" ADD CONSTRAINT "ferias_oficiais_periodo_id_fkey" FOREIGN KEY ("periodo_id") REFERENCES "periodos_aquisitivos"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "folgas" ADD CONSTRAINT "folgas_periodo_id_fkey" FOREIGN KEY ("periodo_id") REFERENCES "periodos_aquisitivos"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "solicitacoes" ADD CONSTRAINT "solicitacoes_colaborador_id_fkey" FOREIGN KEY ("colaborador_id") REFERENCES "colaboradores"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "notas" ADD CONSTRAINT "notas_colaborador_id_fkey" FOREIGN KEY ("colaborador_id") REFERENCES "colaboradores"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "notas" ADD CONSTRAINT "notas_periodo_id_fkey" FOREIGN KEY ("periodo_id") REFERENCES "periodos_aquisitivos"("id") ON DELETE SET NULL ON UPDATE CASCADE;
