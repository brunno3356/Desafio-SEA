# Relatório de defeitos e achados — SEA

Reproduções em 26/09/2026, Windows, Chrome 154.0.8037.57. Aplicação: https://analista-teste.seatecnologia.com.br/. Todas as gravações foram feitas com dados sintéticos próprios; os registros foram removidos após a coleta. Os arquivos JSON preservam status, campos e valores fictícios. Não há documentos ou credenciais reais nas evidências.

Severidade representa impacto; prioridade representa a ordem sugerida para correção. As regras de negócio não documentadas são identificadas como expectativas a confirmar. Nenhum código da aplicação foi alterado por este projeto.

| ID | Título | Severidade | Prioridade | Cobertura |
|---|---|---|---|---|
| BUG-001 | Seleções iniciais de cargo, atividade e EPI não são persistidas | Alta | P1 | Automático: `xfail` |
| BUG-003 | API aceita CPF vazio, obrigatório na interface | Alta | P1 | Automático: `xfail` |
| BUG-006 | Próximo passo não avança após concluir a etapa | Alta | P1 | Exploração |
| BUG-004 | Cadastro novo não aparece na lista até recarregar | Média | P1 | Exploração; teste usa contorno |
| BUG-002 | Cadastro aceita CPF de onze zeros | Média | P2 | Exploração |
| BUG-005 | Quinto cartão é recortado em janela de 1440×1100 | Média | P2 | Exploração; teste usa janela alta |

## BUG-001 — Seleções iniciais não são persistidas

**Severidade/Prioridade:** Alta/P1. **Pré-condições:** abrir Adicionar Funcionário; usar nome fictício único; manter seleções iniciais. Sem autenticação no fluxo disponível.

**Passos:**

1. Preencher nome de teste, CPF `00000000000`, nascimento `01/01/2000`, RG `RG_TESTE_SEM_VALIDADE` e CA `00000`.
2. Manter Cargo 01, Ativid 01 e Capacete de segurança visíveis, sem clicar nessas seleções.
3. Salvar e consultar o nome sintético via GET `/employees`.

**Esperado:** os valores visíveis no formulário devem ser persistidos: cargo `Cargo 01`, atividade `Ativid 01` e valor de EPI correspondente ao capacete.

**Obtido:** POST 201 com `role: ""`; `activity` e `epi` ausentes. GET confirma a perda. O cartão exibe somente nome e CPF. A inspeção do JavaScript público sugere que os valores visuais iniciais não inicializam o estado enviado; essa é uma hipótese de causa, não uma correção aplicada.

**Evidências:** [formulário preenchido](evidencias/cadastro_defaults_antes.png), [requisição POST e registro consultado](evidencias/cadastro_defaults.json), [cartão próprio](evidencias/cadastro_defaults_depois.png). Regressão: `test_cadastro_preserva_selecoes_iniciais_na_api`; falha esperada estrita.

## BUG-003 — API aceita CPF vazio

**Severidade/Prioridade:** Alta/P1. **Pré-condições:** autorização para criar/limpar apenas dados sintéticos; payload no formato `state.employee`.

**Passos:**

1. Preparar um funcionário sintético com nome único e todos os campos da fixture.
2. Enviar POST `/employees` com `state.employee.cpf` igual a `""`.
3. Consultar o ID retornado por GET; excluir apenas esse registro ao final.

**Esperado:** rejeição com erro de validação 4xx (400/422 propostos) e ausência de persistência. A UI declara CPF como `required`, indicando uma regra que deveria ser consistente no servidor; o status exato depende do contrato a alinhar.

**Obtido:** POST 201; CPF vazio permanece no GET 200. A validação da interface pode ser contornada chamando a API diretamente.

**Evidências:** [requisição/resposta e confirmação de limpeza](evidencias/cpf_vazio_api.json). Regressão: `test_post_employee_rejeita_cpf_vazio`; observou 201 em vez de 400/422.

## BUG-006 — Próximo passo não avança

**Severidade/Prioridade:** Alta/P1. **Pré-condições:** listagem carregada com trabalhadores; tela inicial de etapas.

**Passos:**

1. Marcar “A etapa está concluída?” como Sim.
2. Clicar em Próximo passo.
3. Aguardar a mudança de tela; na reprodução, o cabeçalho foi observado por até três segundos.

**Esperado:** avançar para a próxima etapa ou explicar a condição impeditiva. O rótulo do botão indica ação de navegação.

**Obtido:** switch com `aria-checked="true"`, mesmo cabeçalho/listagem e mesma URL `/`, sem orientação de bloqueio. Os nove indicadores continuam “ITEM 1”. O JavaScript público inspecionado renderiza esse botão sem ação de clique, reforçando a observação; não foram inventadas etapas posteriores.

**Evidência:** [ações e estado após clique](evidencias/navegacao_layout.json), campos `etapa_marcada`, `cabecalho_alterou_apos_proximo`, `url_alterou`. Confirmar com produto quais etapas deveriam existir.

## BUG-004 — Lista não mostra cadastro recém-salvo

**Severidade/Prioridade:** Média/P1. **Pré-condições:** listagem carregada; funcionário sintético inexistente antes do teste.

**Passos:**

1. Criar um funcionário pelo formulário e clicar Salvar.
2. Aguardar a API retornar o novo nome na coleção.
3. Procurar o cartão na listagem para a qual o formulário retornou.
4. Recarregar a página.

