
# Importa nossa aplicacao Flask.
from app import app, db
from sqlalchemy import text


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


# TESTE 4: confirma que estamos utilizando o banco exclusivo de testes.
def test_database_isolation():
    with app.app_context():
        active_db = db.session.execute(
            text("SELECT DATABASE()")
        ).scalar()

    assert active_db == "daily_diet_test"
