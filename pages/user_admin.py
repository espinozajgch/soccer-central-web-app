import streamlit as st
from sqlalchemy.orm import Session, joinedload
from db.models import Users, Players, Roles
from db.db import engine
from db.db import hash_password, check_password
from utils import login
from datetime import date

# Session check
login.generarLogin()
if "usuario" not in st.session_state:
    st.stop()

current_user = login.get_logged_in_user()
# Only admin can access
if not current_user or current_user.role_id != 1:
    st.error("Access denied. Only admin users can access this page.")
    st.stop()

st.header("User Management", divider=True)

tabs = st.tabs(["Add User", "Edit User", "Edit Player Profile"])

# ===== TAB 1: ADD USER =====
with tabs[0]:
    with Session(engine) as session:
        if st.session_state.get("user_created_successfully"):
            st.success("User created successfully.")
            st.session_state["user_created_successfully"] = False

        roles = session.query(Roles).order_by(Roles.role_id).all()
        role_names = [r.role_name for r in roles]

        # Role Selection OUTSIDE the form
        st.subheader("Role Selection")
        selected_role_name = st.selectbox("Role", role_names, index=role_names.index("Admin"))
        role_id = next(r.role_id for r in roles if r.role_name == selected_role_name)

        # Form starts here
        with st.form("add_user_form"):
            st.subheader("User Information")

            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            birth_date = st.date_input("Birth Date", value=date(2000, 1, 1))
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            phone = st.text_input("Phone Number")
            country = st.text_input("Country")
            photo_url = st.text_input("Photo URL")

            if selected_role_name == "Player":
                st.subheader("Player Profile")
                number = st.number_input("Jersey Number", value=0)
                school_name = st.text_input("School Name")
                primary_position = st.text_input("Primary Position")
                secondary_position = st.text_input("Secondary Position")
                birth_certificate_on_file = st.checkbox("Birth Certificate on File")
                birthdate_verified = st.checkbox("Birthdate Verified")
                training_location = st.text_input("Training Location")
                grade_level = st.text_input("Grade Level")
                player_phone = st.text_input("Player Phone")
                shirt_size = st.text_input("Shirt Size")
                short_size = st.text_input("Short Size")
                country_of_birth = st.text_input("Country of Birth")
                country_of_citizenship = st.text_input("Country of Citizenship")
                nationality = st.text_input("Nationality")
                city = st.text_input("City")
                registration_date = st.date_input("Registration Date", value=date.today())
                education_level = st.text_input("Education Level")
                last_team = st.text_input("Last Team")
                dominant_foot = st.selectbox("Dominant Foot", ["Right", "Left", "Both", "Unknown"])
                height = st.number_input("Height (cm)", value=170.0, step=1.0)
                weight = st.number_input("Weight (kg)", value=70.0, step=1.0)
                body_fat_percentage = st.number_input("Body Fat Percentage (%)", value=15.0, step=0.1)
                last_measurement_date = st.date_input("Last Measurement Date", value=date.today())
                athlete_number = st.text_input("Athlete Number")
                social_security_number = st.text_input("Social Security Number")
                graduation_date = st.date_input("Graduation Date", value=date(2025, 6, 1))
                insurance_company = st.text_input("Insurance Company")
                insurance_policy_number = st.text_input("Insurance Policy Number")
                insurance_group_number = st.text_input("Insurance Group Number")
                sanctioned_outside_us = st.checkbox("Sanctioned Outside US")
                physician_name = st.text_input("Physician Name")
                physician_phone = st.text_input("Physician Phone")
                health_notes = st.text_area("Health Notes")
                player_activity_history = st.text_area("Player Activity History")
                notes = st.text_area("General Notes")


            submitted = st.form_submit_button("Create User")

            if submitted:
                if not first_name or not last_name or not email or not password or not confirm_password:
                    st.error("You should fill name, email and password fields")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif session.query(Users).filter_by(email=email).first():
                    st.error("A user with this email already exists.")
                else:
                    try:
                        password_hashed = hash_password(password)

                        new_user = Users(
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            password_hash=password_hashed,
                            birth_date=birth_date,
                            gender=gender,
                            phone=phone,
                            country=country,
                            photo_url=photo_url,
                            role_id=role_id
                        )
                        session.add(new_user)
                        session.flush()

                        if role_id == 4:
                             new_player = Players(
                                user_id=new_user.user_id,
                                number=number,
                                school_name=school_name,
                                primary_position=primary_position,
                                secondary_position=secondary_position,
                                birth_certificate_on_file=birth_certificate_on_file,
                                birthdate_verified=birthdate_verified,
                                training_location=training_location,
                                grade_level=grade_level,
                                phone=player_phone,
                                shirt_size=shirt_size,
                                short_size=short_size,
                                country_of_birth=country_of_birth,
                                country_of_citizenship=country_of_citizenship,
                                nationality=nationality,
                                city=city,
                                registration_date=registration_date,
                                education_level=education_level,
                                last_team=last_team,
                                dominant_foot=dominant_foot,
                                height=height,
                                weight=weight,
                                body_fat_percentage=body_fat_percentage,
                                last_measurement_date=last_measurement_date,
                                athlete_number=athlete_number,
                                social_security_number=social_security_number,
                                graduation_date=graduation_date,
                                insurance_company=insurance_company,
                                insurance_policy_number=insurance_policy_number,
                                insurance_group_number=insurance_group_number,
                                sanctioned_outside_us=sanctioned_outside_us,
                                physician_name=physician_name,
                                physician_phone=physician_phone,
                                health_notes=health_notes,
                                player_activity_history=player_activity_history,
                                notes=notes
                            )
                        session.add(new_player)
                        session.commit()

                        st.session_state["user_created_successfully"] = True
                        st.rerun()

                    except Exception as e:
                        session.rollback()
                        st.error(f"Error: {e}")

