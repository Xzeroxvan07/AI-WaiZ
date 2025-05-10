# Modul untuk mengelola media dari WhatsApp
import os
import logging
import requests
import json
import uuid
import config
from datetime import datetime

logger = logging.getLogger(__name__)

class MediaHandler:
    def __init__(self, storage_manager):
        """
        Inisialisasi Media Handler
        
        Args:
            storage_manager: Instance dari StorageManager untuk menyimpan file
        """
        self.storage_manager = storage_manager
        self.upload_folder = config.UPLOAD_FOLDER
        self.processed_folder = config.PROCESSED_FOLDER
        
        # Pastikan direktori ada
        os.makedirs(self.upload_folder, exist_ok=True)
        os.makedirs(self.processed_folder, exist_ok=True)
        
        logger.info("Media Handler diinisialisasi")
    
    def download_media(self, media_id):
        """
        Download media dari WhatsApp API
        
        Args:
            media_id (str): ID media yang akan didownload
        
        Returns:
            str: Path ke file yang didownload atau None jika gagal
        """
        try:
            # Pertama, dapatkan URL media
            url = f"{config.WHATSAPP_API_URL.split('/messages')[0]}/media/{media_id}"
            headers = {
                "Authorization": f"Bearer {config.WHATSAPP_API_TOKEN}"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Gagal mendapatkan URL media: {response.status_code} - {response.text}")
                return None
            
            media_url = response.json().get('url')
            
            if not media_url:
                logger.error("URL media tidak ditemukan dalam respons")
                return None
            
            # Download media dari URL
            media_response = requests.get(media_url, headers=headers)
            
            if media_response.status_code != 200:
                logger.error(f"Gagal mendownload media: {media_response.status_code}")
                return None
            
            # Simpan file
            file_extension = self._get_file_extension(media_response.headers.get('Content-Type', ''))
            filename = f"{media_id}{file_extension}"
            file_path = os.path.join(self.upload_folder, filename)
            
            with open(file_path, 'wb') as f:
                f.write(media_response.content)
            
            logger.info(f"Media {media_id} berhasil didownload ke {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saat mendownload media {media_id}: {str(e)}")
            return None
    
    def _get_file_extension(self, content_type):
        """
        Dapatkan ekstensi file dari Content-Type
        
        Args:
            content_type (str): MIME type dari file
        
        Returns:
            str: Ekstensi file (termasuk titik)
        """
        content_type = content_type.lower()
        
        if content_type.startswith('image/'):
            if 'jpeg' in content_type or 'jpg' in content_type:
                return '.jpg'
            elif 'png' in content_type:
                return '.png'
            elif 'gif' in content_type:
                return '.gif'
            elif 'webp' in content_type:
                return '.webp'
            else:
                return '.img'
        
        elif content_type.startswith('audio/'):
            if 'mpeg' in content_type or 'mp3' in content_type:
                return '.mp3'
            elif 'ogg' in content_type:
                return '.ogg'
            elif 'wav' in content_type:
                return '.wav'
            else:
                return '.audio'
        
        elif content_type.startswith('video/'):
            if 'mp4' in content_type:
                return '.mp4'
            else:
                return '.video'
        
        elif content_type == 'application/pdf':
            return '.pdf'
        
        elif 'msword' in content_type:
            return '.doc'
        
        elif 'vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
            return '.docx'
        
        elif 'vnd.ms-excel' in content_type:
            return '.xls'
        
        elif 'vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type:
            return '.xlsx'
        
        elif 'vnd.ms-powerpoint' in content_type:
            return '.ppt'
        
        elif 'vnd.openxmlformats-officedocument.presentationml.presentation' in content_type:
            return '.pptx'
        
        elif 'text/plain' in content_type:
            return '.txt'
        
        else:
            return '.bin'
    
    def process_document(self, file_path, user_id):
        """
        Proses dokumen yang diterima
        
        Args:
            file_path (str): Path ke file dokumen
            user_id (str): ID pengguna
        
        Returns:
            str: Document ID yang dibuat
        """
        try:
            # Ekstrak nama file dan ekstensi
            filename = os.path.basename(file_path)
            file_extension = os.path.splitext(filename)[1].lower()
            
            # Buat ID dokumen
            doc_id = str(uuid.uuid4())
            
            # Definisikan metadata
            metadata = {
                "original_filename": filename,
                "user_id": user_id,
                "created_at": datetime.now().timestamp(),
                "file_extension": file_extension,
                "file_size": os.path.getsize(file_path)
            }
            
            # Simpan dokumen menggunakan storage manager
            stored_path = self.storage_manager.save_document(doc_id, file_path, metadata)
            
            if stored_path:
                logger.info(f"Dokumen {filename} berhasil diproses sebagai {doc_id}")
                return doc_id
            else:
                logger.error(f"Gagal menyimpan dokumen {filename}")
                return None
                
        except Exception as e:
            logger.error(f"Error saat memproses dokumen: {str(e)}")
            return None
    
    def send_document(self, file_path, recipient_id):
        """
        Kirim dokumen ke pengguna melalui WhatsApp API
        
        Args:
            file_path (str): Path ke file dokumen
            recipient_id (str): ID penerima (nomor WhatsApp)
        
        Returns:
            bool: True jika berhasil dikirim, False jika gagal
        """
        try:
            # Upload dokumen ke WhatsApp servers terlebih dahulu
            upload_url = f"{config.WHATSAPP_API_URL.split('/messages')[0]}/media"
            headers = {
                "Authorization": f"Bearer {config.WHATSAPP_API_TOKEN}"
            }
            
            # Tentukan tipe file
            filename = os.path.basename(file_path)
            file_extension = os.path.splitext(filename)[1].lower()
            
            if file_extension == '.pdf':
                media_type = 'application/pdf'
            elif file_extension in ['.doc', '.docx']:
                media_type = 'application/msword'
            elif file_extension in ['.txt']:
                media_type = 'text/plain'
            else:
                # Default ke binary
                media_type = 'application/octet-stream'
            
            # Buka file untuk upload
            with open(file_path, 'rb') as f:
                files = {
                    'file': (filename, f, media_type)
                }
                
                # Tambahkan messaging_product
                data = {
                    'messaging_product': 'whatsapp'
                }
                
                # Upload file
                response = requests.post(upload_url, headers=headers, data=data, files=files)
            
            if response.status_code != 200:
                logger.error(f"Gagal mengupload file: {response.status_code} - {response.text}")
                return False
            
            # Dapatkan media ID
            media_id = response.json().get('id')
            
            if not media_id:
                logger.error("Media ID tidak ditemukan dalam respons upload")
                return False
            
            # Kirim dokumen menggunakan media ID
            send_url = f"{config.WHATSAPP_API_URL}"
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient_id,
                "type": "document",
                "document": {
                    "id": media_id,
                    "filename": filename,
                    "caption": f"Dokumen Anda: {filename}"
                }
            }
            
            # Kirim pesan dokumen
            send_response = requests.post(
                send_url, 
                headers={
                    "Authorization": f"Bearer {config.WHATSAPP_API_TOKEN}",
                    "Content-Type": "application/json"
                },
                data=json.dumps(payload)
            )
            
            if send_response.status_code == 200:
                logger.info(f"Dokumen {filename} berhasil dikirim ke {recipient_id}")
                return True
            else:
                logger.error(f"Gagal mengirim dokumen: {send_response.status_code} - {send_response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error saat mengirim dokumen: {str(e)}")
            return False
