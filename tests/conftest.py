
import os
from pathlib import Path

from dotenv import dotenv_values

# Localiza o arquivo .env.test na raiz do projeto.
project_root = Path(__file__).resolve().parents[1]
settings = dotenv_values(project_root / ".env.test")

# Impede que os testes utilizem o banco principal.
if (
    settings.get("MYSQL_DATABASE") != "daily_diet_test"
    or settings.get("MYSQL_USER") != "daily_diet_test_user"
    or not settings.get("MYSQL_PASSWORD")
):
    raise RuntimeError("Configuracao do banco de testes invalida.")

# Define as credenciais antes de importar a aplicacao.
for variable in ("MYSQL_DATABASE", "MYSQL_USER", "MYSQL_PASSWORD"):
    os.environ[variable] = settings[variable]

from app import app, db

# Ativa o modo de testes do Flask.
app.config["TESTING"] = True

# Confirma que a conexao utiliza exclusivamente o banco de testes.
with app.app_context():
    if (
        db.engine.url.database != "daily_diet_test"
        or db.engine.url.username != "daily_diet_test_user"
    ):
        raise RuntimeError("Conexao com banco incorreto.")
