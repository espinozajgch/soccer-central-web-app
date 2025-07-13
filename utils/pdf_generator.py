from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import tempfile
import pandas as pd
import requests
import os


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


def build_evaluation_table(df):
    categories = [
        "Core Value", "Skills", "Game Model", "Performance",
        "Mental & Leadership", "Match Performance", "Evolution and Recommendation"
    ]
    table_data = {cat: [] for cat in categories}
    for _, row in df.iterrows():
        for cat in categories:
            if cat.lower() in row['category'].lower():
                table_data[cat].append(row['item'])
                break
    return table_data


def generate_player_report(player_data, player_teams, player_games, player_metrics,
                           player_evaluations, player_videos, player_documents, teams_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_fill_color(10, 15, 61)
    pdf.rect(0, 0, 210, 297, 'F')

    pdf.set_text_color(255, 255, 255)

    # Foto del jugador
    photo_url = player_data.get("photo_url") or "https://cdn-icons-png.flaticon.com/512/149/149071.png"
    if photo_url:
        try:
            response = requests.get(photo_url, stream=True)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as img_tmp:
                    img_tmp.write(response.content)
                    img_path = img_tmp.name
                pdf.image(img_path, x=15, y=15, w=30, h=30)
                os.remove(img_path)
        except:
            pass

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

    # Tabla de evaluaciones al final
    pdf.set_y(120)
    table_data = build_evaluation_table(player_evaluations)
    col_titles = ["Values", "Skills", "Game Model", "Performance", "Mental & Leadership", "Evolution"]
    col_width = 34
    row_height = 12
    header_height = 16

    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(185, 49, 96)
    x_start = pdf.get_x()
    y_start = pdf.get_y()

    for title in col_titles:
        pdf.set_xy(x_start, y_start)
        pdf.multi_cell(col_width, header_height / 2, title, border=1, align="C", fill=True)
        x_start += col_width

    pdf.set_y(y_start + header_height)

    max_rows = max(len(table_data.get(cat, [])) for cat in table_data)
    pdf.set_font("Arial", "", 8)
    pdf.set_fill_color(115, 0, 36)
    for i in range(max_rows):
        for cat_key in ["Core Value", "Skills", "Game Model", "Performance", "Mental & Leadership", "Evolution and Recommendation"]:
            items = table_data.get(cat_key, [])
            text = f"{items[i]}" if i < len(items) else ""
            pdf.multi_cell(col_width, row_height, text[:30], border=1, fill=True, align="L")
        pdf.set_y(pdf.get_y() + row_height)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)