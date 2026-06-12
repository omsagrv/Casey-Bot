import os
import logging
from flask import Flask, request, jsonify

# Esto hará que lo que pase en el bot aparezca en la consola de Railway
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    logger.info("¡Webhook recibido!") # Si ves esto en la consola, ¡ganamos!
    data = request.get_json(silent=True)
    logger.info(f"Datos recibidos: {data}")
    return jsonify({"status": "received"}), 200

# Configuración desde variables de entorno (Railway)
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE_NAME = os.getenv("INSTANCE_NAME", "Casey-Bot")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data or "message" not in data:
        return "OK", 200

    msg = data["message"]
    chat_id = data.get("key", {}).get("remoteJid")
    user_id = data.get("key", {}).get("participant")

    # Detectar imágenes, videos o stickers
    if any(key in msg for key in ["imageMessage", "videoMessage", "stickerMessage"]):
        if detectar_gore(msg): 
            ejecutar_protocolo_proteccion(chat_id, user_id)

    return "OK", 200

def ejecutar_protocolo_proteccion(chat_id, user_id):
    headers = {"apiKey": EVOLUTION_API_KEY, "Content-Type": "application/json"}
    
    # 1. CERRAR EL GRUPO (Solo Admins)
    requests.post(f"{EVOLUTION_API_URL}/group/updateSettings?instance={INSTANCE_NAME}", 
                  json={"chatId": chat_id, "announcement": True}, headers=headers)
    
    # 2. EXPULSAR AL USUARIO
    requests.post(f"{EVOLUTION_API_URL}/group/participants/update?instance={INSTANCE_NAME}", 
                  json={"action": "remove", "participants": [user_id]}, headers=headers)

    # 3. ENVIAR AVISO
    requests.post(f"{EVOLUTION_API_URL}/message/sendText?instance={INSTANCE_NAME}", 
                  json={"number": chat_id, "textMessage": {"text": "Este chat fue protegido por Sey"}}, headers=headers)

def detectar_gore(msg):
    # Aquí irá tu lógica futura con Gemini
    return True 

# entrypoint.sh
#!/bin/bash
set -e
echo "🚀 Iniciando en puerto: $PORT"
exec gunicorn --bind "0.0.0.0:${PORT:-8080}" \
     --workers 2 \
     --timeout 120 \
     --log-level debug \
     --access-logfile - \
     --error-logfile - \
     main:app
