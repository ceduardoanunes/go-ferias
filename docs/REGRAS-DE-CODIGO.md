# Regras de código

Lista de regras e alterações de código a considerar no go-ferias.

## Alterações de código

- Considerar feriados ao marcar férias/folgas no formulário de agendamento (impacta número de dias).
- Considerar período aquisitivo menor de 1 ano (colaborador pode sair antes, mas tem direito).
- Ao pesquisar colaborador, desconsiderar acentos no nome.
- Editar data de período aquisitivo (admin).
- Regras de férias CLT.
- Adicionar filtro por CNPJ.
- Dividir período de férias contábeis por CNPJ quando for o caso do colaborador que mudou de CNPJ.
  - Nesse caso, deixar opção de ocultar o histórico de CNPJ anterior e focar no novo.
  - Nos demais casos, aplicar o mesmo quando o histórico for muito grande.
- Explicar períodos de acordo. Pode chamar de **Transição**: colaborador faz acordo, é desligado, recebe a rescisão e um tempo depois é readmitido, iniciando novo período contábil.
- Voltar férias ao PJ e estagiários:
  - **PJ:** recebem o 1/3 (R$) e 30 dias de férias como um CLT (contrato).
  - **Estagiário:** não recebe 1/3, mas tem direito a 30 dias de férias.

## Pendências / dúvidas

- Verificar se foram lidas as linhas ocultas da planilha.
