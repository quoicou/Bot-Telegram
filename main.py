import feedparser
import requests
import time

ancien_lien = ""

def recup_last_link():
    feed_url = "https://services.lesechos.fr/rss/les-echos-finance-marches.xml"

    blog_feed = feedparser.parse(feed_url)

    link = blog_feed.entries[0].link

    return link

def send_message(link):
    api_key = "INSERER CLE API"
    chat_id = "INSERER CHAT ID"
    text = f"/!\ Voici une nouvelle news ! /!\\n\n {link}"

    url = f"https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={text}"

    requests.get(url)

if __name__ == '__main__':
    while True:
        link = recup_last_link()
        if ancien_lien != link:
            send_message(link)
	    ancien_lien = link
        time.sleep(3600)