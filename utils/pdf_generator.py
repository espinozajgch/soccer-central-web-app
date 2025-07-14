from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import tempfile
import pandas as pd
import requests
import os


class CustomPDF(FPDF):
    def header(self):
        # fondo azul oscuro
        self.set_fill_color(10, 15, 61)
        self.rect(0, 0, 210, 297, 'F')
        self.set_text_color(255, 255, 255)

def generate_styled_radar_chart(data_dict):
    labels = list(data_dict.keys())
    values = list(data_dict.values())
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#0A0F3D')
    ax.set_facecolor('#0A0F3D')
    ax.spines['polar'].set_color('white')
    ax.tick_params(colors='white')
    ax.grid(color='white', linestyle='--', linewidth=0.5)
    ax.plot(angles, values, color='lime', linewidth=2)
    ax.fill(angles, values, color='lime', alpha=0.3)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color='white', fontsize=9)
    ax.set_yticklabels([])
    ax.text(0, 0, f"{int(np.mean(values[:-1]))}", color='white', fontsize=16, ha='center', va='center', weight='bold')
    return fig


# Construir tabla a partir de player_assessments

def build_evaluation_table_from_df(df):
    categories = [
        "Values", "Skills", "Game Model", "Performance",
        "Mental & Leadership", "Match Performance", "Evolution"
    ]
    table = {cat: [] for cat in categories}
    for _, row in df.iterrows():
        cat_key = next((c for c in categories if c.lower() in row['category'].lower()), None)
        if cat_key:
            text = f"{row['item']}: {row['value']}"
            table[cat_key].append(text)
    return table



def generate_player_report(player_data, player_teams, player_games, player_metrics,
                           player_evaluations, player_videos, player_documents, teams_df, player_assessments):

    pdf = CustomPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_text_color(255, 255, 255)

    # Foto del jugador
    photo_url = player_data.get("photo_url") or "https://cdn-icons-png.flaticon.com/512/149/149071.png"

    if photo_url:
        try:
            response = requests.get(photo_url, stream=True, timeout=10)
            content_type = response.headers.get('Content-Type', '')
            print(f"DEBUG: status={response.status_code}, content-type={content_type}")

            if response.status_code == 200 and 'image' in content_type:
                ext = ".jpg" if "jpeg" in content_type else ".png"
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as img_tmp:
                    img_tmp.write(response.content)
                    img_tmp.flush()
                    img_path = img_tmp.name

                # Insertar imagen en el PDF
                pdf.image(img_path, x=15, y=15, w=30, h=30)

                # Eliminar archivo temporal
                os.remove(img_path)
            else:
                print(f"WARNING: Failed to fetch image or invalid content type. Status: {response.status_code}")
        except Exception as e:
            print(f"ERROR loading photo: {e}")


    # Datos debajo de la foto
    y_info = 50
    pdf.set_xy(15, y_info)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, f"{player_data['first_name']} {player_data['last_name']} (ID: {player_data.get('player_id', '')})", ln=1)
    pdf.set_font("Arial", "", 10)
    pdf.set_x(15)
    pdf.cell(0, 6, f"{player_data.get('primary_position', 'N/A')}", ln=1)
    pdf.set_x(15)
    pdf.cell(0, 6, f"DOB: {player_data['birth_date'].strftime('%Y-%m-%d')}", ln=1)
    pdf.set_x(15)
    pdf.cell(0, 6, f"Height: {player_data.get('height', 'N/A')} cm", ln=1)
    pdf.set_x(15)
    pdf.cell(0, 6, f"Weight: {player_data.get('weight', 'N/A')} kg", ln=1)

    # Radar chart centrado
    radar_categories = ["VALUES", "SKILLS", "GAME MODEL", "PERFORMANCE", "LEADERSHIP"]
    radar_data = {}
    for cat in radar_categories:
        subset = player_evaluations[player_evaluations["category"].str.contains(cat, case=False, na=False)]
        radar_data[cat] = round(subset["value"].astype(float).mean(), 1) if not subset.empty else 0

    fig = generate_styled_radar_chart(radar_data)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        fig.savefig(tmp.name, bbox_inches="tight", facecolor=fig.get_facecolor())
        radar_img_path = tmp.name
    plt.close(fig)
    pdf.image(radar_img_path, x=75, y=25, w=60)

    # Specific Trainings a la derecha del radar
    pdf.set_xy(145, 25)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 6, "Specific trainings", ln=1)
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(255, 255, 255)
    for label in ["EPx GK", "EPx SK", "EPx HP", "EPx VA"]:
        pdf.set_x(145)
        pdf.cell(40, 8, f"> {label}", ln=1)

    # === Pintar tabla de evaluaciones horizontal ===
    pdf.set_y(120)
    table_data = build_evaluation_table_from_df(player_assessments)

    col_titles = ["Values", "Skills", "Game Model", "Performance", "Mental & Leadership", "Evolution"]
    col_width = 35
    row_height = 12

    # Estilo cabecera
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(185, 49, 96)
    pdf.set_text_color(255, 255, 255)

    # Cabeceras
    table_margin = (210 - (col_width * len(col_titles))) / 2  # centrar
    pdf.set_x(table_margin)
    for title in col_titles:
        pdf.cell(col_width, row_height, title, border=1, align="C", fill=True)
    pdf.ln(row_height)

    # Cuerpo de la tabla
    pdf.set_font("Arial", "", 8)
    pdf.set_fill_color(115, 0, 36)

    # Calcular máximo número de filas
    max_rows = max(len(table_data.get(col, [])) for col in col_titles)
    
    for i in range(max_rows):
        pdf.set_x(table_margin)
        for col in col_titles:
            items = table_data.get(col, [])
            text = items[i] if i < len(items) else ""
            # Cortar si es muy largo
            text = text[:40] + "..." if len(text) > 43 else text
            pdf.cell(col_width, row_height, text, border=1, fill=True)
        pdf.ln(row_height)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)