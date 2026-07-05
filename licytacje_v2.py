import requests
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urljoin

# --- KONFIGURACJA ŹRÓDEŁ ---

# 1. Krajowa Rada Komornicza (stare linki)
URLS_KRK = [
    "https://licytacje.komornik.pl/wyszukiwarka-licytacji?province=ma%C5%82opolskie&mainCategory=MOVABLE&city=lubie%C5%84",
    "https://licytacje.komornik.pl/wyszukiwarka-licytacji?province=ma%C5%82opolskie&mainCategory=MOVABLE&city=tenczyn",
    "https://licytacje.komornik.pl/wyszukiwarka-licytacji?mainCategory=REAL_ESTATE&city=lubie%C5%84&province=ma%C5%82opolskie",
    "https://licytacje.komornik.pl/wyszukiwarka-licytacji?mainCategory=REAL_ESTATE&city=tenczyn&province=ma%C5%82opolskie"
]

# 2. Sąd Rejonowy w Myślenicach
URL_SR_MYSLENICE = "https://www.myslenice.sr.gov.pl/obwieszczenia-komornicze,m,mg,231"

# 3. Komornik Myślenice (własna strona)
URL_KOMORNIK_MYSLENICE = "https://www.komornikmyslenice.pl/licytacje"

# --- USTAWIENIA ---
PLIK_STANU = "stan.json"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")


def powiadom_discord(wiadomosc):
    if WEBHOOK_URL:
        dane = {"content": wiadomosc}
        requests.post(WEBHOOK_URL, json=dane)
    else:
        print("Brak skonfigurowanego Webhooka Discord!")


def sprawdz_licytacje():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Wczytanie poprzedniego stanu
    poprzednie_linki = set()
    if os.path.exists(PLIK_STANU):
        try:
            with open(PLIK_STANU, 'r', encoding='utf-8') as f:
                poprzednie_linki = set(json.load(f))
        except json.JSONDecodeError:
            print("Błąd odczytu pliku stanu. Zaczynamy od zera.")

    aktualne_linki = set()

    # --- POBIERANIE DANYCH Z RÓŻNYCH STRON ---

    # 1. Krajowa Rada Komornicza
    for url in URLS_KRK:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            for a_tag in soup.find_all('a', class_='auction'):
                href = a_tag.get('href')
                if href:
                    pelny_link = urljoin("https://licytacje.komornik.pl", href)
                    aktualne_linki.add(pelny_link)
        except Exception as e:
            print(f"Błąd podczas sprawdzania KRK ({url}): {e}")

    # 2. Sąd Rejonowy w Myślenicach
    try:
        response = requests.get(URL_SR_MYSLENICE, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Wyszukujemy linki za pomocą ścieżki CSS: wewnątrz ul.main-news -> li -> h4 -> a
        for a_tag in soup.select('ul.main-news li.news-item h4 a'):
            href = a_tag.get('href')
            if href:
                pelny_link = urljoin("https://www.myslenice.sr.gov.pl/", href)
                aktualne_linki.add(pelny_link)
    except Exception as e:
        print(f"Błąd podczas sprawdzania SR Myślenice: {e}")

    # 3. Komornik Myślenice (strona własna)
    try:
        response = requests.get(URL_KOMORNIK_MYSLENICE, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Szukamy linków w liście <ol> -> <li> -> <a>
        for a_tag in soup.select('ol li a'):
            href = a_tag.get('href')
            # Upewniamy się, że to link do szczegółów licytacji, a nie pobieranie załącznika PDF
            if href and href.startswith('/licytacje/'):
                pelny_link = urljoin("https://www.komornikmyslenice.pl", href)
                aktualne_linki.add(pelny_link)
    except Exception as e:
        print(f"Błąd podczas sprawdzania strony Komornika Myślenice: {e}")

    print(f"Łącznie znaleziono {len(aktualne_linki)} ogłoszeń na wszystkich sprawdzanych stronach.")

    # --- PORÓWNANIE I POWIADOMIENIA ---
    nowe_linki = aktualne_linki - poprzednie_linki

    if nowe_linki:
        print(f"Znaleziono {len(nowe_linki)} nowych licytacji!")
        komunikat = "🚨 **Nowe licytacje!**\nZnaleziono nowe ogłoszenia:\n"
        for link in nowe_linki:
            komunikat += f"👉 {link}\n"

        powiadom_discord(komunikat)
    else:
        print("Brak nowych licytacji.")

    # Zapisanie nowego stanu
    with open(PLIK_STANU, 'w', encoding='utf-8') as f:
        json.dump(list(aktualne_linki), f, indent=4)


if __name__ == "__main__":
    sprawdz_licytacje()
