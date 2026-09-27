# Desafio SEA — QA com Selenium, Pytest e Requests

Automação simples para o [sistema do desafio](https://analista-teste.seatecnologia.com.br/), com **5 testes independentes: 4 usam Selenium e 1 usa somente Requests**.

## Os cinco testes atuais

| Teste | Ferramentas | O que verifica |
|---|---|---|
| `test_cadastro_sucesso` | Selenium + Requests | Cadastra Brunno QA com EPI, confere atividade, EPI e CA salvos pela API e verifica o nome na listagem. |
| `test_cadastro_cpf_invalido` | Selenium | Informa CPF com 10 dígitos, confere a validação de tamanho mínimo e verifica que o formulário permanece aberto. |
| `test_inativar_trabalhador` | Requests + Selenium | Cria um registro próprio ativo, altera para inativo pela API e confere o resultado na listagem filtrada. |
| `test_reativar_trabalhador` | Requests + Selenium | Cria um registro próprio inativo, altera para ativo pela API e confere o resultado na listagem filtrada. |
| `test_consulta_employees` | Requests | Consulta `/employees` e verifica status 200, lista JSON, campos e tipos de dados. |

Os dois testes de status alteram os registros pela API porque a exploração não encontrou edição funcional pela interface. Os cenários de escrita usam registros próprios; nenhum teste depende da execução de outro.

**Quantidade de testes não é resultado de execução.** A coleta atual confirmou `5 tests collected`. O CI aprovado verifica o código com Ruff e coleta esses cinco testes: são **0 cenários funcionais executados no CI**. Para executar os cenários no Chrome e na API, use os comandos abaixo e consulte o resultado do Pytest.

## Preparar no Windows / PowerShell

Ambiente utilizado: Windows, Python 3.14.6, Chrome 154.0.8037.57, Selenium 4.49.0, Pytest 9.1.1 e Requests 2.34.2. É necessário acesso à internet para a aplicação e, no primeiro uso, para o Selenium Manager obter o driver. As três dependências diretas estão fixadas em `requirements.txt`; dependências transitivas não estão congeladas.

Na pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

A `.venv` já foi criada e as dependências instaladas no ambiente desta entrega. Se o PowerShell bloquear a ativação, não é preciso alterar a política da máquina: use o executável da `.venv` diretamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest
```

Para sair do ambiente ativado: `deactivate`. A pasta `.venv` não é enviada ao GitHub; cada pessoa cria a sua.

## Executar

Execute os comandos na pasta do projeto, com a `.venv` ativada, inclusive pelo terminal do VS Code.

Todos os cinco testes:

```powershell
python -m pytest -v
```

Somente os dois testes de cadastro:

```powershell
python -m pytest tests/ui/test_cadastro.py -v
```

Cada teste individualmente:

```powershell
python -m pytest tests/ui/test_cadastro.py::test_cadastro_sucesso -v
python -m pytest tests/ui/test_cadastro.py::test_cadastro_cpf_invalido -v
python -m pytest tests/ui/test_status.py::test_inativar_trabalhador -v
python -m pytest tests/ui/test_status.py::test_reativar_trabalhador -v
python -m pytest tests/api/test_employees.py::test_consulta_employees -v
```

Os cenários de cadastro e status criam dados sintéticos e fazem a limpeza ao terminar. A consulta isolada da API é somente leitura. Execute a suíte sequencialmente, pois o sistema é compartilhado.

Para apenas listar e carregar os testes, sem executar os cenários:

```powershell
python -m pytest --collect-only -q
```

`collected` significa encontrado pelo Pytest. `passed` significa que o teste foi executado e suas verificações passaram.

## CI com GitHub Actions e Ruff

O arquivo [ci.yml](.github/workflows/ci.yml) executa a verificação em pushes na branch `codex/qa-sea`, em pull requests destinados a ela e manualmente pela aba Actions.

O workflow prepara o Python, instala `requirements-ci.txt`, analisa `conftest.py` e `tests/` com Ruff e verifica a coleta com Pytest. Ruff procura problemas como imports não utilizados e variáveis indefinidas. Qualquer falha nessas etapas deixa o CI vermelho.

A [primeira execução desse CI foi aprovada](https://github.com/brunno3356/Desafio-SEA/actions/runs/36322513501). Isso confirma a análise estática e o carregamento dos cinco testes. **O CI não abre o Chrome nem executa os fluxos na aplicação ou na API.**

Para reproduzir as verificações do CI localmente:

```powershell
python -m pip install -r requirements-ci.txt
python -m ruff check conftest.py tests
python -m pytest --collect-only -q
```

## Gerar evidências

O relatório JUnit é nativo do Pytest:

```powershell
New-Item -ItemType Directory -Force evidencias
python -m pytest -v --junitxml=evidencias/execucao.xml 2>&1 | Tee-Object -FilePath evidencias/execucao.txt
```

`evidencias/` fica fora do Git e recebe os resultados da execução feita pelo comando acima. A pasta `docs/evidencias/` guarda evidências históricas da exploração inicial. Nunca publique resposta integral de GET `/employees`, HTML ou print da listagem completa: podem conter dados de outras pessoas.

Para obter um print de um formulário preenchido exclusivamente com seus dados fictícios, antes de salvar, adicione temporariamente no teste:

```python
from pathlib import Path

Path("evidencias").mkdir(exist_ok=True)
browser.find_element(By.CSS_SELECTOR, "form").screenshot("evidencias/formulario.png")
```

Capturar um elemento pode fazer o Selenium rolar a página. Revise as evidências antes de compartilhá-las.

## Navegador e fixtures

O trecho central de `conftest.py` é:

```python
from selenium import webdriver

browser = webdriver.Chrome()
browser.get("https://analista-teste.seatecnologia.com.br/")
```

A fixture `browser` cria uma sessão por teste. `yield browser` entrega a sessão à função que pediu o argumento `browser`. O bloco `finally` chama `browser.quit()` mesmo quando um `assert` falha. Não existe BrowserFactory, gerenciador próprio, Page Object ou biblioteca que substitua os comandos do Selenium. O [Selenium Manager](https://www.selenium.dev/documentation/selenium_manager/) acompanha o Selenium desde a versão 4.6 e resolve o driver quando nenhum é fornecido.

A janela é configurada em 1440×1500. As esperas pelo estado dos elementos usam `WebDriverWait`. Há pausas de 5 segundos em pontos de apresentação e antes de fechar o Chrome, para facilitar a visualização. No cadastro com sucesso, o teste espera a persistência pela API e recarrega a página uma vez antes de conferir a listagem.

As outras fixtures são simples:

- `api_url`: devolve a URL que a interface realmente usa.
- `trabalhador`: fornece o nome `Brunno QA` e um RG fictício exclusivo, `RG_TESTE_<identificador>`. No `finally`, procura esse RG, consulta o registro pelo ID, confirma nome e RG e exclui somente o dado daquele teste. Nome e RG são impressos no log para identificar resíduos em caso de erro.

CPF `00000000000` foi escolhido por ser deliberadamente fictício e inválido. A aplicação aceitou esse dado nas execuções realizadas; o teste chamado “sucesso” comprova o fluxo e a persistência, não a validade cadastral do CPF. Já o teste negativo informa `0000000000`, com apenas 10 dígitos, e verifica a validação de tamanho mínimo. Nenhuma credencial é necessária.

Se uma falha de rede impedir a limpeza, o teste pode registrar erro; uma interrupção do processo também pode deixar resíduos. Identifique o RG exclusivo e confirme o ID antes de remover um registro. O nome `Brunno QA` pode se repetir e, sozinho, não identifica o dado daquela execução.

## API utilizada pela suíte

Base: `https://analista-teste.seatecnologia.com.br/employees`.

| Método/rota | Status esperado | Uso nos cinco testes e nas fixtures |
|---|---|---|
| GET `/employees` | 200, lista JSON | Coleção, campos e tipos |
| GET `/employees/{id}` | 200 para registro existente | Consulta do próprio dado de teste |
| POST `/employees` | 201 | Criação de registro sintético nos testes de status |
| PATCH `/employees/{id}` | 200 | Inativação e reativação de registro próprio |
| DELETE `/employees/{id}` | 200 | Limpeza na fixture, seguida de GET que deve retornar 404 |

O corpo utilizado é `{"state": {"employee": {...}}}`. O teste de consulta aceita IDs string ou inteiro. O PATCH envia `state.employee` completo. Essas requisições fazem parte dos cinco cenários e de sua preparação/limpeza; não são casos de teste adicionais.

## Organização e leitura para a entrevista

```text
tests/
  ui/test_cadastro.py
  ui/test_status.py
  api/test_employees.py
.github/workflows/ci.yml
backup/
docs/
  plano_de_testes.md
  relatorio_bugs.md
  diario_ia.md
  estrategia.md
  guia_dos_testes.md
  evidencias/
conftest.py
pytest.ini
requirements.txt
requirements-ci.txt
.gitignore
README.md
```

Não existe `test_login.py`: a exploração não encontrou autenticação. Os dois cenários de cadastro estão em `test_cadastro.py`, em funções independentes.

Para entender o código, comece pela fixture `browser` em `conftest.py`, leia os dois testes de cadastro, os dois de status e, por último, a consulta da API.

## Material histórico

Os documentos e resultados em `docs/` pertencem à exploração e à versão anterior da automação. As quantidades e os comandos antigos desses documentos não representam a suíte atual de cinco testes. A cópia da automação anterior está em `backup/automacao_17_testes_2026-09-27.zip` e não participa da execução principal.
