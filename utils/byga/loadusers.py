import pandas as pd
import mysql.connector
from datetime import datetime

# Proceso para cargar la tabla users de soccercentral con el excel indicado

# Conexión a la BBDD
conn = mysql.connector.connect(
    host='dbmbds.cfngygfor8bi.us-east-1.rds.amazonaws.com',
    user='admin',
    password='mbdsf*2022',
    database='db_soccercentral'
)
cursor = conn.cursor()

# Carga del Excel
df = pd.read_excel("jugadores_byga_completo.xlsx")
df.columns = df.columns.str.strip().str.lower()  # normaliza encabezados


# Hash fijo de la contraseña 
password_hash = "$2b$12$43pTkPPZCNqMBQyev0b8meoovEpagDeqyOHMYa6a2RCnJytXIu9Xy"

insertados = 0
saltados = 0
procesados = 0

print(f" Procesando {len(df)} usuarios...\n")

for _, row in df.iterrows():
    procesados += 1
    try:
        user_id = int(row['id'])
        name = str(row['name']).strip()
        name_parts = name.split()

        if len(name_parts) >= 2:
            first_name = " ".join(name_parts[:-1])
            last_name = name_parts[-1]
        else:
            first_name = name
            last_name = ""

        email = str(row.get("player's email", '')).strip()
        if not email:
            print(f"  Sin email en fila {procesados}, saltado.")
            saltados += 1
            continue

        gender = str(row.get("gender", '')).capitalize().strip() or 'Unknown'
        birth_date = row.get("dob")
        phone = str(row.get("player's phone", '')).strip()
        country = str(row.get("country of citizenship", '')).strip()
        created_at = updated_at = datetime.now()

        # Verificamos si ya existe ese user_id
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if cursor.fetchone():
            print(f"  Usuario existente con ID {user_id} ({email}), saltado.")
            saltados += 1
            continue

        query = """
        INSERT INTO users (
            user_id, role_id, first_name, last_name, email, password_hash,
            birth_date, gender, phone, country, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            user_id, 4, first_name, last_name, email, password_hash,
            birth_date, gender, phone, country, created_at, updated_at
        )

        cursor.execute(query, values)
        insertados += 1
        print(f" Insertado {email} (ID {user_id})")

    except Exception as e:
        print(f" Error en fila {procesados} con email {email}: {e}")
        continue

conn.commit()
cursor.close()
conn.close()

print("\n Proceso finalizado.")
print(f" Usuarios insertados: {insertados}")
print(f" Usuarios existentes o incompletos saltados: {saltados}")
