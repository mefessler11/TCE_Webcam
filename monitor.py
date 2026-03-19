# Import libraries
from datetime import datetime
import argparse
import io
import os
import requests
import pytz
from ultralytics import YOLO
from PIL import Image
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urljoin

load_dotenv()

# Konfiguration (GitHub Secrets)
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
WEBCAM_URL = os.environ["WEBCAM_URL"]
MODEL_PATH = os.environ["MODEL_PATH"]
GOTCOURTS_URL = os.environ["GOTCOURTS_URL"]

# Threshold Anzahl Personen
THRESHOLD_PERSONS = 1

# Confidence-Threshold YOLO
CONFIDENCE_THRESHOLD = 0.4



def fetch_webcam_image():
    print(f"Fetching webcam image from {WEBCAM_URL}")
    response = requests.get(WEBCAM_URL, timeout=10)
    if response.status_code != 200:
        print(f"Failed to fetch webcam page: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    img_tag = soup.find('img')
    if not img_tag or not img_tag.get('src'):
        print("No image found in HTML")
        return None
    
    img_url = urljoin(WEBCAM_URL, img_tag['src'])
    print(f"Fetching actual image from {img_url}")
    img_response = requests.get(img_url, timeout=10)
    if img_response.status_code == 200:
        return img_response.content
    else:
        print(f"Failed to fetch image: {img_response.status_code}")
        return None


def detect_and_count_persons(image):
    model = YOLO(MODEL_PATH)
    results = model(image, conf=CONFIDENCE_THRESHOLD, classes=[0])
    return sum(len(r.boxes) for r in results)


def check_active_reservation():
    tz = pytz.timezone("Europe/Zurich")
    now = datetime.now(tz)
    today = now.strftime("%Y-%m-%d")

    try:
        response = requests.get(
            GOTCOURTS_URL,
            params={"date": today},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"GotCourts-Abfrage fehlgeschlagen: {e}")
        return False

    current_time = data["response"]["currentTime"]

    for res in data["response"]["reservations"]:
        if res["startTime"] <= current_time < res["endTime"]:
            print(f"Aktive Reservation: {res['startTime']//3600:02d}:{(res['startTime']%3600)//60:02d}")
            return True

    for blocking in data["response"]["blockings"]:
        if blocking["startTime"] <= current_time < blocking["endTime"]:
            print("Platz ist blockiert")
            return True

    return False


def send_telegram_alert(person_count: int) -> None:
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    message = (
        f"🚨 *Tennisplatz-Alarm*\n\n"
        f"Jemand ist auf dem Platz ohne Reservation!\n"
        f"🕐 {now}\n"
        f"👤 Erkannte Personen: {person_count}\n\n"
        f"Bitte prüfen: {WEBCAM_URL}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    print("✅ Telegram-Nachricht gesendet.")


def main():
    parser = argparse.ArgumentParser(description="Tennis court monitoring")
    parser.add_argument("--test", action="store_true", help="Test mode: simulate 2 players and no reservation")
    args = parser.parse_args()

    if args.test:
        print("🧪 TEST MODE: Simuliere 2 Spieler, keine Reservation")
        person_count = 2
        has_reservation = False
    else:
        image_bytes = fetch_webcam_image()
        if image_bytes is None:
            return

        image = Image.open(io.BytesIO(image_bytes))
        person_count = detect_and_count_persons(image)
        has_reservation = check_active_reservation()

    print(f"Personen: {person_count}, Reservation: {has_reservation}")

    if person_count >= THRESHOLD_PERSONS and not has_reservation:
        send_telegram_alert(person_count)


if __name__ == "__main__":
    main()