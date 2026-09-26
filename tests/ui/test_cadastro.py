import pytest
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_cadastro_campos_obrigatorios(browser):
    """Salvar vazio deve manter o formulário e indicar o primeiro obrigatório."""
    wait = WebDriverWait(browser, 10)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div:has(> h2) > button")))
    browser.find_element(By.CSS_SELECTOR, "div:has(> h2) > button").click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="name"]')))
    browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    nome = browser.find_element(By.CSS_SELECTOR, 'input[name="name"]')
    assert nome.get_property("validity")["valueMissing"] is True
    assert nome.get_property("validationMessage") != ""
    assert browser.find_element(By.CSS_SELECTOR, "form").is_displayed()


def test_cadastro_cpf_curto(browser):
    """Dez caracteres não atendem ao mínimo de onze do CPF."""
    wait = WebDriverWait(browser, 10)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div:has(> h2) > button")))
    browser.find_element(By.CSS_SELECTOR, "div:has(> h2) > button").click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="cpf"]')))
    browser.find_element(By.CSS_SELECTOR, 'input[name="name"]').send_keys("QA_SEA_VALIDACAO_LOCAL")
    browser.find_element(By.CSS_SELECTOR, 'input[name="cpf"]').send_keys("0000000000")
    browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    cpf = browser.find_element(By.CSS_SELECTOR, 'input[name="cpf"]')
    assert cpf.get_property("validity")["tooShort"] is True
    assert cpf.get_property("validationMessage") != ""
    assert browser.find_element(By.CSS_SELECTOR, "form").is_displayed()


def test_cadastro_sem_epi_oculta_campos(browser):
    """Marcar que não usa EPI remove os campos específicos de EPI."""
    wait = WebDriverWait(browser, 10)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div:has(> h2) > button")))
    browser.find_element(By.CSS_SELECTOR, "div:has(> h2) > button").click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="caNumber"]')))
    browser.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]').click()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'input[name="caNumber"]')))

    assert browser.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]').is_selected()
    assert browser.find_elements(By.CSS_SELECTOR, 'input[name="caNumber"]') == []
    assert browser.find_elements(By.CSS_SELECTOR, 'label[for="epi"]') == []


@pytest.mark.escrita
def test_cadastro_sucesso(trabalhador, browser, api_url):
    """Cadastro com seleções explícitas deve aparecer na listagem após recarregar."""
    wait = WebDriverWait(browser, 15)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div:has(> h2) > button")))
    browser.find_element(By.CSS_SELECTOR, "div:has(> h2) > button").click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="name"]')))
    browser.find_element(By.CSS_SELECTOR, 'input[name="name"]').send_keys(trabalhador["name"])
    browser.find_element(By.CSS_SELECTOR, 'input[name="cpf"]').send_keys(trabalhador["cpf"])
    browser.find_element(By.CSS_SELECTOR, 'input[name="birthDay"]').send_keys("01012000", Keys.TAB)
    browser.find_element(By.CSS_SELECTOR, 'input[name="rg"]').send_keys(trabalhador["rg"])
    browser.find_element(By.CSS_SELECTOR, 'label[for="role"] + div').click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.ant-select-item-option[title="Cargo 02"]')))
    browser.find_element(By.CSS_SELECTOR, '.ant-select-item-option[title="Cargo 02"]').click()
    browser.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]').click()
    browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.clear")))

    # A listagem faz GET antes de o POST terminar (BUG-004).
    # Recarregar é um contorno explícito deste teste de persistência.
    def cadastro_persistido(_):
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        return any(item.get("state", {}).get("employee", {}).get("name") == trabalhador["name"] for item in response.json())

    wait.until(cadastro_persistido)
    browser.refresh()
    wait.until(lambda b: any(trabalhador["name"] in item.text for item in b.find_elements(By.CSS_SELECTOR, 'div:has(> div > img[src*="dots-"])')))
    cartao = next(item for item in browser.find_elements(By.CSS_SELECTOR, 'div:has(> div > img[src*="dots-"])') if trabalhador["name"] in item.text)
    assert cartao.find_element(By.CSS_SELECTOR, "span").text == trabalhador["name"]
    assert "000.000.000-00" in cartao.text
    assert "Cargo 02" in cartao.text
