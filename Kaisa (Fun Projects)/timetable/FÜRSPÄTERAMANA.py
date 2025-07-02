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
name = os.getenv("WEBUNTIS_KLASSE")

if not all([username, password, server, school, useragent]):
    print("Fehler: Mindestens eine WebUntis-Umgebungsvariable ist nicht gesetzt!")
    exit(1)

session = webuntis.Session(
    server=server,
    school=school,
    username=username,
    password=password,
    useragent=useragent,
).login()

years = session.schoolyears()
print("Verfügbare Schuljahre:")
for y in years:
    print(f"- ID {y.id}: {y.name} ({y.start.strftime('%Y-%m-%d')} bis {y.end.strftime('%Y-%m-%d')})")

# Schuljahr-ID per Argument oder interaktiv
if len(sys.argv) > 1:
    try:
        chosen_id = int(sys.argv[1])
    except ValueError:
        print("Ungültige Schuljahr-ID übergeben.")
        session.logout()
        exit(1)
    chosen_year = next((y for y in years if y.id == chosen_id), None)
    if not chosen_year:
        print("Ungültige Schuljahr-ID.")
        session.logout()
        exit(1)
else:
    chosen_id = None
    while chosen_id is None:
        eingabe = input("Bitte Schuljahr-ID eingeben: ").strip()
        if not eingabe.isdigit():
            print("Bitte eine gültige Zahl eingeben.")
            continue
        chosen_id = int(eingabe)
        chosen_year = next((y for y in years if y.id == chosen_id), None)
        if not chosen_year:
            print("Ungültige Schuljahr-ID.")
            chosen_id = None

print(f"Gewähltes Schuljahr: {chosen_year.name} ({chosen_year.start.strftime('%Y-%m-%d')} bis {chosen_year.end.strftime('%Y-%m-%d')})")

klassen = session.klassen()
gefiltert = klassen.filter(name=name)

if not gefiltert:
    print("Klasse nicht gefunden!")
    session.logout()
    exit()

klasse = gefiltert[0]
timetable = session.timetable(
    klasse=klasse,
    start=chosen_year.start.date(),
    end=chosen_year.end.date()
)

stunden_liste = []
for lesson in timetable:
    if not lesson.subjects:
        continue
    eintrag = {
        "date": lesson.start.strftime('%Y-%m-%d'),
        "start": lesson.start.strftime('%H:%M'),
        "end": lesson.end.strftime('%H:%M'),
        "subject": lesson.subjects[0].name,
        "status": "❌ Fällt aus" if getattr(lesson, "code", "") == 'cancelled' else "✅ Findet statt"
    }
    stunden_liste.append(eintrag)

with open("stunden.json", "w", encoding="utf-8") as f:
    json.dump(stunden_liste, f, ensure_ascii=False, indent=2)

print(f"\n{len(stunden_liste)} Einträge wurden in stunden.json gespeichert.")

session.logout()


# mach mal so abfrage mit welche jahre verfügbar sind und welche klassen in dem jahr
