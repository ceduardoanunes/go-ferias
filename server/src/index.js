// Servidor Express do Go Férias! (Node + Prisma).
require('dotenv').config();
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');
const express = require('express');
const cors = require('cors');

// Aplica migrations pendentes ANTES de tudo, toda vez que o processo sobe —
// não depende de ninguém lembrar de rodar `npx prisma migrate deploy` à
// parte (rodar via Docker, PM2, tarefa agendada ou só "node src/index.js"
// dá na mesma). Se falhar, o processo para aqui: melhor não subir do que
// subir servindo com o schema desatualizado (foi o que quebrou a listagem
// de colaboradores em 22/09 — coluna nova sem migration aplicada).
try {
  execSync('npx prisma migrate deploy', { cwd: path.join(__dirname, '..'), stdio: 'inherit' });
} catch (e) {
  console.error('Falha ao aplicar migrations do banco — API não vai subir. Corrija o banco antes de tentar de novo.');
  process.exit(1);
}

const ser = require('./serialize');
const { crudRouter } = require('./routes/crud');
const { smtpAtivo } = require('./mailer');

const app = express();
app.use(cors());
app.use(express.json({ limit: '5mb' })); // fotos em base64 podem ser grandes

// saúde
app.get('/health', (req, res) => res.json({ ok: true, smtp: smtpAtivo }));

// autenticação
app.use('/auth', require('./routes/auth'));

// recursos simples (CRUD com papel)
app.use('/colaboradores', crudRouter({
  model: 'colaborador', tabela: 'colaboradores',
  serializar: ser.colaborador, desserializar: ser.paraPrisma.colaboradores,
  readRoles: ['admin', 'rh', 'leitura'], writeRoles: ['admin'], orderBy: { nome: 'asc' },
}));
app.use('/periodos_aquisitivos', crudRouter({
  model: 'periodoAquisitivo', tabela: 'periodos_aquisitivos',
  serializar: ser.periodo, desserializar: ser.paraPrisma.periodos,
  readRoles: ['admin', 'rh', 'leitura'], writeRoles: ['admin', 'rh'],
}));
app.use('/ferias_oficiais', crudRouter({
  model: 'feriasOficial', tabela: 'ferias_oficiais',
  serializar: ser.lancamento, desserializar: ser.paraPrisma.lancamentos,
  readRoles: ['admin', 'rh', 'leitura'], writeRoles: ['admin', 'rh'],
}));
app.use('/folgas', crudRouter({
  model: 'folga', tabela: 'folgas',
  serializar: ser.lancamento, desserializar: ser.paraPrisma.lancamentos,
  readRoles: ['admin', 'rh', 'leitura'], writeRoles: ['admin', 'rh'],
}));
app.use('/notas', crudRouter({
  model: 'nota', tabela: 'notas',
  serializar: ser.nota, desserializar: ser.paraPrisma.notas,
  readRoles: ['admin', 'rh', 'leitura'], writeRoles: ['admin', 'rh'], orderBy: { criadoEm: 'desc' },
}));

// recursos com regra especial
app.use('/usuarios', require('./routes/usuarios'));
app.use('/solicitacoes', require('./routes/solicitacoes'));
app.use('/auditoria', require('./routes/auditoria'));

// Frontend (arquivo único). Em produção (Render) o index.html fica na raiz do repo,
// então a mesma URL entrega o site e a API. Se não existir (ex.: Docker só da API), ignora.
const FRONT = path.join(__dirname, '..', '..', 'index.html');
if (fs.existsSync(FRONT)) {
  app.get('/', (req, res) => res.sendFile(FRONT));
}

// 404
app.use((req, res) => res.status(404).json({ message: 'Rota não encontrada' }));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Go Férias! API rodando na porta ${PORT}  (SMTP ${smtpAtivo ? 'ativo' : 'não configurado'})`);
});
