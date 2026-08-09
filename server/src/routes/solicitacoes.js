// Solicitações de folga.
//   POST /solicitacoes            → PÚBLICO (colaborador pede sem login)
//   GET  /solicitacoes            → rh/admin
//   POST /solicitacoes/:id/decidir→ rh/admin (aprova/recusa; ao aprovar lança a
//                                     folga e envia e-mail ao colaborador)
const express = require('express');
const prisma = require('../prisma');
const { requireAuth, requirePapel } = require('../auth');
const { auditar } = require('../audit');
const { asy } = require('./crud');
const ser = require('../serialize');
const { enviarEmail, emailSolicitacaoDecidida } = require('../mailer');

const router = express.Router();

// --- envio público (sem autenticação) ---
router.post('/', asy(async (req, res) => {
  const b = req.body;
  if (!b.colaborador_id || !b.inicio) return res.status(400).json({ message: 'Selecione o colaborador e a data.' });
  const s = await prisma.solicitacao.create({
    data: {
      colaboradorId: b.colaborador_id, nome: b.nome || '', tipo: 'folga',
      inicio: new Date(b.inicio), fim: new Date(b.fim || b.inicio), dias: Number(b.dias || 1),
      motivo: b.motivo || '', avalCoordenador: !!b.aval_coordenador, status: 'pendente',
    },
  });
  res.status(201).json(ser.solicitacao(s));
}));

// --- daqui pra baixo, só logado ---
router.use(requireAuth);

router.get('/', requirePapel('admin', 'rh'), asy(async (req, res) => {
  const ss = await prisma.solicitacao.findMany({ orderBy: { criadoEm: 'desc' } });
  res.json(ss.map(ser.solicitacao));
}));

router.post('/:id/decidir', requirePapel('admin', 'rh'), asy(async (req, res) => {
  const aprovar = !!req.body.aprovar;
  const s = await prisma.solicitacao.findUnique({ where: { id: req.params.id } });
  if (!s || s.status !== 'pendente') return res.status(400).json({ message: 'Solicitação não encontrada ou já decidida.' });

  if (aprovar) {
    // escolhe o período: o que contém a data, senão o mais recente
    const pers = await prisma.periodoAquisitivo.findMany({
      where: { colaboradorId: s.colaboradorId }, orderBy: { inicio: 'desc' },
    });
    const per = pers.find((p) => p.inicio <= s.inicio && p.fim >= s.inicio) || pers[0];
    if (!per) return res.status(400).json({ message: 'Colaborador sem período aquisitivo — não foi possível lançar.' });
    await prisma.folga.create({
      data: { periodoId: per.id, inicio: s.inicio, fim: s.fim, dias: s.dias, obs: 'Solicitação aprovada' + (s.motivo ? ` — ${s.motivo}` : '') },
    });
  }

  const atual = await prisma.solicitacao.update({
    where: { id: s.id },
    data: { status: aprovar ? 'aprovada' : 'recusada', decididoEm: new Date(), decididoPor: req.usuario.nome },
  });
  await auditar({ req, acao: 'atualizar', tabela: 'solicitacoes', registroId: s.id, depois: { status: atual.status } });

  // e-mail ao colaborador (se tiver e-mail cadastrado)
  const colab = s.colaboradorId ? await prisma.colaborador.findUnique({ where: { id: s.colaboradorId } }) : null;
  const msg = emailSolicitacaoDecidida(atual, aprovar);
  const resultadoEmail = await enviarEmail({ para: colab?.email, assunto: msg.assunto, html: msg.html });

  res.json({ solicitacao: ser.solicitacao(atual), email: resultadoEmail });
}));

module.exports = router;
