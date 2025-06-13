import pandas as pd
import mysql.connector


# Proceso para cargar la tabla players de soccercentral con el excel indicado

# 1. Leer el Excel
df = pd.read_excel('jugadores_byga_completo.xlsx')

# 2. Conectar a la base de datos
print(" Conectando a la base de datos...")
conn = mysql.connector.connect(
    host='dbmbds.cfngygfor8bi.us-east-1.rds.amazonaws.com',
    user='admin',
    password='mbdsf*2022',
    database='db_soccercentral'
)
cursor = conn.cursor()

# 3. Insertar o actualizar jugadores
print(f" Insertando {len(df)} jugadores...")

for _, row in df.iterrows():
    query = """
    INSERT INTO players (
        player_id, user_id, number, school_name, primary_position,
        secondary_position, birth_certificate_on_file, birthdate_verified,
        training_location, grade_level, phone, shirt_size, short_size,
        country_of_birth, country_of_citizenship, nationality, city,
        registration_date, education_level, last_team, dominant_foot,
        height, athlete_number, social_security_number, graduation_date,
        insurance_company, insurance_policy_number, insurance_group_number,
        sanctioned_outside_us, physician_name, physician_phone, health_notes,
        player_activity_history, notes
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    ON DUPLICATE KEY UPDATE
        user_id = VALUES(user_id),
        number = VALUES(number),
        school_name = VALUES(school_name),
        primary_position = VALUES(primary_position),
        secondary_position = VALUES(secondary_position),
        birth_certificate_on_file = VALUES(birth_certificate_on_file),
        birthdate_verified = VALUES(birthdate_verified),
        training_location = VALUES(training_location),
        grade_level = VALUES(grade_level),
        phone = VALUES(phone),
        shirt_size = VALUES(shirt_size),
        short_size = VALUES(short_size),
        country_of_birth = VALUES(country_of_birth),
        country_of_citizenship = VALUES(country_of_citizenship),
        nationality = VALUES(nationality),
        city = VALUES(city),
        registration_date = VALUES(registration_date),
        education_level = VALUES(education_level),
        last_team = VALUES(last_team),
        dominant_foot = VALUES(dominant_foot),
        height = VALUES(height),
        athlete_number = VALUES(athlete_number),
        social_security_number = VALUES(social_security_number),
        graduation_date = VALUES(graduation_date),
        insurance_company = VALUES(insurance_company),
        insurance_policy_number = VALUES(insurance_policy_number),
        insurance_group_number = VALUES(insurance_group_number),
        sanctioned_outside_us = VALUES(sanctioned_outside_us),
        physician_name = VALUES(physician_name),
        physician_phone = VALUES(physician_phone),
        health_notes = VALUES(health_notes),
        player_activity_history = VALUES(player_activity_history),
        notes = VALUES(notes)
    """
    values = (
        row.get('ID'),
        row.get('user_id'),
        row.get('number'),
        row.get('school_name'),
        row.get('primary_position'),
        row.get('secondary_position'),
        row.get('birth_certificate_on_file'),
        row.get('birthdate_verified'),
        row.get('training_location'),
        row.get('grade_level'),
        row.get('phone'),
        row.get('shirt_size'),
        row.get('short_size'),
        row.get('country_of_birth'),
        row.get('country_of_citizenship'),
        row.get('nationality'),
        row.get('city'),
        row.get('registration_date'),
        row.get('education_level'),
        row.get('last_team'),
        row.get('dominant_foot'),
        row.get('height'),
        row.get('athlete_number'),
        row.get('social_security_number'),
        row.get('graduation_date'),
        row.get('insurance_company'),
        row.get('insurance_policy_number'),
        row.get('insurance_group_number'),
        row.get('sanctioned_outside_us'),
        row.get('physician_name'),
        row.get('physician_phone'),
        row.get('health_notes'),
        row.get('player_activity_history'),
        row.get('notes')
    )
    try:
        cursor.execute(query, values)
    except Exception as e:
        print(f" Error al insertar jugador ID={row.get('ID')}: {e}")

# 4. Confirmar y cerrar
conn.commit()
cursor.close()
conn.close()
print(" Datos cargados y actualizados correctamente.")
