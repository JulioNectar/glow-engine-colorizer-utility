#!/usr/bin/env python3
import os
import shutil
import sys
from pathlib import Path
from PIL import Image
import colorsys
import math
from collections import Counter
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QSlider, QDoubleSpinBox,
                             QCheckBox, QFileDialog, QMessageBox, QGroupBox, QProgressBar,
                             QListWidget, QStackedWidget, QLineEdit, QColorDialog, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QDragEnterEvent, QDropEvent
import numpy as np

SUPPORTED = ['.png', '.jpg', '.jpeg']

class ColorOptionWidget(QWidget):
    colorSelected = pyqtSignal(str)

    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.color_label = QLabel()
        self.color_label.setFixedSize(30, 30)
        self.color_label.setStyleSheet(f"background-color: {self.color}; border: 1px solid #ccc;")

        self.select_btn = QPushButton(self.color)
        self.select_btn.clicked.connect(self.on_color_selected)

        layout.addWidget(self.color_label)
        layout.addWidget(self.select_btn)

    def on_color_selected(self):
        self.colorSelected.emit(self.color)

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
        """Extract the 3 most dominant colors from an image using k-means"""
        try:
            img = Image.open(image_path)
            img = img.resize((100, 100))  # Resize for faster processing
            img = img.convert('RGB')

            # Convert to numpy array
            arr = np.array(img)
            pixels = arr.reshape(-1, 3)

            # Use k-means to find dominant colors
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            kmeans.fit(pixels)

            # Get the top 3 colors by cluster size
            cluster_sizes = np.bincount(kmeans.labels_)
            top_clusters = np.argsort(cluster_sizes)[-3:][::-1]  # Top 3 clusters

            colors = []
            for cluster_idx in top_clusters:
                r, g, b = map(int, kmeans.cluster_centers_[cluster_idx])
                colors.append(f'#{r:02x}{g:02x}{b:02x}')

            return colors

        except Exception as e:
            print(f"Error extracting colors: {e}")
            return None

class ColorizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_path = Path("/Library/GlowThemes")
        self.current_theme = None
        self.extracted_colors = []
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Glow Engine Colorizer")
        self.setGeometry(100, 100, 500, 600)  # Ajuste nas coordenadas para melhor posicionamento

        # Widget central e layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)  # Espaçamento uniforme entre os grupos
        layout.setContentsMargins(20, 20, 20, 20)  # Margens consistentes

        # Theme selection
        theme_group = QGroupBox("Theme Selection")
        theme_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setSpacing(10)
        theme_layout.setContentsMargins(15, 20, 15, 15)

        theme_selection_layout = QHBoxLayout()
        theme_selection_layout.addWidget(QLabel("Select Theme:"))

        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumHeight(30)
        self.load_themes()
        theme_selection_layout.addWidget(self.theme_combo)
        theme_selection_layout.setStretch(1, 1)  # Combo box ocupa espaço extra

        theme_layout.addLayout(theme_selection_layout)

        self.create_new_checkbox = QCheckBox("Create new theme based on selected")
        self.create_new_checkbox.setChecked(True)
        theme_layout.addWidget(self.create_new_checkbox)

        layout.addWidget(theme_group)

        # Color selection
        color_group = QGroupBox("Color Selection")
        color_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        color_layout = QVBoxLayout(color_group)
        color_layout.setSpacing(12)
        color_layout.setContentsMargins(15, 20, 15, 15)

        self.drag_drop_label = DragDropLabel()
        self.drag_drop_label.setMinimumHeight(120)
        self.drag_drop_label.colorsExtracted.connect(self.on_colors_extracted)
        color_layout.addWidget(self.drag_drop_label)

        # Extracted colors grid
        self.colors_grid = QGridLayout()
        self.colors_grid.setSpacing(5)
        self.colors_widget = QWidget()
        self.colors_widget.setLayout(self.colors_grid)
        self.colors_widget.hide()
        color_layout.addWidget(self.colors_widget)

        # Manual color input
        manual_layout = QHBoxLayout()
        manual_layout.setSpacing(10)
        manual_layout.addWidget(QLabel("Or enter HEX color:"))

        self.color_input = QLineEdit("#FF4500")
        self.color_input.setMaximumWidth(100)
        self.color_input.textChanged.connect(self.on_color_changed)
        manual_layout.addWidget(self.color_input)

        self.color_picker_btn = QPushButton("Pick Color")
        self.color_picker_btn.setFixedWidth(100)
        self.color_picker_btn.clicked.connect(self.pick_color)
        manual_layout.addWidget(self.color_picker_btn)

        manual_layout.addStretch()  # Empurra elementos para a esquerda

        color_layout.addLayout(manual_layout)

        # Color preview
        self.color_preview = QLabel()
        self.color_preview.setFixedHeight(40)
        self.color_preview.setStyleSheet("""
            background-color: #FF4500;
            border: 1px solid #ccc;
            border-radius: 4px;
        """)
        color_layout.addWidget(self.color_preview)

        layout.addWidget(color_group)

        # Settings
        settings_group = QGroupBox("Settings")
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(12)
        settings_layout.setContentsMargins(15, 20, 15, 15)

        # Intensity
        intensity_layout = QHBoxLayout()
        intensity_layout.setSpacing(10)
        intensity_label = QLabel("Intensity:")
        intensity_label.setFixedWidth(80)  # Largura fixa para alinhamento
        intensity_layout.addWidget(intensity_label)

        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(0, 100)
        self.intensity_slider.setValue(50)
        self.intensity_slider.valueChanged.connect(self.on_slider_changed)
        intensity_layout.addWidget(self.intensity_slider)

        self.intensity_spin = QDoubleSpinBox()
        self.intensity_spin.setRange(0.0, 1.0)
        self.intensity_spin.setSingleStep(0.1)
        self.intensity_spin.setValue(0.5)
        self.intensity_spin.setFixedWidth(80)
        self.intensity_spin.valueChanged.connect(self.on_spin_changed)
        intensity_layout.addWidget(self.intensity_spin)

        settings_layout.addLayout(intensity_layout)

        # Tinting options
        options_layout = QVBoxLayout()
        options_layout.setSpacing(8)

        self.tint_checkboxes = QCheckBox("Tint CheckBox images")
        self.tint_checkboxes.setChecked(True)
        options_layout.addWidget(self.tint_checkboxes)

        self.tint_windowframes = QCheckBox("Tint WindowFrame images")
        self.tint_windowframes.setChecked(True)
        options_layout.addWidget(self.tint_windowframes)

        settings_layout.addLayout(options_layout)

        layout.addWidget(settings_group)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        layout.addWidget(self.progress_bar)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.process_btn = QPushButton("Process Theme")
        self.process_btn.setFixedHeight(40)
        self.process_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        self.process_btn.clicked.connect(self.process_theme)
        button_layout.addWidget(self.process_btn)

        self.restore_btn = QPushButton("Restore Backup")
        self.restore_btn.setFixedHeight(40)
        self.restore_btn.clicked.connect(self.restore_backup)
        button_layout.addWidget(self.restore_btn)

        layout.addLayout(button_layout)

        # Adicionar espaço flexível no final para melhor distribuição
        layout.addStretch(1)

    def load_themes(self):
        self.theme_combo.clear()
        if self.base_path.exists():
            folders = [f for f in os.listdir(self.base_path) if (self.base_path/f).is_dir()]
            for folder in folders:
                self.theme_combo.addItem(folder, str(self.base_path/folder))

    def on_colors_extracted(self, colors):
        self.extracted_colors = colors
        self.show_color_options(colors)

    def show_color_options(self, colors):
        # Clear existing color options
        for i in reversed(range(self.colors_grid.count())):
            self.colors_grid.itemAt(i).widget().setParent(None)

        # Add new color options
        for i, color in enumerate(colors):
            color_widget = ColorOptionWidget(color)
            color_widget.colorSelected.connect(self.on_color_selected)
            self.colors_grid.addWidget(color_widget, i // 3, i % 3)

        self.colors_widget.show()

    def on_color_selected(self, color):
        self.color_input.setText(color)
        self.update_color_preview(color)

    def on_color_changed(self, color):
        if color.startswith('#'):
            self.update_color_preview(color)

    def update_color_preview(self, color):
        self.color_preview.setStyleSheet(f"background-color: {color}; border: 1px solid #ccc;")

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            self.color_input.setText(hex_color)
            self.update_color_preview(hex_color)

    def on_slider_changed(self, value):
        self.intensity_spin.setValue(value / 100.0)

    def on_spin_changed(self, value):
        self.intensity_slider.setValue(int(value * 100))

    def get_selected_theme(self):
        return Path(self.theme_combo.currentData())

    def process_theme(self):
        try:
            input_dir = self.get_selected_theme()
            if not input_dir.exists():
                QMessageBox.warning(self, "Error", "Selected theme directory doesn't exist")
                return

            color = self.color_input.text().strip()
            if not color.startswith('#'):
                color = '#' + color

            intensity = self.intensity_spin.value()
            create_new = self.create_new_checkbox.isChecked()
            tint_checkboxes = self.tint_checkboxes.isChecked()
            tint_windowframes = self.tint_windowframes.isChecked()

            self.progress_bar.setValue(0)

            # Process the theme
            self.process_theme_files(input_dir, color, intensity, create_new, tint_checkboxes, tint_windowframes)

            QMessageBox.information(self, "Success", "Theme processing completed!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error processing theme: {str(e)}")

    def restore_backup(self):
        try:
            input_dir = self.get_selected_theme()
            self.restore_backup_files(input_dir)
            QMessageBox.information(self, "Success", "Backup restored successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error restoring backup: {str(e)}")

    def process_theme_files(self, input_dir, color, intensity, create_new, tint_checkboxes, tint_windowframes):
        """Process theme files with the given parameters"""
        try:
            folder_name = input_dir.name
            parent_folder = input_dir.parent

            if create_new:
                sanitized_color = color.replace('#','').upper()
                out_folder = parent_folder / f"{folder_name}-colorized#{sanitized_color}_{intensity}"
                out_folder.mkdir(exist_ok=True)

                # Create backup
                self.create_backup(input_dir)

                # Copy all items
                self.copy_all_items(input_dir, out_folder, tint_checkboxes, tint_windowframes)

                # Set output folder for processing
                process_folder = out_folder
            else:
                # When NOT creating new theme, ensure we have a backup
                backup_folder = input_dir / 'backup'
                if not backup_folder.exists():
                    # Create backup if it doesn't exist
                    self.create_backup(input_dir)
                else:
                    # Restore from backup first to ensure original files
                    self.restore_backup_files(input_dir)

                # Set output folder to original theme directory
                process_folder = input_dir

            # Get files to process
            files = self.get_top_level_files(process_folder, tint_checkboxes, tint_windowframes)

            if not files:
                QMessageBox.warning(self, "Warning", "No supported images found to process")
                return

            total_files = len(files)
            for i, file in enumerate(files):
                colorize(file, color, intensity, process_folder, input_dir)
                self.progress_bar.setValue(int((i + 1) / total_files * 100))

        except Exception as e:
            raise Exception(f"Error processing theme files: {str(e)}")

    def restore_backup_files(self, input_dir):
        """Restore backup files"""
        backup_folder = input_dir / 'backup'
        if not backup_folder.exists():
            raise Exception("No backup found")

        files = []
        for item in backup_folder.iterdir():
            if item.is_file() and item.suffix.lower() in SUPPORTED:
                files.append(item)

        for file in files:
            dest = input_dir / file.name
            shutil.copy2(file, dest)

    def create_backup(self, input_dir):
        """Create backup of all image files"""
        backup_folder = input_dir / 'backup'
        backup_folder.mkdir(exist_ok=True)

        all_image_files = self.get_all_image_files(input_dir)

        print(f"Creating backup of {len(all_image_files)} images...")

        backed_up_count = 0
        for file in all_image_files:
            dest = backup_folder / file.name
            if not dest.exists():
                shutil.copy2(file, dest)
                backed_up_count += 1
                print(f"Backed up: {file.name}")

        if backed_up_count == 0:
            print("Backup already exists and is up to date")
        else:
            print(f"Backup created with {backed_up_count} files")

    def get_all_image_files(self, directory):
        """Get all image files from directory"""
        files = []
        for item in directory.iterdir():
            if item.name == 'backup':
                continue
            if item.is_file() and item.suffix.lower() in SUPPORTED:
                files.append(item)
        return files

    def get_top_level_files(self, directory, tint_checkboxes=True, tint_windowframes=True):
        """Get files to process based on user preferences"""
        files = []
        for item in directory.iterdir():
            if item.name == 'backup':
                continue
            if item.is_file() and item.suffix.lower() in SUPPORTED:
                filename_lower = item.name.lower()
                if not tint_checkboxes and filename_lower.startswith('checkbox'):
                    continue
                if not tint_windowframes and (filename_lower.startswith('windowframe') or filename_lower.startswith('frame')):
                    continue
                files.append(item)
        return files

    def copy_all_items(self, src_dir, dest_dir, tint_checkboxes=True, tint_windowframes=True):
        """Copy all items with filtering"""
        for item in src_dir.iterdir():
            if item.name == 'backup':
                continue

            dest_path = dest_dir / item.name

            if item.is_file() and item.suffix.lower() in SUPPORTED:
                filename_lower = item.name.lower()
                should_skip = False

                if not tint_checkboxes and filename_lower.startswith('checkbox'):
                    should_skip = True
                if not tint_windowframes and (filename_lower.startswith('windowframe') or filename_lower.startswith('frame')):
                    should_skip = True

                if should_skip:
                    continue

            if item.is_file():
                shutil.copy2(item, dest_path)
                print(f"Copied: {item.name}")
            elif item.is_dir():
                shutil.copytree(item, dest_path, dirs_exist_ok=True)
                print(f"Copied directory: {item.name}")

# Utility functions
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    return tuple(int(hex_color[i:i+lv//3], 16) for i in range(0, lv, lv//3))

def is_dark_color(hex_color):
    """Check if a color is dark using luminance calculation"""
    r, g, b = hex_to_rgb(hex_color)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return luminance < 0.5

def is_white_pixel(r, g, b, threshold=245):  # Increased from 240 to 220
    """Check if pixel is white or almost white (all channels above threshold)"""
    return r >= threshold and g >= threshold and b >= threshold

def is_black_pixel(r, g, b, threshold=30):  # Increased from 15 to 35
    """Check if pixel is black or almost black (all channels below threshold)"""
    return r <= threshold and g <= threshold and b <= threshold

def colorize(file_path, color, intensity, out_folder, input_dir):
    img = Image.open(file_path).convert("RGBA")
    r_col, g_col, b_col = hex_to_rgb(color)
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue

            # Skip tinting for white, almost white, black, and almost black pixels
            if is_white_pixel(r, g, b) or is_black_pixel(r, g, b):
                continue  # Leave the pixel as-is (white, almost white, black, or almost black)

            # Tinting only for non-white/black pixels
            r_new = round(r*(1-intensity) + r_col*intensity)
            g_new = round(g*(1-intensity) + g_col*intensity)
            b_new = round(b*(1-intensity) + b_col*intensity)
            pixels[x, y] = (r_new, g_new, b_new, a)

    out_path = out_folder / file_path.name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)

def main():
    app = QApplication(sys.argv)
    window = ColorizerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()