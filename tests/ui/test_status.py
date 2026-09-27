import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_inativar_trabalhador(trabalhador, browser, api_url):
    trabalhador["isActive"] = True
    criacao = requests.post(api_url, json={"state": {"employee": trabalhador}}, timeout=15)
    assert criacao.status_code == 201
    registro = criacao.json()
    assert registro["state"]["employee"]["isActive"] is True
    url_registro = f"{api_url}/{registro['id']}"

    # A interface não permite editar: altera pela API e confere a listagem.
    trabalhador["isActive"] = False
    alteracao = requests.patch(url_registro, json={"state": {"employee": trabalhador}}, timeout=15)
    assert alteracao.status_code == 200
    consulta = requests.get(url_registro, timeout=15)
    assert consulta.status_code == 200
    assert consulta.json()["state"]["employee"]["isActive"] is False

    browser.refresh()
    wait = WebDriverWait(browser, 15)
    wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "main"), trabalhador["name"]))
    # O botão de ativos fica imediatamente antes de "Limpar filtros".
    browser.find_element(By.CSS_SELECTOR, "button:has(+ button.clear)").click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.isActive")))
    wait.until_not(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "main"), trabalhador["name"]))
    nome_entre_ativos = trabalhador["name"] in browser.find_element(By.CSS_SELECTOR, "main").text
    assert not nome_entre_ativos, "O trabalhador inativo ainda aparece no filtro de ativos."


def test_reativar_trabalhador(trabalhador, browser, api_url):
    trabalhador["isActive"] = False
    criacao = requests.post(api_url, json={"state": {"employee": trabalhador}}, timeout=15)
    assert criacao.status_code == 201
    registro = criacao.json()
    assert registro["state"]["employee"]["isActive"] is False
    url_registro = f"{api_url}/{registro['id']}"

    trabalhador["isActive"] = True
    alteracao = requests.patch(url_registro, json={"state": {"employee": trabalhador}}, timeout=15)
    assert alteracao.status_code == 200
    consulta = requests.get(url_registro, timeout=15)
    assert consulta.status_code == 200
    assert consulta.json()["state"]["employee"]["isActive"] is True

    browser.refresh()
    wait = WebDriverWait(browser, 15)
    wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "main"), trabalhador["name"]))
    browser.find_element(By.CSS_SELECTOR, "button:has(+ button.clear)").click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.isActive")))
    wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "main"), trabalhador["name"]))
    nome_entre_ativos = trabalhador["name"] in browser.find_element(By.CSS_SELECTOR, "main").text
    assert nome_entre_ativos, "O trabalhador reativado não apareceu no filtro de ativos."
