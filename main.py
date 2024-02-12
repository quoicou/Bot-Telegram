from datetime import datetime, timedelta, time
from bs4 import BeautifulSoup
import multiprocessing
import pandas as pd
import requests
import time as sleep_time
import fear_and_greed
import yfinance as yf
import pytz

def get_api_key():
    api_key = "INSERER CLE"

    return api_key

def get_chat_id():
    chat_id = "INSERER ID CHAT" #c'est 9

    return chat_id

def get_headers():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'
    }

    return headers

def get_heure_actuelle():
    paris_tz = pytz.timezone('Europe/Paris')
    heure_actuelle = datetime.now(paris_tz).time()

    return heure_actuelle

def date_demain():
    # Obtenir la date de demain
    date_demain = datetime.now() + timedelta(days=1)

    # Jour de la semaine en français
    jours = ["LUNDI", "MARDI", "MERCREDI", "JEUDI", "VENDREDI", "SAMEDI", "DIMANCHE"]

    # Mois en français
    mois = ["JANVIER", "FÉVRIER", "MARS", "AVRIL", "MAI", "JUIN", "JUILLET", "AOÛT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE",
            "DÉCEMBRE"]

    # Formater la date
    date_formatee = "{}{}{}".format(jours[date_demain.weekday()], '{:02d}'.format(date_demain.day), mois[date_demain.month - 1])

    return date_formatee

def date_jour_demain():
    # Obtenir la date de demain
    date_demain = datetime.now() + timedelta(days=1)

    # Jour de la semaine en français
    jours = ["LUNDI", "MARDI", "MERCREDI", "JEUDI", "VENDREDI", "SAMEDI", "DIMANCHE"]

    # Formater la date
    jour_demain = "{}".format(jours[date_demain.weekday()])

    return jour_demain

def date_demain_jj_mm_aa():
    date_demain_formattee = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%y")

    return date_demain_formattee

### AGENDA ECOOOO

def liste_pays():
    url = "https://www.zonebourse.com/bourse/agenda/economique/"

    mon_dico = {"FR": "🇫🇷", "IT": "🇮🇹", "JP": "🇯🇵", "DE": "🇩🇪", "CH": "🇨🇭", "EU": "🇪🇺", "GB": "🇬🇧", "US": "🇺🇸", "CN": "🇨🇳", "CA": "🇨🇦", "BE": "🇧🇪", "ES": "🇪🇸", "NL": "🇳🇱"}

    # Faire une requête HTTP pour récupérer le contenu de la page
    response = requests.get(url, headers=get_headers())

    # Parser le contenu de la page avec BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Trouver toutes les balises <i> sur la page
    i_tags = soup.find_all("i")

    classes_list = [i["class"] for i in i_tags if "flag__" in ' '.join(i["class"])]

    # Garder les 2 dernieres lettres des pays
    country_codes = [cls[2][-2:].upper() for cls in classes_list]

    for i in range(len(country_codes)):
        if country_codes[i] in mon_dico:
            country_codes[i] = mon_dico[country_codes[i]]

    return country_codes