**Esperado:** após o salvamento concluído, a lista deve incluir o novo cadastro, sem recarga manual.

**Obtido:** registro existe na API, mas a lista exibida ainda não o contém; após refresh, o cartão aparece. Na captura, o GET da lista respondeu antes do POST 201. O comportamento depende do tempo das requisições; não se afirma que ocorre em todo cadastro.

**Evidência:** [sequência de rede e `refresh_necessario: true`](evidencias/cadastro_defaults.json). O teste `test_cadastro_sucesso` contorna a atualização desatualizada esperando persistência por Requests e recarregando uma vez; não comprova correção desta falha.

## BUG-002 — CPF de onze zeros aceito

**Severidade/Prioridade:** Média/P2. **Pré-condições:** formulário aberto com os demais obrigatórios preenchidos com dados fictícios.

**Passos:**

1. Digitar `00000000000` no CPF.
2. Preencher os demais obrigatórios e salvar.
3. Consultar o registro próprio na API.

**Esperado:** rejeitar uma sequência de CPF inválida, mantendo o formulário e explicando o erro. A expectativa de validar CPF é inferida da natureza do campo e deve ser confirmada com o produto, pois o desafio não fornece regra formal de validação.

**Obtido:** POST 201, CPF de zeros persistido e exibido como `000.000.000-00`. O HTML limita comprimento a onze caracteres, mas a aceitação desse valor foi confirmada. Não foi extrapolado o resultado para todos os CPFs inválidos.

**Evidências:** [formulário](evidencias/cadastro_defaults_antes.png), [requisição e GET](evidencias/cadastro_defaults.json), [cartão próprio](evidencias/cadastro_defaults_depois.png). Os casos de persistência usam zeros intencionalmente para não trabalhar com documento real.

## BUG-005 — Listagem recorta o último cartão

**Severidade/Prioridade:** Média/P2. **Pré-condições:** cinco registros na listagem; quinto registro sintético; janela externa Chrome 1440×1100, altura interna 949 pixels na reprodução.

**Passos:**

1. Abrir a listagem nessa dimensão.
2. Observar o quinto cartão com nome/CPF/atividade/cargo sintéticos.
3. Comparar o conteúdo visível com o DOM e ampliar a janela para altura 1500.

**Esperado:** informações acessíveis com rolagem adequada dentro da lista ou layout que acomode os cartões.

**Obtido:** apenas nome visível; CPF/atividade/cargo estão no DOM, mas recortados pelo painel. Em altura externa 1500 (interna 1349), os mesmos campos ficam visíveis. O botão Próximo passo aparece sobre a região inferior capturada. Não é ausência de dados no servidor.

**Evidências:** [recorte original sem scroll automático](evidencias/listagem_recortada.png), [mesmo cartão em janela alta](evidencias/listagem_janela_alta.png), [dimensões e texto visível/DOM](evidencias/navegacao_layout.json). As capturas incluem somente o cartão sintético e elementos de interface adjacentes.

## SEG-001 — Leitura e mutação sem autenticação

**Classificação:** achado técnico confirmado, risco alto se aplicado a trabalhadores reais; **prioridade sugerida P1 para avaliação de segurança**. Não se afirma violação legal ou exposição de dados reais. O ambiente público do desafio pode ser intencionalmente aberto.

**Pré-condições:** cliente Requests novo, sem cookie ou cabeçalho Authorization. Para mutações, autorização do usuário e registro sintético próprio.

**Passos:**

1. Fazer GET `https://analista-teste.seatecnologia.com.br/employees` sem credenciais.
2. Inspecionar os nomes dos campos, sem copiar valores de terceiros.
3. Em registro próprio, realizar POST, PUT/PATCH e DELETE; registrar status e GET posterior.

**Esperado para uso com dados reais:** política de autenticação/autorização definida e restrição/minimização dos documentos pessoais, inclusive acesso de escrita.

**Obtido:** GET 200 retorna campos `name`, `cpf`, `rg`, `birthDay` e outros; `Cache-Control: public`. Criação e alteração/exclusão do registro sintético também funcionam sem credenciais. Isso comprova acesso anônimo às operações testadas, mas não comprova abuso contra terceiros, cache efetivo por intermediários, identidade real dos cadastros ou violação de LGPD. Nenhuma operação destrutiva foi realizada em registro anterior.

**Evidências:** [GET sem Authorization/Cookie, somente nomes de campos](evidencias/api_privacidade.json), [POST próprio sem Authorization](evidencias/cpf_vazio_api.json), [PUT/PATCH/DELETE próprios e GET 404](evidencias/api_mutacoes.json).

**Recomendação:** antes de produção, alinhar necessidade de acesso público, aplicar autorização no servidor, validar campos obrigatórios e reduzir exposição de documentos. Não usar dados reais neste ambiente de demonstração.

## Outras observações e evidência de execução

O ícone de três pontos não abriu menu; Adicionar EPI manteve um seletor. Esses controles foram registrados como funcionalidades não confirmadas, sem criar testes fictícios de edição ou múltiplos EPIs. Nenhuma tela de login foi encontrada.

[Resumo da execução completa](evidencias/execucao.json): 15 passed e 2 xfailed. Os XMLs completos e logs intermediários estão em `evidencias/` local, ignorada pelo Git. As rodadas anteriores e os erros corrigidos na automação são descritos no diário e na estratégia.
