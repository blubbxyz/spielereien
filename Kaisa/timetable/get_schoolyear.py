import webuntis
from datetime import datetime
from dotenv import load_dotenv
import os
import json
import sys

load_dotenv("D:/i guess/cuh/Kaisa/timetable/timetable.env")

username = os.getenv("WEBUNTIS_USERNAME")
password = os.getenv("WEBUNTIS_PASSWORD")
server = os.getenv("WEBUNTIS_SERVER")
school = os.getenv("WEBUNTIS_SCHOOL")
useragent = os.getenv("WEBUNTIS_USERAGENT")

if not all([username, password, server, school, useragent]):
    print("Fehler: Mindestens eine WebUntis-Umgebungsvariable ist nicht gesetzt!")
    exit(1)

# Schuljahr-ID und optional Zielpfad von Kommandozeile holen
if len(sys.argv) > 1:
    try:
        schuljahr_id = int(sys.argv[1])
    except ValueError:
        print("Bitte Schuljahr-ID als Zahl übergeben!")
        exit(1)
else:
    print("Bitte Schuljahr-ID als Argument übergeben!")
    exit(1)

if len(sys.argv) > 2:
    json_path = sys.argv[2]
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, f"stunden_{schuljahr_id}.json")

session = webuntis.Session(
    server=server,
    school=school,
    username=username,
    password=password,
    useragent=useragent,
).login()

years = session.schoolyears()
chosen_year = next((y for y in years if y.id == schuljahr_id), None)
if not chosen_year:
    print("Ungültige Schuljahr-ID.")
    session.logout()
    exit(1)

# Klasse fest vorgeben wie in timetable_config_date.py
klasse_name = 'FG 31'
klassen = session.klassen()
gefiltert = klassen.filter(name=klasse_name)
if not gefiltert:
    print(f"Klasse '{klasse_name}' nicht gefunden!")
    session.logout()
    exit(1)

klasse = gefiltert[0]
timetable = session.timetable(
    klasse=klasse,
    start=chosen_year.start.date(),
    end=chosen_year.end.date()
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

script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "stunden.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(stunden_dicts, f, ensure_ascii=False, indent=2)

session.logout()
