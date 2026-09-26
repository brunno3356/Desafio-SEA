# Desafio SEA — QA com Selenium, Pytest e Requests

Automação pequena para o [sistema do desafio](https://analista-teste.seatecnologia.com.br/), com exploração funcional, comparação UI/API e evidências sem dados pessoais de terceiros.

**Execução completa em 26/09/2026: 17 casos, 15 aprovados e 2 falhas esperadas (`xfailed`).** Os dois defeitos continuam presentes. Nenhum teste não executado foi contado como aprovado. Veja [resultados](docs/evidencias/execucao.json), [defeitos](docs/relatorio_bugs.md) e [explicação de cada teste](docs/guia_dos_testes.md).

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

Somente casos sem escrita (10 casos):

```powershell
python -m pytest -m "not escrita"
```

Todos os 17 casos, autorizando criação e exclusão **somente dos dados sintéticos daquela execução**:

```powershell
python -m pytest --executar-escrita
```

Sem essa opção, `python -m pytest` pula os sete casos que precisam da fixture de escrita. Isso é `skipped`, não aprovação. Nenhum teste utiliza registros existentes para PUT/PATCH/DELETE. O ambiente compartilhado não deve ser usado para execução paralela da suíte.

Um teste individual:

```powershell
python -m pytest tests/ui/test_cadastro.py::test_cadastro_campos_obrigatorios -v
python -m pytest tests/ui/test_cadastro.py::test_cadastro_sucesso --executar-escrita -v
```

Apenas a API:

```powershell
python -m pytest tests/api --executar-escrita -v
```

Para apresentar os defeitos como falhas convencionais, sem aplicar `xfail`:

```powershell
python -m pytest tests/api/test_employees.py::test_post_employee_rejeita_cpf_vazio tests/integration/test_ui_api.py::test_cadastro_preserva_selecoes_iniciais_na_api --executar-escrita --runxfail -v
```

É esperado que esse último comando termine com falha enquanto BUG-001 e BUG-003 existirem. `xfail(strict=True, raises=AssertionError)` registra a expectativa de falha da asserção; uma correção que faça o teste passar gera `XPASS(strict)` e pede revisão da marca. Exceções de conexão e Selenium não são tratadas como falhas esperadas. As asserções e seus motivos devem ser revisados se o contrato mudar.

## Gerar evidências

O relatório JUnit é nativo do Pytest:

```powershell
New-Item -ItemType Directory -Force evidencias
python -m pytest --executar-escrita --junitxml=evidencias/execucao.xml 2>&1 | Tee-Object -FilePath evidencias/execucao.txt
```

`evidencias/` fica fora do Git. A pasta `docs/evidencias/` contém somente evidências revisadas da entrega: dados sintéticos, nomes dos campos e metadados. Nunca publique resposta integral de GET `/employees`, HTML ou print da listagem completa: podem conter dados de outras pessoas.

Para obter um print de um formulário preenchido exclusivamente com seus dados fictícios, antes de salvar, adicione temporariamente no teste:

```python
from pathlib import Path

Path("evidencias").mkdir(exist_ok=True)
browser.find_element(By.CSS_SELECTOR, "form").screenshot("evidencias/formulario.png")
```

Capturar um elemento pode fazer o Selenium rolar a página. Para BUG-005, a exploração usou captura nativa recortada do Chrome sem esse deslocamento; os testes entregues não precisam de CDP. Não há captura automática de telas de terceiros ao falhar.

## Navegador e fixtures

O trecho central de `conftest.py` é:

```python
from selenium import webdriver

browser = webdriver.Chrome()
browser.get("https://analista-teste.seatecnologia.com.br/")
```

A fixture `browser` cria uma sessão por teste. `yield browser` entrega a sessão à função que pediu o argumento `browser`. O bloco `finally` chama `browser.quit()` mesmo quando um `assert` falha. Não existe BrowserFactory, gerenciador próprio, Page Object ou biblioteca que substitua os comandos do Selenium. O [Selenium Manager](https://www.selenium.dev/documentation/selenium_manager/) acompanha o Selenium desde a versão 4.6 e resolve o driver quando nenhum é fornecido.

A janela é configurada em 1440×1500 para o caso de persistência: em 1440×1100 a lista recorta o quinto cartão (BUG-005). O teste de cadastro espera a persistência pela API e recarrega **uma vez** para contornar a listagem desatualizada (BUG-004). Esses contornos delimitam o que o teste aprova; não significam que os defeitos de interface foram corrigidos.

As outras fixtures são simples:

- `api_url`: devolve a URL que a interface realmente usa.
- `trabalhador`: gera um nome `QA_SEA_<uuid>` único e dados fictícios; no `finally`, localiza o nome exato, confirma novamente o ID/nome e exclui. O nome é impresso no log capturado do Pytest para recuperar resíduos em caso de erro.
- `registro_api`: cria um trabalhador pela API para um caso de PUT, PATCH ou DELETE; aproveita a limpeza da fixture anterior.

CPF `00000000000` foi escolhido por ser deliberadamente fictício e inválido. A versão atual aceita esse dado (BUG-002); o teste chamado “sucesso” comprova o fluxo e a persistência, não validade cadastral do CPF. Nenhuma credencial é necessária ou foi inventada.

Se uma interrupção ou falha de rede impedir a limpeza, o teste registra erro. Consulte somente o nome exato mostrado no log e seu ID antes de removê-lo. Não limpe todos os nomes `QA_SEA_`: podem pertencer a outra execução.

## API confirmada

Base: `https://analista-teste.seatecnologia.com.br/employees`.

| Método/rota | Observado | Verificação |
|---|---|---|
| GET `/employees` | 200, lista JSON | Coleção, campos e tipos |
| GET `/employees/{id}` | 200 para registro existente | Consulta do próprio dado de teste |
| GET ID inexistente | 404, texto `Not Found` | Erro sem presumir JSON |
| HEAD `/employees` | 200, sem corpo | Metadados |
| OPTIONS `/employees` | 204 | Anúncio de métodos, isoladamente não comprova implementação |
| POST `/employees` | 201 | Criação real sintética + GET posterior |
| PUT `/employees/{id}` | 200 | Atualização real de registro próprio + GET |
| PATCH `/employees/{id}` | 200 | Atualização real de registro próprio + GET |
| DELETE `/employees/{id}` | 200 | Exclusão autorizada + GET 404 |

O corpo utilizado pela interface é `{"state": {"employee": {...}}}`. IDs observados são strings e inteiros. Atividade/EPI podem estar ausentes nos dados atuais. Não se afirma suporte a PUT/PATCH/DELETE na rota da coleção. O teste PATCH envia `state.employee` completo; não verifica a semântica de mesclagem de objetos aninhados.

## Organização e leitura para a entrevista

```text
tests/
  ui/test_cadastro.py
  ui/test_listagem.py
  api/test_employees.py
  integration/test_ui_api.py
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
.gitignore
README.md
```

Não existe `test_login.py`: a exploração não encontrou autenticação. Os dois cenários equivalentes solicitados estão em `test_cadastro.py`, em funções independentes.

Comece pela fixture `browser`, depois leia o teste de campos obrigatórios e o [guia dos testes](docs/guia_dos_testes.md). Em seguida, veja o POST com Requests e o teste de comparação das seleções iniciais. Termine com o [plano](docs/plano_de_testes.md), [relatório](docs/relatorio_bugs.md), [prioridades e limites](docs/estrategia.md) e [diário de IA](docs/diario_ia.md).
