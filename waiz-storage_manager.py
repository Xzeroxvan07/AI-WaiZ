# Modul untuk mengelola penyimpanan dokumen dan sesi
import os
import json
import logging
import shutil
import uuid
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class StorageManager:
    def __init__(self, storage_path):
        """
        Inisialisasi Storage Manager
        
        Args:
            storage_path (str): Path direktori untuk menyimpan data sementara
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Directory untuk file dokumen
        self.documents_path = os.path.join(storage_path, "documents")
        os.makedirs(self.documents_path, exist_ok=True)
        
        # Directory untuk metadata session
        self.sessions_path = os.path.join(storage_path, "sessions")
        os.makedirs(self.sessions_path, exist_ok=True)
        
        logger.info(f"Storage Manager diinisialisasi di {storage_path}")

    def save_document(self, doc_id, file_path, metadata=None):
        """
        Simpan dokumen ke penyimpanan
        
        Args:
            doc_id (str): ID unik dokumen
            file_path (str): Path lokal ke file dokumen
            metadata (dict, optional): Metadata tambahan untuk dokumen
        
        Returns:
            str: Path ke file dokumen yang disimpan
        """
        # Buat direktori untuk dokumen jika belum ada
        doc_dir = os.path.join(self.documents_path, doc_id)
        os.makedirs(doc_dir, exist_ok=True)
        
        # Tentukan nama file dan path tujuan
        filename = os.path.basename(file_path)
        dest_path = os.path.join(doc_dir, filename)
        
        # Salin file ke direktori tujuan
        shutil.copy2(file_path, dest_path)
        
        # Simpan metadata jika disediakan
        if metadata:
            metadata_path = os.path.join(doc_dir, "metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Dokumen {doc_id} disimpan ke {dest_path}")
        return dest_path
    
    def get_document_path(self, doc_id, filename=None):
        """
        Dapatkan path ke dokumen yang disimpan
        
        Args:
            doc_id (str): ID dokumen
            filename (str, optional): Nama file spesifik untuk dicari
        
        Returns:
            str: Path ke dokumen atau None jika tidak ditemukan
        """
        doc_dir = os.path.join(self.documents_path, doc_id)
        
        if not os.path.exists(doc_dir):
            logger.warning(f"Direktori dokumen {doc_id} tidak ditemukan")
            return None
        
        if filename:
            file_path = os.path.join(doc_dir, filename)
            if os.path.exists(file_path):
                return file_path
            else:
                logger.warning(f"File {filename} tidak ditemukan di dokumen {doc_id}")
                return None
        else:
            # Jika nama file tidak ditentukan, cari file non-metadata pertama
            for file in os.listdir(doc_dir):
                if file != "metadata.json":
                    return os.path.join(doc_dir, file)
            
            logger.warning(f"Tidak ada file yang ditemukan di dokumen {doc_id}")
            return None
    
    def get_document_metadata(self, doc_id):
        """
        Dapatkan metadata dokumen
        
        Args:
            doc_id (str): ID dokumen
        
        Returns:
            dict: Metadata dokumen atau None jika tidak ditemukan
        """
        metadata_path = os.path.join(self.documents_path, doc_id, "metadata.json")
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error membaca metadata dokumen {doc_id}")
                return None
        else:
            logger.warning(f"Metadata untuk dokumen {doc_id} tidak ditemukan")
            return None
    
    def delete_document(self, doc_id):
        """
        Hapus dokumen dan semua file terkait
        
        Args:
            doc_id (str): ID dokumen
        
        Returns:
            bool: True jika berhasil dihapus, False jika tidak
        """
        doc_dir = os.path.join(self.documents_path, doc_id)
        
        if os.path.exists(doc_dir):
            try:
                shutil.rmtree(doc_dir)
                logger.info(f"Dokumen {doc_id} berhasil dihapus")
                return True
            except Exception as e:
                logger.error(f"Error menghapus dokumen {doc_id}: {str(e)}")
                return False
        else:
            logger.warning(f"Dokumen {doc_id} tidak ditemukan untuk dihapus")
            return False
    
    def save_session_data(self, user_id, data):
        """
        Simpan data sesi pengguna
        
        Args:
            user_id (str): ID pengguna WhatsApp
            data (dict): Data sesi untuk disimpan
        
        Returns:
            bool: True jika berhasil
        """
        # Tambahkan timestamp untuk TTL
        data['last_updated'] = datetime.now().timestamp()
        
        session_file = os.path.join(self.sessions_path, f"{user_id}.json")
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Data sesi untuk {user_id} berhasil disimpan")
            return True
        except Exception as e:
            logger.error(f"Error menyimpan data sesi untuk {user_id}: {str(e)}")
            return False
    
    def get_session_data(self, user_id):
        """
        Dapatkan data sesi pengguna
        
        Args:
            user_id (str): ID pengguna WhatsApp
        
        Returns:
            dict: Data sesi atau empty dict jika tidak ada
        """
        session_file = os.path.join(self.sessions_path, f"{user_id}.json")
        
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.debug(f"Data sesi untuk {user_id} berhasil dimuat")
                return data
            except Exception as e:
                logger.error(f"Error membaca data sesi untuk {user_id}: {str(e)}")
                return {}
        else:
            logger.debug(f"Tidak ada data sesi untuk {user_id}")
            return {}
    
    def clear_session_data(self, user_id):
        """
        Hapus data sesi pengguna
        
        Args:
            user_id (str): ID pengguna WhatsApp
        
        Returns:
            bool: True jika berhasil dihapus
        """
        session_file = os.path.join(self.sessions_path, f"{user_id}.json")
        
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
                logger.debug(f"Data sesi untuk {user_id} berhasil dihapus")
                return True
            except Exception as e:
                logger.error(f"Error menghapus data sesi untuk {user_id}: {str(e)}")
                return False
        else:
            logger.debug(f"Tidak ada data sesi untuk {user_id} yang perlu dihapus")
            return True
    
    def cleanup_expired_data(self, session_ttl=3600, document_ttl=86400):
        """
        Bersihkan data sesi dan dokumen yang sudah kadaluarsa
        
        Args:
            session_ttl (int): Time to live untuk sesi dalam detik (default: 1 jam)
            document_ttl (int): Time to live untuk dokumen dalam detik (default: 1 hari)
        
        Returns:
            tuple: (jumlah sesi dihapus, jumlah dokumen dihapus)
        """
        now = datetime.now().timestamp()
        sessions_deleted = 0
        documents_deleted = 0
        
        # Cleanup sesi
        for filename in os.listdir(self.sessions_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.sessions_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    last_updated = data.get('last_updated', 0)
                    if now - last_updated > session_ttl:
                        os.remove(file_path)
                        sessions_deleted += 1
                        logger.debug(f"Sesi kadaluarsa {filename} dihapus")
                except Exception as e:
                    logger.error(f"Error saat cleanup sesi {filename}: {str(e)}")
        
        # Cleanup dokumen
        for doc_id in os.listdir(self.documents_path):
            doc_dir = os.path.join(self.documents_path, doc_id)
            if os.path.isdir(doc_dir):
                metadata_path = os.path.join(doc_dir, "metadata.json")
                try:
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        created_at = metadata.get('created_at', 0)
                        if now - created_at > document_ttl:
                            shutil.rmtree(doc_dir)
                            documents_deleted += 1
                            logger.debug(f"Dokumen kadaluarsa {doc_id} dihapus")
                    else:
                        # Jika tidak ada metadata, gunakan waktu modifikasi dir
                        dir_mtime = os.path.getmtime(doc_dir)
                        if now - dir_mtime > document_ttl:
                            shutil.rmtree(doc_dir)
                            documents_deleted += 1
                            logger.debug(f"Dokumen kadaluarsa {doc_id} dihapus (berdasarkan mtime)")
                except Exception as e:
                    logger.error(f"Error saat cleanup dokumen {doc_id}: {str(e)}")
        
        logger.info(f"Cleanup: {sessions_deleted} sesi dan {documents_deleted} dokumen dihapus")
        return (sessions_deleted, documents_deleted)
