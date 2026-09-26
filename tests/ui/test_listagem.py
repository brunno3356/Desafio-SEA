from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_listagem_carrega(browser):
    """A listagem deve mostrar seu título e o total após carregar os dados."""
    wait = WebDriverWait(browser, 10)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.clear")))
    wait.until(lambda b: any(x.text.startswith("Ativos ") and x.text.split("/")[-1].isdigit() for x in b.find_elements(By.CSS_SELECTOR, "span")))

    assert browser.find_element(By.CSS_SELECTOR, "h2").text == "Funcionário(s)"
    assert browser.find_element(By.CSS_SELECTOR, "div:has(> h2) > button").text == "+ Adicionar Funcionário"


def test_limpar_filtro_restaura_listagem(browser):
    """Limpar filtros deve desfazer o filtro e restaurar a contagem inicial."""
    wait = WebDriverWait(browser, 10)
    wait.until(lambda b: any(x.text.startswith("Ativos ") and x.text.split("/")[-1].isdigit() for x in b.find_elements(By.CSS_SELECTOR, "span")))
    seletor_cartao = 'div:has(> div > img[src*="dots-"])'
    quantidade_inicial = len(browser.find_elements(By.CSS_SELECTOR, seletor_cartao))
    browser.find_element(By.CSS_SELECTOR, "button:has(+ button.clear)").click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.isActive")))
    browser.find_element(By.CSS_SELECTOR, "button.clear").click()
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "button.isActive")))

    assert browser.find_elements(By.CSS_SELECTOR, "button.isActive") == []
    assert len(browser.find_elements(By.CSS_SELECTOR, seletor_cartao)) == quantidade_inicial
