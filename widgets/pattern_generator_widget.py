from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QSlider, QSpinBox, QGridLayout,
                             QGroupBox, QColorDialog, QFrame, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QColor
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import random
import math

class PatternGeneratorWidget(QWidget):
    patternGenerated = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.primary_color = QColor(0, 0, 0)  # Preto como cor padrão
        self.secondary_color = QColor(255, 255, 255)  # Branco como cor secundária padrão
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Pattern type selection
        pattern_group = QGroupBox("Pattern Configuration")
        pattern_layout = QGridLayout(pattern_group)

        pattern_layout.addWidget(QLabel("Pattern Type:"), 0, 0)
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems([
            "Gradient", "Checkerboard", "Stripes", "Dots",
            "Hexagonal", "Waves", "Noise", "Circles",
            "Diagonal Stripes", "Rays", "Squares", "Triangles"
        ])
        self.pattern_combo.currentTextChanged.connect(self.update_pattern_preview)
        pattern_layout.addWidget(self.pattern_combo, 0, 1)

        # Color selection
        pattern_layout.addWidget(QLabel("Primary Color:"), 1, 0)
        self.primary_color_btn = QPushButton()
        self.primary_color_btn.setFixedSize(30, 30)
        self.primary_color_btn.setStyleSheet(f"background-color: {self.primary_color.name()}; border: 1px solid #ccc;")
        self.primary_color_btn.clicked.connect(self.pick_primary_color)
        pattern_layout.addWidget(self.primary_color_btn, 1, 1)

        pattern_layout.addWidget(QLabel("Secondary Color:"), 2, 0)
        self.secondary_color_btn = QPushButton()
        self.secondary_color_btn.setFixedSize(30, 30)
        self.secondary_color_btn.setStyleSheet(f"background-color: {self.secondary_color.name()}; border: 1px solid #ccc;")
        self.secondary_color_btn.clicked.connect(self.pick_secondary_color)
        pattern_layout.addWidget(self.secondary_color_btn, 2, 1)

        # Pattern settings
        pattern_layout.addWidget(QLabel("Size:"), 3, 0)
        self.size_spin = QSlider(Qt.Horizontal)
        self.size_spin.setRange(5, 500)
        self.size_spin.setValue(50)
        self.size_spin.valueChanged.connect(self.update_pattern_preview)
        pattern_layout.addWidget(self.size_spin, 3, 1)

        pattern_layout.addWidget(QLabel("Density:"), 4, 0)
        self.density_slider = QSlider(Qt.Horizontal)
        self.density_slider.setRange(1, 20)
        self.density_slider.setValue(8)
        self.density_slider.valueChanged.connect(self.update_pattern_preview)
        pattern_layout.addWidget(self.density_slider, 4, 1)

        pattern_layout.addWidget(QLabel("Resolution:"), 5, 0)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["512x512", "1024x1024", "2048x2048", "4096x4096"])
        self.resolution_combo.setCurrentIndex(1)  # 1024x1024 padrão
        self.resolution_combo.currentTextChanged.connect(self.update_pattern_preview)
        pattern_layout.addWidget(self.resolution_combo, 5, 1)

        pattern_layout.addWidget(QLabel("Blur:"), 6, 0)
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(0, 10)
        self.blur_slider.setValue(0)
        self.blur_slider.valueChanged.connect(self.update_pattern_preview)
        pattern_layout.addWidget(self.blur_slider, 6, 1)

        layout.addWidget(pattern_group)


        # Pattern Application Filters
        filter_group = QGroupBox("Apply Pattern To")
        filter_layout = QGridLayout(filter_group)

        self.apply_mica_header = QCheckBox("Mica Header")
        self.apply_mica_header.setChecked(True)
        filter_layout.addWidget(self.apply_mica_header, 0, 0)

        self.apply_mica_sidebar = QCheckBox("Mica Sidebar")
        self.apply_mica_sidebar.setChecked(True)
        filter_layout.addWidget(self.apply_mica_sidebar, 0, 1)

        self.apply_mica_titlebar = QCheckBox("Mica Titlebar")
        self.apply_mica_titlebar.setChecked(True)
        filter_layout.addWidget(self.apply_mica_titlebar, 1, 0)

        self.apply_mica_menu = QCheckBox("Mica Menu")
        self.apply_mica_menu.setChecked(False)
        filter_layout.addWidget(self.apply_mica_menu, 1, 1)

        self.apply_mica_window_bg = QCheckBox("Mica Window BG")
        self.apply_mica_window_bg.setChecked(False)
        filter_layout.addWidget(self.apply_mica_window_bg, 2, 0)

        self.apply_all_mica = QCheckBox("All Mica Elements")
        self.apply_all_mica.setChecked(False)
        self.apply_all_mica.stateChanged.connect(self.toggle_all_mica)
        filter_layout.addWidget(self.apply_all_mica, 2, 1)

        layout.addWidget(filter_group)

        # Generate button
        self.generate_btn = QPushButton("Generate Pattern")
        self.generate_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 10px; }")
        self.generate_btn.clicked.connect(self.generate_pattern)
        layout.addWidget(self.generate_btn)

        # Preview
        preview_group = QGroupBox("Pattern Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_label = QLabel("Pattern Preview")
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFrameStyle(QFrame.Box)
        preview_layout.addWidget(self.preview_label)
        layout.addWidget(preview_group)

        # Generate initial preview
        QTimer.singleShot(100, self.update_pattern_preview)

    def pick_primary_color(self):
        color = QColorDialog.getColor(self.primary_color, self, "Select Primary Color")
        if color.isValid():
            self.primary_color = color
            self.primary_color_btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
            self.update_pattern_preview()

    def pick_secondary_color(self):
        color = QColorDialog.getColor(self.secondary_color, self, "Select Secondary Color")
        if color.isValid():
            self.secondary_color = color
            self.secondary_color_btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
            self.update_pattern_preview()

    def toggle_all_mica(self, state):
        """Toggle all Mica checkboxes"""
        checked = state == Qt.Checked
        self.apply_mica_header.setChecked(checked)
        self.apply_mica_sidebar.setChecked(checked)
        self.apply_mica_titlebar.setChecked(checked)
        self.apply_mica_menu.setChecked(checked)
        self.apply_mica_window_bg.setChecked(checked)

    def get_resolution(self):
        resolution = self.resolution_combo.currentText()
        if resolution == "512x512":
            return 512
        elif resolution == "1024x1024":
            return 1024
        elif resolution == "2048x2048":
            return 2048
        else:  # 4096x4096
            return 4096

    def update_pattern_preview(self):
        # Generate a smaller preview for performance
        pattern_path = self.create_pattern_image(preview=True)
        if pattern_path:
            pixmap = QPixmap(pattern_path)
            scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)

    def generate_pattern(self):
        pattern_path = self.create_pattern_image(preview=False)
        if pattern_path:
            self.patternGenerated.emit(pattern_path)
            self.update_pattern_preview()
            self.show_success_message("Pattern generated successfully!")

    def show_success_message(self, message):
        self.preview_label.setText(message)
        QTimer.singleShot(2000, self.update_pattern_preview)

    def create_pattern_image(self, preview=False):
        """Create a pattern image based on type and parameters"""
        try:
            pattern_type = self.pattern_combo.currentText()
            size = self.size_spin.value()
            density = self.density_slider.value() / 10.0  # Convert to float multiplier
            blur_amount = self.blur_slider.value()

            # Use smaller resolution for preview
            img_size = 300 if preview else self.get_resolution()

            # Convert Qt colors to RGB tuples
            primary_rgb = (self.primary_color.red(), self.primary_color.green(), self.primary_color.blue())
            secondary_rgb = (self.secondary_color.red(), self.secondary_color.green(), self.secondary_color.blue())

            img = Image.new('RGBA', (img_size, img_size), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)

            if pattern_type == "Gradient":
                for i in range(img_size):
                    # Interpolate between colors
                    ratio = i / img_size
                    r = int(primary_rgb[0] * (1 - ratio) + secondary_rgb[0] * ratio)
                    g = int(primary_rgb[1] * (1 - ratio) + secondary_rgb[1] * ratio)
                    b = int(primary_rgb[2] * (1 - ratio) + secondary_rgb[2] * ratio)
                    draw.rectangle([(0, i), (img_size, i+1)], fill=(r, g, b, 255))

            elif pattern_type == "Checkerboard":
                square_size = max(2, size // 2)
                for x in range(0, img_size, square_size):
                    for y in range(0, img_size, square_size):
                        color = primary_rgb if (x // square_size + y // square_size) % 2 == 0 else secondary_rgb
                        draw.rectangle([(x, y), (x+square_size, y+square_size)], fill=color + (255,))

            elif pattern_type == "Stripes":
                stripe_width = max(2, size // 2)
                for x in range(0, img_size, stripe_width * 2):
                    draw.rectangle([(x, 0), (x+stripe_width, img_size)], fill=primary_rgb + (255,))
                    draw.rectangle([(x+stripe_width, 0), (x+stripe_width*2, img_size)], fill=secondary_rgb + (255,))

            elif pattern_type == "Diagonal Stripes":
                stripe_width = max(2, size // 2)
                for i in range(-img_size, img_size, stripe_width * 2):
                    draw.polygon([(i, 0), (i+stripe_width, 0), (i+stripe_width+img_size, img_size), (i+img_size, img_size)],
                               fill=primary_rgb + (255,))
                    draw.polygon([(i+stripe_width, 0), (i+stripe_width*2, 0), (i+stripe_width*2+img_size, img_size), (i+stripe_width+img_size, img_size)],
                               fill=secondary_rgb + (255,))

            elif pattern_type == "Dots":
                spacing = max(5, size // density)
                radius = max(1, size // (4 * density))
                for x in range(radius, img_size, spacing):
                    for y in range(radius, img_size, spacing):
                        draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)],
                                   fill=primary_rgb + (255,))

            elif pattern_type == "Hexagonal":
                hex_size = max(5, size // density)
                for x in range(0, img_size, int(hex_size * 1.5)):
                    for y in range(0, img_size, int(hex_size * math.sqrt(3))):
                        # Draw hexagon
                        points = []
                        for i in range(6):
                            angle = math.pi / 3 * i
                            px = x + hex_size * math.cos(angle)
                            py = y + hex_size * math.sin(angle)
                            points.append((px, py))
                        draw.polygon(points, outline=primary_rgb + (255,), fill=secondary_rgb + (255,))

            elif pattern_type == "Waves":
                amplitude = size * 2
                frequency = density * 0.1
                for x in range(img_size):
                    y_offset = int(amplitude * math.sin(x * frequency))
                    for y in range(img_size):
                        if (y + y_offset) % (size * 2) < size:
                            img.putpixel((x, y), primary_rgb + (255,))
                        else:
                            img.putpixel((x, y), secondary_rgb + (255,))

            elif pattern_type == "Noise":
                for x in range(0, img_size, max(1, size // 10)):
                    for y in range(0, img_size, max(1, size // 10)):
                        if random.random() < density * 0.1:
                            draw.rectangle([(x, y), (x+max(1, size//20), y+max(1, size//20))],
                                         fill=primary_rgb + (255,))

            elif pattern_type == "Circles":
                center = img_size // 2
                max_radius = img_size // 2
                step = max(5, max_radius // (density * 4))
                for r in range(step, max_radius, step):
                    draw.ellipse([(center-r, center-r), (center+r, center+r)],
                               outline=primary_rgb + (255,), width=max(1, size//20))

            elif pattern_type == "Rays":
                center = img_size // 2
                num_rays = int(size * density)
                for i in range(num_rays):
                    angle = 2 * math.pi * i / num_rays
                    end_x = center + img_size * math.cos(angle)
                    end_y = center + img_size * math.sin(angle)
                    draw.line([(center, center), (end_x, end_y)], fill=primary_rgb + (255,), width=max(1, size//20))

            elif pattern_type == "Squares":
                square_size = max(2, size // density)
                for x in range(0, img_size, square_size):
                    for y in range(0, img_size, square_size):
                        if (x // square_size + y // square_size) % 2 == 0:
                            draw.rectangle([(x, y), (x+square_size, y+square_size)],
                                         fill=primary_rgb + (255,))
                        else:
                            draw.rectangle([(x, y), (x+square_size, y+square_size)],
                                         fill=secondary_rgb + (255,))

            elif pattern_type == "Triangles":
                triangle_size = max(5, size // density)
                for x in range(0, img_size, triangle_size):
                    for y in range(0, img_size, triangle_size):
                        if (x // triangle_size + y // triangle_size) % 2 == 0:
                            draw.polygon([(x, y), (x+triangle_size, y), (x, y+triangle_size)],
                                       fill=primary_rgb + (255,))
                        else:
                            draw.polygon([(x+triangle_size, y), (x, y+triangle_size), (x+triangle_size, y+triangle_size)],
                                       fill=secondary_rgb + (255,))

            # Apply blur if requested
            if blur_amount > 0:
                img = img.filter(ImageFilter.GaussianBlur(blur_amount))

            # Save pattern
            pattern_path = Path("temp_pattern.png")
            img.save(pattern_path, "PNG")
            return str(pattern_path)

        except Exception as e:
            print(f"Error generating pattern: {e}")
            return None