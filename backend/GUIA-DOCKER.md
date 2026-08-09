# Guia: como "ligar o backend na tomada" 🔌

Passo a passo pra você (no Mac) subir o backend e ver o app rodando com um banco
de dados de verdade. Não precisa saber programar — é copiar, colar e apertar Enter.

> ⏱️ Tempo total: ~15 minutos (a maior parte é o Docker baixando coisas sozinho).

---

## Antes de começar

Você vai usar duas coisas do Mac:
- **O Docker Desktop** (a "caixa mágica" que sobe o banco + o atendente + o site).
- **O Terminal** (aquela telinha preta onde a gente digita comandos). Pra abrir:
  aperte `Cmd + Espaço`, digite **Terminal**, aperte Enter.

Quando este guia disser "rode isto", significa: copie a linha, cole no Terminal
e aperte **Enter**.

---

## Parte 1 — Instalar o Docker (uma vez só)

1. Abra o navegador e procure por **"Docker Desktop Mac"** (site oficial: docker.com).
2. Baixe o Docker Desktop para Mac. **Atenção ao chip:** se seu Mac é mais novo
   (M1/M2/M3/M4), escolha **Apple Silicon**; se for mais antigo, **Intel**.
   (Pra saber: menu 🍎 → "Sobre este Mac".)
3. Abra o arquivo baixado e **arraste o ícone da baleia 🐳 para a pasta Aplicativos**.
4. Abra o **Docker** (Cmd+Espaço → "Docker" → Enter). Na primeira vez ele pede
   permissões — pode aceitar.
5. **Espere a baleia 🐳 ficar parada** lá em cima na barra do Mac (perto do relógio).
   Baleia parada = Docker pronto. Se estiver "andando"/animada, espere terminar.

> ✅ Como saber que deu certo: abra o Terminal e rode:
> ```bash
> docker --version
> ```
> Se aparecer algo tipo `Docker version 27...`, está instalado.

---

## Parte 2 — Preparar os "segredos" (.env)

O backend precisa de umas senhas. Vamos criar o arquivo de segredos.

1. No Terminal, entre na pasta do backend (copie a linha inteira, com as aspas):
   ```bash
   cd "/Users/gogrow/Downloads/Go! Férias/backend"
   ```
2. Crie o arquivo de segredos a partir do exemplo:
   ```bash
   cp .env.example .env
   ```
3. Gere um segredo forte pro "crachá" (JWT) e já jogue no arquivo:
   ```bash
   echo "JWT_SECRET=$(openssl rand -base64 48)" >> .env
   ```
4. Abra o arquivo pra ajustar as senhas:
   ```bash
   open -e .env
   ```
   Vai abrir no TextEdit. Troque os valores que começam com `troque-...`:
   - `POSTGRES_PASSWORD=` → invente uma senha (ex.: `senhadobanco123`)
   - `AUTHENTICATOR_PASSWORD=` → invente outra (ex.: `senhaatendente123`)
   - `JWT_SECRET=` → **vai aparecer DUAS vezes**; apague a linha antiga
     (a que tem `troque-por-um-segredo...`) e deixe só a nova, gigante, que o
     comando do passo 3 criou.

   Salve (`Cmd + S`) e feche.

> 💡 Não precisa decorar essas senhas. Elas ficam só entre as peças do backend.
> E o arquivo `.env` **não vai pro GitHub** (já está protegido).

---

## Parte 3 — Subir tudo (1 comando)

Ainda na pasta `backend`, rode:
```bash
docker compose up -d
```

Na **primeira vez** ele baixa o Postgres, o PostgREST e o nginx (uns minutos).
Quando terminar, aparece algo como `Started` / `Running` em 3 linhas.

Pra acompanhar a preparação do banco (opcional):
```bash
docker compose logs -f db
```
(pra sair de acompanhar os logs, aperte `Ctrl + C` — isso **não** desliga nada.)

---

## Parte 4 — Ver funcionando

Abra no navegador:

- **O app:** <http://localhost:8080>
- Faça login com **admin@goegrow.com.br** / senha **demo**.

Quer um teste rapidinho de que o backend responde? Rode no Terminal:
```bash
curl -s http://localhost:3000/rpc/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@goegrow.com.br","senha":"demo"}'
```
Se voltar um monte de texto com `"token":"..."`, o cofre está funcionando. 🎉

---

## Parte 5 — Ligar o APP no backend (o "virar a chave")

Por padrão o app ainda usa o "caderninho no bolso" (modo local). Pra ele usar o
armário novo, troque **uma palavra** no `index.html`:

1. Abra o arquivo:
   ```bash
   open -e "/Users/gogrow/Downloads/Go! Férias/index.html"
   ```
   (o TextEdit pode demorar a abrir, é um arquivo grande.)
2. Aperte `Cmd + F`, procure por:  `driver: 'local'`
3. Troque só a palavra `local` por `postgrest`, ficando:  `driver: 'postgrest',`
4. Salve (`Cmd + S`).
5. Recarregue <http://localhost:8080> no navegador.

Agora tudo que você fizer (editar, aprovar, cadastrar) é salvo no banco de verdade.

> Pra voltar ao modo caderninho, é só trocar `postgrest` de volta por `local`.

---

## Se der problema 🩹

| O que aconteceu | O que fazer |
|---|---|
| "Cannot connect to the Docker daemon" | A baleia 🐳 não está pronta. Abra o Docker Desktop e espere ela parar. |
| Porta 8080/3000/5432 "already in use" | Algo já usa a porta. Rode `docker compose down`, feche outros programas e suba de novo. |
| Mudei um arquivo em `sql/` e não surtiu efeito | Os scripts só rodam na 1ª vez. Rode `docker compose down -v && docker compose up -d` (o `-v` recria o banco do zero). |
| Login não funciona / app vazio | Confira que fez a Parte 5 (trocar pra `postgrest`) e recarregou a página. |
| Quero recomeçar do absoluto zero | `docker compose down -v` apaga o banco; `docker compose up -d` monta tudo de novo. |

Deu um erro que não está na tabela? Copie a mensagem e me manda — eu conserto.

---

## Comandos úteis (guarde)

```bash
cd "/Users/gogrow/Downloads/Go! Férias/backend"

docker compose up -d        # liga o backend
docker compose down         # desliga (mantém os dados)
docker compose down -v      # desliga e APAGA os dados (recomeça limpo)
docker compose ps           # mostra o que está rodando
docker compose logs -f      # acompanha o que está acontecendo
```

Desligar o backend **não apaga nada** (só `down -v` apaga). Pode ligar e desligar
à vontade.
