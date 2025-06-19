## Contributing Guidelines for Soccer Central Web App (Python + Streamlit)

Gracias por tu interés en contribuir a Soccer Central. Este proyecto busca mantener estándares de calidad y claridad en el código. Por favor, sigue estas pautas antes de enviar una contribución.

---

### 🛠️ Requisitos del Entorno

* Python 3.10+
* Streamlit
* SQLAlchemy
* Otros paquetes listados en `requirements.txt`

Instalación de dependencias:

```bash
pip install -r requirements.txt
```

---

### 🧱 Convenciones de Código

* Usa `snake_case` para funciones y variables: `get_player_data()`
* Usa `CamelCase` para clases: `PlayerModel`
* Usa `MAYUSCULAS_CON_GUIONES` para constantes: `MAX_SCORE`

---

### 📄 Estructura del Proyecto

* `app.py`: página principal
* `pages/`: páginas secundarias de Streamlit (ej. `sc_assessments.py`)
* `models/`: clases SQLAlchemy (ORM)
* `utils/`: funciones auxiliares (login, formateos, etc.)
* `db/`: configuración y conexión a base de datos
* `assets/`: imágenes, logotipos, etc.

---

### 📑 Convención para Páginas de Streamlit

* `pages/player360.py` → Reporte 360° del jugador
* `pages/player_evaluation.py` → Evaluación de rendimiento

Usa prefijos como `sc_` para agrupar funcionalidad relacionada a Soccer Central.

---

### 🧪 Buenas Prácticas

* Agrupa la lógica principal en una función `main()`.
* Usa `if __name__ == '__main__': main()`
* Añade docstrings y comentarios útiles
* Evita repetir código innecesario
* Usa `@st.cache_resource` donde sea útil para rendimiento
* Usa `st.session_state` para manejar la sesión del usuario

---

### 🔐 Seguridad

* Nunca subas contraseñas ni claves API
* Usa variables de entorno (ej. `.env`) para datos sensibles
* No subas `.env`, `.sqlite` o credenciales en Git

---

### 🧼 Formato y Linter

* Usa [Black](https://black.readthedocs.io/en/stable/) como formateador automático:

  ```bash
  black .
  ```
* Usa `isort` para ordenar imports:

  ```bash
  isort .
  ```

---

### 🧪 Testing

* Usa `pytest` para pruebas unitarias
* Testea funciones críticas (validaciones, transformaciones, acceso a DB)

---

### ✅ Pull Requests

Antes de enviar un PR:

1. Asegúrate de que todo funcione (`streamlit run app.py`)
2. Asegúrate de que no subes archivos locales (`.venv`, `.env`, `.DS_Store`, etc.)
3. Comenta claramente lo que hace tu contribución
4. Añade capturas o descripciones si afecta a la UI

Gracias por contribuir a Soccer Central 🙌
