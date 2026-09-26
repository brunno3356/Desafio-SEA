# Como explicar o código

## Selenium em comandos diretos

```python
wait = WebDriverWait(browser, 10)
wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="name"]')))
browser.find_element(By.CSS_SELECTOR, 'input[name="name"]').send_keys("QA_SEA_TESTE")
```

`WebDriverWait` recebe o navegador e o prazo máximo. `until` repete a condição até ela ser verdadeira, ou lança `TimeoutException`; não espera dez segundos obrigatoriamente. `EC` é apenas o apelido do módulo de condições do próprio Selenium. `By.CSS_SELECTOR` informa a estratégia. `find_element` devolve o primeiro elemento; `send_keys` digita nele. `find_elements` devolve uma lista, inclusive vazia. Usamos [esperas explícitas](https://www.selenium.dev/documentation/webdriver/waits/), sem `time.sleep` e sem espera implícita.

Um `assert condição` é a decisão do teste: se a condição for falsa, o Pytest falha. Conseguir clicar, sozinho, não é aprovação. `get_property("validity")` lê o objeto de validade nativa do HTML; `get_attribute("aria-checked")` lê o estado exposto pelo switch. Não comparamos a frase exata da validação porque o idioma do Chrome pode mudar.

No [Cypress](https://docs.cypress.io/app/core-concepts/retry-ability), consultas e asserções encadeadas podem ser repetidas automaticamente. Aqui as instruções Python executam em sequência; o `assert` simples não repete a busca. A espera explícita deve resolver o carregamento antes da asserção.

## Seletores inspecionados

| CSS | O que encontra e por que foi escolhido |
|---|---|
| `input[name="name"]` / `cpf` / `rg` / `birthDay` / `caNumber` | Atributos reais e descritivos; os campos não têm IDs |
| `button[type="submit"]` | Botão Salvar, com tipo explícito |
| `div:has(> h2) > button` | Botão Adicionar no contêiner do título; não depende de classe CSS gerada |
| `label[for="role"] + div` | Componente de cargo imediatamente após o label; não é um `<select>` nativo |
| `.ant-select-item-option[title="Cargo 02"]` | Opção real e visível do componente Ant Design |
| `input[type="checkbox"]` | Único checkbox do formulário: trabalhador não usa EPI |
| `button:has(+ button.clear)` | Botão de ativos imediatamente anterior a Limpar filtros |
| `button.clear` / `button.isActive` | Classe semântica observada, não hash de estilo |
| `div:has(> div > img[src*="dots-"])` | Cada cartão com o ícone de três pontos em um filho direto |

Em CSS, `>` significa filho direto, `+` significa próximo irmão e `:has(...)` seleciona quem contém a relação descrita. Esses seletores estruturais são uma alternativa na ausência de `id` e `data-testid`; ainda dependem do DOM e do nome do ícone. Se o front-end mudar, inspecione novamente. IDs dinâmicos `rc_select_0` não foram usados.

## Casos de interface

| Função | Objetivo e seletores | Motivo da espera | O que os asserts validam / esperado |
|---|---|---|---|
| `test_cadastro_campos_obrigatorios` | Abrir formulário e salvar vazio; botão Adicionar, `input[name="name"]`, submit | React precisa montar o formulário antes da interação | `valueMissing=True`, mensagem não vazia e formulário ainda aberto |
| `test_cadastro_cpf_curto` | Digitar dez zeros em `input[name="cpf"]`; preencher nome para ele não ser o primeiro bloqueio | Aguardar campo CPF visível | `tooShort=True`, mensagem presente e envio bloqueado |
| `test_cadastro_sem_epi_oculta_campos` | Marcar `input[type="checkbox"]` | Aguardar CA antes e sua remoção depois do clique | Checkbox marcado; CA e label de EPI ausentes |
| `test_cadastro_sucesso` | Preencher nome, CPF fictício, data e RG; escolher Cargo 02; marcar sem EPI; salvar | Aguardar formulário/opção, persistência por GET e cartão após um único refresh | Nome exato, CPF formatado e cargo no cartão; não apenas fechamento do formulário |
| `test_listagem_carrega` | `h2`, botão Adicionar e spans de contagem | O HTML pode aparecer antes do GET; esperar contador com total numérico | Título e ação de cadastro corretos |
| `test_limpar_filtro_restaura_listagem` | Botão de ativos, `button.clear`, cartões | Esperar dados, ativação e remoção de `.isActive` | Estado do filtro removido e mesma quantidade inicial de cartões |

No campo de data, `send_keys("01012000", Keys.TAB)` foi verificado no Chrome em português e produziu `2000-01-01`. A data foi escolhida com dia=mês para evitar inversão entre esses componentes; outras configurações de navegador podem exigir revisão. Não usamos JavaScript para preencher valores ou ignorar validações.

O cadastro inclui dois contornos documentados: consulta à API para aguardar o POST antes de recarregar e janela alta para ver o último cartão. A consulta por nome usa uma expressão geradora: examina os registros e devolve verdadeiro se encontrar o nome exclusivo. Isso não repete o clique Salvar nem cria registros novamente.

## Casos de API

Requests não usa seletores nem `WebDriverWait`. Cada chamada aguarda a resposta HTTP e tem `timeout=15`. Esse limite de conexão/leitura não é um prazo global exato para todo o teste. `json=...` serializa o dicionário Python e envia JSON; `response.json()` interpreta a resposta. `raise_for_status()` transforma um erro HTTP em exceção quando não estamos testando aquele erro intencionalmente.

| Função | Objetivo | Asserts / resultado esperado |
|---|---|---|
| `test_get_employees_estrutura_e_tipos` | Contrato mínimo observado da coleção | 200, Content-Type JSON, lista, IDs string/int, campos textuais e booleanos presentes com os tipos corretos |
| `test_head_employees_sem_corpo` | Metadados da coleção | 200, corpo vazio e Content-Type JSON |
| `test_options_employees_anuncia_metodos` | Ver anúncio de métodos | 204 e conjunto anunciado; os testes de escrita comprovam a execução real |
| `test_get_employee_inexistente` | Erro de recurso inexistente | 404 e texto `Not Found`; não tenta decodificar erro como JSON |
| `test_post_employee_persiste_dados` | Criar um trabalhador | 201, ID presente, GET 200 e todos os campos iguais aos enviados |
| `test_put_employee_atualiza_cargo` | Mudar cargo do próprio registro | PUT 200, GET 200 e objeto completo atualizado, preservando os demais campos |
| `test_patch_employee_atualiza_status` | Mudar ativo/inativo do próprio registro | PATCH 200, GET 200 e objeto completo igual ao esperado |
| `test_delete_employee_remove_registro` | Excluir somente o registro recém-criado | DELETE 200 e GET posterior 404 |
| `test_post_employee_rejeita_cpf_vazio` | Levar a obrigatoriedade da UI à API | Esperado 400/422; observado 201, portanto BUG-003 e `xfail` |

`campos_texto` é uma tupla com os nomes dos campos. O `for` verifica o mesmo contrato para cada registro/campo; não mistura cenários distintos em uma função. Em uma coleção vazia, esse teste valida o formato de lista, mas não prova os tipos de um item; os casos com criação própria cobrem essa parte. Igualdades de objetos completos aparecem apenas com dados sintéticos. Para dados preexistentes, guardamos o resultado da comparação em um booleano antes do `assert`, evitando que a introspecção de falha imprima nomes ou documentos.

## Casos de integração

| Função | Objetivo e seletores | Espera | Asserts / esperado |
|---|---|---|---|
| `test_filtro_ativos_corresponde_api` | Obter `isActive=True` por Requests e comparar aos cartões após o filtro | Contador carregado e botão `.isActive` | Os nomes da UI devem corresponder exatamente aos da API, ordenados em memória |
| `test_cadastro_preserva_selecoes_iniciais_na_api` | Cadastrar sem alterar Cargo 01 / Ativid 01 / Capacete de segurança; seletores de inputs e `label + div .ant-select-selection-item` | Formulário montado, fechamento após submit e GET contendo o nome exclusivo | Nome/CPF/cargo/atividade/EPI devem refletir o formulário; BUG-001 provoca `xfail` |

No segundo caso, `next(..., False)` devolve o primeiro funcionário com o nome esperado; se ainda não existe, devolve `False` e o `until` consulta novamente. O rótulo “Capacete de segurança” corresponde ao valor `capacete-de-segurança`, confirmado na inspeção do front-end. O teste compara os dados do próprio cadastro, sem depender de qual registro aparece primeiro na coleção.

## Por que existem fixtures de dados

Fixtures são preparação e encerramento compartilhados pelo Pytest, não uma camada escondendo o Selenium. `trabalhador` não faz cadastro: apenas prepara os dados e garante limpeza posterior; cada teste decide como criar. `registro_api` acrescenta a criação necessária para testar uma atualização ou exclusão de forma independente. Quando a função pede essas fixtures como argumentos, o Pytest resolve as dependências. O código após o `yield` executa no encerramento, conforme o [modelo de fixtures do Pytest](https://docs.pytest.org/en/stable/how-to/fixtures.html).

Na entrevista, explique os limites junto dos resultados: os defeitos não foram corrigidos no site; não houve login para testar; erros de rede não são evidência suficiente de bug; valores de CPF fictícios não equivalem a dados de negócio válidos.

As verificações de preparação/limpeza usam `pytest.fail(...)` quando encontram uma inconsistência. A exceção gerada é diferente de `AssertionError`, então não é absorvida pelo `xfail(raises=AssertionError)` dos defeitos conhecidos. Um status inesperado no teste de CPF vazio também falha normalmente. Isso impede que um erro de infraestrutura ou de limpeza seja apresentado como reprodução do bug esperado.
