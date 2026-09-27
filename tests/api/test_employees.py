import requests


def test_consulta_employees(api_url):
    resposta = requests.get(api_url, timeout=15)
    assert resposta.status_code == 200
    assert resposta.headers["Content-Type"].startswith("application/json")

    registros = resposta.json()
    assert isinstance(registros, list), "A API deve retornar uma lista."

    for registro in registros:
        # Os asserts de tipo não imprimem nomes ou documentos de terceiros.
        id_valido = type(registro.get("id")) in (int, str)
        assert id_valido, "O registro deve ter um ID inteiro ou string."
        trabalhador = registro.get("state", {}).get("employee", {})
        for campo in ("name", "cpf", "birthDay", "rg", "gender", "role"):
            texto_valido = isinstance(trabalhador.get(campo), str)
            assert texto_valido, f"Campo {campo} ausente ou fora do tipo string."
        assert isinstance(trabalhador.get("isActive"), bool)
        assert isinstance(trabalhador.get("usesEpi"), bool)