def agenda_eco():
    heure_debut = time(17, 00)
    heure_fin = time(21, 00)
    date_ajd = datetime.now().strftime('%Y-%m-%d')

    url = "https://www.zonebourse.com/bourse/agenda/economique/"

    while True:
        if date_jour_demain() != "SAMEDI" and date_jour_demain() != "DIMANCHE":
            if heure_debut <= get_heure_actuelle() <= heure_fin and recup_lien(4) != date_ajd:

                response = requests.get(url, headers=get_headers())
                url = response.text

                tables = pd.read_html(url, encoding='utf-8')

                # Vérification si des tableaux ont été trouvés
                if tables:
                    table = tables[0]

                    table["Pays"] = table["Pays"].astype(str)

                    country_codes = liste_pays()

                    elements_en_trop = len(country_codes)-len(table)
                    #print(elements_en_trop)

                    # Enlever les premiers elements présents dans la bannière du site (inutile pour nous)
                    country_codes = country_codes[elements_en_trop:]

                    for i in range(len(country_codes)):
                        table.loc[i, "Pays"] = country_codes[i]

                    filtered_table = table.loc[table["Unnamed: 0"] == date_demain()]

                    filtered_table_copy = filtered_table.copy()
                    filtered_table_copy.drop(columns=["Unnamed: 0"], inplace=True)
                    filtered_table_copy.drop(columns=["Période précédente"], inplace=True)

                    text = format_table(filtered_table_copy)

                    print(text)

                    update_lien(4, date_ajd)

                    send_telegram_message(text)

                sleep_time.sleep(86400)

            else:
                print("Pas l'heure pour l'Agenda Economique ou déjà publié aujourd'hui")
                sleep_time.sleep(3600)
        else:
            print("Pas d'agenda économique pour le week-end")
            sleep_time.sleep(86400)

def format_table(table):
    headers = table.columns
    formatted_table = []
    formatted_table.append(f"AGENDA ECONOMIQUE DE DEMAIN ({date_demain_jj_mm_aa()})\n")
    formatted_table.append(f"Heure | Pays | Publication\n")
    for _, row in table.iterrows():
        formatted_table.append(" | ".join(str(row[col]) for col in headers) + "\n")
    return "\n".join(formatted_table)

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{get_api_key()}/sendMessage"
    payload = {
        "chat_id": get_chat_id(),
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

### FIN AGENDA ECOOO

### MORNING MEETING

def morning_meeting():
    url = "https://www.zonebourse.com/videos/la-chronique-bourse/"

    heure_debut = time(8, 00)
    heure_fin = time(9, 30)

    while True:
        if heure_debut <= get_heure_actuelle() <= heure_fin:
            response = requests.get(url, headers=get_headers())

            soup = BeautifulSoup(response.content, "html.parser")

            link = soup.find("a", href=lambda href: href and "/actualite-bourse/" in href and "-4" in href)

            href = link.get("href")

            if recup_lien(1) != href:
                print(f"Nouveau Morning Meeting trouvé : https://www.zonebourse.com{href}")
                update_lien(1, href)
                lien = f"https://www.zonebourse.com{href}"
                send_message_morning_meeting(lien)
            else:
                print("Pas de nouveau Morning Meeting")
                sleep_time.sleep(120)

        else:
            print("Pas l'heure pour le Morning Meeting")
            sleep_time.sleep(3600)

def send_message_morning_meeting(link):
    text = f"⚠️ NEWSSSSSS ⚠️\n\nVoici LE MORNING MEETING ! \n\n {link}"

    url = f"https://api.telegram.org/bot{get_api_key()}/sendMessage?chat_id={get_chat_id()}&text={text}"

    requests.get(url)

### FIN MORNING MEETING

### POINT QUOTIDIEN

def get_headers_veille():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
    }

    return headers

def veille_quotidienne():
    heure_debut = time(17, 00)
    heure_fin = time(21, 00)

    while True:
        if date_jour_demain() != "DIMANCHE" and date_jour_demain() != "LUNDI":
            if heure_debut <= get_heure_actuelle() <= heure_fin:

                send_message_veille_quotidienne(new_fear_and_greed(), yield_us(), yield_eu(), vix_update())

                sleep_time.sleep(86400)
            else:
                print("Pas l'heure pour Veille Quotidienne")
                sleep_time.sleep(3600)

        print("Pas le jour pour Veille Quotidienne")
        sleep_time.sleep(86400)

def vix_update():
    # Objet Ticker pour le VIX (symbole : ^VIX)
    vix_ticker = yf.Ticker("^VIX")

    # Historique du VIX DataFrame
    vix_history = vix_ticker.history(period="1y")

    update = f"{vix_history.Close.to_list()[-1]:.2f}"

    variation = vix_history.Close.to_list()[-1] - vix_history.Close.to_list()[-2]

    if variation != 0:
        if variation > 0:
            result = f'{update} (➕{variation:.2f})'
        else:
            result = f'{update} (➖{float(str(variation).replace("-", "")):.2f})'
    else:
        result = f'{update} (➕0%)'

    return result

