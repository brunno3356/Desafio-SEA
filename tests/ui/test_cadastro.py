import time

import requests
from selenium.webdriver.support.ui import WebDriverWait

from pages.cadastro_page import CadastroPage
from pages.listagem_page import ListagemPage


def test_cadastro_sucesso(trabalhador, browser, api_url):
    listagem = ListagemPage(browser)
    cadastro = CadastroPage(browser)
    listagem.abrir_cadastro()
    cadastro.preencher_dados(
        nome=trabalhador["name"],
        cpf=trabalhador["cpf"],
        nascimento="01012000",
        rg=trabalhador["rg"],
    )
    cadastro.selecionar_cargo("Cargo 02")

    # Usa EPI: mantém "O trabalhador não usa EPI" desmarcado.
    cadastro.preencher_epi(atividade="Ativid 02", epi="Luvas descartáveis", ca="00000")
    assert not cadastro.sem_epi_marcado()

    time.sleep(5)  # Pausa para visualizar o formulário preenchido.
    cadastro.salvar()

    # Contorna a falha intermitente da listagem: aguarda a gravação antes da recarga.
    def cadastro_salvo(_):
        resposta = requests.get(api_url, timeout=15)
        resposta.raise_for_status()
        for registro in resposta.json():
            if registro.get("state", {}).get("employee", {}).get("rg") == trabalhador["rg"]:
                return registro["state"]["employee"]
        return False

    dados_salvos = WebDriverWait(browser, 15).until(cadastro_salvo)
    assert dados_salvos["activity"] == "Ativid 02"
    assert dados_salvos["epi"] == "luvas-descartaveis"
    assert dados_salvos["caNumber"] == "00000"
    listagem.recarregar()
    listagem.aguardar_trabalhador(trabalhador["name"])
    nome_na_listagem = listagem.trabalhador_visivel(trabalhador["name"])
    assert listagem.titulo() == "Funcionário(s)"
    assert nome_na_listagem, "O trabalhador cadastrado não apareceu na listagem."


def test_cadastro_cpf_invalido(trabalhador, browser):
    listagem = ListagemPage(browser)
    cadastro = CadastroPage(browser)
    listagem.abrir_cadastro()

    # Preenche os obrigatórios, mas informa um CPF com apenas 10 dígitos.
    cadastro.preencher_dados(
        nome=trabalhador["name"],
        cpf="0000000000",
        nascimento="01012000",
        rg=trabalhador["rg"],
    )
    cadastro.marcar_sem_epi()
    time.sleep(5)  # Pausa para visualizar o CPF inválido antes de salvar.
    cadastro.salvar()

    assert cadastro.validade_cpf()["tooShort"] is True
    assert cadastro.mensagem_validacao_cpf() != ""
    assert cadastro.formulario_visivel()
