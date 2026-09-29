from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ListagemPage:
    ADICIONAR = "h2 + button"
    CONTEUDO = "main"
    TITULO = "h2"
    FILTRO_ATIVOS = "button:has(+ button.clear)"
    FILTRO_SELECIONADO = "button.isActive"

    def __init__(self, browser):
        self.browser = browser
        self.wait = WebDriverWait(browser, 15)

    def abrir_cadastro(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADICIONAR)))
        self.browser.find_element(By.CSS_SELECTOR, self.ADICIONAR).click()

    def recarregar(self):
        self.browser.refresh()

    def aguardar_trabalhador(self, nome):
        self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, self.CONTEUDO), nome))

    def titulo(self):
        return self.browser.find_element(By.CSS_SELECTOR, self.TITULO).text

    def trabalhador_visivel(self, nome):
        return nome in self.browser.find_element(By.CSS_SELECTOR, self.CONTEUDO).text

    def filtrar_ativos(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.FILTRO_ATIVOS)))
        self.browser.find_element(By.CSS_SELECTOR, self.FILTRO_ATIVOS).click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.FILTRO_SELECIONADO)))

    def quantidade_com_nome(self, nome):
        nomes_na_tela = self.browser.find_element(By.CSS_SELECTOR, self.CONTEUDO).text.splitlines()
        return nomes_na_tela.count(nome)

    def aguardar_quantidade_com_nome(self, nome, quantidade):
        self.wait.until(lambda _: self.quantidade_com_nome(nome) == quantidade)
