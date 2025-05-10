# File utama aplikasi Document Assistant

from flask import Flask, request, jsonify
import requests
import os
import json
import logging
import uuid
from datetime import datetime
import config

# Import modul kustom
from document_processor import DocumentProcessor
from nlp_engine import NLPEngine
from storage_manager import StorageManager

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize aplikasi Flask
app = Flask(__name__)

# Initialize modul-modul utama
nlp_engine = NLPEngine()
doc_processor = DocumentProcessor()
storage_manager = StorageManager(config.TEMP_STORAGE_PATH)

# Pastikan direktori penyimpanan sementara ada
os.makedirs(config.TEMP_STORAGE_PATH, exist_ok=True)

# Endpoint untuk verifikasi webhook WhatsApp
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode and token:
        if mode == 'subscribe' and token == config.WEBHOOK_VERIFY_TOKEN:
            logger.info("Webhook verified")
            return challenge
        else:
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    
    return jsonify({"status": "error", "message": "Invalid request"}), 400

# Endpoint untuk menerima pesan WhatsApp
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        logger.info(f"Received webhook data: {data}")
        
        # Periksa apakah ini adalah pesan WhatsApp
        if 'object' in data and data['object'] == 'whatsapp_business_account':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    if change.get('field') == 'messages':
                        process_whatsapp_message(change.get('value', {}))
            
            return jsonify({"status": "success"}), 200
        
        return jsonify({"status": "error", "message": "Not a WhatsApp message"}), 400
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def process_whatsapp_message(value):
    """Proses pesan masuk dari WhatsApp"""
    try:
        # Ekstrak metadata pesan
        message_data = value.get('messages', [{}])[0] if value.get('messages') else {}
        if not message_data:
            logger.warning("No message data found")
            return
        
        sender_id = message_data.get('from')
        message_id = message_data.get('id')
        message_timestamp = message_data.get('timestamp')
        
        # Ekstrak konten pesan berdasarkan jenisnya
        message_type = message_data.get('type')
        message_content = ""
        
        if message_type == 'text':
            # Pesan teks biasa
            message_content = message_data.get('text', {}).get('body', '')
        
        elif message_type == 'audio':
            # Pesan audio (voice note) - butuh transcription service
            message_content = "[VOICE MESSAGE - Transcription needed]"
            # Di implementasi nyata, Anda perlu mengunduh file audio dan 
            # menggunakan layanan transkripsi seperti Google Speech-to-Text
        
        elif message_type == 'document':
            # Dokumen yang dikirim user
            document_id = message_data.get('document', {}).get('id')
            document_name = message_data.get('document', {}).get('filename', 'unknown_file')
            # Di implementasi nyata, Anda perlu mengunduh dokumen
            message_content = f"[DOCUMENT RECEIVED: {document_name}]"
            
            # Simpan informasi dokumen untuk diproses
            nlp_engine.update_context(sender_id, {
                'last_document_id': document_id,
                'last_document_name': document_name
            })
        
        # Proses pesan dengan NLP engine
        if message_content:
            intent, entities, context = nlp_engine.process_message(message_content, sender_id)
            
            # Tangani intent yang terdeteksi
            response = handle_document_intent(intent, entities, context, sender_id)
            
            # Kirim respons ke WhatsApp
            send_whatsapp_message(sender_id, response)
    
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")

