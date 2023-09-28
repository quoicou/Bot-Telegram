from bs4 import BeautifulSoup
import multiprocessing
import feedparser
import requests
import time
import datetime

def update_lien(type, href):
    chemin = "INSERER CHEMIN"

    if type == 1:
        with open(f"{chemin}//lien_morning_meeting.txt", "w") as fichier:
            fichier.write(href)
    else:
        with open(f"{chemin}//lien_morningstar.txt", "w") as fichier:
            fichier.write(href)

def recup_lien(type):
    chemin = "INSERER CHEMIN"

    if type == 1:
        with open(f"{chemin}//lien_morning_meeting.txt", "r") as fichier:
            contenu = fichier.read()
            return contenu
    else:
        with open(f"{chemin}//lien_morningstar.txt", "r") as fichier:
            contenu = fichier.read()
            return contenu

def morning_meeting():
    url = "https://www.zonebourse.com/videos/la-chronique-bourse/"

    heure_debut = datetime.time(8, 00)
    heure_fin = datetime.time(9, 30)

    while True:
        heure_actuelle = datetime.datetime.now().time()

        if heure_debut < heure_actuelle < heure_fin:
            response = requests.get(url)

            soup = BeautifulSoup(response.content, "html.parser")

            link = soup.find("a", href=lambda href: href and "/actualite-bourse/" in href and "-44" in href)

            href = link.get("href")

            if recup_lien(1) != href:
                print(f"Nouveau morning meeting trouvé : https://www.zonebourse.com{href}")
                update_lien(1, href)
                lien = f"https://www.zonebourse.com{href}"
                send_message(1, lien)
            else:
                print("Pas de nouveau Morning Meeting")
                time.sleep(60)

        else:
            print("Pas l'heure pour le Morning Meeting")
            time.sleep(3600)

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
        time.sleep(3600)

def send_message(type, link):
    api_key = "CLE_API"
    chat_id = "CHAT_ID"
    if type == 1:
        text = f"Voici LE MORNING MEETING ! \n\n {link}"
    else:
        text = f"Voici une nouvelle news ! \n\n {link}"

    url = f"https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={text}"

    requests.get(url)

if __name__ == '__main__':
    process_1 = multiprocessing.Process(target=news_morningstar)
    process_2 = multiprocessing.Process(target=morning_meeting)

    process_1.start()
    process_2.start()
