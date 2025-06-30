## Contributing Guidelines for Soccer Central Web App (Python + Streamlit)

Thank you for your interest in contributing to Soccer Central. This project aims to maintain high standards of code quality and clarity. Please follow these guidelines before submitting a contribution.

---

### 🛠️ Environment Requirements

* Python 3.10+
* Streamlit
* SQLAlchemy
* Other packages listed in `requirements.txt`

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

### 🧱 Code Conventions

* Use `snake_case` for functions and variables: `get_player_data()`
* Use `CamelCase` for classes: `PlayerModel`
* Use `UPPER_SNAKE_CASE` for constants: `MAX_SCORE`

---

### 📄 Project Structure

* `app.py`: main page
* `pages/`: additional Streamlit pages (e.g., `sc_assessments.py`)
* `models/`: SQLAlchemy classes (ORM)
* `utils/`: helper functions (login, formatting, etc.)
* `db/`: database configuration and connection
* `assets/`: images, logos, etc.

---

### 📑 Streamlit Page Naming Convention

* `pages/player360.py` → 360° Player Report
* `pages/player_evaluation.py` → Performance Evaluation

Use prefixes like `sc_` to group functionality related to Soccer Central.

---

### 🧪 Best Practices

* Wrap the main logic in a `main()` function.
* Use `if __name__ == '__main__': main()`
* Add helpful docstrings and comments
* Avoid unnecessary code repetition
* Use `@st.cache_resource` where appropriate for performance
* Use `st.session_state` to manage user session

---

### 🔐 Security

* Never commit passwords or API keys
* Use environment variables (e.g., `.env`) for sensitive data
* Do not upload `.env`, `.sqlite`, or credentials to Git

---

### 🧼 Formatting & Linting

* Use [Black](https://black.readthedocs.io/en/stable/) as the automatic formatter:

  ```bash
  black .
  ```
* Use `isort` to organize imports:

  ```bash
  isort .
  ```

---

### 🧪 Testing

* Use `pytest` for unit testing
* Test critical functions (validation, transformations, DB access)

---

### ✅ Pull Requests

Before submitting a PR:

1. Make sure everything runs (`streamlit run app.py`)
2. Ensure no local files are committed (`.venv`, `.env`, `.DS_Store`, etc.)
3. Clearly describe what your contribution does
4. Include screenshots or descriptions if it affects the UI

Thank you for contributing to Soccer Central 🙌

