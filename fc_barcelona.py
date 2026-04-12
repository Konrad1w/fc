import requests
import os

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

url = "https://www.fcbarcelona.com/en/tickets/football/regular/laliga/fcbarcelona-realmadrid"
headers = {"User-Agent": "Mozilla/5.0"}

def send_discord(msg):
    requests.post(WEBHOOK_URL, json={"content": msg})

html = requests.get(url, headers=headers).text

if "Temporarily unavailable" not in html:
    send_discord("🚨 Ticket page changed! Check now!")
    print("FOUND!")
else:
    print("Still unavailable")