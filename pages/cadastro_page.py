from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class CadastroPage:
    NOME = 'input[name="name"]'
    CPF = 'input[name="cpf"]'
    NASCIMENTO = 'input[name="birthDay"]'
    RG = 'input[name="rg"]'
    CARGO = 'label[for="role"] + div'
    SEM_EPI = 'input[type="checkbox"]'
    CA = 'input[name="caNumber"]'
    ATIVIDADE = 'label[for="activity"] + div'
    EPI = 'label[for="epi"] + div'
    OPCAO = '.ant-select-item-option[title="{}"]'
    SALVAR = 'button[type="submit"]'
    FORMULARIO = "form"

    def __init__(self, browser):
        # Recebe o Chrome que a fixture já abriu; não cria outro navegador.
        self.browser = browser
        self.wait = WebDriverWait(browser, 15)

    def preencher_dados(self, nome, cpf, nascimento, rg):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.NOME)))
        self.browser.find_element(By.CSS_SELECTOR, self.NOME).send_keys(nome)
        self.browser.find_element(By.CSS_SELECTOR, self.CPF).send_keys(cpf)
        self.browser.find_element(By.CSS_SELECTOR, self.NASCIMENTO).send_keys(nascimento, Keys.TAB)
        self.browser.find_element(By.CSS_SELECTOR, self.RG).send_keys(rg)

    def selecionar_cargo(self, cargo):
        self.browser.find_element(By.CSS_SELECTOR, self.CARGO).click()
        opcao = self.OPCAO.format(cargo)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, opcao)))
        self.browser.find_element(By.CSS_SELECTOR, opcao).click()

    def preencher_epi(self, atividade, epi, ca):
        self.browser.find_element(By.CSS_SELECTOR, self.CA).send_keys(ca)
        self.browser.find_element(By.CSS_SELECTOR, self.ATIVIDADE).click()
        opcao_atividade = self.OPCAO.format(atividade)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, opcao_atividade)))
        self.browser.find_element(By.CSS_SELECTOR, opcao_atividade).click()

        self.browser.find_element(By.CSS_SELECTOR, self.EPI).click()
        opcao_epi = self.OPCAO.format(epi)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, opcao_epi)))
        self.browser.find_element(By.CSS_SELECTOR, opcao_epi).click()

    def marcar_sem_epi(self):
        if not self.sem_epi_marcado():
            self.browser.find_element(By.CSS_SELECTOR, self.SEM_EPI).click()

    def sem_epi_marcado(self):
        return self.browser.find_element(By.CSS_SELECTOR, self.SEM_EPI).is_selected()

    def salvar(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.SALVAR)))
        self.browser.find_element(By.CSS_SELECTOR, self.SALVAR).click()

    def validade_cpf(self):
        return self.browser.find_element(By.CSS_SELECTOR, self.CPF).get_property("validity")

    def mensagem_validacao_cpf(self):
        return self.browser.find_element(By.CSS_SELECTOR, self.CPF).get_property("validationMessage")

    def formulario_visivel(self):
        return self.browser.find_element(By.CSS_SELECTOR, self.FORMULARIO).is_displayed()
