# klassenaufliste:
# import webuntis

# s = webuntis.Session(
#     server='https://melete.webuntis.com',     # Deine WebUntis-URL
#     school='RBB Schwerin-Technik',           # Schulname (wie bei der Anmeldung)
#     username='fg31',
#     password='Schwerin02*',
#     useragent='Python-Test'
# ).login()

# # Alle Klassen ausgeben
# klassen = s.klassen()
# for klasse in klassen:
#     print(f"ID: {klasse.id} | Name: '{klasse.name}'")

# s.logout()



import webuntis
from datetime import date
import os 
from dotenv import load_dotenv

load_dotenv()  # lädt die .env

username = os.getenv("WEBUNTIS_USERNAME")
password = os.getenv("WEBUNTIS_PASSWORD")
server = os.getenv("WEBUNTIS_SERVER")
school = os.getenv("WEBUNTIS_SCHOOL")

s = webuntis.Session(
    server='https://melete.webuntis.com',
    school='RBB Schwerin-Technik',
    username='fg31',
    password='Schwerin02*',
    useragent='Python-Test'
).login()
klassen = s.klassen()
gefiltert = klassen.filter(name='FG 31')

if not gefiltert:
    print("Klasse 'FG 31' nicht gefunden!")
    s.logout()
    exit()

klasse = gefiltert[0]
timetable = s.timetable(klasse=klasse, start=date.today(), end=date.today())


for lesson in timetable:
    if not lesson.subjects:
        continue 
    
    start = lesson.start.strftime('%H:%M')
    end = lesson.end.strftime('%H:%M')
    subject = lesson.subjects[0].name
    room = lesson.rooms[0].name

    status = "❌ Fällt aus" if lesson.code == 'cancelled' else "✅ Findet statt"

    print(f"{start}-{end} | {subject} | {room} | {status}")

s.logout()

