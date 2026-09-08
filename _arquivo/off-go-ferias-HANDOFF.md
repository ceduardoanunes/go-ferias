# Go Férias — Handoff de continuação

> Cole este arquivo numa nova sessão do Claude Code (no Windows) para retomar o contexto.
> Abra o Claude na mesma pasta onde estiver o `go-ferias_6.html`.

## O projeto
- **Arquivo único**: `go-ferias_6.html` — app de gestão de férias/folgas da **Go & Grow** (HTML+CSS+JS puro, ~3700 linhas).
- **Sem backend**: usa `localStorage` (modo demo). Login demo: `admin@goegrow.com.br` / senha `demo` (admin vê tudo, incl. "Minha Conta"). Também `rh@...` e `consulta@...`.
- **Marca/paleta**: creme `#F2F1EE`, grafite `#1C1B1A`, vermelho `#C4193B` (férias), teal/verde `#12836A` (folga), âmbar `#B4720A`, azul `#2F5FA8`. Fonte DM Sans.
- **Estrutura**: sidebar preta de ícones + views (Dashboard, Agenda, Calendário, Colaboradores, Relatórios, Perfil, Minha Conta). Ordem do menu: Dashboard → Agenda → Calendário → Colaboradores → Relatórios. Abre no **Dashboard** por padrão (rota `#/dashboard`; Colaboradores virou `#/colaboradores`).

## O que foi feito nesta sessão (redesign do DASHBOARD, `#viewDash`)
Redesenhado do zero inspirado em referências que o usuário mandou (Smart Home, Crowz, Invo, Healthcare). Estado atual:
- **Banner de boas-vindas** (`.dx-hero`): fundo creme/pêssego, saudação + data + resumo + totais (27/17/10), e uma **ilustração SVG animada** de rede sob palmeiras (`.dx-hero-art`): palmeiras com folíolos + cocos, sol com raios, pessoa na rede, areia. Animações CSS: `.dx-hammock` (balança), `.dx-crown-l/.dx-crown-r` (folhas), `.dx-sun-glow` (pulsa), `.dx-cloud` (flutua). Respeita `prefers-reduced-motion`.
- **4 tiles coloridos de KPI** (`.dx-kpi` c-teal/c-amber/c-blue/c-red): Ausentes hoje / na semana / no mês / Férias vencendo, com fotos (mini-avatares com anel vermelho=férias, verde=folga).
- **Calendário SEMANAL** (`.dx-week-card`): 7 dias (Seg–Dom), dia atual destacado, avatares dos ausentes sob cada dia, navegação por semana. (substituiu o mensal)
- **Card "Próximos meses"** (`#dxForecast`): próximos 6 meses com quantas pessoas já têm férias marcadas (barra + avatares + número).
- **Coluna lateral** (`.dashx-aside`): "Ausentes hoje" (membros), "Férias vencendo" (lista), e gráfico **"Ausências por mês"** = barras com o mês de pico destacado em vermelho + **bolha de tooltip** flutuante (estilo Invo) + número grande.

## Detalhes que podem confundir
- `.dash-card`/`.dash-card-title` são usados também nos **Relatórios** — não reduzir globalmente (o dash usa `#viewDash .dash-card-title` menor).
- Bug conhecido de SVG: animação CSS (`transform`) num `<g>` **sobrescreve** o `transform="translate()"` do atributo. Solução usada: aninhar grupos (grupo externo posiciona, grupo interno anima).
- Mini-avatares: `.mini-av.tipo-ferias` = anel vermelho, `.tipo-folga` = anel verde (aplicado no sistema todo).

## Como testar (headless, com auto-login)
```bash
# copia o arquivo e injeta uma sessão demo antes do IIFE final "(async function(){"
# depois serve e tira screenshot com Chrome headless:
python3 -m http.server 8080 &
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --screenshot=out.png --window-size=1440,1200 "http://localhost:8080/go-ferias_6.html#/dashboard"
```
(No Windows: `chrome.exe --headless=new --screenshot=out.png ...`) A sessão demo é gravada em `sessionStorage["goferias_sessao"]`.

## Possíveis próximos passos / pendências
- Refinar mais a ilustração/animação do banner se necessário (tamanho, velocidade).
- O usuário gostou da direção "colorida/amigável" das referências; manter esse estilo nas demais telas se for evoluir.
- Nada quebrado conhecido; JS balanceado (chaves/parênteses conferidos).

## Referências visuais usadas (para o estilo)
1. Smart Home Dashboard (tiles coloridos + banner com ilustração + card de membros).
2. Crowz / Invo (stats com tendência, gráfico com **bolha** de destaque num ponto).
3. Healthcare dashboard (o **calendário semanal** em faixa de dias).
