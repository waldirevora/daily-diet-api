
import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.engine import URL
from datetime import datetime


# Carrega as variaveis de ambiente do arquivo .env.
load_dotenv()

# Cria a instancia principal da aplicacao Flask.
app = Flask(__name__)


# Configura a conexao com o MySQL executado no Docker.
# Os dados de acesso sao recuperados das variaveis de ambiente.
app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
    "mysql+pymysql",
    username=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    host="127.0.0.1",
    port=3307,
    database=os.getenv("MYSQL_DATABASE"),
)

# Inicializa o SQLAlchemy para manipular o banco pelo Python.
db = SQLAlchemy(app)


# MODELO: USUARIO
# Representa a tabela users no banco de dados.
class User(db.Model):
    __tablename__ = "users"

    # Identificador unico e nome obrigatorio do usuario.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Relacionamento: um usuario pode possuir varias refeicoes.
    meals = db.relationship("Meal", back_populates="user")


# MODELO: REFEICAO
# Representa a tabela meals no banco de dados.
class Meal(db.Model):
    __tablename__ = "meals"

    # Dados que identificam e descrevem cada refeicao.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    eaten_at = db.Column(db.DateTime, nullable=False)
    is_on_diet = db.Column(db.Boolean, nullable=False)

    # Chave estrangeira que vincula a refeicao a um usuario.
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Permite acessar o usuario associado a refeicao.
    user = db.relationship("User", back_populates="meals")


# ROTA: GET /
# Retorna uma mensagem para confirmar que a API esta funcionando.
@app.get("/")
def home():
    return {"message": "Daily Diet API funcionando!"}


# ROTA: GET /health/db
# Executa uma consulta simples para verificar a conexao com o MySQL.
@app.get("/health/db")
def health_db():
    resultado = db.session.execute(text("SELECT 1")).scalar()

    return {"database": "connected", "result": resultado}


# ROTA: POST /users
# Recebe um nome em JSON, valida os dados e cadastra um usuario.
@app.post("/users")
def create_user():

    # Recupera os dados enviados no corpo da requisicao.
    data = request.get_json(silent=True)

    # Verifica se recebemos um objeto JSON valido.
    if not isinstance(data, dict):
        return {"error": "Envie um objeto JSON valido."}, 400

    name = data.get("name")

    # Impede o cadastro de usuarios sem um nome valido.
    if not isinstance(name, str) or not name.strip():
        return {"error": "O nome e obrigatorio."}, 400

    # Cria o objeto User e salva o registro no banco.
    user = User(name=name.strip())

    db.session.add(user)
    db.session.commit()

    # Retorna os dados cadastrados com HTTP 201 (Created).
    return {
        "id": user.id,
        "name": user.name
    }, 201


# ROTA: POST /meals
# Cadastra uma nova refeicao vinculada a um usuario existente.
@app.post("/meals")
def create_meal():

    # Recebe as informacoes enviadas em formato JSON.
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error": "Envie um JSON valido."}, 400

    # Extrai os campos necessarios para cadastrar a refeicao.
    name = data.get("name")
    description = data.get("description")
    eaten_at = data.get("eaten_at")
    is_on_diet = data.get("is_on_diet")
    user_id = data.get("user_id")

    # Valida o nome e a descricao da refeicao.
    if not isinstance(name, str) or not name.strip():
        return {"error": "O nome e obrigatorio."}, 400

    if not isinstance(description, str) or not description.strip():
        return {"error": "A descricao e obrigatoria."}, 400

    # Verifica se o indicador da dieta e um valor booleano.
    if not isinstance(is_on_diet, bool):
        return {"error": "is_on_diet deve ser true ou false."}, 400

    # Garante que o ID do usuario seja um inteiro positivo.
    if type(user_id) is not int or user_id < 1:
        return {"error": "user_id deve ser um inteiro positivo."}, 400

    # Verifica se recebemos a data e hora como texto.
    if not isinstance(eaten_at, str):
        return {"error": "Informe uma data e hora validas."}, 400

    # Converte a data recebida para um objeto datetime.
    # O try/except trata datas que nao podem ser convertidas.
    try:
        meal_date = datetime.fromisoformat(eaten_at)
    except ValueError:
        return {"error": "Formato de data e hora invalido."}, 400

    # Consulta o banco para verificar se o usuario existe.
    user = db.session.get(User, user_id)

    if user is None:
        return {"error": "Usuario nao encontrado."}, 404

    # Cria o objeto Meal com os dados previamente validados.
    meal = Meal(
        name=name.strip(),
        description=description.strip(),
        eaten_at=meal_date,
        is_on_diet=is_on_diet,
        user_id=user.id
    )

    # Adiciona a refeicao e confirma sua gravacao no banco.
    db.session.add(meal)
    db.session.commit()

    # Retorna a refeicao cadastrada com HTTP 201 (Created).
    return {
        "id": meal.id,
        "name": meal.name,
        "description": meal.description,
        "eaten_at": meal.eaten_at.isoformat(),
        "is_on_diet": meal.is_on_diet,
        "user_id": meal.user_id
    }, 201


