# Rodar o backend no Windows 🪟

Mesma receita do Mac, com os ajustes do Windows. Objetivo: ver o backend
rodando e responder no navegador.

> ⏱️ Na primeira vez, ~20–30 min (a maior parte é o Docker baixando sozinho).

---

## Parte 1 — Instalar o Docker Desktop (uma vez)

1. No navegador (Edge serve), vá em **docker.com/products/docker-desktop**.
2. Baixe **"Download for Windows"**.
3. Rode o instalador (`Docker Desktop Installer.exe`). Deixe **marcado** o uso do
   **WSL 2** (é uma peça do Windows que o Docker precisa — o instalador ativa).
4. Ao final ele pode pedir para **reiniciar o PC**. Reinicie.
5. Abra o **Docker Desktop** (menu Iniciar → "Docker"). Aceite os termos.
6. Espere a **baleia 🐳 ficar verde/parada** no cantinho (perto do relógio).
   Verde = pronto.

> Se aparecer um aviso pedindo para **ativar a virtualização** ou instalar/atualizar
> o **WSL**, siga o que ele indicar (às vezes é só clicar num link e reiniciar).

---

## Parte 2 — Pegar o código

O jeito mais simples, sem instalar nada:

1. Abra **github.com/ceduardoanunes/go-ferias** (faça login com a conta que tem
   acesso ao repositório).
2. Clique no botão verde **"Code"** → **"Download ZIP"**.
3. Salve e **extraia** o ZIP numa pasta fácil, ex.: `Documentos`. Vai virar uma
   pasta tipo `go-ferias-main`.

> (Alternativa: copiar a pasta do projeto do Mac via pen drive / Google Drive.
> Se copiar, ignore as pastas `node_modules` — não precisam ir.)

---

## Parte 3 — Ligar

1. Confirme que o **Docker Desktop está aberto** e a baleia está verde.
2. Abra o **PowerShell** (menu Iniciar → digite "PowerShell" → Enter).
3. Entre na pasta `server` do projeto (ajuste o caminho para onde você extraiu):
   ```powershell
   cd "$HOME\Documents\go-ferias-main\server"
   ```
4. Crie o arquivo de configuração (já vem pronto para teste local):
   ```powershell
   copy .env.example .env
   ```
5. Suba tudo (primeira vez demora, baixa as imagens):
   ```powershell
   docker compose up -d --build
   ```

---

## Parte 4 — Ver funcionando ✅

- **No navegador:** abra **http://localhost:3000/health**
  → deve aparecer `{"ok":true,"smtp":false}`. É o backend vivo!
- **No Docker Desktop:** aba **"Containers"** → grupo **`server`** com **`api`** e
  **`db`** verdes = rodando.
- **Segurança (bônus):** abra **http://localhost:3000/colaboradores** →
  `{"message":"Não autenticado"}`. Isso é o sistema **te barrando** sem login — é
  o esperado.

Login de teste (se for testar o app inteiro): **admin@goegrow.com.br** / **demo**.

---

## Ligar / desligar depois

```powershell
cd "$HOME\Documents\go-ferias-main\server"
docker compose up -d      # liga
docker compose down       # desliga (dados ficam salvos)
```
Ou use os botões **Start/Stop** no Docker Desktop, no grupo `server`.

## Se travar 🩹

| Aconteceu | Faça |
|---|---|
| "Docker daemon not running" | Abra o Docker Desktop e espere a baleia ficar verde. |
| Pediu WSL / virtualização | Siga o link que ele mostra e reinicie o PC. |
| Porta 3000 ocupada | No `.env`, adicione a linha `API_PORT=3001` e suba de novo; teste em `http://localhost:3001/health`. |
| Mudei algo e não surtiu efeito | `docker compose down -v` e depois `docker compose up -d --build` (recria do zero). |

Deu um erro que não está aqui? Me manda a mensagem que eu ajudo.
