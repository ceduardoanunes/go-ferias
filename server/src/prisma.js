// Cliente Prisma (instância única reaproveitada em toda a app)
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

module.exports = prisma;
