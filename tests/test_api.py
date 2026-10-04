
# Importa nossa aplicacao Flask.
from app import app


# TESTE 1: verifica se a rota principal funciona.
def test_home():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Daily Diet API funcionando!"
    }


# TESTE 2: verifica o tratamento de uma rota inexistente.
def test_route_not_found():
    client = app.test_client()

    response = client.get("/rota-inexistente")

    assert response.status_code == 404


# TESTE 3: verifica a conexao com o MySQL.
def test_database_connection():
    client = app.test_client()

    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.get_json()["database"] == "connected"
    assert response.get_json()["result"] == 1