# ===== TAB 2: EDIT USER =====
with tabs[1]:
    with Session(engine) as session:
        if st.session_state.get("user_updated_successfully"):
            st.success("User updated successfully.")
            st.session_state["user_updated_successfully"] = False

        users = session.query(Users).options(joinedload(Users.role)).order_by(Users.last_name).all()
        if not users:
            st.info("No users found.")
            st.stop()

        roles = session.query(Roles).order_by(Roles.role_id).all()
        role_names = [r.role_name for r in roles]

        selected_user = st.selectbox(
            "Select User",
            users,
            format_func=lambda u: f"{u.first_name} {u.last_name} (ID: {u.user_id})"
        )

        with st.form("edit_user_form"):
            st.subheader("Edit User Information")
            first_name = st.text_input("First Name", value=selected_user.first_name)
            last_name = st.text_input("Last Name", value=selected_user.last_name)
            email = st.text_input("Email", value=selected_user.email or "")
            phone = st.text_input("Phone Number", value=selected_user.phone or "")
            country = st.text_input("Country", value=selected_user.country or "")
            selected_role_name = st.selectbox(
                "Role",
                role_names,
                index=role_names.index(selected_user.role.role_name if selected_user.role else "Player")
            )
            role_id = next(r.role_id for r in roles if r.role_name == selected_role_name)

            submitted = st.form_submit_button("Save Changes")

            if submitted:
                try:
                    user = session.query(Users).filter_by(user_id=selected_user.user_id).one()

                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = email
                    user.phone = phone
                    user.country = country
                    user.role_id = role_id

                    session.commit()

                    st.session_state["user_updated_successfully"] = True
                    st.rerun()

                except Exception as e:
                    session.rollback()
                    st.error(f"Update error: {e}")

