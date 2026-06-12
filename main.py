import os
import google.generativeai as genai
from flask import Flask, request
import requests

app = Flask(__name__)

# Configuración desde variables de entorno (Railway)
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE_NAME = "Casey Bot" # Asegúrate de poner el nombre de tu instancia aquí

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
        # Aquí iría la lógica de análisis con Gemini
        # Si Gemini detecta contenido Gore (Simulación):
        if detectar_gore(msg): 
            ejecutar_protocolo_proteccion(chat_id, user_id)

    return "OK", 200

def ejecutar_protocolo_proteccion(chat_id, user_id):
    headers = {"apiKey": EVOLUTION_API_KEY, "Content-Type": "application/json"}
    
    # 1. Expulsar al usuario
    requests.post(f"{EVOLUTION_API_URL}/group/participants/update?instance={INSTANCE_NAME}", 
                  json={"action": "remove", "participants": [user_id]}, headers=headers)

    # 2. Enviar el aviso de protección
    requests.post(f"{EVOLUTION_API_URL}/message/sendText?instance={INSTANCE_NAME}", 
                  json={"number": chat_id, "textMessage": {"text": "Este chat fue protegido por Sey"}}, headers=headers)
    
    # 3. Cerrar el grupo (Solo Administradores pueden hablar)
    requests.post(f"{EVOLUTION_API_URL}/group/updateSettings?instance={INSTANCE_NAME}", 
                  json={"chatId": chat_id, "announcement": True}, headers=headers)

def detectar_gore(msg):
    # Lógica de Gemini para analizar el contenido
    return True # Temporal para pruebas

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
