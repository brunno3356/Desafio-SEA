import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_cadastro_sucesso(trabalhador, browser, api_url):
    wait = WebDriverWait(browser, 15)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "h2 + button")))
    browser.find_element(By.CSS_SELECTOR, "h2 + button").click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="name"]')))

    browser.find_element(By.CSS_SELECTOR, 'input[name="name"]').send_keys(trabalhador["name"])
    browser.find_element(By.CSS_SELECTOR, 'input[name="cpf"]').send_keys(trabalhador["cpf"])
    browser.find_element(By.CSS_SELECTOR, 'input[name="birthDay"]').send_keys("01012000", Keys.TAB)
    browser.find_element(By.CSS_SELECTOR, 'input[name="rg"]').send_keys(trabalhador["rg"])
    browser.find_element(By.CSS_SELECTOR, 'label[for="role"] + div').click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[title="Cargo 02"]')))
    browser.find_element(By.CSS_SELECTOR, '[title="Cargo 02"]').click()
    browser.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]').click()
    browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    # O site atualiza a lista antes de terminar de salvar. Aguarda e recarrega uma vez.
    def cadastro_salvo(_):
        resposta = requests.get(api_url, timeout=15)
        resposta.raise_for_status()
        for registro in resposta.json():
            if registro.get("state", {}).get("employee", {}).get("name") == trabalhador["name"]:
                return True
        return False

    wait.until(cadastro_salvo)
    browser.refresh()
    wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, "main"), trabalhador["name"]))
    nome_na_listagem = trabalhador["name"] in browser.find_element(By.CSS_SELECTOR, "main").text
    assert browser.find_element(By.CSS_SELECTOR, "h2").text == "Funcionário(s)"
    assert nome_na_listagem, "O trabalhador cadastrado não apareceu na listagem."


def test_cadastro_campo_obrigatorio(browser):
    wait = WebDriverWait(browser, 10)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "h2 + button")))
    browser.find_element(By.CSS_SELECTOR, "h2 + button").click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="name"]')))

    # Preenche os outros obrigatórios e deixa somente Nome vazio.
    browser.find_element(By.CSS_SELECTOR, 'input[name="cpf"]').send_keys("00000000000")
    browser.find_element(By.CSS_SELECTOR, 'input[name="birthDay"]').send_keys("01012000", Keys.TAB)
    browser.find_element(By.CSS_SELECTOR, 'input[name="rg"]').send_keys("RG_TESTE")
    browser.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]').click()
    browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    nome = browser.find_element(By.CSS_SELECTOR, 'input[name="name"]')
    assert nome.get_property("validity")["valueMissing"] is True
    assert nome.get_property("validationMessage") != ""
    assert browser.find_element(By.CSS_SELECTOR, "form").is_displayed()
