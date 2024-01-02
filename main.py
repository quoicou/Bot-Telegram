from datetime import datetime, timedelta, time
from bs4 import BeautifulSoup
import multiprocessing
import feedparser
import pandas as pd
import requests
import time as sleep_time
import fear_and_greed

def get_api_key():
    api_key = "INSEREZ CLE API"

    return api_key

def get_chat_id():
    chat_id = "INSERER CHAT ID"

    return chat_id

def get_heure_actuelle():
    heure_actuelle = datetime.now().time()

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

def get_headers():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
    }

    return headers

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
    heure_debut = time(18, 00)
    heure_fin = time(23, 00)
    date_ajd = datetime.now().strftime('%Y-%m-%d')

    url = "https://www.zonebourse.com/bourse/agenda/economique/"

    while True:
        if date_jour_demain() != "SAMEDI" and date_demain() != "DIMANCHE":
            if heure_debut <= get_heure_actuelle() <= heure_fin and recup_lien(4) != date_ajd:

                tables = pd.read_html(url, encoding='utf-8')

                # Vérification si des tableaux ont été trouvés
                if tables:
                    table = tables[0]

                    table["Pays"] = table["Pays"].astype(str)

                    country_codes = liste_pays()

                    elements_en_trop = len(country_codes)-len(table)
                    print(elements_en_trop)

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

def recup_lien(type):
    chemin = "INSERER CHEMIN"

    if type == 1:
        with open(f"{chemin}//lien_morning_meeting.txt", "r") as fichier:
            contenu = fichier.read()
            return contenu
    elif type == 2:
        with open(f"{chemin}//lien_morningstar.txt", "r") as fichier:
            contenu = fichier.read()
            return contenu
    elif type == 3:
        with open(f"{chemin}//lien_point_hebdo.txt", "r") as fichier:
            contenu = fichier.read()
            return contenu
    else:
        with open(f"{chemin}//date_dernier_agenda_eco.txt", "r") as fichier:
            contenu = fichier.read()
            return contenu

def update_lien(type, href):
    chemin = "INSERER CHEMIN"

    if type == 1:
        with open(f"{chemin}//lien_morning_meeting.txt", "w") as fichier:
            fichier.write(href)
    elif type == 2:
        with open(f"{chemin}//lien_morningstar.txt", "w") as fichier:
            fichier.write(href)
    elif type == 3:
        with open(f"{chemin}//lien_point_hebdo.txt", "w") as fichier:
            fichier.write(href)
    else:
        with open(f"{chemin}//date_dernier_agenda_eco.txt", "w") as fichier:
            fichier.write(href)

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
                send_message(1, lien)
            else:
                print("Pas de nouveau Morning Meeting")
                sleep_time.sleep(120)

        else:
            print("Pas l'heure pour le Morning Meeting")
            sleep_time.sleep(3600)

def news_morningstar():
    feed_url = "https://www.morningstar.fr/fr/news/rss.aspx?lang=fr-FR"

    while True:
        blog_feed = feedparser.parse(feed_url)

        href = blog_feed.entries[0].link

        if recup_lien(2) != href:
            href = href.replace("«", "").replace("»", "")

            print(f"Nouvel article trouvé : {href}")
            update_lien(2, href)
            send_message(2, href)
        else:
            print("Pas de news de Morningstar")

        sleep_time.sleep(3600)

def new_fear_and_greed():
    heure_debut = time(8, 00)
    heure_fin = time(14, 00)

    fear_and_greed_value = int(fear_and_greed.get().value)

    while True:
        if heure_debut <= get_heure_actuelle() <= heure_fin:
            if fear_and_greed_value >= 75:
                message = f"INDEX : {fear_and_greed_value}\n\nWARNING nous sommes en EXTREME GREED !!!"
                send_message(4, message)

            elif fear_and_greed_value >= 70 and fear_and_greed_value < 75:
                message = f"INDEX : {fear_and_greed_value}\n\nAttention nous approchons du palier : EXTREME GREED"
                send_message(4, message)

            elif fear_and_greed_value <= 25:
                message = f"INDEX : {fear_and_greed_value}\n\nWARNING nous sommes en EXTREME FEAR !!!"
                send_message(4, message)

            elif fear_and_greed_value > 25 and fear_and_greed_value <= 30:
                message = f"INDEX : {fear_and_greed_value}\n\nAttention nous approchons du palier : EXTREME FEAR"
                send_message(4, message)

            else:
                print("Rien de particulier sur le Fear & Greed")

        sleep_time.sleep(86400)

def dernier_vendredi():
    # Obtenez la date actuelle
    aujourd_hui = datetime.now()

    # Calculez le jour de la semaine (0 pour lundi, 1 pour mardi, ..., 6 pour dimanche)
    jour_semaine = aujourd_hui.weekday()

    # Calculez le nombre de jours à soustraire pour atteindre le dernier jeudi
    jours_a_soustraire = (jour_semaine - 2) % 7

    # Soustrayez le nombre de jours pour obtenir le dernier jeudi
    dernier_vendredi = aujourd_hui - timedelta(days=jours_a_soustraire)

    # Formatez la date au format "aaaa-mm-jj"
    date_formattee = dernier_vendredi.strftime("%Y-%m-%d")

    return date_formattee

def point_hebdo():
    date = dernier_vendredi()

    query = f"site:www.zonebourse.com/actualite-bourse/Le-point-hebdo-de-l-investisseur after:{date}"

    url = f"https://www.google.com/search?q={query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3"}

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    results = soup.find_all('a')

    lien_hebdo = None

    for result in results:
        lien = result.get("href")
        if "Le-point-hebdo-de-l-investisseur-" in lien:
            lien_hebdo = (lien.split('&')[0]).replace("/url?q=", "")

    if lien_hebdo != None:
        if recup_lien(3) != lien_hebdo:
            print(f"Nouveau Point Hebdo trouvé : {lien_hebdo}")
            update_lien(3, lien_hebdo)
            send_message(3, lien_hebdo)

    else:
        print("Pas de nouveau Point Hebdo")

    sleep_time.sleep(86400)

def send_message(type, link):
    if type == 1:
        text = f"/!\ NEWSSSSSS /!\ \n\nVoici LE MORNING MEETING ! \n\n {link}"
    elif type == 2:
        text = f"/!\ INFORMATION /!\ \n\nVoici une nouvelle news ! \n\n {link}"
    elif type == 3:
        text = f"/!\ INSTRUISEZ-VOUS /!\ \n\nVoici le nouveau Point Hebdo de l'Investisseur ! \n\n {link}"
    else:
        text = f"/!\ FEAR AND GREED /!\ \n\n{link}\n"

    url = f"https://api.telegram.org/bot{get_api_key()}/sendMessage?chat_id={get_chat_id()}&text={text}"

    requests.get(url)

if __name__ == '__main__':
    process_1 = multiprocessing.Process(target=news_morningstar)
    process_2 = multiprocessing.Process(target=morning_meeting)
    process_3 = multiprocessing.Process(target=agenda_eco)
    process_4 = multiprocessing.Process(target=point_hebdo)
    process_5 = multiprocessing.Process(target=new_fear_and_greed)

    process_1.start()
    process_2.start()
    process_3.start()
    process_4.start()
    process_5.start()
