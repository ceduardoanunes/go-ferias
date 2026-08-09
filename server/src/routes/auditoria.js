// GET /auditoria?limit=500 → rh/admin
const express = require('express');
const prisma = require('../prisma');
const { requireAuth, requirePapel } = require('../auth');
const { asy } = require('./crud');
const ser = require('../serialize');

const router = express.Router();
router.use(requireAuth, requirePapel('admin', 'rh'));

router.get('/', asy(async (req, res) => {
  const limit = Math.min(Number(req.query.limit) || 500, 2000);
  const rows = await prisma.auditoria.findMany({ orderBy: { ts: 'desc' }, take: limit });
  res.json(rows.map(ser.auditoria));
}));

module.exports = router;
