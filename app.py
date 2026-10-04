import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.engine import URL

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


if __name__ == '__main__':
    app.run(debug=True)