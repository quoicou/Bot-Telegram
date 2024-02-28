from datetime import datetime, timedelta, time
import multiprocessing
import json
import requests
import yfinance as yf
import time as sleep_time
import pytz

def get_api_key():
    api_key = "SINERT API KEY"

    return api_key

def get_chat_id():
    chat_id = "INSERT CHAT ID" #c'est 3

    return chat_id

def get_heure_actuelle():
    paris_tz = pytz.timezone('Europe/Paris')
    heure_actuelle = datetime.now(paris_tz).time()

    return heure_actuelle

def veille_quotidienne_crypto():
    heure_debut = time(17, 00)
    heure_fin = time(21, 00)

    while True:
        if heure_debut <= get_heure_actuelle() <= heure_fin:

            BTC_open, BTC_close, BTC_volume, ETH_open, ETH_close, SOL_open, SOL_close = top_crypto()

            send_message_veille_quotidienne_crypto(BTC_open, BTC_close, BTC_volume, ETH_open, ETH_close, SOL_open, SOL_close, fng_crypto())

            sleep_time.sleep(86400)
        else:
            print("Pas l'heure pour Veille Quotidienne Crypto")
            sleep_time.sleep(3600)

    print("Pas le jour pour Veille Quotidienne Crypto")
    sleep_time.sleep(86400)

def top_crypto():
    BTC_Ticker = yf.Ticker("BTC-USD")
    BTC = BTC_Ticker.history(period="today").drop(columns=["Dividends", "Stock Splits", "High", "Low"])

    BTC_open = f'{BTC["Open"].iloc[0]:.2f}'
    BTC_close = f'{BTC["Close"].iloc[0]:.2f}'
    BTC_volume = f'{BTC["Volume"].iloc[0]/ 1_000_000_000:.3f}'

    ETH_Ticker = yf.Ticker("ETH-USD")
    ETH = ETH_Ticker.history(period="today").drop(columns=["Dividends", "Stock Splits", "Volume", "High", "Low"])

    ETH_open = f'{ETH["Open"].iloc[0]:.2f}'
    ETH_close = f'{ETH["Close"].iloc[0]:.2f}'

    SOL_Ticker = yf.Ticker("SOL-USD")
    SOL = SOL_Ticker.history(period="today").drop(columns=["Dividends", "Stock Splits", "Volume", "High", "Low"])

    SOL_open = f'{SOL["Open"].iloc[0]:.2f}'
    SOL_close = f'{SOL["Close"].iloc[0]:.2f}'

    return BTC_open, BTC_close, BTC_volume, ETH_open, ETH_close, SOL_open, SOL_close

def fng_crypto():
    url = "https://api.alternative.me/fng/"

    response = requests.get(url)
    data = json.loads(response.content)
    fng_value = data.get("data")[0]["value"]

    return fng_value

def send_message_veille_quotidienne_crypto(BTC_open, BTC_close, BTC_volume, ETH_open, ETH_close, SOL_open, SOL_close, fng):
    text = f"⚠️ VEILLE QUOTIDIENNE ⚠️\n\n▶️ Fear N' Greed Crypto : {fng}\n\n▶️ Volume BTC : {BTC_volume} Mrds\n\n▶️ BTC : {BTC_open} -> {BTC_close}\n\n▶️ ETH : {ETH_open} -> {ETH_close}\n\n▶️ SOL : {SOL_open} -> {SOL_close}\n\n(Prix en $)"

    print(text)

    url = f"https://api.telegram.org/bot{get_api_key()}/sendMessage?chat_id={get_chat_id()}&text={text}&silent=True"

    requests.get(url)

#top perf/flop
#dominance btc/altcoin

if __name__ == '__main__':
    process_1 = multiprocessing.Process(target=veille_quotidienne_crypto)

    process_1.start()
