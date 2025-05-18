import io
import matplotlib.pyplot as plt
import requests
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
)
#from common_utils import radar_chart

# Función para crear el gráfico de radar con matplotlib
def create_radar_chart_matplotlib():
    # Datos de ejemplo: categorías y valores
    categories = ['On Ball', 'Intelligence', 'Shot', 'Defensive', 'Aerial', 'Physical']
    values = [15, 18, 20, 12, 16, 10]  # Ejemplo de valores
    n = len(categories)
    
    # Cerrar el gráfico: se repite el primer valor y ángulo
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]
    
    # Crear el gráfico en un subplot polar
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    ax.plot(angles, values, 'o-', linewidth=2, label="Skill")
    ax.fill(angles, values, alpha=0.25)
    
    # Configurar etiquetas de cada ángulo
    ax.set_thetagrids(np.degrees(angles[:-1]), categories)
    ax.set_ylim(0, 25)  # Ajusta el rango según tus datos
    
    return fig

#***********************************************************************************************************************************
def create_pdf(df_info1, df_info2):
    buffer = io.BytesIO()
    # Configuración del documento PDF (tamaño carta y márgenes)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # --- Sección 1: Información Personal ---
    # Título principal
    title = Paragraph("PLAYER REPORT SOCCER CENTRAL ACADEMY", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    # Insertar el logo debajo del título
    logo_path = "./assets/images/soccer-central.png"
    try:
        # Ajusta el tamaño (width y height) según sea necesario
        logo = RLImage(logo_path, width=200, height=50)
        logo.hAlign = "LEFT"  # Esta línea alinea el logo a la izquierda
        story.append(logo)
        story.append(Spacer(1, 12))
    except Exception as e:
        story.append(Paragraph("Error al cargar el logo: " + str(e), styles["Normal"]))
        
    # Título de la sección de información personal
    personal_title = Paragraph("GENERAL INFO", styles['Heading2'])
    story.append(personal_title)
    story.append(Spacer(1, 6))
    
    # Convertir la primera fila de df_info1 en una tabla de dos columnas (Campo y Valor)
    personal_data = [["Personal Info", ""]]
    for index, row in df_info1.iterrows():
        personal_data.append([str(row["Personal Info"]), str(row[""])])

    personal_table = Table(personal_data, hAlign='LEFT')
    personal_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    
    # Cargar la foto del jugador (obtenida de la URL)
    
    photo_url = "https://media.gettyimages.com/id/1365815844/es/foto/mexico-city-mexico-argentina-captain-diego-maradona-pictured-before-the-fifa-1986-world-cup.jpg?s=612x612&w=gi&k=20&c=vmUfSD2BY0_TQqFi8btORJj6OlNIBTvhkq1RrsY9kV4="

    # Se evalúa si la URL no es nula o vacía
    if photo_url and pd.notna(photo_url):
        try:
            response = requests.get(photo_url)
            if response.status_code == 200:
                photo_buffer = io.BytesIO(response.content)
                # Se define un tamaño fijo (por ejemplo, 150x150 píxeles); ajústalo según necesites
                player_img = RLImage(photo_buffer, width=150, height=150)
                player_img.hAlign = "RIGHT"  # Esta línea alinea el logo a la izquierda
                #story.append(player_img)
                #story.append(Spacer(1, 12))
                # Mostrar la información Personal y la foto lado a lado usando una tabla de 2 columnas
                personal_and_photo = Table([[personal_table, player_img]], colWidths=[200, 200])
                personal_and_photo.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('ALIGN', (1,0), (1,0), 'CENTER'),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                    ('BOX', (0,0), (-1,-1), 0.25, colors.blue),
                ]))
                #Imprimiendo Info.
                story.append(personal_and_photo)
        except Exception as e:
            story.append(Paragraph("Error al cargar la imagen: " + str(e), styles['Normal']))
            story.append(Spacer(1, 12))

    
    #story.append(Spacer(1, 24))


    # --- Sección 2: Perfil y Radar Chart ---
    profile_title = Paragraph("PLAYER PROFILE & STATS", styles['Heading2'])
    story.append(profile_title)
    story.append(Spacer(1, 12))
    
    # Crear una tabla con la información del perfil a partir de df_info2

    profile_data = [["Profile", ""]]
    for index, row in df_info2.iterrows():
        profile_data.append([str(row["Profile"]), str(row[""])])
    
    profile_table = Table(profile_data, hAlign='LEFT')
    profile_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    
    # Generar el gráfico de radar y convertirlo en imagen (formato PNG)
    # Llamar a la función para obtener el gráfico
    fig = create_radar_chart_matplotlib()
    try:
        # Guardar la figura en formato PNG en memoria
        chart_buffer = io.BytesIO()
        fig.savefig(chart_buffer, format="png", bbox_inches='tight')
        chart_buffer.seek(0)
        # Crear el objeto de imagen para ReportLab
        radar_img = RLImage(chart_buffer, width=250, height=250)
    except Exception as e:
        radar_img = Paragraph("Error al generar gráfico radar: " + str(e), styles['Normal'])
    
    # Mostrar la información de perfil y el gráfico lado a lado usando una tabla de 2 columnas
    profile_and_chart = Table([[profile_table, radar_img]], colWidths=[250, 250])
    profile_and_chart.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
        ('BOX', (0,0), (-1,-1), 0.25, colors.grey)
    ]))
    story.append(profile_and_chart)
    story.append(Spacer(1, 6))
    
    # --- Sección 3: Conclusiones ---
    conclusions_title = Paragraph("SUMMARY", styles['Heading2'])
    story.append(conclusions_title)
    story.append(Spacer(1, 6))
    
    # Se incluye un párrafo con conclusiones por skill. Puedes adaptar el texto según análisis o estadísticas.
    conclusion_text = """
    Below are the conclusions about each of the player's skills:
    <br/><br/>
    <b>On Ball:</b> Displays exceptional ball control and agility when dribbling.<br/>
    <b>Intelligence:</b> Exhibits outstanding game vision and anticipates plays effectively.<br/>
    <b>Shot:</b> Possesses a powerful and accurate shot, making the most of scoring opportunities.<br/>
    <b>Defensive:</b> Shows solid defensive strategies with impressive marking and interception skills.<br/>
    <b>Aerial:</b> Excels in aerial duels, leveraging timing and positioning to win headers.<br/>
    <b>Physical:</b> Demonstrates superior physical strength and endurance in duels.<br/>
    """
    styles = getSampleStyleSheet()
    custom_body = ParagraphStyle(
    name='CustomBody',
    parent=styles['BodyText'],
    fontSize=14,    # Cambia 14 por el tamaño deseado
    alignment=TA_JUSTIFY,
    leading=20      # Ajusta el interlineado si es necesario
    )
    conclusions_para = Paragraph(conclusion_text, custom_body)
    story.append(conclusions_para)
    
    # Construir el documento PDF en el buffer y regresar el buffer para su descarga
    doc.build(story)
    buffer.seek(0)
    return buffer