# Modul untuk NLP dan pemrosesan intent
import re
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class NLPEngine:
    def __init__(self):
        self.user_contexts = {}  # Untuk menyimpan konteks percakapan user
        
        # Intent patterns - pola regex sederhana untuk mendeteksi intent
        # Dalam implementasi nyata, sebaiknya gunakan NLP framework seperti
        # Dialogflow, RASA, atau model ML kustom
        self.intent_patterns = {
            "create_document": [
                r"(?i)buat(?:\s+sebuah|\s+satu)?\s+dokumen(?:\s+baru)?(?:\s+tentang|\s+dengan\s+judul|\s+berjudul)?(?:\s+['"]?([^'"]*)['"]?)?",
                r"(?i)bikin(?:\s+sebuah|\s+satu)?\s+dokumen(?:\s+baru)?(?:\s+tentang|\s+dengan\s+judul|\s+berjudul)?(?:\s+['"]?([^'"]*)['"]?)?",
                r"(?i)tulis(?:\s+sebuah|\s+satu)?\s+(?:paper|makalah|dokumen)(?:\s+tentang|\s+dengan\s+judul|\s+berjudul)?(?:\s+['"]?([^'"]*)['"]?)?",
                r"(?i)mulai(?:\s+sebuah|\s+satu)?\s+dokumen(?:\s+baru)?(?:\s+tentang|\s+dengan\s+judul|\s+berjudul)?(?:\s+['"]?([^'"]*)['"]?)?",
                r"(?i)create(?:\s+a|\s+new)?\s+document(?:\s+about|\s+titled|\s+on)?(?:\s+['"]?([^'"]*)['"]?)?"
            ],
            "add_text": [
                r"(?i)tambah(?:kan)?\s+(?:teks|paragraf|kalimat|konten)(?:\s+ini)?(?:\s+ke(?:\s+bagian|\s+seksi|\s+section)?\s+([^:]*))?(:|$)",
                r"(?i)masuk(?:kan)?\s+(?:teks|paragraf|kalimat|konten)(?:\s+ini)?(?:\s+ke(?:\s+bagian|\s+seksi|\s+section)?\s+([^:]*))?(:|$)",
                r"(?i)add(?:\s+this)?\s+(?:text|paragraph|sentence|content)(?:\s+to(?:\s+the)?\s+([^:]*)\s+section)?(:|$)"
            ],
            "edit_text": [
                r"(?i)(?:edit|ubah|ganti)\s+['"]([^'"]*)['"](?:\s+menjadi|\s+dengan|\s+jadi)\s+['"]([^'"]*)['"](?:\s+di(?:\s+bagian|\s+seksi|\s+section)?\s+([^:]*))?",
                r"(?i)replace\s+['"]([^'"]*)['"](?:\s+with)\s+['"]([^'"]*)['"](?:\s+in(?:\s+the)?\s+([^:]*)\s+section)?"
            ],
            "export_document": [
                r"(?i)export(?:\s+dokumen(?:\s+ini)?|\s+file(?:\s+ini)?)(?:\s+sebagai|\s+ke)?\s+(pdf|docx)",
                r"(?i)konversi(?:\s+dokumen(?:\s+ini)?|\s+file(?:\s+ini)?)(?:\s+ke)?\s+(pdf|docx)",
                r"(?i)ubah(?:\s+dokumen(?:\s+ini)?|\s+file(?:\s+ini)?)(?:\s+menjadi|\s+ke)?\s+(pdf|docx)",
                r"(?i)kirim(?:\s+dokumen(?:\s+ini)?|\s+file(?:\s+ini)?)(?:\s+sebagai|\s+dalam(?:\s+format)?)?\s+(pdf|docx)",
                r"(?i)download(?:\s+dokumen(?:\s+ini)?|\s+file(?:\s+ini)?)(?:\s+sebagai|\s+dalam(?:\s+format)?)?\s+(pdf|docx)"
            ],
            "help": [
                r"(?i)bantuan",
                r"(?i)tolong",
                r"(?i)help",
                r"(?i)cara(?:\s+pakai|menggunakan)",
                r"(?i)how(?:\s+to(?:\s+use)?)"
            ]
        }
    
    def process_message(self, message, user_id):
        """Proses pesan dan ekstrak intent, entities, dan context"""
        logger.info(f"Processing message from {user_id}: {message}")
        
        # Default values
        intent = "unknown"
        entities = {}
        context = self.get_context(user_id)
        
        # Cek setiap intent pattern
        for intent_name, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message)
                if match:
                    intent = intent_name
                    
                    # Ekstrak entity berdasarkan intent
                    if intent == "create_document":
                        if match.group(1):
                            entities["document_title"] = match.group(1).strip() 
                        if "pdf" in message.lower():
                            entities["document_type"] = "pdf"
                        else:
                            entities["document_type"] = "docx"
                    
                    elif intent == "add_text":
                        if match.group(1):
                            entities["section"] = match.group(1).strip().lower()
                        # Ekstrak konten setelah ":"
                        content_match = re.search(r"(?::|^)(.+)$", message)
                        if content_match:
                            entities["content"] = content_match.group(1).strip()
                        else:
                            entities["content"] = message
                    
                    elif intent == "edit_text":
                        if match.group(1):
                            entities["old_text"] = match.group(1).strip()
                        if match.group(2):
                            entities["new_text"] = match.group(2).strip()
                        if len(match.groups()) > 2 and match.group(3):
                            entities["section"] = match.group(3).strip().lower()
                    
                    elif intent == "export_document":
                        if match.group(1):
                            entities["format"] = match.group(1).strip().lower()
                    
                    # Begitu menemukan match, hentikan pencarian
                    break
            
            # Jika sudah menemukan intent, hentikan iterasi
            if intent != "unknown":
                break
        
        # Jika intent masih tidak diketahui tapi ada dokumen aktif,
        # anggap sebagai "add_text" ke dokumen
        if intent == "unknown" and context.get("current_document"):
            intent = "add_text"
            entities["content"] = message
        
        # Update last activity
        self.update_context(user_id, {"last_activity": datetime.now().isoformat()})
        
        logger.info(f"Detected intent: {intent} with entities: {entities}")
        return intent, entities, context
    
    def update_context(self, user_id, context_updates):
        """Update konteks percakapan user"""
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {}
        
        self.user_contexts[user_id].update(context_updates)
        logger.debug(f"Updated context for {user_id}: {self.user_contexts[user_id]}")
    
    def get_context(self, user_id):
        """Dapatkan konteks percakapan user saat ini"""
        return self.user_contexts.get(user_id, {})
    
    def clear_context(self, user_id):
        """Hapus konteks percakapan user"""
        if user_id in self.user_contexts:
            del self.user_contexts[user_id]
            logger.debug(f"Cleared context for {user_id}")
