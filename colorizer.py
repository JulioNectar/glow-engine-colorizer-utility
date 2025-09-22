#!/usr/bin/env python3
import os
import shutil
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw
import colorsys
import math
from collections import Counter
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QSlider, QDoubleSpinBox,
                             QCheckBox, QFileDialog, QMessageBox, QGroupBox, QProgressBar,
                             QListWidget, QStackedWidget, QLineEdit, QColorDialog, QGridLayout,
                             QTabWidget, QSpinBox, QRadioButton, QButtonGroup, QTextEdit,
                             QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QColor, QDragEnterEvent, QDropEvent, QPalette
import numpy as np

SUPPORTED = ['.png', '.jpg', '.jpeg']
CONFIG_FILE = 'colorizer_config.json'

class ColorProfileWidget(QWidget):
    profileSelected = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.profiles = {
            "Ocean Blue": {"color": "#0066CC", "intensity": 0.6, "saturation": 1.2, "brightness": 1.0},
            "Forest Green": {"color": "#228B22", "intensity": 0.5, "saturation": 1.1, "brightness": 0.95},
            "Sunset Orange": {"color": "#FF6B35", "intensity": 0.7, "saturation": 1.3, "brightness": 1.1},
            "Royal Purple": {"color": "#663399", "intensity": 0.6, "saturation": 1.15, "brightness": 0.9},
            "Cherry Red": {"color": "#DC143C", "intensity": 0.65, "saturation": 1.25, "brightness": 1.05},
            "Golden Yellow": {"color": "#FFD700", "intensity": 0.55, "saturation": 1.2, "brightness": 1.15},
            "Deep Pink": {"color": "#FF1493", "intensity": 0.6, "saturation": 1.3, "brightness": 1.0},
            "Teal": {"color": "#008080", "intensity": 0.5, "saturation": 1.1, "brightness": 0.95},
            "Slate Gray": {"color": "#708090", "intensity": 0.4, "saturation": 0.8, "brightness": 0.9},
            "Coral": {"color": "#FF7F50", "intensity": 0.6, "saturation": 1.2, "brightness": 1.1}
        }
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Profile selector
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Select Profile:"))

        self.profile_combo = QComboBox()
        self.profile_combo.addItem("Custom")
        for name in self.profiles.keys():
            self.profile_combo.addItem(name)
        self.profile_combo.currentTextChanged.connect(self.on_profile_changed)
        profile_layout.addWidget(self.profile_combo)

        self.apply_btn = QPushButton("Apply Profile")
        self.apply_btn.clicked.connect(self.apply_profile)
        profile_layout.addWidget(self.apply_btn)

        layout.addLayout(profile_layout)

        # Profile preview
        self.preview_label = QLabel("Profile Preview")
        self.preview_label.setMinimumHeight(40)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        layout.addWidget(self.preview_label)

    def on_profile_changed(self, profile_name):
        if profile_name in self.profiles:
            profile = self.profiles[profile_name]
            self.preview_label.setStyleSheet(
                f"background-color: {profile['color']}; color: white; "
                f"border: 2px solid #333; padding: 5px; font-weight: bold;"
            )
            self.preview_label.setText(f"{profile_name}")

    def apply_profile(self):
        current = self.profile_combo.currentText()
        if current in self.profiles:
            self.profileSelected.emit(self.profiles[current])

