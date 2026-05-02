from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os

app = Flask(__name__)

# ===== NTFY CONFIG =====
NTFY_TOPIC = "porte-connectee-joel"  # doit correspondre a ce que tu as mis dans l'app

# ===== ENDPOINT ESP32 =====
@app.route('/alerte', methods=['POST'])
def recevoir_alerte():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Pas de données"}), 400

        temperature = data.get('temp', 0)
        humidite    = data.get('hum',  0)
        angle       = data.get('angle', 0)

        print(f"[{datetime.now()}] Alerte reçue — {temperature}°C  {humidite}%  angle:{angle}°")

        envoyer_notification_ntfy(temperature, humidite, angle)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"Erreur: {e}")
        return jsonify({"error": str(e)}), 500


def envoyer_notification_ntfy(temperature, humidite, angle):
    """Envoie une notification push via ntfy.sh — gratuit, sans compte"""
    try:
        response = requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=f"Quelqu'un est devant la porte !\n🌡️ {temperature}°C  💧 {humidite}%  📡 {angle}°",
            headers={
                "Title":    "Mouvement detecte !",
                "Priority": "urgent",
                "Tags":     "warning,door"
            }
        )
        if response.status_code == 200:
            print("Notification ntfy envoyee !")
        else:
            print(f"Erreur ntfy: {response.status_code}")
    except Exception as e:
        print(f"Erreur ntfy: {e}")


# ===== PAGE DE TEST =====
@app.route('/', methods=['GET'])
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Porte Connectée - Backend</title>
        <meta charset="UTF-8">
        <style>
            body{font-family:Arial;background:#0f0f13;color:white;padding:20px;text-align:center}
            .status{background:#1a1a24;padding:20px;border-radius:10px;margin-top:20px}
            .info{color:#94a3b8;margin-top:10px}
            .btn{background:#3b82f6;color:white;border:none;padding:12px 24px;border-radius:8px;cursor:pointer;font-size:16px;margin-top:16px}
        </style>
    </head>
    <body>
        <h1>Porte Connectee - Backend</h1>
        <div class="status">
            <p>Serveur actif !</p>
            <p class="info">Endpoint: POST /alerte</p>
            <p class="info">Notifications via: ntfy.sh</p>
        </div>
        <form action="/test" method="get">
            <button class="btn" type="submit">Tester la notification</button>
        </form>
    </body>
    </html>
    '''

# ===== ROUTE DE TEST RAPIDE =====
@app.route('/test', methods=['GET'])
def test():
    """Permet de tester la notif directement depuis le navigateur"""
    envoyer_notification_ntfy(22.5, 45.0, 90)
    return '''
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8">
    <style>body{font-family:Arial;background:#0f0f13;color:white;padding:20px;text-align:center}</style>
    </head>
    <body>
        <h2>Notification de test envoyee !</h2>
        <p style="color:#94a3b8">Verifie ton telephone</p>
        <a href="/" style="color:#3b82f6">Retour</a>
    </body>
    </html>
    '''

# ===== LANCEMENT =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)