def handle_document_intent(intent, entities, context, user_id):
    """Handle berbagai intent terkait dokumen"""
    
    logger.info(f"Handling intent: {intent} with entities: {entities}")
    
    if intent == "create_document":
        # Ekstrak judul dan tipe dokumen
        doc_title = entities.get('document_title', 'Dokumen Tanpa Judul')
        doc_type = entities.get('document_type', 'docx')
        
        # Buat dokumen baru
        doc_id = doc_processor.create_document(doc_title, doc_type)
        
        # Simpan ID dokumen dalam konteks user
        nlp_engine.update_context(user_id, {'current_document': doc_id})
        
        return f"Dokumen {doc_type.upper()} baru dengan judul '{doc_title}' telah dibuat. Apa yang ingin Anda tambahkan ke dalamnya?"
    
    elif intent == "add_text":
        # Dapatkan dokumen saat ini dari konteks
        doc_id = nlp_engine.get_context(user_id).get('current_document')
        if not doc_id:
            return "Tidak ada dokumen aktif. Silakan buat atau pilih dokumen terlebih dahulu."
        
        # Ekstrak bagian dan konten teks
        section = entities.get('section', 'body')
        content = entities.get('content', '')
        
        # Tambahkan teks ke dokumen
        doc_processor.add_text(doc_id, section, content)
        
        return f"Teks telah ditambahkan ke bagian {section}. Apa yang ingin Anda lakukan selanjutnya?"
    
    elif intent == "edit_text":
        # Dapatkan dokumen saat ini dari konteks
        doc_id = nlp_engine.get_context(user_id).get('current_document')
        if not doc_id:
            return "Tidak ada dokumen aktif. Silakan buat atau pilih dokumen terlebih dahulu."
        
        # Ekstrak bagian, teks lama, dan teks baru
        section = entities.get('section', 'body')
        old_text = entities.get('old_text', '')
        new_text = entities.get('new_text', '')
        
        if old_text and new_text:
            # Edit teks di dokumen
            success = doc_processor.edit_text(doc_id, section, old_text, new_text)
            if success:
                return f"Teks '{old_text}' telah diubah menjadi '{new_text}' di bagian {section}."
            else:
                return f"Tidak dapat menemukan teks '{old_text}' di bagian {section}."
        else:
            return "Mohon tentukan teks yang ingin diubah dan penggantinya."
    
    elif intent == "export_document":
        # Dapatkan dokumen saat ini dari konteks
        doc_id = nlp_engine.get_context(user_id).get('current_document')
        if not doc_id:
            return "Tidak ada dokumen aktif. Silakan buat atau pilih dokumen terlebih dahulu."
        
        # Ekspor dokumen ke format yang diminta
        format_type = entities.get('format', 'docx')
        try:
            file_path = doc_processor.export_document(doc_id, format_type)
            
            # Kirim notifikasi karena file akan dikirim terpisah
            message = f"Dokumen Anda telah diekspor sebagai {format_type.upper()}. Sedang mengirim file..."
            
            # Di implementasi nyata, Anda perlu mengunggah file ke WhatsApp API
            # dan mengirimkannya ke pengguna
            
            return message
        except Exception as e:
            logger.error(f"Error exporting document: {str(e)}")
            return f"Terjadi kesalahan saat mengekspor dokumen: {str(e)}"
    
    elif intent == "help":
        # Kirim bantuan penggunaan
        help_text = """
Berikut adalah perintah yang dapat Anda gunakan:

- "Buat dokumen baru tentang [judul]"
- "Tambahkan teks ini ke bagian [bagian]"
- "Ubah [teks lama] menjadi [teks baru]"
- "Ekspor dokumen sebagai PDF/DOCX"
- "Bantu saya" untuk melihat perintah ini lagi
        """
        return help_text
    
    # Intent lainnya bisa ditambahkan di sini
    
    return "Saya tidak yakin apa yang ingin Anda lakukan dengan dokumen Anda. Anda dapat membuat, mengedit, atau mengekspor dokumen."

def send_whatsapp_message(recipient_id, message):
    """Kirim pesan teks melalui WhatsApp API"""
    url = config.WHATSAPP_API_URL
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.WHATSAPP_API_TOKEN}"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_id,
        "type": "text",
        "text": {
            "body": message
        }
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        logger.info(f"WhatsApp API response: {response.status_code} - {response.text}")
        return response.json()
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return None

# Endpoint untuk pengujian
@app.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({"status": "ok", "message": "WhatsApp Document Assistant is running"})

if __name__ == '__main__':
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG_MODE
    )
