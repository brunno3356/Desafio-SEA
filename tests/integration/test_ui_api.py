import pytest
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_filtro_ativos_corresponde_api(browser, api_url):
    response = requests.get(api_url, timeout=15)
    assert response.status_code == 200
    registros = response.json()
    esperados = sorted(x["state"]["employee"]["name"] for x in registros if x["state"]["employee"]["isActive"])
    wait = WebDriverWait(browser, 10)
    wait.until(lambda b: any(x.text.startswith("Ativos ") and x.text.split("/")[-1].isdigit() for x in b.find_elements(By.CSS_SELECTOR, "span")))
    browser.find_element(By.CSS_SELECTOR, "button:has(+ button.clear)").click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.isActive")))
    nomes_ui = sorted(item.find_element(By.CSS_SELECTOR, "span").text for item in browser.find_elements(By.CSS_SELECTOR, 'div:has(> div > img[src*="dots-"])'))
    # Comparamos em memória; não registramos nomes de terceiros na evidência.
    mesmos_nomes = nomes_ui == esperados
    assert mesmos_nomes, "O filtro de ativos diverge da resposta da API."


@pytest.mark.escrita
@pytest.mark.xfail(strict=True, raises=AssertionError, reason="BUG-001: seleções iniciais não são persistidas")
def test_cadastro_preserva_selecoes_iniciais_na_api(trabalhador, browser, api_url):
    """Valores visíveis no formulário devem ser enviados e persistidos."""
    wait = WebDriverWait(browser, 15)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div:has(> h2) > button")))
    browser.find_element(By.CSS_SELECTOR, "div:has(> h2) > button").click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="name"]')))
    browser.find_element(By.CSS_SELECTOR, 'input[name="name"]').send_keys(trabalhador["name"])
    browser.find_element(By.CSS_SELECTOR, 'input[name="cpf"]').send_keys(trabalhador["cpf"])
    browser.find_element(By.CSS_SELECTOR, 'input[name="birthDay"]').send_keys("01012000", Keys.TAB)
    browser.find_element(By.CSS_SELECTOR, 'input[name="rg"]').send_keys(trabalhador["rg"])
    browser.find_element(By.CSS_SELECTOR, 'input[name="caNumber"]').send_keys(trabalhador["caNumber"])
    cargo_visivel = browser.find_element(By.CSS_SELECTOR, 'label[for="role"] + div .ant-select-selection-item').text
    atividade_visivel = browser.find_element(By.CSS_SELECTOR, 'label[for="activity"] + div .ant-select-selection-item').text
    epi_visivel = browser.find_element(By.CSS_SELECTOR, 'label[for="epi"] + div .ant-select-selection-item').get_attribute("title")
    assert epi_visivel == "Capacete de segurança"
    browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "form")))

    def buscar_cadastro(_):
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        return next((x["state"]["employee"] for x in response.json() if x.get("state", {}).get("employee", {}).get("name") == trabalhador["name"]), False)

    employee = wait.until(buscar_cadastro)
    obtidos = {"name": employee.get("name"), "cpf": employee.get("cpf"), "role": employee.get("role"), "activity": employee.get("activity"), "epi": employee.get("epi")}
    esperados = {"name": trabalhador["name"], "cpf": trabalhador["cpf"], "role": cargo_visivel, "activity": atividade_visivel, "epi": "capacete-de-segurança"}
    assert obtidos == esperados
