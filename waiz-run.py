# run.py - Script untuk menjalankan aplikasi WhatsApp Document Assistant

import argparse
import logging
import sys
from dotenv import load_dotenv # Import load_dotenv untuk memuat .env di entry point
import os

# Muat variabel lingkungan dari file .env di awal script
# Ini memastikan variabel tersedia saat config.py diimport oleh app.py
load_dotenv()

# Import aplikasi Flask dari app.py
# Pastikan nama file Anda benar-benar app.py dan di direktori yang sama
try:
    from app import app
    from app import logger as app_logger # Ambil logger yang sudah dikonfigurasi di app.py
    from app import storage_manager # Jika perlu akses storage_manager untuk task cleanup dll.
    app_logger.info("Successfully imported Flask app from app.py")
except ImportError:
    logging.error("ERROR: Could not import Flask app from app.py.")
    logging.error("Please make sure app.py exists in the same directory and has 'app = Flask(__name__)' defined.")
    sys.exit(1)
except Exception as e:
    logging.error(f"An unexpected error occurred during app import: {e}", exc_info=True)
    sys.exit(1)

# Anda bisa menambahkan konfigurasi logging tambahan di sini jika run.py butuh log terpisah
# Tapi biasanya logging dikonfigurasi di app.py atau modul konfigurasi
# Untuk sederhana, kita gunakan logger dari app.py

def main():
    """Fungsi utama untuk memparsing argumen dan menjalankan aplikasi Flask."""
    parser = argparse.ArgumentParser(
        description="Run WhatsApp Document Assistant Flask App"
    )
    parser.add_argument(
        '--host',
        type=str,
        default=os.getenv("HOST", "0.0.0.0"), # Ambil default dari env atau 0.0.0.0
        help='Host IP address to run the Flask app on.'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=int(os.getenv("PORT", 5000)), # Ambil default dari env atau 5000
        help='Port number to run the Flask app on.'
    )
    parser.add_argument(
        '--debug',
        action='store_true', # Default False jika tidak ada
        help='Enable Flask debug mode.'
    )
    # Anda bisa menambahkan argumen lain, misalnya untuk menjalankan task cleanup terpisah

    args = parser.parse_args()

    # Gunakan logger dari app.py untuk konsistensi
    app_logger.info(f"Starting Flask application on {args.host}:{args.port} with DEBUG={args.debug}")
    app_logger.info("Press Ctrl+C to shut down.")

    # Jalankan aplikasi Flask
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    except Exception as e:
        app_logger.error(f"Failed to run Flask application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
