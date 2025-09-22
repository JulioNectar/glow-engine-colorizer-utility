#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from core.colorizer_app import ColorizerApp

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    window = ColorizerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()