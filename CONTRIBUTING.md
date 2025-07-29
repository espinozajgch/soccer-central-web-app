Contributing Guidelines for Soccer Central Web App (Flask + HTML + JS)
Thank you for your interest in contributing to Soccer Central. This project provides a modern scouting and football analytics platform powered by Flask and an external API (Iterpro). Please follow these guidelines before submitting a contribution.

- Environment Requirements

Python 3.10+
Flask
requests
python-dotenv

All dependencies listed in requirements.txt

To install dependencies:
pip install -r requirements.txt

- Code Conventions
-- Python (Flask)

Use snake_case for variables and functions → get_players()
Use CamelCase for class names → PlayerProfile
Use UPPER_SNAKE_CASE for constants → BASE_URL

-- JavaScript
Use camelCase for functions and variables → fetchPlayers()

Write clear, modular, and documented code

Avoid repeating DOM queries or logic

- Project Structure

soccer-central-web-app/
├── app.py                # Main Flask app
├── iterpro_client.py     # API client for Iterpro
├── db/                   # Database configuration (if used)
├── templates/            # HTML templates (Jinja2)
│   ├── base.html
│   └── index.html
├── static/               # Static assets (JS, CSS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── utils/                # Utility Python scripts
├── .env                  # Environment variables (ignored by Git)
├── requirements.txt

- Best Practices
Wrap logic in functions where applicable

Keep views clean — offload logic to iterpro_client.py or utils/

Use @app.route() decorators for clear routing

Keep HTML templates semantic and accessible

Minimize inline JavaScript in templates

- Security
Never commit API keys or credentials

Use .env files and load them with python-dotenv

Make sure .env, .sqlite, and sensitive files are in .gitignore

- Formatting & Linting
Use Black for Python formatting: black .
Use isort to organize Python imports: isort .
Format your HTML and JS with an editor like VSCode using Prettier or similar extensions.

- Pull Requests
Before submitting a pull request:

Make sure the app runs locally (flask run)

Do not include personal config files (.DS_Store, .vscode/, etc.)

Clearly describe the purpose of the PR

Include screenshots or examples if your change affects the UI

Keep commits clean and meaningful

Thank you for contributing to Soccer Central!