#!/usr/bin/env python3

"""
AI-WaiZ: Asisten Virtual Berbasis Suara
"""

import os
import sys
import argparse
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

def check_dependencies():
    """Memeriksa dependensi yang diperlukan"""
    try:
        form app import app
        import speech_recognition as sr
        import pyttsx3
        from openai import OpenAI
        return True
    except ImportError as e:
        logger.error(f"Dependensi tidak terpenuhi: {e}")
        logger.info("Jalankan: pip install -r requirements.txt")
        return False

def check_config():
    """Memeriksa file konfigurasi"""
    CONFIG_FILE = Path("config.json")
    if not CONFIG_FILE.exists():
        logger.error(f"File konfigurasi tidak ditemukan: {CONFIG_FILE}")
        return False
    
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        
        # Periksa API key
        if config.get("openai_api_key") == "YOUR_API_KEY_HERE":
            logger.error("API key OpenAI belum dikonfigurasi")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Gagal memuat konfigurasi: {e}")
        return False

def main():
    """Fungsi utama"""
    parser = argparse.ArgumentParser(description="AI-WaiZ: Asisten Virtual Berbasis Suara")
    parser.add_argument("--web", action="store_true", help="Jalankan dalam mode web UI")
    parser.add_argument("--debug", action="store_true", help="Aktifkan mode debug")
    
    args = parser.parse_args()
    
    # Set level logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Mode debug diaktifkan")
    
    # Periksa dependensi
    if not check_dependencies():
        return 1
    
    # Periksa konfigurasi
    if not check_config():
        return 1
    
    try:
        if args.web:
            # Jalankan mode web UI
            logger.info("Memulai mode web UI...")
            from webui import main as run_webui
            run_webui()
        else:
            # Jalankan mode CLI
            logger.info("Memulai mode CLI...")
            from run import main as run_cli
            run_cli()
    except KeyboardInterrupt:
        logger.info("Program dihentikan oleh pengguna")
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
