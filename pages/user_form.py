import streamlit as st
from datetime import date
from db import SessionLocal
from models import Users
import bcrypt
from sqlalchemy.orm import Session

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def User_Form():
    st.header(" Gestión de Usuarios", divider="gray")
    session: Session = SessionLocal()

    tabs = st.tabs(["➕ Nuevo Usuario", "✏️ Editar Usuario"])

    # =============== TAB 1: NUEVO USUARIO ===================
    with tabs[0]:
        with st.form("new_user_form"):
            st.subheader("Registrar nuevo usuario")

            first_name = st.text_input("Nombre")
            last_name = st.text_input("Apellido")
            email = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")
            birth_date = st.date_input("Fecha de nacimiento", value=date(2000, 1, 1))
            gender = st.selectbox("Género", ["Masculino", "Femenino", "Otro"])
            phone = st.text_input("Teléfono")
            country = st.text_input("País")
            photo_url = st.text_input("URL de Foto")
            role_id = st.number_input("ID de Rol", min_value=1, value=1)

            submitted = st.form_submit_button("Crear Usuario")

            if submitted:
                # Validación mínima
                if not email or not password:
                    st.error("Email y contraseña son obligatorios.")
                else:
                    existing = session.query(Users).filter_by(email=email).first()
                    if existing:
                        st.error("Ya existe un usuario con ese correo.")
                    else:
                        new_user = Users(
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            password_hash=hash_password(password),
                            birth_date=birth_date,
                            gender=gender,
                            phone=phone,
                            country=country,
                            photo_url=photo_url,
                            role_id=role_id
                        )
                        session.add(new_user)
                        session.commit()
                        st.success(f" Usuario creado con ID {new_user.user_id}")

    # =============== TAB 2: EDITAR USUARIO ===================
    with tabs[1]:
        usuarios = session.query(Users).order_by(Users.user_id).all()
        if not usuarios:
            st.info("No hay usuarios registrados.")
            return

        selected = st.selectbox(
            "Selecciona un usuario para editar",
            options=usuarios,
            format_func=lambda u: f"{u.user_id} - {u.first_name} {u.last_name}"
        )

        with st.form("edit_user_form"):
            st.subheader(f"Editando usuario ID {selected.user_id}")

            first_name = st.text_input("Nombre", value=selected.first_name)
            last_name = st.text_input("Apellido", value=selected.last_name)
            email = st.text_input("Correo electrónico", value=selected.email)
            password = st.text_input("Nueva contraseña", type="password", placeholder="Dejar en blanco para no cambiar")
            birth_date = st.date_input("Fecha de nacimiento", value=selected.birth_date or date(2000, 1, 1))
            gender = st.selectbox("Género", ["Masculino", "Femenino", "Otro"],
                                  index=["Masculino", "Femenino", "Otro"].index(selected.gender or "Masculino"))
            phone = st.text_input("Teléfono", value=selected.phone)
            country = st.text_input("País", value=selected.country)
            photo_url = st.text_input("URL de Foto", value=selected.photo_url)
            role_id = st.number_input("ID de Rol", min_value=1, value=selected.role_id or 1)

            submitted_edit = st.form_submit_button("Guardar Cambios")

            if submitted_edit:
                selected.first_name = first_name
                selected.last_name = last_name
                selected.email = email
                selected.birth_date = birth_date
                selected.gender = gender
                selected.phone = phone
                selected.country = country
                selected.photo_url = photo_url
                selected.role_id = role_id
                if password:
                    selected.password_hash = hash_password(password)

                session.commit()
                st.success(" Usuario actualizado correctamente.")
