# TCE Webcam Monitor

Automatisches Monitoring-System für den Tennisplatz mit Personenerkennung und GotCourts-Integration.

## Features

- **Webcam-Analyse**: Lädt Bilder von der Tennisplatz-Webcam
- **Personenerkennung**: Nutzt YOLOv8 zur Erkennung von Personen auf dem Platz
- **Reservierungsprüfung**: Prüft via GotCourts-API, ob eine aktive Reservation besteht
- **Telegram-Alerts**: Sendet Benachrichtigungen bei unbefugter Nutzung

## Setup

1. **Dependencies installieren:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   ```

2. **Environment-Variablen konfigurieren:**
   
   Erstelle eine `.env`-Datei:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   WEBCAM_URL=https://tcecam.ritternet.ch
   MODEL_PATH=yolov8n.pt
   GOTCOURTS_URL=https://apps.gotcourts.com/de/api/public/clubs/108/reservations
   ```

3. **YOLOv8-Modell herunterladen:**
   ```bash
   wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
   ```

## Verwendung

**Normal-Modus:**
```bash
python monitor.py
```

**Test-Modus** (simuliert 2 Spieler ohne Reservation):
```bash
python monitor.py --test
```

## GitHub Actions

Die Secrets müssen in GitHub unter **Settings → Secrets and variables → Actions** angelegt werden:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `WEBCAM_URL`
- `MODEL_PATH`
- `GOTCOURTS_URL`

## Konfiguration

- **THRESHOLD_PERSONS**: Mindestanzahl erkannter Personen für Alarm (Standard: 1)
- **CONFIDENCE_THRESHOLD**: YOLO-Konfidenz-Schwellwert (Standard: 0.4)
