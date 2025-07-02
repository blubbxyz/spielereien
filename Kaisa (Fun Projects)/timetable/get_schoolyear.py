import webuntis
from datetime import datetime
from dotenv import load_dotenv
import os
import json
import sys

load_dotenv("D:/i guess/cuh/Kaisa (Fun Projects)/timetable/timetable.env")

username = os.getenv("WEBUNTIS_USERNAME")
password = os.getenv("WEBUNTIS_PASSWORD")
server = os.getenv("WEBUNTIS_SERVER")
school = os.getenv("WEBUNTIS_SCHOOL")
useragent = os.getenv("WEBUNTIS_USERAGENT")
klasse_name = os.getenv("WEBUNTIS_KLASSE")  # <-- Klasse aus ENV

if not all([username, password, server, school, useragent, klasse_name]):
    print("Fehler: Mindestens eine WebUntis-Umgebungsvariable ist nicht gesetzt!")
    exit(1)

# Zeitraum für das ganze Schuljahr festlegen (hier Beispiel: 2024-09-02 bis 2025-07-22)
startdatum = datetime.strptime("2024-09-02", "%Y-%m-%d").date()
enddatum = datetime.strptime("2025-07-11", "%Y-%m-%d").date()

script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "stunden.json")

session = webuntis.Session(
    server=server,
    school=school,
    username=username,
    password=password,
    useragent=useragent,
).login()

klassen = session.klassen()
gefiltert = klassen.filter(name=klasse_name)
if not gefiltert:
    print(f"Klasse '{klasse_name}' nicht gefunden!")
    session.logout()
    exit(1)

klasse = gefiltert[0]
timetable = session.timetable(
    klasse=klasse,
    start=startdatum,
    end=enddatum
)

stunden = []
for lesson in timetable:
    if not lesson.subjects:
        continue

    datum = lesson.start.strftime('%Y-%m-%d')
    start_uhr = lesson.start.strftime('%H:%M')
    end_uhr = lesson.end.strftime('%H:%M')
    subject = lesson.subjects[0].name
    status = "❌ Fällt aus" if getattr(lesson, "code", "") == 'cancelled' else "✅ Findet statt"

    stunden.append((lesson.start, datum, start_uhr, end_uhr, subject, status))

stunden.sort(key=lambda x: x[0])

stunden_dicts = [
    {
        "datum": datum,
        "start": start_uhr,
        "end": end_uhr,
        "subject": subject,
        "status": status
    }
    for _, datum, start_uhr, end_uhr, subject, status in stunden
]

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(stunden_dicts, f, ensure_ascii=False, indent=2)

session.logout()
