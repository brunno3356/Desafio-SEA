import time
from uuid import uuid4

import pytest
import requests
from selenium import webdriver


@pytest.fixture
def browser():
    browser = webdriver.Chrome()
    try:
        browser.set_window_size(1440, 1500)
        browser.get("https://analista-teste.seatecnologia.com.br/")
        yield browser
    finally:
        time.sleep(5)  # Mantém o resultado visível antes de fechar o Chrome.
        browser.quit()


@pytest.fixture
def api_url():
    return "https://analista-teste.seatecnologia.com.br/employees"


@pytest.fixture
def trabalhador(api_url):
    dados = {
        "name": "Brunno QA",
        "cpf": "00000000000",  # Fictício; a aplicação aceita, mas não é CPF válido.
        "birthDay": "2000-01-01",
        "rg": "RG_TESTE_" + uuid4().hex[:12],
        "gender": "masculino",
        "isActive": False,
        "role": "Cargo 02",
        "usesEpi": False,
        "activity": "",
        "epi": "",
        "caNumber": "",
    }
    print("Dados deste teste:", dados["name"], dados["rg"])
    try:
        yield dados
    finally:
        # Localiza o RG fictício exclusivo e limpa pelo ID; nomes podem se repetir.
        resposta = requests.get(api_url, timeout=15)
        resposta.raise_for_status()
        for registro in resposta.json():
            if registro.get("state", {}).get("employee", {}).get("rg") == dados["rg"]:
                url_registro = f"{api_url}/{registro['id']}"
                consulta = requests.get(url_registro, timeout=15)
                consulta.raise_for_status()
                assert consulta.json()["state"]["employee"]["name"] == dados["name"]
                assert consulta.json()["state"]["employee"]["rg"] == dados["rg"]
                exclusao = requests.delete(url_registro, timeout=15)
                assert exclusao.status_code == 200, "Não foi possível limpar o registro."
                assert requests.get(url_registro, timeout=15).status_code == 404
