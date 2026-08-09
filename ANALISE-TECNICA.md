# Análise Técnica — Go Férias!

> Avaliação completa do sistema (`index.html`, arquivo único de ~6.792 linhas / ~1,5 MB).
> Foco técnico e realista: segurança, bugs, consistência funcional, UI/UX, design e arquitetura.
> Data da análise: 2026-08-09. · Atualizado após correção do item 3.1 (permissão de cadastro).

---

## Resumo executivo

O Go Férias! é um app de gestão de férias/folgas **bem acabado na camada visual** — sistema de cards coerente, paleta de marca consistente, ilustrações, autocompletes navegáveis por teclado, export PDF com cabeçalho/rodapé da marca. A qualidade de **craft de UI está acima da média** para uma ferramenta interna.

Os riscos reais **não estão no visual**, e sim em três frentes:

1. **Modelo de segurança** — só é aceitável porque o sistema é projetado para migrar ao backend PostgREST/JWT. No modo `local` (o ativo hoje), a segurança é praticamente nula.
2. **Integridade de dados** — alguns campos permitem gravar valores incoerentes (dias que não batem com o intervalo de datas) e há um bug latente de fuso horário.
3. **Consistência funcional** — a divisão de permissões RH × Admin está incoerente, e o caminho de persistência do formulário público não funciona no modo backend.

Nenhum desses impede a demo de rodar. Todos importam antes de um uso real multiusuário.

**Nota geral por área:**

| Área | Nota | Comentário |
|------|------|-----------|
| Design visual / craft de UI | ★★★★★ | Coeso, de marca, detalhista |
| UX / fluxos | ★★★★☆ | Bons fluxos; faltam feedbacks de erro/permissão |
| Segurança | ★★☆☆☆ | OK só como demo; depende 100% do backend futuro |
| Correção / bugs | ★★★☆☆ | Escaping sólido; falhas de integridade e fuso |
| Acessibilidade | ★★☆☆☆ | Base fraca (ARIA, foco, contraste) |
| Arquitetura / manutenção | ★★★☆☆ | Monólito intencional; duplicações e código morto |

---

## 1. Segurança

### 1.1 [CRÍTICO — produção] Senhas em texto puro
`Store.data.usuarios` (e `Auth.demoUsers`) guardam o campo `senha` em **texto puro** no localStorage. Qualquer pessoa com acesso ao dispositivo lê todas as senhas pelo DevTools. Só é mitigado ao trocar para o driver `postgrest` (login via `/rpc/login` com JWT). O driver ativo hoje é o `local`.
- **Local:** `Store` (linha ~3071), `Auth.demoUsers` (linha ~3188), `salvarUsuario` (linha ~4428).
- **Recomendação:** nunca usar o modo `local` para dados reais de pessoas; a autenticação real precisa ser 100% no backend.

### 1.2 [ALTO] Sessão e permissões só no cliente
A sessão é um JSON em `sessionStorage` com validade de 12h e **sem assinatura** — trivial de forjar (foi exatamente o que fiz para gerar os screenshots desta análise). Todos os checks (`podeEditar`, `podeAdministrar`, etc.) rodam no cliente e são contornáveis pelo console no modo local.
- **Local:** `Auth.restore/persist` (linha ~3194), `Auth.pode*` (linha ~3241).
- **Recomendação:** aceitável só para demo local single-user. Em uso real, a autorização precisa ser reforçada pelo backend (RLS no Postgres / PostgREST).

### 1.3 [MÉDIO] Exposição de dados a visitantes não autenticados
O formulário público "Solicitar folga" (antes do login) faz **autocomplete do diretório inteiro de colaboradores ativos** (nome, cargo, setor) para qualquer visitante anônimo, e aceita solicitações ilimitadas para qualquer pessoa, sem rate-limit nem captcha. Superfície de **enumeração de funcionários + spam**.
- **Local:** `wireSolicPublic` (linha ~6690).
- **Recomendação:** exigir algum dado de verificação, limitar taxa, e não devolver a lista completa no autocomplete público.

### 1.4 [BAIXO] Credenciais de demo impressas na tela de login
"Modo demonstração — use rh@goegrow.com.br / senha demo" aparece na tela de login. Remover antes de qualquer deploy real.

### 1.5 [POSITIVO] Proteção contra XSS está sólida
`esc()` (linha ~2935) é um escapador de entidades HTML correto e é aplicado de forma **consistente** a todos os campos digitados pelo usuário (nome, função, obs, motivo) antes de irem para `innerHTML`. O `toast()` usa `textContent`. Não encontrei injeção de dado de usuário sem escape nas telas.

---

## 2. Bugs / Correção