# ===== TAB 3: EDIT PLAYER =====
with tabs[2]:
    with Session(engine) as session:
        if st.session_state.get("player_updated_successfully"):
            st.success("Player profile updated successfully.")
            st.session_state["player_updated_successfully"] = False

        players = session.query(Players).options(joinedload(Players.user)).join(Users).filter(Users.role_id == 4).order_by(Users.last_name).all()

        if not players:
            st.info("No players found.")
            st.stop()

        selected_player = st.selectbox(
            "Select Player",
            players,
            format_func=lambda p: f"{p.user.first_name} {p.user.last_name} (ID: {p.player_id})"
        )

        with st.form("edit_player_form"):
            st.subheader("Edit Player Profile")
            number = st.number_input("Jersey Number", value=selected_player.number or 0)
            school_name = st.text_input("School Name", value=selected_player.school_name or "")
            primary_position = st.text_input("Primary Position", value=selected_player.primary_position or "")
            secondary_position = st.text_input("Secondary Position", value=selected_player.secondary_position or "")
            birth_certificate_on_file = st.checkbox("Birth Certificate on File", value=selected_player.birth_certificate_on_file)
            birthdate_verified = st.checkbox("Birthdate Verified", value=selected_player.birthdate_verified)
            training_location = st.text_input("Training Location", value=selected_player.training_location or "")
            grade_level = st.text_input("Grade Level", value=selected_player.grade_level or "")
            player_phone = st.text_input("Player Phone", value=selected_player.phone or "")
            shirt_size = st.text_input("Shirt Size", value=selected_player.shirt_size or "")
            short_size = st.text_input("Short Size", value=selected_player.short_size or "")
            country_of_birth = st.text_input("Country of Birth", value=selected_player.country_of_birth or "")
            country_of_citizenship = st.text_input("Country of Citizenship", value=selected_player.country_of_citizenship or "")
            nationality = st.text_input("Nationality", value=selected_player.nationality or "")
            city = st.text_input("City", value=selected_player.city or "")
            registration_date = st.date_input("Registration Date", value=selected_player.registration_date or date.today())
            education_level = st.text_input("Education Level", value=selected_player.education_level or "")
            last_team = st.text_input("Last Team", value=selected_player.last_team or "")
            dominant_foot = st.selectbox("Dominant Foot", ["Right", "Left", "Both", "Unknown"], index=["Right", "Left", "Both", "Unknown"].index(selected_player.dominant_foot or "Right"))
            height = st.number_input("Height (cm)", value=float(selected_player.height or 170), step=1.0)
            weight = st.number_input("Weight (kg)", value=float(selected_player.weight or 70), step=1.0)
            body_fat_percentage = st.number_input("Body Fat Percentage (%)", value=float(selected_player.body_fat_percentage or 15), step=0.1)
            last_measurement_date = st.date_input("Last Measurement Date", value=selected_player.last_measurement_date or date.today())
            athlete_number = st.text_input("Athlete Number", value=selected_player.athlete_number or "")
            social_security_number = st.text_input("Social Security Number", value=selected_player.social_security_number or "")
            graduation_date = st.date_input("Graduation Date", value=selected_player.graduation_date or date(2025, 6, 1))
            insurance_company = st.text_input("Insurance Company", value=selected_player.insurance_company or "")
            insurance_policy_number = st.text_input("Insurance Policy Number", value=selected_player.insurance_policy_number or "")
            insurance_group_number = st.text_input("Insurance Group Number", value=selected_player.insurance_group_number or "")
            sanctioned_outside_us = st.checkbox("Sanctioned Outside US", value=selected_player.sanctioned_outside_us)
            physician_name = st.text_input("Physician Name", value=selected_player.physician_name or "")
            physician_phone = st.text_input("Physician Phone", value=selected_player.physician_phone or "")
            health_notes = st.text_area("Health Notes", value=selected_player.health_notes or "")
            player_activity_history = st.text_area("Player Activity History", value=selected_player.player_activity_history or "")
            notes = st.text_area("General Notes", value=selected_player.notes or "")

            submitted = st.form_submit_button("Save Changes")
            if submitted:
                try:
                    player = session.query(Players).filter_by(player_id=selected_player.player_id).one()
                    player.number = number
                    player.school_name = school_name
                    player.primary_position = primary_position
                    player.secondary_position = secondary_position
                    player.birth_certificate_on_file = birth_certificate_on_file
                    player.birthdate_verified = birthdate_verified
                    player.training_location = training_location
                    player.grade_level = grade_level
                    player.phone = player_phone
                    player.shirt_size = shirt_size
                    player.short_size = short_size
                    player.country_of_birth = country_of_birth
                    player.country_of_citizenship = country_of_citizenship
                    player.nationality = nationality
                    player.city = city
                    player.registration_date = registration_date
                    player.education_level = education_level
                    player.last_team = last_team
                    player.dominant_foot = dominant_foot
                    player.height = height
                    player.weight = weight
                    player.body_fat_percentage = body_fat_percentage
                    player.last_measurement_date = last_measurement_date
                    player.athlete_number = athlete_number
                    player.social_security_number = social_security_number
                    player.graduation_date = graduation_date
                    player.insurance_company = insurance_company
                    player.insurance_policy_number = insurance_policy_number
                    player.insurance_group_number = insurance_group_number
                    player.sanctioned_outside_us = sanctioned_outside_us
                    player.physician_name = physician_name
                    player.physician_phone = physician_phone
                    player.health_notes = health_notes
                    player.player_activity_history = player_activity_history
                    player.notes = notes

                    session.commit()
                    st.session_state["player_updated_successfully"] = True
                    st.rerun()
                except Exception as e:
                    session.rollback()
                    st.error(f"Error updating player: {e}")

