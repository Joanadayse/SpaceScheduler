SpaceScheduler
SpaceScheduler é uma aplicação web para agendamento de espaços. Usuários podem se cadastrar, fazer login, visualizar espaços disponíveis e realizar reservas de forma prática.

🚀 Tecnologias Utilizadas
Python

Flask

PostgreSQL

SQLAlchemy

Flask-WTF

Bootstrap (via HTML/CSS)

🛠️ Como Executar Localmente
Clone o repositório:
````
git clone https://github.com/Joanadayse/SpaceScheduler.git
````
````
cd SpaceScheduler
````
Crie e ative um ambiente virtual:
````
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
````
Instale as dependências:

````
pip install -r requirements.txt
````
Configure as variáveis de ambiente:

Crie um arquivo .env (ou configure diretamente no app.py se estiver usando localmente).

Defina variáveis como DATABASE_URL, SECRET_KEY, etc.

Execute a aplicação:
````
flask run

````
🌐 Deploy
O projeto foi implantado no Render, utilizando Gunicorn como servidor WSGI e PostgreSQL como banco de dados.
[Deploy](https://spacescheduler.onrender.com)