class PatternGeneratorWidget(QWidget):
    patternGenerated = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Pattern type selection
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel("Pattern Type:"))

        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems([
            "Gradient", "Checkerboard", "Stripes", "Dots",
            "Hexagonal", "Waves", "Noise", "Circles"
        ])
        pattern_layout.addWidget(self.pattern_combo)

        layout.addLayout(pattern_layout)

        # Pattern settings
        settings_layout = QGridLayout()

        settings_layout.addWidget(QLabel("Size:"), 0, 0)
        self.size_spin = QSpinBox()
        self.size_spin.setRange(10, 200)
        self.size_spin.setValue(50)
        settings_layout.addWidget(self.size_spin, 0, 1)

        settings_layout.addWidget(QLabel("Density:"), 1, 0)
        self.density_slider = QSlider(Qt.Horizontal)
        self.density_slider.setRange(1, 10)
        self.density_slider.setValue(5)
        settings_layout.addWidget(self.density_slider, 1, 1)

        layout.addLayout(settings_layout)

        # Generate button
        self.generate_btn = QPushButton("Generate Pattern")
        self.generate_btn.clicked.connect(self.generate_pattern)
        layout.addWidget(self.generate_btn)

        # Preview
        self.preview_label = QLabel("Pattern Preview")
        self.preview_label.setMinimumHeight(100)
        self.preview_label.setStyleSheet("border: 1px solid #ccc;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label)

    def generate_pattern(self):
        pattern_type = self.pattern_combo.currentText()
        size = self.size_spin.value()
        density = self.density_slider.value()

        # Generate pattern image
        pattern_path = self.create_pattern_image(pattern_type, size, density)
        if pattern_path:
            self.patternGenerated.emit(pattern_path)

            # Show preview
            pixmap = QPixmap(pattern_path)
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)

    def create_pattern_image(self, pattern_type, size, density):
        """Create a pattern image based on type and parameters"""
        try:
            img_size = 512
            img = Image.new('RGBA', (img_size, img_size), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)

            if pattern_type == "Gradient":
                for i in range(img_size):
                    color = int(255 * (i / img_size))
                    draw.rectangle([(0, i), (img_size, i+1)], fill=(color, color, color, 255))

            elif pattern_type == "Checkerboard":
                square_size = size
                for x in range(0, img_size, square_size):
                    for y in range(0, img_size, square_size):
                        if (x // square_size + y // square_size) % 2 == 0:
                            draw.rectangle([(x, y), (x+square_size, y+square_size)],
                                         fill=(0, 0, 0, 255))

            elif pattern_type == "Stripes":
                stripe_width = size
                for x in range(0, img_size, stripe_width * 2):
                    draw.rectangle([(x, 0), (x+stripe_width, img_size)], fill=(0, 0, 0, 255))

            elif pattern_type == "Dots":
                spacing = size
                radius = size // (2 * density)
                for x in range(radius, img_size, spacing):
                    for y in range(radius, img_size, spacing):
                        draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)],
                                   fill=(0, 0, 0, 255))

            elif pattern_type == "Circles":
                center = img_size // 2
                max_radius = img_size // 2
                step = max_radius // (density * 2)
                for r in range(step, max_radius, step):
                    draw.ellipse([(center-r, center-r), (center+r, center+r)],
                               outline=(0, 0, 0, 255), width=2)

            # Save pattern
            pattern_path = Path("temp_pattern.png")
            img.save(pattern_path)
            return str(pattern_path)

        except Exception as e:
            print(f"Error generating pattern: {e}")
            return None

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

class ColorizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_path = Path("/Library/GlowThemes")
        self.current_theme = None
        self.extracted_colors = []
        self.current_config = {}
        self.load_config()
        self.setup_ui()

    def load_config(self):
        """Load saved configuration"""
        try:
            config_path = Path(CONFIG_FILE)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.current_config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            self.current_config = {}

    def save_config(self, theme_path, color, intensity, saturation, brightness):
        """Save current configuration"""
        try:
            self.current_config[str(theme_path)] = {
                "color": color,
                "intensity": intensity,
                "saturation": saturation,
                "brightness": brightness,
                "timestamp": str(Path(theme_path).stat().st_mtime) if Path(theme_path).exists() else ""
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.current_config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def setup_ui(self):
        self.setWindowTitle("Glow Engine Colorizer - Enhanced")
        self.setGeometry(100, 100, 700, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Create tab widget for organized interface
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Tab 1: Main Controls
        main_tab = QWidget()
        self.setup_main_tab(main_tab)
        self.tab_widget.addTab(main_tab, "Main Controls")

        # Tab 2: Color Profiles
        profiles_tab = QWidget()
        self.setup_profiles_tab(profiles_tab)
        self.tab_widget.addTab(profiles_tab, "Color Profiles")

        # Tab 3: Pattern Generator
        patterns_tab = QWidget()
        self.setup_patterns_tab(patterns_tab)
        self.tab_widget.addTab(patterns_tab, "Pattern Generator")

        # Tab 4: Advanced Settings
        advanced_tab = QWidget()
        self.setup_advanced_tab(advanced_tab)
        self.tab_widget.addTab(advanced_tab, "Advanced")

        # Progress bar (outside tabs)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        main_layout.addWidget(self.progress_bar)

        # Action buttons (outside tabs)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.process_btn = QPushButton("Process Theme")
        self.process_btn.setFixedHeight(40)
        self.process_btn.setStyleSheet("QPushButton { font-weight: bold; background-color: #007bff; color: white; }")
        self.process_btn.clicked.connect(self.process_theme)
        button_layout.addWidget(self.process_btn)

        self.restore_btn = QPushButton("Restore Backup")
        self.restore_btn.setFixedHeight(40)
        self.restore_btn.clicked.connect(self.restore_backup)
        button_layout.addWidget(self.restore_btn)

        self.load_last_btn = QPushButton("Load Last Config")
        self.load_last_btn.setFixedHeight(40)
        self.load_last_btn.clicked.connect(self.load_last_config)
        button_layout.addWidget(self.load_last_btn)

        main_layout.addLayout(button_layout)

    def setup_main_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setSpacing(15)

        # Theme selection
        theme_group = QGroupBox("Theme Selection")
        theme_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        theme_layout = QVBoxLayout(theme_group)

        theme_selection_layout = QHBoxLayout()
        theme_selection_layout.addWidget(QLabel("Select Theme:"))

        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumHeight(30)
        self.load_themes()
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_selection_layout.addWidget(self.theme_combo)

        theme_layout.addLayout(theme_selection_layout)

        self.create_new_checkbox = QCheckBox("Create new theme based on selected")
        self.create_new_checkbox.setChecked(True)
        theme_layout.addWidget(self.create_new_checkbox)

        # Current theme info
        self.theme_info_label = QLabel("No theme selected")
        self.theme_info_label.setStyleSheet("color: #666; padding: 5px;")
        theme_layout.addWidget(self.theme_info_label)

        layout.addWidget(theme_group)

        # Color selection
        color_group = QGroupBox("Color Selection")
        color_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        color_layout = QVBoxLayout(color_group)

        self.drag_drop_label = DragDropLabel()
        self.drag_drop_label.setMinimumHeight(120)
        self.drag_drop_label.colorsExtracted.connect(self.on_colors_extracted)
        color_layout.addWidget(self.drag_drop_label)

        # Extracted colors grid
        self.colors_grid = QGridLayout()
        self.colors_widget = QWidget()
        self.colors_widget.setLayout(self.colors_grid)
        self.colors_widget.hide()
        color_layout.addWidget(self.colors_widget)

        # Manual color input
        manual_layout = QHBoxLayout()
        manual_layout.addWidget(QLabel("Or enter HEX color:"))

        self.color_input = QLineEdit("#FF4500")
        self.color_input.setMaximumWidth(100)
        self.color_input.textChanged.connect(self.on_color_changed)
        manual_layout.addWidget(self.color_input)

        self.color_picker_btn = QPushButton("Pick Color")
        self.color_picker_btn.clicked.connect(self.pick_color)
        manual_layout.addWidget(self.color_picker_btn)

        manual_layout.addStretch()
        color_layout.addLayout(manual_layout)

        # Color preview
        self.color_preview = QLabel()
        self.color_preview.setFixedHeight(40)
        self.color_preview.setStyleSheet("background-color: #FF4500; border: 1px solid #ccc;")
        color_layout.addWidget(self.color_preview)

        layout.addWidget(color_group)

        # Color adjustments
        adjustments_group = QGroupBox("Color Adjustments")
        adjustments_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        adjustments_layout = QVBoxLayout(adjustments_group)

        # Intensity
        intensity_layout = QHBoxLayout()
        intensity_layout.addWidget(QLabel("Intensity:"))
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(0, 100)
        self.intensity_slider.setValue(50)
        self.intensity_slider.valueChanged.connect(self.on_intensity_changed)
        intensity_layout.addWidget(self.intensity_slider)
        self.intensity_spin = QDoubleSpinBox()
        self.intensity_spin.setRange(0.0, 1.0)
        self.intensity_spin.setSingleStep(0.1)
        self.intensity_spin.setValue(0.5)
        self.intensity_spin.valueChanged.connect(self.on_intensity_spin_changed)
        intensity_layout.addWidget(self.intensity_spin)
        adjustments_layout.addLayout(intensity_layout)

        # Saturation
        saturation_layout = QHBoxLayout()
        saturation_layout.addWidget(QLabel("Saturation:"))
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(0, 200)
        self.saturation_slider.setValue(100)
        saturation_layout.addWidget(self.saturation_slider)
        self.saturation_label = QLabel("1.0x")
        saturation_layout.addWidget(self.saturation_label)
        self.saturation_slider.valueChanged.connect(lambda v: self.saturation_label.setText(f"{v/100:.1f}x"))
        adjustments_layout.addLayout(saturation_layout)

        # Brightness
        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(QLabel("Brightness:"))
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(50, 150)
        self.brightness_slider.setValue(100)
        brightness_layout.addWidget(self.brightness_slider)
        self.brightness_label = QLabel("1.0x")
        brightness_layout.addWidget(self.brightness_label)
        self.brightness_slider.valueChanged.connect(lambda v: self.brightness_label.setText(f"{v/100:.1f}x"))
        adjustments_layout.addLayout(brightness_layout)

        layout.addWidget(adjustments_group)

    def setup_profiles_tab(self, parent):
        layout = QVBoxLayout(parent)

        self.profile_widget = ColorProfileWidget()
        self.profile_widget.profileSelected.connect(self.apply_profile)
        layout.addWidget(self.profile_widget)

        # Custom profile creator
        custom_group = QGroupBox("Create Custom Profile")
        custom_layout = QVBoxLayout(custom_group)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Profile Name:"))
        self.profile_name_input = QLineEdit()
        name_layout.addWidget(self.profile_name_input)
        custom_layout.addLayout(name_layout)

        self.save_profile_btn = QPushButton("Save Current as Profile")
        self.save_profile_btn.clicked.connect(self.save_custom_profile)
        custom_layout.addWidget(self.save_profile_btn)

        layout.addWidget(custom_group)
        layout.addStretch()

    def setup_patterns_tab(self, parent):
        layout = QVBoxLayout(parent)

        self.pattern_widget = PatternGeneratorWidget()
        self.pattern_widget.patternGenerated.connect(self.on_pattern_generated)
        layout.addWidget(self.pattern_widget)

        # Pattern application options
        apply_group = QGroupBox("Pattern Application")
        apply_layout = QVBoxLayout(apply_group)

        self.pattern_blend_slider = QSlider(Qt.Horizontal)
        self.pattern_blend_slider.setRange(0, 100)
        self.pattern_blend_slider.setValue(50)
        blend_layout = QHBoxLayout()
        blend_layout.addWidget(QLabel("Blend Amount:"))
        blend_layout.addWidget(self.pattern_blend_slider)
        self.blend_label = QLabel("50%")
        blend_layout.addWidget(self.blend_label)
        self.pattern_blend_slider.valueChanged.connect(lambda v: self.blend_label.setText(f"{v}%"))
        apply_layout.addLayout(blend_layout)

        self.apply_pattern_checkbox = QCheckBox("Apply Pattern to Theme")
        apply_layout.addWidget(self.apply_pattern_checkbox)

        layout.addWidget(apply_group)
        layout.addStretch()

    def setup_advanced_tab(self, parent):
        layout = QVBoxLayout(parent)

        # Processing options
        processing_group = QGroupBox("Processing Options")
        processing_layout = QVBoxLayout(processing_group)

        self.preserve_transparency = QCheckBox("Preserve Original Transparency")
        self.preserve_transparency.setChecked(True)
        processing_layout.addWidget(self.preserve_transparency)

        self.tint_checkboxes = QCheckBox("Tint CheckBox images")
        self.tint_checkboxes.setChecked(True)
        processing_layout.addWidget(self.tint_checkboxes)

        self.tint_windowframes = QCheckBox("Tint WindowFrame images")
        self.tint_windowframes.setChecked(True)
        processing_layout.addWidget(self.tint_windowframes)

        self.preserve_whites = QCheckBox("Preserve Pure Whites")
        self.preserve_whites.setChecked(True)
        processing_layout.addWidget(self.preserve_whites)

        self.preserve_blacks = QCheckBox("Preserve Pure Blacks")
        self.preserve_blacks.setChecked(True)
        processing_layout.addWidget(self.preserve_blacks)

        layout.addWidget(processing_group)

        # Threshold settings
        threshold_group = QGroupBox("Color Thresholds")
        threshold_layout = QVBoxLayout(threshold_group)

        white_layout = QHBoxLayout()
        white_layout.addWidget(QLabel("White Threshold:"))
        self.white_threshold = QSpinBox()
        self.white_threshold.setRange(200, 255)
        self.white_threshold.setValue(245)
        white_layout.addWidget(self.white_threshold)
        threshold_layout.addLayout(white_layout)

        black_layout = QHBoxLayout()
        black_layout.addWidget(QLabel("Black Threshold:"))
        self.black_threshold = QSpinBox()
        self.black_threshold.setRange(0, 100)
        self.black_threshold.setValue(30)
        black_layout.addWidget(self.black_threshold)
        threshold_layout.addLayout(black_layout)

        layout.addWidget(threshold_group)

        # History
        history_group = QGroupBox("Theme History")
        history_layout = QVBoxLayout(history_group)

        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(150)
        self.update_history_list()
        history_layout.addWidget(self.history_list)

        layout.addWidget(history_group)
        layout.addStretch()

    def on_theme_changed(self, theme_name):
        """Handle theme selection change"""
        if theme_name:
            theme_path = self.get_selected_theme()
            if str(theme_path) in self.current_config:
                config = self.current_config[str(theme_path)]
                self.theme_info_label.setText(
                    f"Last used: {config['color']} at {config['intensity']:.1f} intensity"
                )
            else:
                self.theme_info_label.setText("No previous configuration found")

    def load_last_config(self):
        """Load the last used configuration for current theme"""
        theme_path = self.get_selected_theme()
        if str(theme_path) in self.current_config:
            config = self.current_config[str(theme_path)]
            self.color_input.setText(config['color'])
            self.intensity_spin.setValue(config['intensity'])
            self.saturation_slider.setValue(int(config.get('saturation', 1.0) * 100))
            self.brightness_slider.setValue(int(config.get('brightness', 1.0) * 100))
            QMessageBox.information(self, "Config Loaded",
                                   f"Loaded configuration for {theme_path.name}")

    def update_history_list(self):
        """Update the history list widget"""
        self.history_list.clear()
        for theme_path, config in self.current_config.items():
            theme_name = Path(theme_path).name
            self.history_list.addItem(
                f"{theme_name}: {config['color']} ({config['intensity']:.1f})"
            )

    def apply_profile(self, profile):
        """Apply a color profile"""
        self.color_input.setText(profile['color'])
        self.intensity_spin.setValue(profile['intensity'])
        self.saturation_slider.setValue(int(profile['saturation'] * 100))
        self.brightness_slider.setValue(int(profile['brightness'] * 100))

    def save_custom_profile(self):
        """Save current settings as custom profile"""
        name = self.profile_name_input.text()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a profile name")
            return

        profile = {
            "color": self.color_input.text(),
            "intensity": self.intensity_spin.value(),
            "saturation": self.saturation_slider.value() / 100,
            "brightness": self.brightness_slider.value() / 100
        }

        # Add to profile widget
        self.profile_widget.profiles[name] = profile
        self.profile_widget.profile_combo.addItem(name)
        QMessageBox.information(self, "Success", f"Profile '{name}' saved!")

    def on_pattern_generated(self, pattern_path):
        """Handle generated pattern"""
        self.current_pattern_path = pattern_path
        QMessageBox.information(self, "Pattern Generated",
                               "Pattern generated successfully! It will be applied during processing.")

    def on_intensity_changed(self, value):
        self.intensity_spin.setValue(value / 100.0)

    def on_intensity_spin_changed(self, value):
        self.intensity_slider.setValue(int(value * 100))

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

    def get_selected_theme(self):
        return Path(self.theme_combo.currentData()) if self.theme_combo.currentData() else None

    def process_theme(self):
        try:
            input_dir = self.get_selected_theme()
            if not input_dir or not input_dir.exists():
                QMessageBox.warning(self, "Error", "Selected theme directory doesn't exist")
                return

            color = self.color_input.text().strip()
            if not color.startswith('#'):
                color = '#' + color

            intensity = self.intensity_spin.value()
            saturation = self.saturation_slider.value() / 100.0
            brightness = self.brightness_slider.value() / 100.0
            create_new = self.create_new_checkbox.isChecked()
            tint_checkboxes = self.tint_checkboxes.isChecked()
            tint_windowframes = self.tint_windowframes.isChecked()
            preserve_transparency = self.preserve_transparency.isChecked()
            preserve_whites = self.preserve_whites.isChecked()
            preserve_blacks = self.preserve_blacks.isChecked()
            white_threshold = self.white_threshold.value()
            black_threshold = self.black_threshold.value()

            self.progress_bar.setValue(0)

            # Save configuration
            self.save_config(str(input_dir), color, intensity, saturation, brightness)

            # Process the theme
            self.process_theme_files(
                input_dir, color, intensity, saturation, brightness,
                create_new, tint_checkboxes, tint_windowframes,
                preserve_transparency, preserve_whites, preserve_blacks,
                white_threshold, black_threshold
            )

            # Update history
            self.update_history_list()

            QMessageBox.information(self, "Success", "Theme processing completed!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error processing theme: {str(e)}")

    def restore_backup(self):
        try:
            input_dir = self.get_selected_theme()
            if not input_dir:
                QMessageBox.warning(self, "Error", "Please select a theme first")
                return
            self.restore_backup_files(input_dir)
            QMessageBox.information(self, "Success", "Backup restored successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error restoring backup: {str(e)}")

    def process_theme_files(self, input_dir, color, intensity, saturation, brightness,
                           create_new, tint_checkboxes, tint_windowframes,
                           preserve_transparency, preserve_whites, preserve_blacks,
                           white_threshold, black_threshold):
        """Process theme files with enhanced parameters"""
        try:
            folder_name = input_dir.name
            parent_folder = input_dir.parent

            if create_new:
                sanitized_color = color.replace('#','').upper()
                out_folder = parent_folder / f"{folder_name}-colorized#{sanitized_color}_{intensity:.1f}"
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
                    self.create_backup(input_dir)
                else:
                    self.restore_backup_files(input_dir)

                process_folder = input_dir

            # Get files to process
            files = self.get_top_level_files(process_folder, tint_checkboxes, tint_windowframes)

            if not files:
                QMessageBox.warning(self, "Warning", "No supported images found to process")
                return

            # Apply pattern if enabled
            pattern_path = None
            pattern_blend = 0
            if hasattr(self, 'apply_pattern_checkbox') and self.apply_pattern_checkbox.isChecked():
                if hasattr(self, 'current_pattern_path'):
                    pattern_path = self.current_pattern_path
                    pattern_blend = self.pattern_blend_slider.value() / 100.0

            total_files = len(files)
            for i, file in enumerate(files):
                colorize_enhanced(
                    file, color, intensity, saturation, brightness,
                    process_folder, input_dir,
                    preserve_transparency, preserve_whites, preserve_blacks,
                    white_threshold, black_threshold,
                    pattern_path, pattern_blend
                )
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

# Enhanced utility functions
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    return tuple(int(hex_color[i:i+lv//3], 16) for i in range(0, lv, lv//3))

def rgb_to_hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    return colorsys.rgb_to_hsv(r, g, b)

def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)

def adjust_color_hsv(r, g, b, saturation_factor, brightness_factor):
    """Adjust color saturation and brightness in HSV space"""
    h, s, v = rgb_to_hsv(r, g, b)
    s = min(1.0, s * saturation_factor)
    v = min(1.0, v * brightness_factor)
    return hsv_to_rgb(h, s, v)

def is_white_pixel(r, g, b, threshold=245):
    """Check if pixel is white or almost white"""
    return r >= threshold and g >= threshold and b >= threshold

def is_black_pixel(r, g, b, threshold=30):
    """Check if pixel is black or almost black"""
    return r <= threshold and g <= threshold and b <= threshold

def apply_pattern_overlay(img, pattern_path, blend_amount):
    """Apply a pattern overlay to an image"""
    try:
        pattern = Image.open(pattern_path).convert("RGBA")
        pattern = pattern.resize(img.size, Image.LANCZOS)

        # Blend pattern with image
        blended = Image.blend(img, pattern, blend_amount)
        return blended
    except Exception as e:
        print(f"Error applying pattern: {e}")
        return img

def colorize_enhanced(file_path, color, intensity, saturation, brightness,
                      out_folder, input_dir, preserve_transparency=True,
                      preserve_whites=True, preserve_blacks=True,
                      white_threshold=245, black_threshold=30,
                      pattern_path=None, pattern_blend=0):
    """Enhanced colorization with all new features"""
    img = Image.open(file_path).convert("RGBA")
    r_col, g_col, b_col = hex_to_rgb(color)
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]

            # Preserve transparency if enabled
            if preserve_transparency and a == 0:
                continue

            # Skip white/black pixels if preservation is enabled
            if preserve_whites and is_white_pixel(r, g, b, white_threshold):
                continue
            if preserve_blacks and is_black_pixel(r, g, b, black_threshold):
                continue

            # Apply color tinting
            r_new = round(r*(1-intensity) + r_col*intensity)
            g_new = round(g*(1-intensity) + g_col*intensity)
            b_new = round(b*(1-intensity) + b_col*intensity)

            # Apply saturation and brightness adjustments
            r_new, g_new, b_new = adjust_color_hsv(r_new, g_new, b_new, saturation, brightness)

            # Clamp values
            r_new = max(0, min(255, r_new))
            g_new = max(0, min(255, g_new))
            b_new = max(0, min(255, b_new))

            pixels[x, y] = (r_new, g_new, b_new, a)

    # Apply pattern if specified
    if pattern_path and pattern_blend > 0:
        img = apply_pattern_overlay(img, pattern_path, pattern_blend)

    out_path = out_folder / file_path.name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    window = ColorizerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()