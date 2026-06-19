import json
import requests
import pandas as pd
from bs4 import BeautifulSoup

if __name__ == "__main__":

    url = "https://en.wikipedia.org/wiki/Template:2026_FIFA_World_Cup_third-place_table"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find('table', {'class': 'wikitable'})

    rows = []
    for tr in table.find_all('tr'):
        # Extraemos todas las celdas (tanto th como td)
        cells = tr.find_all(['td', 'th'])
        # Obtenemos el texto de cada celda y limpiamos espacios
        row_data = [cell.get_text(strip=True) for cell in cells]
        if row_data:
            rows.append(row_data)

    data = rows[1:]
    match_ids = [74, 77, 79, 80, 81, 82, 85, 87]
    pairing_table = {}

    for row in data:
        grupos = [g for g in row[1:13] if g and g.strip()]
        key = ",".join(sorted(grupos))
        asignaciones = [a for a in row[13:22] if a]
        pairing_table[key] = {str(m_id): team for m_id, team in zip(match_ids, asignaciones)}

    with open("data/third_place.json", "w") as f:
        json.dump(pairing_table, f, indent=4)

    

    