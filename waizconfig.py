# Konfigurasi untuk WhatsApp Document Assistant

# WhatsApp Business API Configuration
WHATSAPP_API_URL = "https://graph.facebook.com/v17.0/PHONE_NUMBER_ID/messages"
WHATSAPP_API_TOKEN = "YOUR_WHATSAPP_API_TOKEN"
WHATSAPP_PHONE_NUMBER_ID = "YOUR_WHATSAPP_PHONE_NUMBER_ID"

# Server Configuration
DEBUG_MODE = True
PORT = 5000
HOST = "0.0.0.0"

# Storage Configuration
TEMP_STORAGE_PATH = "./temp_storage"
DOCUMENT_TTL = 3600  # Time to live for documents in seconds (1 hour)

# Security Configuration
WEBHOOK_VERIFY_TOKEN = "your_secure_verify_token"  # Token untuk verifikasi webhook

# NLP Configuration 
# Bisa diganti dengan konfigurasi untuk NLP engine yang Anda pilih
# (contoh: Dialogflow, RASA, dll)
NLP_ENGINE = "rule_based"  # simple rule-based untuk contoh ini
