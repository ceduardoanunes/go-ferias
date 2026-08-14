// Serializadores: convertem os objetos do Prisma (camelCase, datas como Date)
// para o MESMO formato que o frontend já consome (snake_case, datas 'YYYY-MM-DD').
// Assim a integração com o app existente fica direta.

const dia = (d) => (d instanceof Date ? d.toISOString().slice(0, 10) : d || null); // só data
const ts = (d) => (d instanceof Date ? d.toISOString() : d || null); // data+hora

const colaborador = (c) => c && ({
  id: c.id, nome: c.nome, email: c.email || null, funcao: c.funcao,
  departamento: c.departamento, unidade: c.unidade, regime: c.regime,
  admissao: dia(c.admissao), foto: c.foto || null, ativo: c.ativo,
});

const periodo = (p) => p && ({
  id: p.id, colaborador_id: p.colaboradorId, inicio: dia(p.inicio), fim: dia(p.fim),
  situacao: p.situacao, pago_em: dia(p.pagoEm),
});

const lancamento = (f) => f && ({
  id: f.id, periodo_id: f.periodoId, inicio: dia(f.inicio), fim: dia(f.fim),
  dias: f.dias, obs: f.obs || '',
});

const solicitacao = (s) => s && ({
  id: s.id, colaborador_id: s.colaboradorId, nome: s.nome, tipo: s.tipo,
  inicio: dia(s.inicio), fim: dia(s.fim), dias: s.dias, motivo: s.motivo || '',
  aval_coordenador: s.avalCoordenador, status: s.status,
  criado_em: ts(s.criadoEm), decidido_em: ts(s.decididoEm), decidido_por: s.decididoPor || null,
});

const nota = (n) => n && ({
  id: n.id, colaborador_id: n.colaboradorId, periodo_id: n.periodoId || null,
  categoria: n.categoria, texto: n.texto, data: dia(n.data), criado_em: ts(n.criadoEm),
});

const usuario = (u) => u && ({ // NUNCA inclui senhaHash
  id: u.id, nome: u.nome, email: u.email, papel: u.papel, foto: u.foto || null,
  criado_em: ts(u.criadoEm),
});

const auditoria = (a) => a && ({
  id: a.id, ts: ts(a.ts), usuario_nome: a.usuarioNome, usuario_email: a.usuarioEmail,
  acao: a.acao, tabela: a.tabela, registro_id: a.registroId, detalhe: a.detalhe,
  dados_antes: a.dadosAntes, dados_depois: a.dadosDepois,
});

// converte o corpo (snake_case, vindo do frontend) para o formato do Prisma (camelCase)
const paraPrisma = {
  // obs: passamos undefined (não null) p/ campos ausentes, para que `limpo()` os
  // remova e um PATCH parcial não zere colunas não enviadas. `null` explícito limpa.
  colaboradores: (b) => ({
    nome: b.nome, email: b.email, funcao: b.funcao, departamento: b.departamento,
    unidade: b.unidade, regime: b.regime,
    admissao: b.admissao ? new Date(b.admissao) : undefined,
    foto: b.foto, ativo: b.ativo,
  }),
  periodos: (b) => ({
    colaboradorId: b.colaborador_id, inicio: b.inicio ? new Date(b.inicio) : undefined,
    fim: b.fim ? new Date(b.fim) : undefined, situacao: b.situacao,
    pagoEm: b.pago_em ? new Date(b.pago_em) : (b.pago_em === null ? null : undefined),
  }),
  lancamentos: (b) => ({
    periodoId: b.periodo_id, inicio: b.inicio ? new Date(b.inicio) : undefined,
    fim: b.fim ? new Date(b.fim) : undefined, dias: b.dias, obs: b.obs,
  }),
  solicitacoes: (b) => ({
    colaboradorId: b.colaborador_id, nome: b.nome, tipo: b.tipo,
    inicio: b.inicio ? new Date(b.inicio) : undefined, fim: b.fim ? new Date(b.fim) : undefined,
    dias: b.dias, motivo: b.motivo, avalCoordenador: b.aval_coordenador,
    status: b.status, decididoEm: b.decidido_em ? new Date(b.decidido_em) : undefined,
    decididoPor: b.decidido_por,
  }),
  notas: (b) => ({
    colaboradorId: b.colaborador_id,
    periodoId: b.periodo_id === undefined ? undefined : (b.periodo_id || null),
    categoria: b.categoria, texto: b.texto,
    data: b.data ? new Date(b.data) : (b.data === null ? null : undefined),
  }),
};

// remove chaves undefined (para PATCH parcial não sobrescrever com undefined)
const limpo = (obj) => Object.fromEntries(Object.entries(obj).filter(([, v]) => v !== undefined));

module.exports = {
  colaborador, periodo, lancamento, solicitacao, nota, usuario, auditoria,
  paraPrisma, limpo,
};
