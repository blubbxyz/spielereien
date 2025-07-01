from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def terminal():
    output = ""
    if request.method == "POST":
        befehl = request.form["befehl"]
        try:
            result = subprocess.run(
                ["python", befehl],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout + "\n" + result.stderr
        except Exception as e:
            output = f"Fehler beim Ausführen: {e}"
    return render_template("index.html", output=output)

if __name__ == "__main__":
    app.run(debug=True)
