
# FUNCAO AUXILIAR: cadastra um usuario para os testes.
def make_user(client, name="Waldir"):
    response = client.post("/users", json={"name": name})

    assert response.status_code == 201

    return response.get_json()["id"]


# FUNCAO AUXILIAR: cadastra uma refeicao para os testes.
def make_meal(client, user_id):
    response = client.post("/meals", json={
        "name": "Almoco",
        "description": "Arroz, frango e salada",
        "eaten_at": "2026-10-04T12:30:00",
        "is_on_diet": True,
        "user_id": user_id
    })

    assert response.status_code == 201

    return response.get_json()["id"]


# TESTE 1: cadastro de usuario e refeicao.
def test_create_meal(client):
    user_id = make_user(client)
    meal_id = make_meal(client, user_id)

    assert isinstance(meal_id, int)
    assert meal_id > 0


# TESTE 2: listagem e consulta individual.
def test_list_and_get_meal(client):
    user_id = make_user(client)
    meal_id = make_meal(client, user_id)

    response = client.get(f"/users/{user_id}/meals")

    assert response.status_code == 200
    assert len(response.get_json()["meals"]) == 1

    response = client.get(
        f"/users/{user_id}/meals/{meal_id}"
    )

    assert response.status_code == 200
    assert response.get_json()["id"] == meal_id

    # Outro usuario nao pode consultar essa refeicao.
    other_user_id = make_user(client, "Outro usuario")

    response = client.get(
        f"/users/{other_user_id}/meals/{meal_id}"
    )

    assert response.status_code == 404


# TESTE 3: edicao de uma refeicao.
def test_update_meal(client):
    user_id = make_user(client)
    meal_id = make_meal(client, user_id)

    response = client.put(
        f"/users/{user_id}/meals/{meal_id}",
        json={
            "name": "Jantar",
            "description": "Peixe e legumes",
            "eaten_at": "2026-10-04T20:00:00",
            "is_on_diet": False
        }
    )

    assert response.status_code == 200
    assert response.get_json()["name"] == "Jantar"
    assert response.get_json()["is_on_diet"] is False

    # Confirma que a alteracao foi persistida.
    saved = client.get(
        f"/users/{user_id}/meals/{meal_id}"
    )

    assert saved.get_json()["name"] == "Jantar"


# TESTE 4: exclusao de uma refeicao.
def test_delete_meal(client):
    user_id = make_user(client)
    meal_id = make_meal(client, user_id)

    response = client.delete(
        f"/users/{user_id}/meals/{meal_id}"
    )

    assert response.status_code == 200

    # Uma refeicao excluida nao deve ser encontrada.
    response = client.get(
        f"/users/{user_id}/meals/{meal_id}"
    )

    assert response.status_code == 404


# TESTE 5: validacao de dados invalidos.
def test_invalid_meal(client):
    user_id = make_user(client)

    data = {
        "name": "Almoco",
        "description": "Frango e salada",
        "eaten_at": "2026-10-04T12:30:00",
        "is_on_diet": True,
        "user_id": user_id
    }

    # Indicador da dieta com tipo incorreto.
    response = client.post(
        "/meals",
        json={**data, "is_on_diet": "sim"}
    )

    assert response.status_code == 400

    # Data invalida.
    response = client.post(
        "/meals",
        json={**data, "eaten_at": "data-invalida"}
    )

    assert response.status_code == 400

    # Usuario inexistente.
    response = client.post(
        "/meals",
        json={**data, "user_id": 9999}
    )

    assert response.status_code == 404
