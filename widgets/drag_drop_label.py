from PyQt5.QtWidgets import QLabel, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from pathlib import Path
from PIL import Image
from collections import Counter

class DragDropLabel(QLabel):
    colorsExtracted = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Drag & drop wallpaper here\nor click to browse")
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 10px;
                padding: 20px;
                background-color: #f8f9fa;
                color: #666;
            }
            QLabel:hover {
                border-color: #007bff;
                background-color: #e3f2fd;
            }
        """)
        self.setMinimumSize(200, 100)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.extract_colors_from_image(file_path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Wallpaper", "",
                "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)"
            )
            if file_path:
                self.extract_colors_from_image(file_path)

    def extract_colors_from_image(self, file_path):
        try:
            colors = self.extract_dominant_colors(file_path)
            if colors:
                self.colorsExtracted.emit(colors)
                self.setStyleSheet(f"""
                    QLabel {{
                        border: 2px solid #28a745;
                        border-radius: 10px;
                        padding: 20px;
                        background-color: #f8f9fa;
                        color: #666;
                        font-weight: bold;
                    }}
                """)
                self.setText("Colors extracted! Select one below")
            else:
                QMessageBox.warning(self, "Error", "Could not extract colors from image")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error processing image: {str(e)}")

    def extract_dominant_colors(self, image_path):
        """Extract the 5 most dominant colors from an image"""
        try:
            img = Image.open(image_path)
            img = img.resize((100, 100))
            img = img.convert('RGB')

            # Simple color extraction without sklearn
            pixels = img.getdata()
            color_counts = Counter(pixels)

            # Get top 5 colors
            top_colors = color_counts.most_common(5)

            colors = []
            for (r, g, b), _ in top_colors:
                colors.append(f'#{r:02x}{g:02x}{b:02x}')

            return colors[:5] if len(colors) >= 5 else colors

        except Exception as e:
            print(f"Error extracting colors: {e}")
            return None