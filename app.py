import os

from flask import Flask
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

@app.get("/")
def home():
    return {"message": "Daily Diet API funcionando!"}

@app.get("/health/db")
def health_db():
    resultado = db.session.execute(text("SELECT 1")).scalar()
    return {"database": "connected", "result": resultado}

if __name__ == '__main__':
    app.run(debug=True)