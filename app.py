import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.engine import URL
from datetime import datetime

# Carrega as variaveis do arquivo .env
load_dotenv()

app = Flask(__name__)


# Configuracao da conexao MySQL
app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
    "mysql+pymysql",
    username=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    host="127.0.0.1",
    port=3307,
    database=os.getenv("MYSQL_DATABASE"),
)

# Inicializa a integração com o banco
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    meals = db.relationship("Meal", back_populates="user")


class Meal(db.Model):
    __tablename__ = "meals"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    eaten_at = db.Column(db.DateTime, nullable=False)
    is_on_diet = db.Column(db.Boolean, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    user = db.relationship("User", back_populates="meals")


@app.get("/")
def home():
    return {"message": "Daily Diet API funcionando!"}

@app.get("/health/db")
def health_db():
    resultado = db.session.execute(text("SELECT 1")).scalar()
    return {"database": "connected", "result": resultado}


@app.post("/users")
def create_user():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error": "Envie um objeto JSON valido."}, 400

    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return {"error": "O nome e obrigatorio."}, 400

    user = User(name=name.strip())

    db.session.add(user)
    db.session.commit()

    return {
        "id": user.id,
        "name": user.name
    }, 201


@app.post("/meals")
def create_meal():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error": "Envie um JSON valido."}, 400

    name = data.get("name")
    description = data.get("description")
    eaten_at = data.get("eaten_at")
    is_on_diet = data.get("is_on_diet")
    user_id = data.get("user_id")

    if not isinstance(name, str) or not name.strip():
        return {"error": "O nome e obrigatorio."}, 400

    if not isinstance(description, str) or not description.strip():
        return {"error": "A descricao e obrigatoria."}, 400

    if not isinstance(is_on_diet, bool):
        return {"error": "is_on_diet deve ser true ou false."}, 400

    if type(user_id) is not int or user_id < 1:
        return {"error": "user_id deve ser um inteiro positivo."}, 400

    if not isinstance(eaten_at, str):
        return {"error": "Informe uma data e hora validas."}, 400

    try:
        meal_date = datetime.fromisoformat(eaten_at)
    except ValueError:
        return {"error": "Formato de data e hora invalido."}, 400

    user = db.session.get(User, user_id)

    if user is None:
        return {"error": "Usuario nao encontrado."}, 404

    meal = Meal(
        name=name.strip(),
        description=description.strip(),
        eaten_at=meal_date,
        is_on_diet=is_on_diet,
        user_id=user.id
    )

    db.session.add(meal)
    db.session.commit()

    return {
        "id": meal.id,
        "name": meal.name,
        "description": meal.description,
        "eaten_at": meal.eaten_at.isoformat(),
        "is_on_diet": meal.is_on_diet,
        "user_id": meal.user_id
    }, 201


if __name__ == '__main__':
    app.run(debug=True)