# Plano de testes — SEA Tecnologia

Exploração iniciada em 26/09/2026. Fonte de escopo: PDF original do desafio, lido integralmente (uma página em imagem). Ambiente: https://analista-teste.seatecnologia.com.br/. API confirmada: https://analista-teste.seatecnologia.com.br/employees.

## Objetivo e premissas

Verificar cadastro, consulta, consistência entre UI/API e exposição de dados. Não existe especificação formal: diferenciar regra observada de expectativa de negócio. O atributo `required` da interface é evidência de obrigatoriedade, mas não substitui um contrato de API. Validar CPF é uma expectativa de integridade a confirmar com o produto; `00000000000` é deliberadamente inválido.

A exploração encontrou uma única URL, `/`, com listagem e formulário alternados por estado do React. Não foi encontrado login na navegação disponível, nem usuário/senha. Não foram criados `test_login_sucesso` ou `test_login_falha` fictícios. Os equivalentes são `test_cadastro_sucesso` e `test_cadastro_campos_obrigatorios`.

## Inventário observado

| Área | Comportamento/campos confirmados |
|---|---|
| Listagem | Nome, CPF formatado, atividade quando presente, cargo, contador ativos/total |
| Filtros | Ver apenas ativos; Limpar filtros |
| Cadastro | Ativo/inativo (inativo inicial); nome; sexo (masculino inicial); CPF; nascimento; RG; cargo |
| EPI | Checkbox “O trabalhador não usa EPI”; atividade; EPI; número do CA |
| Arquivo | Seletor de atestado opcional; persistência/upload não confirmado |
| Obrigatórios HTML | Nome, CPF, nascimento, RG e CA quando exibido |
| CPF | `minlength=11`, `maxlength=11`; sem máscara no formulário |
| Seleções iniciais | Cargo 01, Ativid 01, Capacete de segurança; ver BUG-001 |
| Etapas | Nove indicadores “ITEM 1”; switch “A etapa está concluída?” e botão Próximo passo; não assumir nove formulários funcionais |
| Edição/exclusão UI | Ícone de três pontos sem menu identificado após clique; não há fluxo confirmado |
| Rotas/autenticação | Nenhum link `<a>` e nenhum campo de senha encontrados na tela explorada |

Validação vazia observada no Chrome em português: “Preencha este campo.” Os testes usam `validity` e mensagem não vazia porque a redação depende do idioma do navegador.

## Cobertura planejada

| ID | Prioridade | Cenário | Abordagem |
|---|---|---|---|
| UI-01 | P1 | Salvar com obrigatórios vazios | Selenium, bloqueio nativo e permanência do formulário |
| UI-02 | P1 | CPF com dez caracteres | Selenium, `tooShort` e mensagem |
| UI-03 | P2 | Marcar que não usa EPI | Selenium, seleção e remoção de campos condicionais |
| UI-04 | P1 | Cadastro com seleção explícita de cargo | Selenium, identidade/CPF/cargo na listagem |
| UI-05 | P1 | Carregar listagem | Selenium, título, botão e contador carregado |
| UI-06 | P2 | Limpar filtro de ativos | Selenium, estado e quantidade restaurados |
| API-01 | P1 | GET coleção, JSON e tipos | Requests; campos observados, sem imprimir valores |
| API-02 | P2 | HEAD e OPTIONS | Casos independentes; sem corpo e anúncio de métodos |
| API-03 | P1 | Consultar ID inexistente | GET 404, corpo de erro observado |
| API-04 | P1 | POST e persistência | Registro sintético, 201 e GET comparando os campos |
| API-05 | P2 | PUT e PATCH | Casos independentes em registros próprios, resposta e GET posterior |
| API-06 | P1 | DELETE | Apenas registro próprio, seguido de GET 404 |
| API-07 | P1 | CPF obrigatório vazio pela API | Esperar rejeição; preservar regressão de BUG-003 |
| INT-01 | P1 | Filtro ativos versus API | Comparar os nomes completos em memória, não apenas contagem |
| INT-02 | P1 | Valores iniciais UI versus API | Cadastrar pela UI; comparar identidade, CPF e seleções |
| SEG-01 | P1 | Leitura e escrita sem autenticação | Requisições sem credenciais; escrita somente em dados próprios |

## Dados, isolamento e limpeza

Cada teste de escrita recebe nome `QA_SEA_<uuid>` exclusivo, RG com texto de teste, nascimento fictício e CPF de zeros. Esse CPF é aceito pela versão atual, mas não é um documento válido: o teste de persistência não comprova conformidade da regra de CPF. Não geramos documentos potencialmente pertencentes a pessoas reais.

A opção `--executar-escrita` habilita criação e limpeza. O usuário autorizou em 26/09/2026 PUT/PATCH/DELETE somente dos registros sintéticos desta sessão/suíte. A fixture procura o nome exato daquele teste, consulta novamente o ID, confere o nome e exclui; nunca apaga por prefixo genérico. Falha na limpeza é erro de execução, não aprovação. Interrupção forçada do processo pode impedir o `finally`: conferir resíduos antes de nova execução.

Testes sequenciais, Chrome novo por caso de UI, sem depender da ordem dos testes. O ambiente é compartilhado: alterações de outros usuários podem causar divergências entre a leitura da API e a UI. Não rodar em paralelo neste ambiente.

## Critérios de conclusão

Executar os casos possíveis; relatar `passed`, `failed`, `skipped`, `xfailed` separadamente. Cada defeito precisa de reprodução e evidência. `xfail` indica defeito conhecido ainda existente, nunca aprovação; `strict=True` exige revisão quando ele deixar de ocorrer. Não encobrir erros de seletor, conexão ou preparação como defeitos esperados.

## Fora do escopo desta rodada

Carga/stress, exploração invasiva, enumeração massiva, acesso a contas, alteração de registros anteriores, uploads de atestados reais, varredura de rotas privadas, comparação entre navegadores/dispositivos, acessibilidade completa e avaliação jurídica de LGPD. Campos obrigatórios individuais além de nome/CPF e todas as combinações de datas, sexo e EPI permanecem cobertura parcial. Os limites e motivos estão em `estrategia.md`.
