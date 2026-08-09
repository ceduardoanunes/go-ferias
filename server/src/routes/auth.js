// POST /auth/login  → { token, nome, email, papel }
// GET  /auth/me     → dados do usuário logado
const express = require('express');
const prisma = require('../prisma');
const { conferirSenha, gerarToken, requireAuth } = require('../auth');
const { auditar } = require('../audit');
const { asy } = require('./crud');

const router = express.Router();

router.post('/login', asy(async (req, res) => {
  const email = String(req.body.email || '').trim().toLowerCase();
  const senha = String(req.body.senha || '');
  const u = await prisma.usuario.findUnique({ where: { email } });
  if (!u || !(await conferirSenha(senha, u.senhaHash))) {
    await auditar({ acao: 'login_falhou', detalhe: `Credenciais inválidas para ${email}` });
    return res.status(401).json({ message: 'E-mail ou senha inválidos' });
  }
  const token = gerarToken(u);
  await auditar({ req: { usuario: u }, acao: 'login', detalhe: 'Acesso ao sistema' });
  res.json({ token, nome: u.nome, email: u.email, papel: u.papel });
}));

router.get('/me', requireAuth, (req, res) => {
  const { nome, email, papel } = req.usuario;
  res.json({ nome, email, papel });
});

module.exports = router;
