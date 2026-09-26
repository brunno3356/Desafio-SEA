from uuid import uuid4

import pytest
import requests
from selenium import webdriver


def pytest_addoption(parser):
    parser.addoption(
        "--executar-escrita",
        action="store_true",
        help="Cria dados QA_SEA_ e autoriza excluir somente os dados de cada teste.",
    )


@pytest.fixture
def browser():
    # Selenium Manager encontra/obtém o driver compatível com o Chrome.
    browser = webdriver.Chrome()
    try:
        browser.set_window_size(1440, 1500)
        browser.get("https://analista-teste.seatecnologia.com.br/")
        yield browser
    finally:
        browser.quit()


@pytest.fixture
def api_url():
    return "https://analista-teste.seatecnologia.com.br/employees"


@pytest.fixture
def trabalhador(request, api_url):
    if not request.config.getoption("--executar-escrita"):
        pytest.skip("Use --executar-escrita para criar e limpar dados sintéticos.")

    nome = "QA_SEA_" + uuid4().hex
    print(f"Dado sintético deste teste: {nome}")
    dados = {
        "name": nome,
        "cpf": "00000000000",  # Dado deliberadamente fictício; não é CPF válido.
        "birthDay": "2000-01-01",
        "rg": "RG_TESTE_SEM_VALIDADE",
        "gender": "masculino",
        "isActive": False,
        "role": "Cargo 02",
        "usesEpi": False,
        "activity": "Ativid 02",
        "epi": "luvas-descartaveis",
        "caNumber": "00000",
    }
    try:
        yield dados
    finally:
        # Executa mesmo se um assert falhar. Nunca limpa pelo prefixo genérico.
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        registros = response.json()
        for registro in registros:
            if registro.get("state", {}).get("employee", {}).get("name") != nome:
                continue
            item_url = f"{api_url}/{registro['id']}"
            atual = requests.get(item_url, timeout=15)
            atual.raise_for_status()
            dono_confirmado = atual.json().get("state", {}).get("employee", {}).get("name") == nome
            if not dono_confirmado:
                pytest.fail("Limpeza interrompida: nome do registro mudou.")
            exclusao = requests.delete(item_url, timeout=15)
            if exclusao.status_code != 200:
                pytest.fail(f"Falha ao limpar dado sintético: {nome}")
            verificacao = requests.get(item_url, timeout=15)
            if verificacao.status_code != 404:
                pytest.fail(f"Registro sintético ainda existe: {nome}")


@pytest.fixture
def registro_api(trabalhador, api_url):
    response = requests.post(api_url, json={"state": {"employee": trabalhador}}, timeout=15)
    if response.status_code != 201:
        pytest.fail(f"Preparação falhou: POST retornou {response.status_code}.")
    registro = response.json()
    if "id" not in registro:
        pytest.fail("Preparação falhou: POST não retornou ID.")
    return registro
