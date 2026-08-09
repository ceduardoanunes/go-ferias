// Seed mínimo: usuários de acesso (senha "demo") + Carlos/Amanda para testar.
// Idempotente — pode rodar em todo boot sem duplicar.
require('dotenv').config();
const prisma = require('../src/prisma');
const bcrypt = require('bcryptjs');

async function main() {
  const senhaHash = await bcrypt.hash('demo', 10);
  const usuarios = [
    { nome: 'Administrador', email: 'admin@goegrow.com.br', papel: 'admin' },
    { nome: 'RH Go & Grow', email: 'rh@goegrow.com.br', papel: 'rh' },
    { nome: 'Consulta Geral', email: 'consulta@goegrow.com.br', papel: 'leitura' },
  ];
  for (const u of usuarios) {
    await prisma.usuario.upsert({ where: { email: u.email }, update: {}, create: { ...u, senhaHash } });
  }

  if ((await prisma.colaborador.count()) === 0) {
    await prisma.colaborador.create({
      data: {
        nome: 'Carlos Eduardo Nunes', email: null, funcao: 'Designer Gráfico',
        departamento: 'Criação', unidade: 'Granbery', regime: 'CLT', admissao: new Date('2018-05-14'),
        periodos: {
          create: [
            { inicio: new Date('2025-07-30'), fim: new Date('2026-07-29'), situacao: 'acumulando' },
            {
              inicio: new Date('2024-07-30'), fim: new Date('2025-07-29'), situacao: 'pago',
              ferias: { create: [{ inicio: new Date('2025-07-30'), fim: new Date('2025-08-28'), dias: 30 }] },
            },
          ],
        },
      },
    });
    await prisma.colaborador.create({
      data: {
        nome: 'Amanda Guerra de Castro Pires', email: null, funcao: 'Atendimento OFF',
        departamento: 'Corporativo', unidade: 'Quintas da Avenida', regime: 'CLT', admissao: new Date('2019-06-06'),
        periodos: {
          create: [
            { inicio: new Date('2025-08-06'), fim: new Date('2026-08-05'), situacao: 'acumulando' },
            {
              inicio: new Date('2024-08-06'), fim: new Date('2025-08-05'), situacao: 'programado',
              ferias: { create: [
                { inicio: new Date('2026-01-12'), fim: new Date('2026-02-01'), dias: 21 },
                { inicio: new Date('2026-05-06'), fim: new Date('2026-05-14'), dias: 9 },
              ] },
            },
          ],
        },
      },
    });
  }
  console.log('Seed concluído.');
}

main().catch((e) => { console.error(e); process.exit(1); }).finally(() => prisma.$disconnect());
