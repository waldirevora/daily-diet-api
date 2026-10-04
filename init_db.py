
# Importa a aplicacao Flask e a instancia do banco de dados.
from app import app, db


# Cria o contexto da aplicacao para permitir operacoes no banco.
with app.app_context():

    # Cria as tabelas definidas nos modelos, caso ainda nao existam.
    db.create_all()

    # Confirma que a operacao foi executada sem apresentar erros.
    print("Tabelas criadas com sucesso!")
