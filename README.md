# Daily Diet API

API REST desenvolvida como desafio prático de Python da Rocketseat. Permite registrar e gerenciar refeições por usuário, identificando se cada refeição está dentro ou fora da dieta.

## Funcionalidades

- Cadastro de usuários.
- Cadastro de refeições com nome, descrição, data e hora e indicador de dieta.
- Listagem das refeições de um usuário, da mais recente para a mais antiga.
- Consulta individual, edição e exclusão de refeições.
- Persistência de dados em MySQL.
- Testes automatizados com banco exclusivo para testes.

## Tecnologias

Python, Flask, Flask-SQLAlchemy, PyMySQL, MySQL 8.4, Docker Compose e Pytest.

## Pré-requisitos

- Python (projeto desenvolvido com 3.14.7).
- Docker Desktop com Docker Compose em funcionamento.
- Git, caso deseje clonar o repositório.
- PowerShell (os comandos abaixo são para Windows).

## Instalação e execução

No PowerShell, clone o repositório e entre na pasta do projeto:

```powershell
git clone https://github.com/waldirevora/daily-diet-api.git
cd daily-diet-api
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz com os valores abaixo e substitua as senhas por credenciais locais próprias:

```dotenv
MYSQL_ROOT_PASSWORD=defina_uma_senha_root_forte
MYSQL_DATABASE=daily_diet
MYSQL_USER=daily_diet_user
MYSQL_PASSWORD=defina_uma_senha_da_aplicacao
```

Suba o banco de dados e verifique o container:

```powershell
docker compose up -d
docker compose ps
```

O MySQL utiliza a porta `3306` internamente e é disponibilizado somente em `127.0.0.1:3307` no computador. As informações persistem no volume Docker `mysql_data`.

Crie as tabelas e inicie a API:

```powershell
python init_db.py
python app.py
```

Com o servidor em execução, abra `http://127.0.0.1:5000/` ou `http://127.0.0.1:5000/health/db`.

> Execute os comandos `docker compose` dentro da pasta `daily-diet-api`, onde está o arquivo `compose.yaml`. O modo debug do Flask é apenas para desenvolvimento local.

## Endpoints

| Método | Rota                               | Operação                                        |
| ------ | ---------------------------------- | ----------------------------------------------- |
| GET    | `/`                                | Verificar funcionamento da API                  |
| GET    | `/health/db`                       | Verificar conexão com o banco                   |
| POST   | `/users`                           | Cadastrar usuário                               |
| POST   | `/meals`                           | Cadastrar refeição                              |
| GET    | `/users/<user_id>/meals`           | Listar refeições de um usuário                  |
| GET    | `/users/<user_id>/meals/<meal_id>` | Consultar uma refeição                          |
| PUT    | `/users/<user_id>/meals/<meal_id>` | Atualizar todos os campos editáveis da refeição |
| DELETE | `/users/<user_id>/meals/<meal_id>` | Excluir uma refeição                            |

### Exemplo: cadastrar um usuário

Envie `POST /users` com este JSON:

```json
{
  "name": "Usuario de exemplo"
}
```

### Exemplo: cadastrar uma refeição

Envie `POST /meals` com este JSON (ajuste `user_id` para um usuário existente):

```json
{
  "name": "Almoco",
  "description": "Arroz, frango e salada",
  "eaten_at": "2026-10-04T12:30:00",
  "is_on_diet": true,
  "user_id": 1
}
```

Para atualizar a refeição com `PUT`, envie os quatro campos editáveis: `name`, `description`, `eaten_at` e `is_on_diet`. O ID e o usuário associado são preservados. A API responde com códigos HTTP como `200` (sucesso), `201` (criado), `400` (dados inválidos) e `404` (registro não encontrado ou vínculo incompatível).

## Testes automatizados

Os testes CRUD utilizam um banco separado chamado `daily_diet_test`. A fixture de testes remove e recria tabelas **nesse banco de testes**, portanto nunca utilize nele dados que queira preservar.

Antes da primeira execução, crie o banco e o usuário de testes. Com o container em funcionamento, abra o MySQL administrativo:

```powershell
docker compose exec db mysql -u root -p
```

Dentro do prompt `mysql>`, execute (troque a senha de exemplo por outra de uso local):

```sql
CREATE DATABASE IF NOT EXISTS daily_diet_test
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'daily_diet_test_user'@'%'
IDENTIFIED BY 'defina_uma_senha_exclusiva_de_teste';

GRANT ALL PRIVILEGES ON daily_diet_test.*
TO 'daily_diet_test_user'@'%';

EXIT;
```

Crie um arquivo `.env.test` na raiz (não publique no GitHub):

```dotenv
MYSQL_DATABASE=daily_diet_test
MYSQL_USER=daily_diet_test_user
MYSQL_PASSWORD=defina_uma_senha_exclusiva_de_teste
```

A senha de `.env.test` deve corresponder à definida para esse usuário no MySQL. Execute a suíte:

```powershell
python -m pytest -v -p no:cacheprovider
```

A opção `-p no:cacheprovider` evita problemas de permissão com o cache do Pytest em diretórios sincronizados pelo OneDrive. Na última validação informada, **9 testes passaram**.

Os arquivos `.env` e `.env.test` estão excluídos do versionamento por `.gitignore`. O projeto é didático: as rotas associam dados por identificador de usuário, mas **não implementam autenticação real** para uso em produção.

## Estrutura principal

```text
daily-diet-api/
├── app.py
├── init_db.py
├── compose.yaml
├── requirements.txt
├── .gitignore
└── tests/
    ├── conftest.py
    ├── test_api.py
    └── test_crud.py
```

`.env`, `.env.test` e `.venv/` são arquivos e diretórios locais ignorados pelo Git.

## Repositório

https://github.com/waldirevora/daily-diet-api
