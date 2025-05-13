#!/usr/bin/env python3

import os
import sys
import threading
import time
import json
import logging
from pathlib import Path

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("AI-WaiZ")

# Periksa versi Python
if sys.version_info < (3, 8):
    logger.error("Python 3.8 atau yang lebih baru diperlukan!")
    sys.exit(1)

# Coba import dependency yang diperlukan
try:
    import speech_recognition as sr
    import pyttsx3
    import openai
except ImportError as e:
    logger.error(f"Gagal mengimpor modul yang diperlukan: {e}")
    logger.info("Silakan jalankan: pip install -r requirements.txt")
    sys.exit(1)

# Pastikan file konfigurasi ada
CONFIG_FILE = Path("config.json")
if not CONFIG_FILE.exists():
    logger.error(f"File konfigurasi tidak ditemukan: {CONFIG_FILE}")
    # Buat file konfigurasi contoh
    default_config = {
        "openai_api_key": "YOUR_API_KEY_HERE",
        "language": "id",
        "voice_id": 0,
        "hotword": "waiz",
        "model": "gpt-3.5-turbo"
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(default_config, f, indent=4)
    logger.info(f"File konfigurasi contoh telah dibuat: {CONFIG_FILE}")
    logger.info("Harap edit file tersebut dengan API key dan pengaturan yang benar!")
    sys.exit(1)

# Muat konfigurasi
try:
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    
    # Periksa kelengkapan konfigurasi
    required_keys = ["openai_api_key", "language", "voice_id", "model"]
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        logger.error(f"Kunci konfigurasi yang diperlukan tidak ditemukan: {', '.join(missing_keys)}")
        sys.exit(1)
    
    # Atur API key OpenAI jika digunakan
    if "openai_api_key" in config and config["openai_api_key"] != "YOUR_API_KEY_HERE":
        openai.api_key = config["openai_api_key"]
    else:
        logger.warning("API key OpenAI tidak dikonfigurasi dengan benar!")
except Exception as e:
    logger.error(f"Gagal memuat konfigurasi: {e}")
    sys.exit(1)

# Inisialisasi mesin text-to-speech
try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if config.get("voice_id", 0) < len(voices):
        engine.setProperty('voice', voices[config["voice_id"]].id)
    engine.setProperty('rate', 150)
except Exception as e:
    logger.error(f"Gagal menginisialisasi mesin text-to-speech: {e}")
    sys.exit(1)

def speak(text):
    """Fungsi untuk mengubah teks menjadi ucapan"""
    try:
        logger.info(f"AI: {text}")
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        logger.error(f"Gagal mengucapkan teks: {e}")

def listen():
    """Fungsi untuk mendengarkan dan mengenali ucapan"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        logger.info("Mendengarkan...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language=config.get("language", "id"))
            logger.info(f"Anda: {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            logger.info("Tidak dapat mengenali ucapan")
            return ""
        except sr.RequestError as e:
            logger.error(f"Layanan pengenalan ucapan error: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error saat mendengarkan: {e}")
            return ""

def get_ai_response(prompt):
    """Fungsi untuk mendapatkan respons dari AI"""
    try:
        response = openai.ChatCompletion.create(
            model=config.get("model", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "Kamu adalah asisten AI bernama WaiZ yang membantu dan ramah."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error saat meminta respons AI: {e}")
        return "Maaf, saya mengalami kesulitan untuk merespons saat ini."

def main():
    """Fungsi utama program"""
    logger.info("AI-WaiZ sedang dimulai...")
    speak("Hai, saya WaiZ, asisten AI Anda. Saya siap membantu.")
    
    hotword = config.get("hotword", "waiz").lower()
    
    while True:
        try:
            text = listen()
            
            # Periksa hotword
            if hotword in text:
                speak("Ya, saya mendengarkan.")
                text = listen()
                if text:
                    response = get_ai_response(text)
                    speak(response)
            
            # Keluar dari program jika diminta
            if "matikan" in text or "keluar" in text or "tutup" in text:
                speak("Sampai jumpa lagi!")
                break
                
            time.sleep(0.1)  # Sedikit delay untuk menghindari CPU usage tinggi
            
        except KeyboardInterrupt:
            logger.info("Program dihentikan oleh pengguna.")
            break
        except Exception as e:
            logger.error(f"Error tidak terduga: {e}")
            continue

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        speak("Terjadi kesalahan. Program akan dimatikan.")
        sys.exit(1)
