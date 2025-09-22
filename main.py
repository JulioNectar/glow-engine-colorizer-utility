#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from core.colorizer_app import ColorizerApp
import sys
import traceback

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions"""
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"Uncaught exception: {error_msg}")

    # Salvar em arquivo de log
    with open('error_log.txt', 'w') as f:
        f.write(error_msg)

    sys.exit(1)


sys.excepthook = handle_exception

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    window = ColorizerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()