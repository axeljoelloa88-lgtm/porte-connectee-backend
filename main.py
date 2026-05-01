from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

# ===== CONFIGURATION ONESIGNAL =====
# REMPLACE PAR TES VRAIES CLÉS !
ONESIGNAL_APP_ID = "15c6233e-8f44-440d-b55b-bc039598550d"
ONESIGNAL_REST_API_KEY = "os_v2_app_cxdcgpupirca3nk3xqbzlgcvbvrise2jniyewtfgbhe4oh5g6glq22ineeywlcf2dzubzcmbyz3vdnacwlxkeckch3hyowbtopcoujy"

# ===== ENDPOINT QUE L'ESP32 APPELERA =====
@app.route('/alerte', methods=['POST'])
def recevoir_alerte():
    try:
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
        envoyer_notification_onesignal(temperature, humidite, angle)
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({"error": str(e)}), 500

def envoyer_notification_onesignal(temperature, humidite, angle):
    """Envoie une notification push via OneSignal"""
    
    # Message principal : mouvement près de la porte
    titre = "🚨 Mouvement près de la porte !"
    corps_message = f"🌡️ {temperature}°C  |  💧 {humidite}%\n📡 Angle radar: {angle}°"
    
    # Construction de la requête OneSignal
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

# ===== PAGE DE TEST (optionnel) =====
@app.route('/', methods=['GET'])
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Porte Connectée - Backend</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial; background: #0f0f13; color: white; padding: 20px; text-align: center; }
            .status { background: #1a1a24; padding: 20px; border-radius: 10px; margin-top: 20px; }
            .online { color: #22c55e; }
            .endpoint { background: #22222f; padding: 10px; border-radius: 5px; font-family: monospace; }
        </style>
    </head>
    <body>
        <h1>🔒 Porte Connectée - Backend</h1>
        <div class="status">
            <p>✅ Serveur actif !</p>
            <p>Endpoint alerte: <span class="endpoint">POST /alerte</span></p>
        </div>
        <p style="color: #94a3b8; margin-top: 20px;">En attente des notifications de l'ESP32...</p>
    </body>
    </html>
    '''

# ===== LANCEMENT =====
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)