### 2.1 [MÉDIO — latente] Bug de fuso horário em `iso()`
`iso(d) = d.toISOString().slice(0,10)` serializa em **UTC**, enquanto `pd()` constrói datas em **hora local**. O round-trip só é correto em fusos **iguais ou a oeste de UTC** (seguro no Brasil, UTC-3). A leste de UTC (UTC+x), as datas deslocam **-1 dia**.
- **Local:** `iso` (linha 2922), `pd` (linha 2923).
- **Recomendação:** montar o ISO a partir de `getFullYear/getMonth/getDate` locais, não de `toISOString()`. Latente hoje, mas quebra silenciosamente se algum usuário estiver em fuso positivo.

### 2.2 [MÉDIO] `dias` pode contradizer o intervalo de datas
Nos lançamentos (`salvarLanc`, `salvarEdicaoLanc`), o campo "dias" é um número livre. O modal auto-preenche a partir das datas, mas o usuário **pode sobrescrever** para qualquer valor — não há validação de que `dias` corresponde a início→fim. Resultado: registros incoerentes (ex.: intervalo de 3 dias gravado como 30) que depois alimentam os cálculos de saldo e os relatórios.
- **Local:** `salvarLanc` (linha ~4269), `salvarEdicaoLanc` (linha ~4395).
- **Recomendação:** validar/forçar `dias` contra o intervalo, ou torná-lo somente-leitura derivado das datas.

### 2.3 [MÉDIO] Solicitações públicas se perdem no caminho PostgREST
`wireSolicPublic` empurra direto para `Store.data.solicitacoes` e chama `Store.save()`, que é **no-op quando `driver!=='local'`**. No modo produção (postgrest) pretendido, as solicitações públicas **nunca persistem** no backend — somem no reload. Esse caminho de escrita não foi abstraído como os demais (`Store.insert`).
- **Local:** `wireSolicPublic` submit (linha ~6744), `Store.save` (linha 3085).

### 2.4 [BAIXO] Sem tratamento de erro global
Não há `window.onerror` nem `unhandledrejection`. Uma exceção dentro de qualquer render deixa a view parcial/vazia sem nenhum aviso ao usuário.
- **Recomendação:** um handler global que ao menos dispara um `toast` de "algo deu errado".

### 2.5 [BAIXO] `migrarNovosSetores` injeta pessoas fictícias no init
Conveniência de seed que insere **3 colaboradores fictícios** (Camila/Eduardo/Larissa) sempre que um setor está vazio, a cada init no modo local. Perigoso se o modo local algum dia for usado com dados reais.
- **Local:** `migrarNovosSetores` (linha ~3090).

### 2.6 [BAIXO] Sem validação de data de admissão
`salvarColab`/`editarColab` não validam admissão contra datas futuras/absurdas. Uma admissão no futuro gera "tempo de casa" negativo.

---

## 3. Consistência funcional / Permissões

### 3.1 [RESOLVIDO] RH podia CRIAR mas não EDITAR colaborador
- **Era:** o botão "Novo colaborador" aparecia para `podeEditar()` (RH + admin) e `salvarColab` exigia só `guard()` (RH podia criar), enquanto `editarColab`/`toggleAtivoColab` exigiam `podeAdministrar()` (admin apenas). Resultado incoerente: RH adicionava uma pessoa mas não conseguia corrigir um typo nem inativá-la.
- **Correção aplicada (2026-08-09):** cadastro de colaborador passou a exigir `podeAdministrar()` — botão oculto para não-admin, gate no `Modals.novoColab` e no `Actions.salvarColab`. Agora **criar, editar e inativar** são todos admin-only, consistentes entre si. O RH mantém a edição de lançamentos de férias/folga (`podeEditar`), mas não mexe no cadastro de pessoas.
- **Local:** botão (linha 3582), `novoColab` (linha 4015), `salvarColab` (linha ~4308).

### 3.2 [BAIXO] `#/conta` para usuário "leitura" cai no dashboard sem aviso
Um usuário de leitura que navega para `#/conta` não tem a rota reconhecida (checagem de permissão) e o roteador resolve silenciosamente para o dashboard, sem mensagem de "sem permissão".
- **Local:** `route` (linha ~6607).

---

## 4. Design / UI / UX

### 4.1 [MÉDIO] Sem modo escuro
Zero tratamento de `prefers-color-scheme`/`data-theme`. Tema único claro. Legítimo se for decisão de produto, mas é uma limitação a registrar.

### 4.2 [MÉDIO] Breakpoints responsivos fragmentados
**14 valores distintos** de `max-width` (520/540/560/600/640/680/760/820/900/960/980/1000/1080/1100/1200). Cada componente inventou o seu — não há escala/token de breakpoint. Risco de manutenção e de comportamento irregular entre faixas.
- **Recomendação:** consolidar em 3–4 breakpoints padronizados.

