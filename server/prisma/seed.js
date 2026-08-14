// Seed mínimo: apenas os usuários de acesso (senha "demo").
// Idempotente — pode rodar em todo boot sem duplicar.
// Os colaboradores de demonstração (Carlos/Amanda) foram REMOVIDOS: os dados
// reais vêm da migração FORM 18 (backend/import/). Não recriar demo no seed —
// se a tabela ficasse vazia, o seed ressuscitaria a demo apagada.
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

  console.log('Seed concluído (apenas usuários de acesso).');
}

main().catch((e) => { console.error(e); process.exit(1); }).finally(() => prisma.$disconnect());
