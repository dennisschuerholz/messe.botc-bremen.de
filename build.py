import json
from datetime import datetime
from pathlib import Path

# Eingabe
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

# Ausgabe-Ordner
out_dir = Path("build")
ics_dir = out_dir / "ics"
ics_dir.mkdir(parents=True, exist_ok=True)

# Hilfsfunktionen
def format_dt(dt_str):
    return datetime.fromisoformat(dt_str).strftime("%Y%m%dT%H%M%S")

def format_time(dt_str):
    return datetime.fromisoformat(dt_str).strftime("%H:%M")

def generate_ics(event, day):
    uid = f"{day}{event['slot']}@botc-bremen.de"
    start = format_dt(event["start"])
    end = format_dt(event["end"])
    title = event["title"]

    return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//botc-bremen.de//NONSGML v1.0//DE
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}
DTSTART:{start}
DTEND:{end}
SUMMARY:{title}
END:VEVENT
END:VCALENDAR
"""

def generate_redirect_html(ics_filename):
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>Download Termin</title>
  <meta http-equiv="refresh" content="0; url=/ics/{ics_filename}">
</head>
<body>
  <p>Falls der Download nicht automatisch startet: <a href="/ics/{ics_filename}">Hier klicken</a>.</p>
</body>
</html>
"""

# Übersicht sammeln
overview_entries = []

# Verarbeitung
for day, slots in data.items():
    for ev in slots:
        start_time = datetime.fromisoformat(ev["start"]).strftime("%H%M")
        start_display = format_time(ev["start"])
        end_display = format_time(ev["end"])
        ics_filename = f"{day}-{start_time}.ics"

        # .ics-Datei schreiben
        with open(ics_dir / ics_filename, "w", encoding="utf-8") as f:
            f.write(generate_ics(ev, day))

        # HTML-Redirect-Seite erzeugen
        slot_dir = out_dir / day / str(ev["slot"])
        slot_dir.mkdir(parents=True, exist_ok=True)
        with open(slot_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(generate_redirect_html(ics_filename))

        # Übersichtseintrag merken
        overview_entries.append(
            f'<li><a href="/{day}/{ev["slot"]}/">{day}, {start_display}–{end_display}: {ev["title"]}</a></li>'
        )

# Übersicht schreiben
overview_html = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>BotC Messe-Termine</title>
</head>
<body>
  <h1>BotC Messe-Termine</h1>
  <ul>
    {"".join(overview_entries)}
  </ul>
</body>
</html>
"""

with open(out_dir / "index.html", "w", encoding="utf-8") as f:
    f.write(overview_html)

print("Build abgeschlossen. Dateien liegen in:", out_dir)
