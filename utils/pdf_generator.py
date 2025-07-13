from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import tempfile
import pandas as pd
import requests
import os


def generate_radar_chart(data_dict):
    labels = list(data_dict.keys())
    values = list(data_dict.values())
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(3.2, 3.2), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='gray', alpha=0.4)
    ax.plot(angles, values, color='black', linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.text(0, 0, f"{int(np.mean(values[:-1]))}", ha='center', va='center', fontsize=16, weight='bold')
    return fig


def build_evaluation_table(df):
    categories = [
        "Core Value", "Skills", "Game Model", "Performance",
        "Mental & Leadership", "Match Performance", "Evolution and Recommendation"
    ]
    table_data = {cat: [] for cat in categories}

    for _, row in df.iterrows():
        for cat in categories:
            if cat.lower() in row['category'].lower():
                table_data[cat].append((row['item'], row['value']))
                break
    return table_data


def generate_player_report(player_data, player_teams, player_games, player_metrics,
                           player_evaluations, player_videos, player_documents, teams_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)

    # Posiciones fijas para layout estilo captura
    left_x = 20
    top_y = 15

    # 1. FOTO DEL JUGADOR
    photo_url = player_data.get("photo_url", "")
    image_height = 40
    try:
        if photo_url:
            response = requests.get(photo_url, stream=True)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as img_tmp:
                    img_tmp.write(response.content)
                    img_path = img_tmp.name
                pdf.image(img_path, x=left_x, y=top_y, w=35, h=image_height)
                os.remove(img_path)
    except Exception as e:
        print("Image error:", e)

    # 2. DATOS PERSONALES debajo de la imagen
    text_y_start = top_y + image_height + 4
    pdf.set_xy(left_x, text_y_start)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, f"{player_data['first_name']} {player_data['last_name']} (ID: {player_data.get('player_id', '')})", ln=1)

    pdf.set_font("Arial", "", 10)
    pdf.set_x(left_x)
    pdf.cell(0, 6, f"{player_data.get('primary_position', 'N/A')}", ln=1)
    pdf.set_x(left_x)
    pdf.cell(0, 6, f"DOB: {player_data['birth_date'].strftime('%Y-%m-%d')}", ln=1)
    pdf.set_x(left_x)
    pdf.cell(0, 6, f"Height: {player_data.get('height', 'N/A')}cm", ln=1)
    pdf.set_x(left_x)
    pdf.cell(0, 6, f"Weight: {player_data.get('weight', 'N/A')}kg", ln=1)

    # 3. RADAR CHART centrado
    radar_categories = ["Leadership", "Match Performance", "Physical", "Core Value", "Skills", "Tactical"]
    radar_data = {}
    for cat in radar_categories:
        subset = player_evaluations[player_evaluations["category"].str.contains(cat, case=False, na=False)]
        radar_data[cat] = round(subset["value"].astype(float).mean(), 1) if not subset.empty else 0

    fig = generate_radar_chart(radar_data)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        fig.savefig(tmp.name, bbox_inches="tight")
        radar_img_path = tmp.name
    pdf.image(radar_img_path, x=75, y=20, w=60)
    plt.close(fig)

    # 4. Specific Trainings (bloque a la derecha)
    pdf.set_xy(145, 20)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "Specific trainings", ln=1)

    pdf.set_font("Arial", "", 10)
    for label in ["Gatekeeper", "Skills", "HP", "VA"]:
        pdf.set_x(145)
        pdf.cell(0, 6, f">EPx    {label}", ln=1)

    # 5. TABLA DE EVALUACIÓN mucho más abajo
    pdf.set_y(110)  # Ajustado para evitar solape

    table_data = build_evaluation_table(player_evaluations)
    col_titles = ["Values", "Skills", "Game Model", "Performance", "Mental and Leadership", "Evolution and Recommendation"]
    col_width = pdf.w / len(col_titles) - 4
    row_height = 6

    pdf.set_font("Arial", "B", 9)
    for title in col_titles:
        pdf.cell(col_width, row_height, title[:24], border=1, align="C")
    pdf.ln(row_height)

    max_rows = max(len(table_data.get(cat, [])) for cat in table_data)
    pdf.set_font("Arial", "", 8)
    for i in range(max_rows):
        for cat_key in ["Core Value", "Skills", "Game Model", "Performance", "Mental & Leadership", "Evolution and Recommendation"]:
            items = table_data.get(cat_key, [])
            text = f"{items[i][0]}" if i < len(items) else ""
            pdf.cell(col_width, row_height, text[:30], border=1)
        pdf.ln(row_height)

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return BytesIO(pdf_bytes)
