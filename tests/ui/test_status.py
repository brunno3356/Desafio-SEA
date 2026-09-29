import time

import requests

from pages.listagem_page import ListagemPage


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

    # Pode haver outros trabalhadores chamados Brunno QA: compara a quantidade.
    lista = requests.get(api_url, timeout=15)
    assert lista.status_code == 200
    ativos_esperados = 0
    for item in lista.json():
        dados = item["state"]["employee"]
        if dados["name"] == trabalhador["name"] and dados["isActive"]:
            ativos_esperados += 1

    listagem = ListagemPage(browser)
    listagem.recarregar()
    listagem.aguardar_trabalhador(trabalhador["name"])
    time.sleep(5)  # Pausa para visualizar a listagem antes do filtro.
    listagem.filtrar_ativos()
    listagem.aguardar_quantidade_com_nome(trabalhador["name"], ativos_esperados)
    assert listagem.quantidade_com_nome(trabalhador["name"]) == ativos_esperados


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

    lista = requests.get(api_url, timeout=15)
    assert lista.status_code == 200
    ativos_esperados = 0
    for item in lista.json():
        dados = item["state"]["employee"]
        if dados["name"] == trabalhador["name"] and dados["isActive"]:
            ativos_esperados += 1

    listagem = ListagemPage(browser)
    listagem.recarregar()
    listagem.aguardar_trabalhador(trabalhador["name"])
    time.sleep(5)  # Pausa para visualizar a listagem antes do filtro.
    listagem.filtrar_ativos()
    listagem.aguardar_quantidade_com_nome(trabalhador["name"], ativos_esperados)
    assert listagem.quantidade_com_nome(trabalhador["name"]) == ativos_esperados
