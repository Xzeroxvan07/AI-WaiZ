#!/usr/bin/env python3

import os
import sys
import time
import json
import logging
from pathlib import Path
from threading import Thread, Event

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("AI-WaiZ-WebUI")

# Import modul utama
try:
    import speech_recognition as sr
    import pyttsx3
    from openai import OpenAI
    from flask import Flask, render_template, request, jsonify
except ImportError as e:
    logger.error(f"Gagal mengimpor modul yang diperlukan: {e}")
    logger.info("Silakan jalankan: pip install -r requirements.txt")
    sys.exit(1)

# Pastikan file konfigurasi ada
CONFIG_FILE = Path("config.json")
if not CONFIG_FILE.exists():
    logger.error(f"File konfigurasi tidak ditemukan: {CONFIG_FILE}")
    sys.exit(1)

# Muat konfigurasi
try:
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
except Exception as e:
    logger.error(f"Gagal memuat konfigurasi: {e}")
    sys.exit(1)

# Inisialisasi OpenAI client
client = OpenAI(api_key=config.get("openai_api_key"))

# Inisialisasi Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Variabel global untuk status
is_listening = False
stop_event = Event()
conversation_history = []

# Inisialisasi TTS engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
if 0 <= config.get("voice_id", 0) < len(voices):
    engine.setProperty('voice', voices[config.get("voice_id")].id)
engine.setProperty('rate', config.get("speech_rate", 150))

def speak(text):
    """Fungsi untuk mengucapkan teks"""
    try:
        logger.info(f"AI: {text}")
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception as e:
        logger.error(f"Error pada TTS: {e}")
        return False

def listen_once():
    """Fungsi untuk mendengarkan satu perintah"""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            logger.info("Mendengarkan input suara...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5)
            
        text = recognizer.recognize_google(audio, language=config.get("language", "id"))
        logger.info(f"Input suara: {text}")
        return text.lower()
    except Exception as e:
        logger.error(f"Error saat mendengarkan: {e}")
        return ""

def get_ai_response(prompt):
    """Dapatkan respons dari model AI"""
    try:
        # Tambahkan pesan ke riwayat percakapan
        conversation_history.append({"role": "user", "content": prompt})
        
        # Siapkan messages untuk API
        messages = [
            {"role": "system", "content": "Kamu adalah asisten AI bernama WaiZ yang membantu dan ramah."}
        ]
        # Tambahkan riwayat percakapan (batasi jumlah pesan untuk menghemat token)
        messages.extend(conversation_history[-5:])
        
        # Buat API call
        response = client.chat.completions.create(
            model=config.get("model", "gpt-3.5-turbo"),
            messages=messages,
            max_tokens=config.get("max_tokens", 150),
            temperature=config.get("temperature", 0.7)
        )
        
        # Dapatkan teks respons
        response_text = response.choices[0].message.content.strip()
        
        # Tambahkan respons ke riwayat percakapan
        conversation_history.append({"role": "assistant", "content": response_text})
        
        return response_text
    except Exception as e:
        logger.error(f"Error saat meminta respons AI: {e}")
        return "Maaf, saya mengalami kesulitan untuk merespons saat ini."

def voice_assistant_thread():
    """Thread untuk asisten suara"""
    global is_listening
    
    speak("Asisten suara WaiZ telah diaktifkan.")
    
    hotword = config.get("hotword", "waiz").lower()
    is_active = False
    
    while not stop_event.is_set():
        try:
            if not is_active:
                # Mode hotword - menunggu aktivasi
                text = listen_once()
                if hotword in text:
                    is_active = True
                    speak("Ya, saya mendengarkan.")
            else:
                # Mode aktif - mendengarkan perintah
                text = listen_once()
                if text:
                    # Periksa untuk keluar dari mode aktif
                    if "kembali ke hotword" in text or "mode siaga" in text:
                        speak("Kembali ke mode hotword.")
                        is_active = False
                        continue
                    
                    # Proses perintah/pertanyaan
                    response = get_ai_response(text)
                    speak(response)
                else:
                    # Jika tidak ada input, kembali ke mode hotword
                    is_active = False
            
            # Periksa perintah keluar
            if "matikan asisten" in text:
                speak("Mematikan asisten suara.")
                break
                
            time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error di thread asisten suara: {e}")
            time.sleep(1)
    
    is_listening = False
    logger.info("Thread asisten suara berhenti.")

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('message', '')
        
        if not user_input:
            return jsonify({"error": "Pesan kosong"}), 400
        
        # Dapatkan respons dari AI
        response = get_ai_response(user_input)
        
        return jsonify({
            "response": response,
            "history": conversation_history
        })
    except Exception as e:
        logger.error(f"Error pada API chat: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "Teks kosong"}), 400
        
        # Ucapkan teks
        success = speak(text)
        
        return jsonify({"success": success})
    except Exception as e:
        logger.error(f"Error pada API TTS: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/voice/start', methods=['POST'])
def start_voice():
    global is_listening
    
    if is_listening:
        return jsonify({"status": "Asisten suara sudah berjalan"}), 400
    
    try:
        # Reset stop event
        stop_event.clear()
        
        # Mulai thread asisten suara
        voice_thread = Thread(target=voice_assistant_thread)
        voice_thread.daemon = True
        voice_thread.start()
        
        is_listening = True
        return jsonify({"status": "Asisten suara dimulai"})
    except Exception as e:
        logger.error(f"Error saat memulai asisten suara: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/voice/stop', methods=['POST'])
def stop_voice():
    global is_listening
    
    if not is_listening:
        return jsonify({"status": "Asisten suara tidak aktif"}), 400
    
    try:
        # Set stop event untuk menghentikan thread
        stop_event.set()
        
        # Tunggu sebentar untuk thread berhenti
        time.sleep(1)
        
        return jsonify({"status": "Asisten suara dihentikan"})
    except Exception as e:
        logger.error(f"Error saat menghentikan asisten suara: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    # Kembalikan konfigurasi (kecuali API key)
    safe_config = {k: v for k, v in config.items() if k != 'openai_api_key'}
    return jsonify(safe_config)

def main():
    """Fungsi utama untuk menjalankan web UI"""
    try:
        logger.info("Memulai WaiZ Web UI...")
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logger.error(f"Error saat menjalankan server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
