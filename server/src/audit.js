// Grava linhas de auditoria. Chamado pelas rotas após inserir/atualizar/excluir.
const prisma = require('./prisma');

async function auditar({ req, acao, tabela, registroId, detalhe, antes, depois }) {
  try {
    await prisma.auditoria.create({
      data: {
        usuarioNome: req?.usuario?.nome || null,
        usuarioEmail: req?.usuario?.email || null,
        acao,
        tabela: tabela || null,
        registroId: registroId || null,
        detalhe: detalhe || null,
        dadosAntes: antes || undefined,
        dadosDepois: depois || undefined,
      },
    });
  } catch (e) {
    console.error('[audit] falha ao registrar:', e.message);
  }
}

module.exports = { auditar };
