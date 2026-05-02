from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

# ===== LECTURE DES CLÉS DEPUIS LES VARIABLES D'ENVIRONNEMENT =====
ONESIGNAL_APP_ID = os.environ.get("ONESIGNAL_APP_ID")
ONESIGNAL_REST_API_KEY = os.environ.get("ONESIGNAL_REST_API_KEY")

# Vérification au démarrage
print(f"🔑 OneSignal App ID: {'OK' if ONESIGNAL_APP_ID else '❌ MANQUANT'}")
print(f"🔑 OneSignal API Key: {'OK' if ONESIGNAL_REST_API_KEY else '❌ MANQUANT'}")

# ===== ENDPOINT QUE L'ESP32 APPELERA =====
@app.route('/alerte', methods=['POST'])
def recevoir_alerte():
    try:
        # Vérifie que les clés sont présentes
        if not ONESIGNAL_APP_ID or not ONESIGNAL_REST_API_KEY:
            print("❌ Clés OneSignal manquantes !")
            return jsonify({"error": "Clés OneSignal non configurées"}), 500

        # Reçoit les données de l'ESP32
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Pas de données"}), 400
        
        message = data.get('message', 'Mouvement détecté !')
        temperature = data.get('temp', 0)
        humidite = data.get('hum', 0)
        angle = data.get('angle', 0)
        
        print(f"[{datetime.now()}] 📡 Alerte reçue de l'ESP32")
        print(f"   - Message: {message}")
        print(f"   - Température: {temperature}°C")
        print(f"   - Humidité: {humidite}%")
        print(f"   - Angle: {angle}°")
        
        # Envoie la notification via OneSignal
        envoyer_notification_onesignal(message, temperature, humidite, angle)
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({"error": str(e)}), 500

def envoyer_notification_onesignal(message, temperature, humidite, angle):
    """Envoie une notification push via OneSignal"""
    
    titre = "🚨 Mouvement près de la porte !"
    corps_message = f"🌡️ {temperature}°C  |  💧 {humidite}%\n📡 Angle radar: {angle}°"
    
    url = "https://onesignal.com/api/v1/notifications"
    
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_REST_API_KEY}"
    }
    
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "headings": {"fr": titre},
        "contents": {"fr": corps_message},
        "included_segments": ["Subscribed Users"],
        "data": {
            "type": "alerte_porte",
            "temperature": temperature,
            "humidite": humidite,
            "angle": angle,
            "timestamp": datetime.now().isoformat()
        },
        "android_visibility": 1,
        "priority": 10
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        
        if response.status_code == 200:
            print(f"✅ Notification envoyée ! ID: {result.get('id')}")
        else:
            print(f"❌ Erreur OneSignal: {result}")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi OneSignal: {e}")

# ===== PAGE DE TEST =====
@app.route('/', methods=['GET'])
def index():
    status_api = "✅ Configurée" if ONESIGNAL_APP_ID else "❌ Non configurée"
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Porte Connectée - Backend</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial; background: #0f0f13; color: white; padding: 20px; text-align: center; }}
            .status {{ background: #1a1a24; padding: 20px; border-radius: 10px; margin-top: 20px; }}
            .online {{ color: #22c55e; }}
            .info {{ color: #94a3b8; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <h1>🔒 Porte Connectée - Backend</h1>
        <div class="status">
            <p>✅ Serveur actif !</p>
            <p>📢 OneSignal: {status_api}</p>
            <p class="info">Endpoint: POST /alerte</p>
        </div>
    </body>
    </html>
    '''

# ===== LANCEMENT =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)