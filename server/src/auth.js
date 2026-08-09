// Autenticação: hash de senha (bcrypt), emissão/validação de JWT e middlewares
// de proteção por papel (admin / rh / leitura).
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'troque-este-segredo';
const JWT_EXPIRA = process.env.JWT_EXPIRA || '12h';

const hashSenha = (senha) => bcrypt.hash(senha, 10);
const conferirSenha = (senha, hash) => bcrypt.compare(senha, hash);

function gerarToken(usuario) {
  return jwt.sign(
    { sub: usuario.id, nome: usuario.nome, email: usuario.email, papel: usuario.papel },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRA }
  );
}

// exige um token válido; popula req.usuario
function requireAuth(req, res, next) {
  const h = req.headers.authorization || '';
  const token = h.startsWith('Bearer ') ? h.slice(7) : null;
  if (!token) return res.status(401).json({ message: 'Não autenticado' });
  try {
    req.usuario = jwt.verify(token, JWT_SECRET);
    next();
  } catch {
    res.status(401).json({ message: 'Sessão inválida ou expirada' });
  }
}

// exige que o papel do usuário esteja entre os permitidos
const requirePapel = (...papeis) => (req, res, next) => {
  if (!req.usuario) return res.status(401).json({ message: 'Não autenticado' });
  if (!papeis.includes(req.usuario.papel)) {
    return res.status(403).json({ message: 'Sem permissão para esta ação' });
  }
  next();
};

module.exports = { hashSenha, conferirSenha, gerarToken, requireAuth, requirePapel, JWT_SECRET };
