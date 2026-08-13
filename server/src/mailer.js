// Envio de e-mail via SMTP (nodemailer). Configuração vem do .env.
// Se o SMTP não estiver configurado, as funções apenas logam e não quebram o fluxo.
const nodemailer = require('nodemailer');

const {
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, SMTP_SECURE,
} = process.env;

let transporter = null;
if (SMTP_HOST) {
  transporter = nodemailer.createTransport({
    host: SMTP_HOST,
    port: Number(SMTP_PORT || 587),
    secure: String(SMTP_SECURE) === 'true', // true = porta 465
    auth: SMTP_USER ? { user: SMTP_USER, pass: SMTP_PASS } : undefined,
  });
}

async function enviarEmail({ para, assunto, html, texto }) {
  if (!transporter) {
    console.warn('[mailer] SMTP não configurado — e-mail NÃO enviado:', assunto, '→', para);
    return { enviado: false, motivo: 'smtp-nao-configurado' };
  }
  if (!para) return { enviado: false, motivo: 'sem-destinatario' };
  try {
    await transporter.sendMail({
      from: SMTP_FROM || SMTP_USER,
      to: para,
      subject: assunto,
      text: texto || undefined,
      html: html || undefined,
    });
    return { enviado: true };
  } catch (e) {
    console.error('[mailer] falha ao enviar:', e.message);
    return { enviado: false, motivo: e.message };
  }
}

// ---- modelos de mensagem ----
const fmt = (d) => (d ? new Date(d).toLocaleDateString('pt-BR') : '');

const emailSolicitacaoDecidida = (solic, aprovada) => ({
  assunto: aprovada ? 'Sua solicitação de folga foi aprovada ✓' : 'Sua solicitação de folga foi recusada',
  html: `
    <p>Olá, ${solic.nome || 'colaborador(a)'}!</p>
    <p>Sua solicitação de folga de <b>${fmt(solic.inicio)}</b> a <b>${fmt(solic.fim)}</b>
       (${solic.dias} dia(s)) foi <b>${aprovada ? 'APROVADA' : 'recusada'}</b>.</p>
    ${aprovada ? '<p>A folga já foi lançada no sistema.</p>' : ''}
    <p style="color:#6b7280;font-size:13px;margin-top:16px;border-top:1px solid #e5e7eb;padding-top:8px">
       ${aprovada ? 'Aprovada' : 'Recusada'} por <b>${solic.decididoPor || solic.decidido_por || '—'}</b>
       em <b>${fmt(solic.decididoEm || solic.decidido_em)}</b>.</p>
    <p>— Go Férias! · RH</p>`,
});

module.exports = { enviarEmail, emailSolicitacaoDecidida, smtpAtivo: !!transporter };
