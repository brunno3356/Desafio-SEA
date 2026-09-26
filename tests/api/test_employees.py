import pytest
import requests


def test_get_employees_estrutura_e_tipos(api_url):
    response = requests.get(api_url, timeout=15)
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")
    registros = response.json()
    assert isinstance(registros, list)
    campos_texto = ("name", "cpf", "birthDay", "rg", "gender", "role", "caNumber")
    for registro in registros:
        # Mensagens só descrevem o campo: não imprimimos valores pessoais.
        id_valido = type(registro.get("id")) in (int, str)
        assert id_valido, "ID deve ser inteiro ou string, conforme observado."
        employee = registro.get("state", {}).get("employee", {})
        for campo in campos_texto:
            tipo_correto = isinstance(employee.get(campo), str)
            assert tipo_correto, f"Campo {campo} ausente ou fora do tipo string."
        for campo in ("isActive", "usesEpi"):
            tipo_correto = isinstance(employee.get(campo), bool)
            assert tipo_correto, f"Campo {campo} ausente ou fora do tipo booleano."


def test_head_employees_sem_corpo(api_url):
    response = requests.head(api_url, timeout=15)
    assert response.status_code == 200
    assert response.content == b""
    assert response.headers["Content-Type"].startswith("application/json")


def test_options_employees_anuncia_metodos(api_url):
    response = requests.options(api_url, timeout=15)
    assert response.status_code == 204
    metodos = {x.strip() for x in response.headers["Access-Control-Allow-Methods"].split(",")}
    assert {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE"}.issubset(metodos)


def test_get_employee_inexistente(api_url):
    response = requests.get(f"{api_url}/qa-sea-inexistente-49ea08ca75", timeout=15)
    assert response.status_code == 404
    assert response.text == "Not Found"


@pytest.mark.escrita
def test_post_employee_persiste_dados(trabalhador, api_url):
    response = requests.post(api_url, json={"state": {"employee": trabalhador}}, timeout=15)
    assert response.status_code == 201
    registro = response.json()
    assert "id" in registro
    consulta = requests.get(f"{api_url}/{registro['id']}", timeout=15)
    assert consulta.status_code == 200
    assert consulta.json()["state"]["employee"] == trabalhador


@pytest.mark.escrita
def test_put_employee_atualiza_cargo(registro_api, trabalhador, api_url):
    trabalhador["role"] = "Cargo 03"
    item_url = f"{api_url}/{registro_api['id']}"
    response = requests.put(item_url, json={"state": {"employee": trabalhador}}, timeout=15)
    assert response.status_code == 200
    consulta = requests.get(item_url, timeout=15)
    assert consulta.status_code == 200
    assert consulta.json()["state"]["employee"] == trabalhador


@pytest.mark.escrita
def test_patch_employee_atualiza_status(registro_api, trabalhador, api_url):
    trabalhador["isActive"] = True
    item_url = f"{api_url}/{registro_api['id']}"
    # Enviamos state completo; este caso não presume mesclagem dos campos aninhados.
    response = requests.patch(item_url, json={"state": {"employee": trabalhador}}, timeout=15)
    assert response.status_code == 200
    consulta = requests.get(item_url, timeout=15)
    assert consulta.status_code == 200
    assert consulta.json()["state"]["employee"] == trabalhador


@pytest.mark.escrita
def test_delete_employee_remove_registro(registro_api, api_url):
    item_url = f"{api_url}/{registro_api['id']}"
    response = requests.delete(item_url, timeout=15)
    assert response.status_code == 200
    consulta = requests.get(item_url, timeout=15)
    assert consulta.status_code == 404


@pytest.mark.escrita
@pytest.mark.xfail(strict=True, raises=AssertionError, reason="BUG-003: API aceita CPF vazio")
def test_post_employee_rejeita_cpf_vazio(trabalhador, api_url):
    trabalhador["cpf"] = ""
    response = requests.post(api_url, json={"state": {"employee": trabalhador}}, timeout=15)
    if response.status_code not in (201, 400, 422):
        pytest.fail(f"Status inesperado, diferente do BUG-003: {response.status_code}")
    assert response.status_code in (400, 422), "API deveria rejeitar CPF vazio, obrigatório na UI."
