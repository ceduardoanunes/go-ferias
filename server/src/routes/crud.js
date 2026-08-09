// Fábrica de rotas CRUD (list / create / update / delete) com proteção por papel,
// serialização para o formato do frontend e auditoria automática.
const express = require('express');
const prisma = require('../prisma');
const { requireAuth, requirePapel } = require('../auth');
const { auditar } = require('../audit');
const { limpo } = require('../serialize');

const asy = (fn) => (req, res) => fn(req, res).catch((e) => {
  console.error(e);
  res.status(400).json({ message: e.message });
});

function crudRouter({ model, tabela, serializar, desserializar, readRoles, writeRoles, orderBy }) {
  const r = express.Router();
  r.use(requireAuth);

  r.get('/', requirePapel(...readRoles), asy(async (req, res) => {
    const rows = await prisma[model].findMany(orderBy ? { orderBy } : undefined);
    res.json(rows.map(serializar));
  }));

  r.post('/', requirePapel(...writeRoles), asy(async (req, res) => {
    const row = await prisma[model].create({ data: limpo(desserializar(req.body)) });
    await auditar({ req, acao: 'inserir', tabela, registroId: row.id, depois: row });
    res.status(201).json(serializar(row));
  }));

  r.patch('/:id', requirePapel(...writeRoles), asy(async (req, res) => {
    const antes = await prisma[model].findUnique({ where: { id: req.params.id } });
    const row = await prisma[model].update({ where: { id: req.params.id }, data: limpo(desserializar(req.body)) });
    await auditar({ req, acao: 'atualizar', tabela, registroId: row.id, antes, depois: row });
    res.json(serializar(row));
  }));

  r.delete('/:id', requirePapel(...writeRoles), asy(async (req, res) => {
    const antes = await prisma[model].findUnique({ where: { id: req.params.id } });
    await prisma[model].delete({ where: { id: req.params.id } });
    await auditar({ req, acao: 'excluir', tabela, registroId: req.params.id, antes });
    res.status(204).end();
  }));

  return r;
}

module.exports = { crudRouter, asy };