# ROTA: GET /users/<user_id>/meals
# Lista todas as refeicoes pertencentes ao usuario informado.
@app.get("/users/<int:user_id>/meals")
def list_meals(user_id):

    # Verifica se o usuario solicitado existe.
    user = db.session.get(User, user_id)

    if user is None:
        return {"error": "Usuario nao encontrado."}, 404

    # Consulta as refeicoes do usuario e ordena da mais recente.
    meals = db.session.execute(
        db.select(Meal)
        .where(Meal.user_id == user_id)
        .order_by(Meal.eaten_at.desc())
    ).scalars().all()

    # Converte cada objeto Meal em um dicionario para retornar JSON.
    return {
        "meals": [
            {
                "id": meal.id,
                "name": meal.name,
                "description": meal.description,
                "eaten_at": meal.eaten_at.isoformat(),
                "is_on_diet": meal.is_on_diet,
                "user_id": meal.user_id
            }
            for meal in meals
        ]
    }, 200


# ROTA: GET /users/<user_id>/meals/<meal_id>
# Consulta uma refeicao especifica de determinado usuario.
@app.get("/users/<int:user_id>/meals/<int:meal_id>")
def get_meal(user_id, meal_id):

    # Procura a refeicao utilizando sua chave primaria.
    meal = db.session.get(Meal, meal_id)

    # Confirma que ela existe e pertence ao usuario informado.
    if meal is None or meal.user_id != user_id:
        return {
            "error": "Refeicao nao encontrada para este usuario."
        }, 404

    # Retorna os dados completos da refeicao encontrada.
    return {
        "id": meal.id,
        "name": meal.name,
        "description": meal.description,
        "eaten_at": meal.eaten_at.isoformat(),
        "is_on_diet": meal.is_on_diet,
        "user_id": meal.user_id
    }, 200


# ROTA: PUT /users/<user_id>/meals/<meal_id>
# Atualiza os dados de uma refeicao pertencente ao usuario.
@app.put("/users/<int:user_id>/meals/<int:meal_id>")
def update_meal(user_id, meal_id):

    # Procura a refeicao e verifica se pertence ao usuario.
    meal = db.session.get(Meal, meal_id)

    if meal is None or meal.user_id != user_id:
        return {"error": "Refeicao nao encontrada."}, 404

    # Recebe os novos dados em formato JSON.
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error": "Envie um JSON valido."}, 400

    name = data.get("name")
    description = data.get("description")
    eaten_at = data.get("eaten_at")
    is_on_diet = data.get("is_on_diet")

    # Valida os campos obrigatorios.
    if not isinstance(name, str) or not name.strip():
        return {"error": "O nome e obrigatorio."}, 400

    if not isinstance(description, str) or not description.strip():
        return {"error": "A descricao e obrigatoria."}, 400

    if not isinstance(is_on_diet, bool):
        return {"error": "is_on_diet deve ser true ou false."}, 400

    if not isinstance(eaten_at, str):
        return {"error": "Informe uma data e hora validas."}, 400

    # Converte a data recebida para datetime.
    try:
        meal_date = datetime.fromisoformat(eaten_at)
    except ValueError:
        return {"error": "Formato de data e hora invalido."}, 400

    # Atualiza os atributos do objeto existente.
    meal.name = name.strip()
    meal.description = description.strip()
    meal.eaten_at = meal_date
    meal.is_on_diet = is_on_diet

    # Confirma as alteracoes no MySQL.
    db.session.commit()

    # Retorna a refeicao atualizada.
    return {
        "id": meal.id,
        "name": meal.name,
        "description": meal.description,
        "eaten_at": meal.eaten_at.isoformat(),
        "is_on_diet": meal.is_on_diet,
        "user_id": meal.user_id
    }, 200


# ROTA: DELETE /users/<user_id>/meals/<meal_id>
# Exclui uma refeicao pertencente ao usuario informado.
@app.delete("/users/<int:user_id>/meals/<int:meal_id>")
def delete_meal(user_id, meal_id):

    # Procura a refeicao pelo seu identificador.
    meal = db.session.get(Meal, meal_id)

    # Verifica se existe e pertence ao usuario correto.
    if meal is None or meal.user_id != user_id:
        return {"error": "Refeicao nao encontrada."}, 404

    # Remove a refeicao e confirma a exclusao no banco.
    db.session.delete(meal)
    db.session.commit()

    # Retorna uma confirmacao da exclusao.
    return {
        "message": "Refeicao excluida com sucesso.",
        "id": meal_id
    }, 200


# Inicia o servidor apenas quando este arquivo e executado diretamente.
# O debug facilita o desenvolvimento e nao deve ser usado em producao.
if __name__ == '__main__':
    app.run(debug=True)
