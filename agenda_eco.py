from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import requests

def date_demain():
    # Obtenir la date de demain
    date_demain = datetime.now() + timedelta(days=1)

    # Jour de la semaine en français
    jours = ["LUNDI", "MARDI", "MERCREDI", "JEUDI", "VENDREDI", "SAMEDI", "DIMANCHE"]

    # Mois en français
    mois = ["JANVIER", "FÉVRIER", "MARS", "AVRIL", "MAI", "JUIN", "JUILLET", "AOÛT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE",
            "DÉCEMBRE"]

    # Formater la date
    date_formatee = "{}{}{}".format(jours[date_demain.weekday()], date_demain.day, mois[date_demain.month - 1])

    return date_formatee

def date_demain_jj_mm_aa():
    date_demain_formattee = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%y")

    return date_demain_formattee

def get_url():
    url = "https://www.zonebourse.com/bourse/agenda/economique/"

    return url

def get_headers():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
    }

    return headers

def liste_pays():

    # Faire une requête HTTP pour récupérer le contenu de la page
    response = requests.get(get_url(), headers=get_headers())

    # Parser le contenu de la page avec BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Trouver toutes les balises <i> sur la page
    i_tags = soup.find_all("i")

    classes_list = [i["class"] for i in i_tags if "flag__" in ' '.join(i["class"])]

    # Afficher la liste des classes dans l'ordre
    country_codes = [cls[2][-2:].upper() for cls in classes_list]

    return country_codes

def agenda_eco(country_codes):

    tables = pd.read_html(get_url(), encoding='utf-8')

    # Vérification si des tableaux ont été trouvés
    if tables:
        table = tables[0]

        table["Pays"] = table["Pays"].astype(str)

        for i in range(len(country_codes)):
            table.loc[i, "Pays"] = country_codes[i]

        filtered_table = table.loc[table["Unnamed: 0"] == date_demain()]

        filtered_table_copy = filtered_table.copy()
        filtered_table_copy.drop(columns=["Unnamed: 0"], inplace=True)
        filtered_table_copy.drop(columns=["Période précédente"], inplace=True)

        return filtered_table_copy

def format_table(table):
    headers = table.columns
    formatted_table = []
    formatted_table.append(f"AGENDA ECONOMIQUE DE DEMAIN ({date_demain_jj_mm_aa()})\n")
    formatted_table.append("| " + " | ".join(headers) + " |")
    formatted_table.append("------------------------------------------------------------")
    for _, row in table.iterrows():
        formatted_table.append("| " + " | ".join(str(row[col]) for col in headers) + " |\n")
    return "\n".join(formatted_table)


def send_telegram_message(api_key, chat_id, text):
    url = f"https://api.telegram.org/bot{api_key}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

    print(text)

if __name__ == '__main__':
    country_codes = liste_pays()
    filtered_table = agenda_eco(country_codes)
    formatted_table = format_table(filtered_table)
    api_key = "INSERER CLE API"
    chat_id = "INSERER CHAT ID"
    send_telegram_message(api_key, chat_id, formatted_table)

