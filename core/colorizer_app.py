import os
import shutil
import json
import plistlib
from pathlib import Path
from collections import Counter
from PyQt5.QtWidgets import QColorDialog
from utils.color_utils import hex_to_rgb, adjust_color_hsv
from widgets.color_variations_widget import ColorVariationsWidget

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QSlider, QDoubleSpinBox,
                             QCheckBox, QFileDialog, QMessageBox, QGroupBox, QProgressBar,
                             QListWidget, QLineEdit, QGridLayout, QTabWidget, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from widgets.drag_drop_label import DragDropLabel
from widgets.color_profile_widget import ColorProfileWidget
from widgets.pattern_generator_widget import PatternGeneratorWidget
from widgets.plist_settings_widget import PlistSettingsWidget
from utils.image_processing import colorize_enhanced
from utils.color_utils import hex_to_rgb
from utils.file_utils import get_all_image_files, get_top_level_files

from widgets.manual_color_adjustment_widget import ManualColorAdjustmentWidget


SUPPORTED = ['.png', '.jpg', '.jpeg']
CONFIG_FILE = 'colorizer_config.json'

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

        # Tab 2: Manual Color Adjustment (NEW)
        manual_tab = QWidget()
        self.setup_manual_tab(manual_tab)
        self.tab_widget.addTab(manual_tab, "Manual Colors")

        # Tab 3: Color Profiles
        profiles_tab = QWidget()
        self.setup_profiles_tab(profiles_tab)
        self.tab_widget.addTab(profiles_tab, "Color Profiles")

        # Tab 4: Pattern Generator
        patterns_tab = QWidget()
        self.setup_patterns_tab(patterns_tab)
        self.tab_widget.addTab(patterns_tab, "Pattern Generator")

        # Tab 5: Advanced Settings
        advanced_tab = QWidget()
        self.setup_advanced_tab(advanced_tab)
        self.tab_widget.addTab(advanced_tab, "Advanced")

        # Tab 6: Plist Settings
        plist_tab = QWidget()
        self.setup_plist_tab(plist_tab)
        self.tab_widget.addTab(plist_tab, "Plist Settings")

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
        self.drag_drop_label.setMinimumHeight(30)
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

        self.color_input = QLineEdit("##E6E0FF")
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
        self.color_preview.setStyleSheet("background-color: #E6E0FF; border: 1px solid #ccc;")
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

        # Color Variations
        variations_group = QGroupBox("Color Variations")
        variations_layout = QVBoxLayout(variations_group)

        self.color_variations_widget = ColorVariationsWidget()
        self.color_variations_widget.variationSelected.connect(self.on_variation_selected)
        variations_layout.addWidget(self.color_variations_widget)

        layout.addWidget(variations_group)

    def setup_manual_tab(self, parent):
        layout = QVBoxLayout(parent)

        self.manual_color_widget = ManualColorAdjustmentWidget()
        self.manual_color_widget.colorChanged.connect(self.on_manual_color_changed)
        layout.addWidget(self.manual_color_widget)

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
        self.white_threshold.setRange(100, 255)
        self.white_threshold.setValue(254)
        white_layout.addWidget(self.white_threshold)
        threshold_layout.addLayout(white_layout)

        black_layout = QHBoxLayout()
        black_layout.addWidget(QLabel("Black Threshold:"))
        self.black_threshold = QSpinBox()
        self.black_threshold.setRange(0, 200)
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

    def setup_plist_tab(self, parent):
        layout = QVBoxLayout(parent)

        self.plist_widget = PlistSettingsWidget()
        layout.addWidget(self.plist_widget)

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

    def on_manual_color_changed(self, item_name, color):
        """Handle manual color changes for specific items"""
        print(f"Color changed for {item_name}: {color}")
        # Store the manual color adjustments
        if not hasattr(self, 'manual_colors'):
            self.manual_colors = {}
        self.manual_colors[item_name] = color

    def load_last_config(self):
        """Load the last used configuration for current theme"""
        theme_path = self.get_selected_theme()
        if str(theme_path) in self.current_config:
            config = self.current_config[str(theme_path)]
            self.color_input.setText(config['color'])
            self.intensity_spin.setValue(config['intensity'])
            self.saturation_slider.setValue(int(config.get('saturation', 1.0) * 100))
            self.brightness_slider.setValue(int(config.get('brightness', 1.0) * 100))

            # Reset manual colors when loading a new config
            if hasattr(self, 'manual_colors'):
                self.manual_colors = {}
            if hasattr(self, 'manual_color_widget'):
                self.manual_color_widget.set_base_color(config['color'])

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

        # Reset manual colors when applying a profile
        if hasattr(self, 'manual_colors'):
            self.manual_colors = {}
        if hasattr(self, 'manual_color_widget'):
            self.manual_color_widget.set_base_color(profile['color'])

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
            from widgets.color_option_widget import ColorOptionWidget
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
            # Update color variations
            if hasattr(self, 'color_variations_widget'):
                self.color_variations_widget.set_base_color(color)
            # Update manual color widget
            if hasattr(self, 'manual_color_widget'):
                self.manual_color_widget.set_base_color(color)

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

            # Process the plist file
            self.process_plist_file(input_dir, color, intensity, saturation, brightness, create_new)

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
            files = get_top_level_files(process_folder, tint_checkboxes, tint_windowframes, SUPPORTED)

            if not files:
                QMessageBox.warning(self, "Warning", "No supported images found to process")
                return

            # Apply pattern if enabled
            pattern_path = None
            pattern_blend = 0
            pattern_filters = []

            if hasattr(self, 'apply_pattern_checkbox') and self.apply_pattern_checkbox.isChecked():
                if hasattr(self, 'current_pattern_path'):
                    pattern_path = self.current_pattern_path
                    pattern_blend = self.pattern_blend_slider.value() / 100.0

                    # Get pattern filters from UI
                    if hasattr(self.pattern_widget, 'apply_mica_header') and self.pattern_widget.apply_mica_header.isChecked():
                        pattern_filters.append('Mica: Header')
                    if hasattr(self.pattern_widget, 'apply_mica_sidebar') and self.pattern_widget.apply_mica_sidebar.isChecked():
                        pattern_filters.append('Mica: Sidebar')
                    if hasattr(self.pattern_widget, 'apply_mica_titlebar') and self.pattern_widget.apply_mica_titlebar.isChecked():
                        pattern_filters.append('Mica: Titlebar')
                    if hasattr(self.pattern_widget, 'apply_mica_menu') and self.pattern_widget.apply_mica_menu.isChecked():
                        pattern_filters.append('Mica: Menu')
                    if hasattr(self.pattern_widget, 'apply_mica_window_bg') and self.pattern_widget.apply_mica_window_bg.isChecked():
                        pattern_filters.append('Mica: WindowBackground')

            # Check for color variations
            use_variations = (hasattr(self, 'color_variations_widget') and
                             self.color_variations_widget.enable_variations.isChecked())

            variations = []
            if use_variations:
                variations = self.color_variations_widget.variations

            total_files = len(files)
            for i, file in enumerate(files):
                # Determine which color to use for this file
                if use_variations and variations:
                    # Use different color variation for each file (cyclic)
                    variation_index = i % len(variations)
                    file_color = variations[variation_index]
                else:
                    file_color = color

                # Check if pattern should be applied to this file
                apply_pattern_to_file = False
                if pattern_path and pattern_filters:
                    filename = file.name
                    # Check if filename matches any of the selected filters
                    for pattern_filter in pattern_filters:
                        if filename.startswith(pattern_filter):
                            apply_pattern_to_file = True
                            break

                colorize_enhanced(
                    file, file_color, intensity, saturation, brightness,
                    process_folder, input_dir,
                    preserve_transparency, preserve_whites, preserve_blacks,
                    white_threshold, black_threshold,
                    pattern_path if apply_pattern_to_file else None,  # Only apply pattern if file matches filters
                    pattern_blend if apply_pattern_to_file else 0
                )
                self.progress_bar.setValue(int((i + 1) / total_files * 100))

            # Check for manual color overrides
            manual_color = None
            if hasattr(self, 'manual_colors') and file.name in self.manual_colors:
                manual_color = self.manual_colors[file.name]

            # Use manual color if specified, otherwise use the determined color
            final_color = manual_color if manual_color else file_color

            colorize_enhanced(
                file, final_color, intensity, saturation, brightness,
                process_folder, input_dir,
                preserve_transparency, preserve_whites, preserve_blacks,
                white_threshold, black_threshold,
                pattern_path if apply_pattern_to_file else None,
                pattern_blend if apply_pattern_to_file else 0
            )

        except Exception as e:
            raise Exception(f"Error processing theme files: {str(e)}")

    def process_plist_file(self, input_dir, color, intensity, saturation, brightness, create_new):
        """Process the settings.plist file with all available options"""
        try:
            if create_new:
                folder_name = input_dir.name
                parent_folder = input_dir.parent
                sanitized_color = color.replace('#','').upper()
                out_folder = parent_folder / f"{folder_name}-colorized#{sanitized_color}_{intensity:.1f}"
                plist_path = out_folder / "settings.plist"
            else:
                plist_path = input_dir / "settings.plist"

            if not plist_path.exists():
                print(f"No settings.plist found at {plist_path}")
                return

            # Load the plist file
            with open(plist_path, 'rb') as f:
                plist_data = plistlib.load(f)

            # Get all settings from UI
            active_shadow = self.plist_widget.active_shadow_spin.value()
            inactive_shadow = self.plist_widget.inactive_shadow_spin.value()
            dock_reflection = self.plist_widget.dock_reflection_checkbox.isChecked()
            dock_touches_ground = self.plist_widget.dock_touches_ground_checkbox.isChecked()
            dock_slices = self.plist_widget.dock_slices_input.text()
            hide_window_rim = self.plist_widget.hide_window_rim_checkbox.isChecked()
            mini_toolbar = self.plist_widget.mini_toolbar_checkbox.isChecked()
            patch_appearance = self.plist_widget.patch_appearance_checkbox.isChecked()
            control_spacing = self.plist_widget.control_spacing_spin.value()

            # Mica settings
            mica_header = self.plist_widget.mica_header_checkbox.isChecked()
            mica_sidebar = self.plist_widget.mica_sidebar_checkbox.isChecked()
            mica_titlebar = self.plist_widget.mica_titlebar_checkbox.isChecked()
            mica_menu = self.plist_widget.mica_menu_checkbox.isChecked()
            mica_window_bg = self.plist_widget.mica_window_bg_checkbox.isChecked()

            # Asset slice settings
            window_frame_mask_1x = self.plist_widget.window_frame_mask_1x.text()
            window_frame_base_1x = self.plist_widget.window_frame_base_1x.text()
            window_frame_mask_2x = self.plist_widget.window_frame_mask_2x.text()
            window_frame_base_2x = self.plist_widget.window_frame_base_2x.text()

            # Update basic settings
            plist_data['gWindowShadowActiveRadius'] = active_shadow
            plist_data['gWindowShadowInactiveRadius'] = inactive_shadow
            plist_data['gDockReflection'] = dock_reflection
            plist_data['gDockTouchesGround'] = dock_touches_ground
            plist_data['gDockSlices'] = dock_slices
            plist_data['gHideWindowRim'] = hide_window_rim
            plist_data['gMiniToolbar'] = mini_toolbar
            plist_data['gPatchAppearance'] = patch_appearance
            plist_data['gControlSpacing'] = control_spacing

            # Update Mica settings
            if 'gMicaTile' not in plist_data:
                plist_data['gMicaTile'] = {}

            mica_dict = plist_data['gMicaTile']

            # Header Mica
            mica_dict['Mica: Header_Active_Normal_Off_Base0'] = mica_header
            mica_dict['Mica: Header_Active_Normal_Off_Base0@2x'] = mica_header
            mica_dict['Mica: Header_Inactive_Normal_Off_Base0'] = mica_header
            mica_dict['Mica: Header_Inactive_Normal_Off_Base0@2x'] = mica_header
            mica_dict['Mica: Header-Opaque_Active_Normal_Off_Base0'] = mica_header
            mica_dict['Mica: Header-Opaque_Active_Normal_Off_Base0@2x'] = mica_header
            mica_dict['Mica: Header-Opaque_Inactive_Normal_Off_Base0'] = mica_header
            mica_dict['Mica: Header-Opaque_Inactive_Normal_Off_Base0@2x'] = mica_header

            # Sidebar Mica
            mica_dict['Mica: Sidebar_Active_Normal_Off_Base0'] = mica_sidebar
            mica_dict['Mica: Sidebar_Active_Normal_Off_Base0@2x'] = mica_sidebar
            mica_dict['Mica: Sidebar_Inactive_Normal_Off_Base0'] = mica_sidebar
            mica_dict['Mica: Sidebar_Inactive_Normal_Off_Base0@2x'] = mica_sidebar
            mica_dict['Mica: Sidebar-Opaque_Active_Normal_Off_Base0'] = mica_sidebar
            mica_dict['Mica: Sidebar-Opaque_Active_Normal_Off_Base0@2x'] = mica_sidebar
            mica_dict['Mica: Sidebar-Opaque_Inactive_Normal_Off_Base0'] = mica_sidebar
            mica_dict['Mica: Sidebar-Opaque_Inactive_Normal_Off_Base0@2x'] = mica_sidebar

            # Titlebar Mica
            mica_dict['Mica: Titlebar_Active_Normal_Off_Base0'] = mica_titlebar
            mica_dict['Mica: Titlebar_Active_Normal_Off_Base0@2x'] = mica_titlebar
            mica_dict['Mica: Titlebar_Inactive_Normal_Off_Base0'] = mica_titlebar
            mica_dict['Mica: Titlebar_Inactive_Normal_Off_Base0@2x'] = mica_titlebar
            mica_dict['Mica: Titlebar-Opaque_Active_Normal_Off_Base0'] = mica_titlebar
            mica_dict['Mica: Titlebar-Opaque_Active_Normal_Off_Base0@2x'] = mica_titlebar
            mica_dict['Mica: Titlebar-Opaque_Inactive_Normal_Off_Base0'] = mica_titlebar
            mica_dict['Mica: Titlebar-Opaque_Inactive_Normal_Off_Base0@2x'] = mica_titlebar

            # Menu Mica
            mica_dict['Mica: Menu_Active_Normal_Off_Base0'] = mica_menu
            mica_dict['Mica: Menu_Active_Normal_Off_Base0@2x'] = mica_menu
            mica_dict['Mica: Menu_Inactive_Normal_Off_Base0'] = mica_menu
            mica_dict['Mica: Menu_Inactive_Normal_Off_Base0@2x'] = mica_menu
            mica_dict['Mica: Menu-Opaque_Active_Normal_Off_Base0'] = mica_menu
            mica_dict['Mica: Menu-Opaque_Active_Normal_Off_Base0@2x'] = mica_menu
            mica_dict['Mica: Menu-Opaque_Inactive_Normal_Off_Base0'] = mica_menu
            mica_dict['Mica: Menu-Opaque_Inactive_Normal_Off_Base0@2x'] = mica_menu

            # Window Background Mica
            mica_dict['Mica: WindowBackground_Active_Normal_Off_Base0'] = mica_window_bg
            mica_dict['Mica: WindowBackground_Active_Normal_Off_Base0@2x'] = mica_window_bg
            mica_dict['Mica: WindowBackground_Inactive_Normal_Off_Base0'] = mica_window_bg
            mica_dict['Mica: WindowBackground_Inactive_Normal_Off_Base0@2x'] = mica_window_bg
            mica_dict['Mica: WindowBackground-Opaque_Active_Normal_Off_Base0'] = mica_window_bg
            mica_dict['Mica: WindowBackground-Opaque_Active_Normal_Off_Base0@2x'] = mica_window_bg
            mica_dict['Mica: WindowBackground-Opaque_Inactive_Normal_Off_Base0'] = mica_window_bg
            mica_dict['Mica: WindowBackground-Opaque_Inactive_Normal_Off_Base0@2x'] = mica_window_bg

            # Update asset slice settings
            if 'gAssetSlice' not in plist_data:
                plist_data['gAssetSlice'] = {}

            asset_dict = plist_data['gAssetSlice']
            asset_dict['WindowFrame_WindowShapeEdges_Regular_Active_Normal_Off_Mask0'] = window_frame_mask_1x
            asset_dict['WindowFrame_WindowShapeEdges_Regular_Active_Normal_Off_Base0'] = window_frame_base_1x
            asset_dict['WindowFrame_WindowShapeEdges_Regular_Active_Normal_Off_Mask0@2x'] = window_frame_mask_2x
            asset_dict['WindowFrame_WindowShapeEdges_Regular_Active_Normal_Off_Base0@2x'] = window_frame_base_2x
            asset_dict['WindowFrame_WindowShapeEdges_Regular_Inactive_Normal_Off_Mask0'] = window_frame_mask_1x
            asset_dict['WindowFrame_WindowShapeEdges_Regular_Inactive_Normal_Off_Base0'] = window_frame_base_1x
            asset_dict['WindowFrame_WindowShapeEdges_Regular_Inactive_Normal_Off_Mask0@2x'] = window_frame_mask_2x
            asset_dict['WindowFrame_WindowShapeEdges_Regular_Inactive_Normal_Off_Base0@2x'] = window_frame_base_2x

            # Update color values if gColors exists
            if 'gColors' in plist_data:
                color_dict = plist_data['gColors']
                r_col, g_col, b_col = hex_to_rgb(color)

                # Aplicar ajustes de saturação e brilho à cor base
                r_col_adj, g_col_adj, b_col_adj = adjust_color_hsv(r_col, g_col, b_col, saturation, brightness)

                for key, value in color_dict.items():
                    if isinstance(value, str) and value.startswith('#'):
                        # Extract original color components
                        original_hex = value.lstrip('#')
                        if len(original_hex) == 8:  # RGBA format
                            r_orig = int(original_hex[0:2], 16)
                            g_orig = int(original_hex[2:4], 16)
                            b_orig = int(original_hex[4:6], 16)
                            a_orig = original_hex[6:8]

                            # Apply color tinting with adjusted color
                            r_new = round(r_orig*(1-intensity) + r_col_adj*intensity)
                            g_new = round(g_orig*(1-intensity) + g_col_adj*intensity)
                            b_new = round(b_orig*(1-intensity) + b_col_adj*intensity)

                            # Clamp values
                            r_new = max(0, min(255, r_new))
                            g_new = max(0, min(255, g_new))
                            b_new = max(0, min(255, b_new))

                            # Create new color value
                            new_color = f"#{r_new:02x}{g_new:02x}{b_new:02x}{a_orig}"
                            color_dict[key] = new_color

            # Save the modified plist
            with open(plist_path, 'wb') as f:
                plistlib.dump(plist_data, f)

            print(f"Updated settings.plist at {plist_path}")

        except Exception as e:
            print(f"Error processing plist file: {e}")
            raise

    def create_backup(self, input_dir):
        """Create backup of all image files and plist"""
        backup_folder = input_dir / 'backup'
        backup_folder.mkdir(exist_ok=True)

        # Get all image files
        all_image_files = get_all_image_files(input_dir, SUPPORTED)

        # Get plist file if exists
        plist_file = input_dir / "settings.plist"
        if plist_file.exists():
            all_image_files.append(plist_file)

        print(f"Creating backup of {len(all_image_files)} files...")

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

    def copy_all_items(self, src_dir, dest_dir, tint_checkboxes=True, tint_windowframes=True):
         """Copy all items with filtering, including plist and Mica files"""
         for item in src_dir.iterdir():
             if item.name == 'backup':
                 continue

             dest_path = dest_dir / item.name

             if item.is_file():
                 # Always copy plist file and Mica files
                 if (item.name == "settings.plist" or
                     item.name.startswith('Mica:') or
                     'Mica' in item.name):
                     shutil.copy2(item, dest_path)
                     print(f"Copied: {item.name}")
                     continue

                 # Filter image files based on user preferences
                 if item.suffix.lower() in SUPPORTED:
                     filename_lower = item.name.lower()
                     should_skip = False

                     if not tint_checkboxes and filename_lower.startswith('checkbox'):
                         should_skip = True
                     if not tint_windowframes and (filename_lower.startswith('windowframe') or filename_lower.startswith('frame')):
                         should_skip = True

                     if should_skip:
                         continue

                     shutil.copy2(item, dest_path)
                     print(f"Copied: {item.name}")
                 else:
                     # Copy other non-image files
                     shutil.copy2(item, dest_path)
                     print(f"Copied: {item.name}")
             elif item.is_dir():
                 shutil.copytree(item, dest_path, dirs_exist_ok=True)
                 print(f"Copied directory: {item.name}")

    def restore_backup_files(self, input_dir):
        """Restore backup files including plist"""
        backup_folder = input_dir / 'backup'
        if not backup_folder.exists():
            raise Exception("No backup found")

        files = []
        for item in backup_folder.iterdir():
            # Include both image files and plist file
            if (item.is_file() and
                (item.suffix.lower() in SUPPORTED or item.name == "settings.plist")):
                files.append(item)

        for file in files:
            dest = input_dir / file.name
            shutil.copy2(file, dest)
            print(f"Restored: {file.name}")

    def on_variation_selected(self, color):
        """Handle color variation selection"""
        self.color_input.setText(color)
        self.update_color_preview(color)