### 4.3 [BAIXO] "Colaborador" (singular) como título do diretório
A página lista 30 pessoas, os cabeçalhos de seção dizem "N colaboradores" e os filtros dizem "Todas 30" — o título no singular destoa do conteúdo plural. (Mudança recente a pedido; vale reconsiderar.)

### 4.4 [BAIXO] Sobrecarga semântica de cor
O vermelho carrega **três** significados: férias (ícone sol / KPIs), status "férias vencendo", e o **anel de pendência** no avatar do diretório. Ao mesmo tempo, o status "Em férias" (pessoa em gozo hoje) usa **azul**, não vermelho — ou seja, o único lugar onde a pessoa está *literalmente* de férias não é vermelho. E folga oscila entre `--teal` (#12836A, KPIs/status) e `--green` (#1E8A57, anel do mini-avatar) — **dois verdes** para o mesmo conceito.
- A regra "verde = folga / vermelho = férias" é majoritariamente respeitada, mas tem essas exceções.
- **Recomendação:** um verde canônico para folga; decidir se "em gozo" segue a cor do tipo (vermelho férias) em vez de azul.

### 4.5 [BAIXO] Contraste baixo em `--faint`
`--faint` (#A6A39D sobre `--bg` #F2F1EE) tem contraste ~1,9:1, **muito abaixo do WCAG AA** (4,5:1) para texto. Usado em 45 lugares — para marca d'água decorativa tudo bem, mas qualquer rótulo real em `--faint` fica difícil de ler.

### 4.6 [BAIXO] Acessibilidade rasa
~24 atributos aria/role em 6,8k linhas. Botões de ícone da sidebar usam `title` (não `aria-label`); sem skip-link; sem gestão de foco na troca de rota; modais não fazem focus-trap nem declaram `role="dialog"`/`aria-modal`. Os autocompletes customizados têm boa navegação por teclado — mas a base geral de a11y é fraca.

### 4.7 [BAIXO] Marca d'água "Hoje" cortada no dashboard
O wordmark gigante "Hoje" fica parcialmente escondido atrás dos cards de KPI, lendo mais como glitch de render do que como efeito intencional.

### 4.8 [POSITIVO] Craft visual forte
Sistema de cards consistente (`.dx-stat`), paleta de marca coesa, hero ilustrado dia/noite, autocompletes navegáveis por teclado, bons estados vazios, PDF com cabeçalho/rodapé de marca. Linguagem visual coerente e acima da média para ferramenta interna.

---

## 5. Arquitetura / Manutenção

### 5.1 [MÉDIO] Monólito de 6,8k linhas / ~1,5 MB em um arquivo
CSS + JS + fontes base64 + Chart.js + jsPDF, tudo em um `index.html`. **Intencional** (restrição de CSP/offline, documentada no CLAUDE.md), mas implica: sem fronteiras de módulo, sem tree-shaking, custo alto de parse, diffs grosseiros no versionamento e ferramentas que engasgam no arquivo.

### 5.2 [BAIXO] IDs de elemento compartilhados entre templates de modal
`novoColab` e `editarColab` reusam `nNome/nFuncao/nAdm/fotoFile/...`. Seguro hoje porque só um modal existe no DOM por vez, mas é um footgun latente se dois modais coexistirem.

### 5.3 [BAIXO] CSS morto retido de propósito
Estilos de features removidas (`ag-cal2`, `ag-tl`, `ag-week`, resquícios de `dx-kpi`) mantidos deliberadamente (CLAUDE.md). Razoável no curto prazo, mas acumula.

### 5.4 [BAIXO] Cálculo duplicado entre tela e PDF
Cobertura/média/pico são recomputados de forma independente em `renderGraficos` e em cada `exportarRelatorio*`. Risco de divergência (tela e PDF podem discordar se um lado mudar).

---

## 6. Priorização recomendada

**Antes de qualquer uso real (multiusuário / dados reais):**
1. Migrar autenticação e autorização para o backend (1.1, 1.2) — pré-requisito inegociável.
2. Corrigir persistência das solicitações públicas no modo backend (2.3).
3. ~~Resolver a incoerência de permissão RH criar × editar (3.1).~~ ✅ **Feito** — cadastro de colaborador agora é admin-only.
4. Restringir a exposição do diretório no formulário público (1.3).

**Robustez / integridade (curto prazo):**
5. Validar `dias` contra o intervalo de datas (2.2).
6. Corrigir o `iso()` para hora local (2.1).
7. Handler de erro global (2.4) + validação de admissão (2.6).

**Polimento (quando sobrar tempo):**
8. Verde único para folga e revisão da semântica de "em gozo" (4.4).
9. Consolidar breakpoints (4.2), rever contraste de `--faint` (4.5), base de a11y (4.6).
10. Extrair cálculos compartilhados tela/PDF (5.4).

---

*As referências de linha apontam para o estado do arquivo na data da análise e podem deslocar com edições posteriores.*
