# Go Férias! — instruções pra subir no servidor

Sistema de controle de férias/folgas da empresa. Estava rodando no Render
(plano grátis, expirou) — agora precisa subir no servidor interno.

Este zip tem: este arquivo, o snapshot dos dados reais (`saida_render/`), o
script que carrega esses dados (`carregar_no_local.py`) e o handoff técnico
completo (`PARA-O-TI.md`).

O **código** está no GitHub: `github.com/ceduardoanunes/go-ferias` (peça
acesso ao Carlos, se ainda não tiver).

---

## Passo 1 — Pegar o código

```bash
git clone https://github.com/ceduardoanunes/go-ferias.git
cd go-ferias/server
```

## Passo 2 — Configurar

```bash
cp .env.example .env
```

Abra o `.env` e troque:
- `POSTGRES_PASSWORD` — uma senha forte
- `DATABASE_URL` — mesma senha, no formato que já está lá
- `JWT_SECRET` — uma string aleatória longa (`openssl rand -base64 48`)
- `SMTP_*` — se quiser que os e-mails de aprovação/recusa de folga saiam,
  senão deixe `SMTP_HOST` vazio (o sistema funciona sem, só não manda e-mail)

## Passo 3 — Subir

Precisa de **Docker** instalado. Depois:

```bash
docker compose up -d --build
curl http://localhost:3000/health
```

Deve responder `{"ok":true,...}`. Isso sobe o Postgres + a API + o site,
tudo junto, ainda **vazio** (só o usuário de teste do seed:
`admin@goegrow.com.br` / `demo`).

## Passo 4 — Carregar os dados reais

```bash
cd ../backend/import       # a pasta que veio dentro deste mesmo zip
py carregar_no_local.py --url http://localhost:3000
```

(Ajuste a URL se o servidor não for local — ex.: `http://10.0.0.5:3000`.)

Isso recria os 111 colaboradores e todo o histórico (períodos, férias,
folgas, notas) a partir do `saida_render/` que está neste zip. Roda uma
vez só — rodar de novo contra o mesmo banco duplica os dados.

## Passo 5 — Usuários de verdade

O login de admin/RH **não migra com senha** (a API antiga nunca guarda a
senha em texto nem devolve o hash). Entre com `admin@goegrow.com.br` / `demo`,
**troque essa senha** e cadastre os acessos reais em **Minha Conta → Usuários**.

## Depois disso (não trava o uso, mas fica pendente)

- Backup do Postgres (rotina — o Render tinha o dele próprio, esse precisa de um)
- HTTPS / domínio interno
- `cors()` da API restrito ao domínio final (hoje está aberto)

## Dúvida?

`PARA-O-TI.md` (neste zip) tem o detalhe técnico completo — endpoints,
estrutura do código, o que cada coisa faz. Qualquer travamento, chama o
Carlos.
