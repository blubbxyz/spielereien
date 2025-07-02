import subprocess
import json
import os

# Zeitraum abfragen
startdatum = input("Startdatum (YYYY-MM-DD): ")
enddatum = input("Enddatum (YYYY-MM-DD): ")

subprocess.run([
    "python", "Kaisa/timetable/timetable_config_date.py", startdatum, enddatum
])

# Absoluten Pfad zur stunden.json im gleichen Ordner wie dieses Skript bestimmen
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "stunden.json")

with open(json_path, "r", encoding="utf-8") as f:
    stunden = json.load(f)

# Statistik berechnen: Wie oft ist welches Fach ausgefallen?
stats = {}
for eintrag in stunden:
    fach = eintrag["subject"]
    if fach not in stats:
        stats[fach] = {"ausgefallen": 0, "gesamt": 0}
    stats[fach]["gesamt"] += 1
    if eintrag["status"].startswith("❌"):
        stats[fach]["ausgefallen"] += 1

# Tabelle ausgeben
print("\nStatistik (Fach | Ausgefallen / Gesamt | Prozent ausgefallen):")
print("-" * 55)
for fach, werte in sorted(stats.items()):
    gesamt = werte["gesamt"]
    ausgefallen = werte["ausgefallen"]
    prozent = (ausgefallen / gesamt * 100) if gesamt else 0
    print(f"{fach:20} | {ausgefallen:3} / {gesamt:3} | {prozent:5.1f}%")