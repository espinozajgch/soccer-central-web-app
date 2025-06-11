from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time


# Proceso para obtener los datos de byga con selenium

# Configurar navegador
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # LOGIN
    driver.get("https://soccercentralsa.byga.net/users/sign_in")
    time.sleep(2)
    driver.find_element(By.ID, "user_email").send_keys("lucas.bracamonte@sportsdatacampus.com")
    driver.find_element(By.ID, "user_password").send_keys("Qwer1357", Keys.RETURN)
    time.sleep(5)

    jugadores = []
    headers = []
    page = 1

    while True:
        driver.get(f"https://soccercentralsa.byga.net/players?page={page}")
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table", {"class": "table"})

        if not table or not table.find("tbody"):
            print(f"Página {page} vacía o fin del listado.")
            break

        # Obtener cabecera de la tabla solo una vez
        if not headers:
            header_row = table.find("thead").find("tr")
            headers = [th.text.strip() for th in header_row.find_all("th")]

        rows = table.find("tbody").find_all("tr")
        if not rows:
            print(f" Fin de jugadores en la página {page}.")
            break

        for row in rows:
            cols = row.find_all("td")
            jugador = {}
            for i in range(len(headers)):
                valor = cols[i].text.strip() if i < len(cols) else ""
                jugador[headers[i]] = valor
            jugadores.append(jugador)

        print(f" Página {page} procesada con {len(rows)} jugadores.")
        page += 1

    # Guardar en Excel
    df = pd.DataFrame(jugadores)
    df.to_excel("jugadores_byga_completo.xlsx", index=False)
    print(" Excel generado correctamente: jugadores_byga_completo.xlsx")

finally:
    driver.quit()
