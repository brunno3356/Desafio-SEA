# Estratégia e prioridades

Priorizei a integridade do cadastro e a comparação entre o que a tela mostra e o que a API persiste. São riscos centrais em um sistema de trabalhadores e EPIs: perder cargo/atividade/EPI é mais relevante que um detalhe visual. Em seguida, cobri as validações obrigatórias, a listagem, o filtro de ativos e os métodos HTTP realmente confirmados. A exploração de privacidade verificou requisições sem credenciais e operações apenas em dados sintéticos próprios.

O PDF não define um contrato formal. Antes de codificar testes, inspecionei DOM, controles, JavaScript público e tráfego de rede do Chrome. GET e POST foram encontrados na aplicação; GET/HEAD/OPTIONS foram consultados diretamente. PUT/PATCH/DELETE foram confirmados somente depois da autorização para operar nos registros sintéticos. Um cabeçalho anunciando métodos não foi tratado como prova suficiente.

## Decisões técnicas

- Selenium com Chrome real e Selenium Manager; Pytest organiza casos e fixtures; Requests inspeciona a API diretamente.
- Sem Page Objects, fábrica de navegador, gerenciador próprio, Cypress, Playwright, SeleniumBase ou plugins de relatórios.
- Funções independentes e dados exclusivos por caso. A repetição curta dos comandos de formulário é intencional para o aprendizado.
- CSS por atributos existentes, com relações estruturais onde faltam IDs. Classes com hashes gerados foram evitadas.
- Esperas por condições observáveis, sem `time.sleep`, sem reenvio automático de POST e sem repetição do teste para esconder falhas.
- Escrita exige `--executar-escrita`; limpeza por nome exclusivo e ID confirmado. O usuário autorizou esses deletes em 26/09/2026. Nunca excluir por prefixo genérico.
- Evidências públicas contêm somente dados fictícios ou metadados. Respostas completas de terceiros não foram salvas no repositório.

## Como interpretar os resultados

A rodada completa final teve **15 passed e 2 xfailed**, sem falhas inesperadas ou erros de encerramento. Os dois `xfail` são regressões dos BUG-001 e BUG-003 e não representam funcionalidades corretas. `--runxfail` permite demonstrá-los como falhas normais.

Houve rodadas anteriores: a primeira teve 14 passed, 3 failed e 1 erro de limpeza por timeout; o reteste teve 1 failed e 2 xfailed. A espera que recarregava a página foi corrigida. O recorte do cartão foi investigado separadamente e documentado. O registro pendente do timeout foi identificado, conferido e excluído com GET posterior 404. Não foi atribuído ao produto um bug de indisponibilidade a partir desse timeout isolado.

O teste de persistência usa janela alta e recarrega uma vez após confirmar o POST pela API, por causa de BUG-004/005. Isso permite verificar o dado salvo, mas não valida atualização automática da listagem nem layout usual. O fluxo usa CPF de zeros aceito pela aplicação; não constitui teste de CPF válido. As limitações estão explícitas para evitar uma falsa leitura do resultado verde.

A [consulta final de limpeza](evidencias/limpeza_final.json) encontrou novamente quatro registros, como no início, e nenhum nome com prefixo `QA_SEA_`. Essa verificação foi somente de leitura; a limpeza efetiva sempre usou a identidade individual de cada dado criado.

## O que ficou fora e por quê

| Área | Decisão |
|---|---|
| Login, perfis e autorização por papel | Não há autenticação disponível no fluxo explorado; não inventar campos, contas ou regras |
| Demais etapas | Indicadores são “ITEM 1”; Próximo passo não alterou a tela; falta fluxo funcional confirmado |
| Editar/excluir pela UI | Três pontos não abriu menu na exploração; CRUD foi verificado pela API com dados próprios |
| Upload/atestado | Não foram enviados documentos; apenas presença do seletor opcional confirmada |
| Múltiplas atividades/EPIs | Clique em Adicionar EPI manteve um seletor; combinações e submissão por “Adicionar outra atividade” não foram exercitadas |
| Validações exaustivas | Nome/CPF vazio, CPF curto e CPF repetido cobertos; limites de idade, datas futuras, RG, sexo, CA e todos os comprimentos permanecem parciais |
| Tipos inválidos enviados ao servidor | Não foi enviado CPF numérico/objeto: poderia quebrar a listagem compartilhada que chama `.replace()` em CPF |
| DELETE/PUT/PATCH na coleção | Não presumidos nem exercitados; execução confirmada na rota individual |
| Segurança ofensiva, carga e concorrência | Não autorizadas; risco desnecessário ao ambiente compartilhado |
| Cross-browser, mobile e acessibilidade completa | Chrome desktop priorizado; não são resultados implicitamente cobertos |
| CI automático | Não configurado para evitar escrita recorrente no serviço compartilhado; execução manual reproduzível é suficiente para esta entrega |
| Conformidade LGPD | Achados técnicos não demonstram titularidade dos dados, base legal ou violação jurídica |

Próxima rodada sugerida: alinhar o contrato esperado de CPF e dos campos EPI; corrigir/retestar perda de seleções e obrigatoriedade na API; aguardar o POST antes de atualizar a lista; depois avaliar etapas, upload e outros tamanhos de tela. Para uma versão produtiva, definir autenticação/autorização e minimização de dados antes de utilizar cadastros reais.