def new_fear_and_greed():
    fear_and_greed_value = int(fear_and_greed.get().value)

    return fear_and_greed_value

def yield_us():
    liste_yield = []
    taux_us = 0

    url = 'https://www.bloomberg.com/markets/rates-bonds'

    response = requests.get(url, headers=get_headers_veille())

    soup = BeautifulSoup(response.text, 'html.parser')

    all_values = soup.find_all(class_='data-table-row-cell__value')

    for value in all_values:
        liste_yield.append(value.text)

    taux_us_transfo = int(liste_yield[21].replace('+', '').replace('-', ''))

    if taux_us_transfo >= 10:
        taux_us = f'0.{taux_us_transfo}'
    else:
        taux_us = f'0.0{taux_us_transfo}'

    if taux_us_transfo != 0:
        if liste_yield[21][0] == "+":
            taux_us = f'{liste_yield[20]} (➕{taux_us}%)'
        else:
            taux_us = f'{liste_yield[20]} (➖{taux_us}%)'
    else:
        taux_us = f'{liste_yield[20]}% (➕0%)'

    return taux_us

def yield_eu():
    liste_yield = []

    url = 'https://www.euribor-rates.eu/fr/taux-euribor-actuels/2/euribor-taux-3-mois/'

    response = requests.get(url, headers=get_headers())

    soup = BeautifulSoup(response.text, 'html.parser')

    all_values = soup.find_all(class_='text-right')

    for value in all_values:
        liste_yield.append(value.text)

    eu_yield = liste_yield[0].replace(',', '.').replace(' ', '').replace('%', '')

    eu_yield_j_1 = liste_yield[1].replace(',', '.').replace(' ', '').replace('%', '')

    diff = float(eu_yield) - float(eu_yield_j_1)

    if diff >= 0:
        diff = f'➕{diff:.3f}%'
    else:
        diff = float(str(diff).replace('-', ''))
        diff = f'➖{diff:.3f}%'

    eu_yield = f'{eu_yield}% ({diff})'

    return(eu_yield)

def send_message_veille_quotidienne(f_et_g, us_yield, eu_yield, vix_variation):
    text = f"⚠️ VEILLE QUOTIDIENNE ⚠️\n\n▶️ Fear N' Greed : {f_et_g}\n\n▶️ Taux US* : {us_yield}\n\n▶️ Taux EU** : {eu_yield}\n\n▶️ VIX : {vix_variation}\n\n🚧 Attente des variations SP500/Nasdaq/CAC/DAX\n\n🚧 Attente des variations cryptos\n\n*10-Year Government Bond Yields\n**EURIBOR 3 mois"

    print(text)

    url = f"https://api.telegram.org/bot{get_api_key()}/sendMessage?chat_id={get_chat_id()}&text={text}&silent=True"

    requests.get(url)

### FIN POINT QUOTIDIEN

### GESTION FICHIER

def recup_lien(type):
    if type == 1:
        with open(f"lien_morning_meeting.txt", "r") as fichier:
            contenu = fichier.read()
            return contenu
    else:
        with open(f"date_dernier_agenda_eco.txt", "r") as fichier:
            contenu = fichier.read()
            return contenu

def update_lien(type, href):
    if type == 1:
        with open(f"lien_morning_meeting.txt", "w") as fichier:
            fichier.write(href)
    else:
        with open(f"date_dernier_agenda_eco.txt", "w") as fichier:
            fichier.write(href)

### FIN GESTION FICHIER

if __name__ == '__main__':
    process_1 = multiprocessing.Process(target=morning_meeting)
    process_2 = multiprocessing.Process(target=agenda_eco)
    process_3 = multiprocessing.Process(target=veille_quotidienne)

    process_1.start()
    process_2.start()
    process_3.start()
