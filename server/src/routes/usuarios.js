// Usuários — só admin. Senha nunca em texto: criada/alterada com hash aqui.
const express = require('express');
const prisma = require('../prisma');
const { requireAuth, requirePapel, hashSenha } = require('../auth');
const { auditar } = require('../audit');
const { asy } = require('./crud');
const ser = require('../serialize');

const router = express.Router();
router.use(requireAuth, requirePapel('admin'));

router.get('/', asy(async (req, res) => {
  const us = await prisma.usuario.findMany({ orderBy: { nome: 'asc' } });
  res.json(us.map(ser.usuario));
}));

router.post('/', asy(async (req, res) => {
  const { nome, email, senha, papel, foto } = req.body;
  if (!nome || !email || !senha) return res.status(400).json({ message: 'Nome, e-mail e senha são obrigatórios.' });
  const existe = await prisma.usuario.findUnique({ where: { email: email.toLowerCase() } });
  if (existe) return res.status(409).json({ message: 'Já existe um usuário com este e-mail.' });
  const u = await prisma.usuario.create({
    data: { nome, email: email.toLowerCase(), senhaHash: await hashSenha(senha), papel, foto: foto || null },
  });
  await auditar({ req, acao: 'inserir', tabela: 'usuarios', registroId: u.id, depois: { nome, email, papel } });
  res.status(201).json(ser.usuario(u));
}));

router.patch('/:id', asy(async (req, res) => {
  const { nome, papel, foto, senha } = req.body;
  const data = ser.limpo({ nome, papel, foto });
  if (senha) data.senhaHash = await hashSenha(senha); // troca de senha opcional
  const u = await prisma.usuario.update({ where: { id: req.params.id }, data });
  await auditar({ req, acao: 'atualizar', tabela: 'usuarios', registroId: u.id, depois: { nome: u.nome, papel: u.papel } });
  res.json(ser.usuario(u));
}));

router.delete('/:id', asy(async (req, res) => {
  const alvo = await prisma.usuario.findUnique({ where: { id: req.params.id } });
  if (alvo && alvo.email === req.usuario.email) {
    return res.status(400).json({ message: 'Você não pode remover o próprio acesso.' });
  }
  await prisma.usuario.delete({ where: { id: req.params.id } });
  await auditar({ req, acao: 'excluir', tabela: 'usuarios', registroId: req.params.id, antes: alvo && { nome: alvo.nome, email: alvo.email } });
  res.status(204).end();
}));

module.exports = router;
