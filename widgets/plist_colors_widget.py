from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QGroupBox, QLabel, QPushButton, QColorDialog,
                             QScrollArea, QFrame, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
import plistlib
from pathlib import Path
import traceback


class PlistColorsWidget(QWidget):
    colorsChanged = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.color_mappings = {}
        self.current_plist_path = None
        self.original_colors = {}  # Armazenar cores originais
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Info label
        info_label = QLabel("Edit individual color values from the settings.plist file.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(info_label)

        # Status label
        self.status_label = QLabel("No plist loaded")
        self.status_label.setStyleSheet("color: #dc3545; padding: 5px; background-color: #f8f9fa; border-radius: 5px;")
        layout.addWidget(self.status_label)

        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        # Container widget
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)

        # Set up scroll area
        self.scroll_area.setWidget(self.container_widget)
        layout.addWidget(self.scroll_area)

        # Action buttons
        button_layout = QHBoxLayout()

        self.apply_btn = QPushButton("Apply Color Changes")
        self.apply_btn.clicked.connect(self.apply_all_colors)
        self.apply_btn.setEnabled(False)
        button_layout.addWidget(self.apply_btn)

        self.reset_btn = QPushButton("Reset Colors")
        self.reset_btn.clicked.connect(self.reset_colors)
        self.reset_btn.setEnabled(False)
        button_layout.addWidget(self.reset_btn)

        layout.addLayout(button_layout)

    def set_plist_path(self, plist_path):
        """Load colors from plist file"""
        print(f"DEBUG: set_plist_path called with: {plist_path}")

        if not plist_path or not Path(plist_path).exists():
            self.status_label.setText("Error: Plist file not found")
            return False

        try:
            # Clear previous content
            self.clear_content()

            with open(plist_path, 'rb') as f:
                plist_data = plistlib.load(f)

            print(f"DEBUG: Loaded plist with {len(plist_data)} keys")

            # Store the current plist path
            self.current_plist_path = plist_path

            # Look for colors in different possible locations
            color_entries = {}

            # Try gColors first
            gcolors = plist_data.get("gColors", {})
            if gcolors:
                # Aceitar cores de 7 dígitos (#RRGGBB) e 8 dígitos (#RRGGBBAA)
                color_entries = {k: v for k, v in gcolors.items()
                                 if isinstance(v, str) and
                                 (v.startswith('#') and len(v) in [7, 8, 9])}  # 7, 8 ou 9 caracteres
                print(f"DEBUG: Found {len(color_entries)} color entries in gColors")

            # If no colors in gColors, try root level
            if not color_entries:
                color_entries = {k: v for k, v in plist_data.items()
                                 if isinstance(v, str) and
                                 (v.startswith('#') and len(v) in [7, 8, 9])}
                print(f"DEBUG: Found {len(color_entries)} color entries in root level")

            print(f"DEBUG: Total color entries found: {len(color_entries)}")

            if not color_entries:
                self.status_label.setText("No color entries found in plist")
                return False

            # Store original colors
            self.original_colors = color_entries.copy()

            # Create color editor
            self.create_color_editor(color_entries)

            self.status_label.setText(f"Loaded {len(color_entries)} colors from {Path(plist_path).name}")
            self.status_label.setStyleSheet(
                "color: #28a745; padding: 5px; background-color: #f8f9fa; border-radius: 5px;")

            self.apply_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)

            return True

        except Exception as e:
            error_msg = f"Error loading plist: {str(e)}"
            print(f"DEBUG: {error_msg}")
            print(traceback.format_exc())
            self.status_label.setText(error_msg)
            return False

    def clear_content(self):
        """Clear all content"""
        for i in reversed(range(self.container_layout.count())):
            item = self.container_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
        self.color_mappings = {}
        self.original_colors = {}

    def create_color_editor(self, color_entries):
        """Create the color editing interface"""
        # Group by categories
        categories = self.categorize_colors(color_entries)

        for category_name, colors in categories.items():
            if colors:
                group_box = self.create_category_group(category_name, colors, color_entries)
                self.container_layout.addWidget(group_box)

        self.container_layout.addStretch()

    def categorize_colors(self, color_entries):
        """Categorize colors logically"""
        categories = {
            'System Colors': [],
            'Control Colors': [],
            'Text Colors': [],
            'Background Colors': [],
            'Other Colors': []
        }

        for key in color_entries.keys():
            key_lower = key.lower()

            if any(word in key_lower for word in ['system', 'blue', 'green', 'red', 'orange']):
                categories['System Colors'].append(key)
            elif any(word in key_lower for word in ['control', 'button', 'bezel']):
                categories['Control Colors'].append(key)
            elif any(word in key_lower for word in ['text', 'label', 'font']):
                categories['Text Colors'].append(key)
            elif any(word in key_lower for word in ['background', 'window', 'desktop']):
                categories['Background Colors'].append(key)
            else:
                categories['Other Colors'].append(key)

        return categories

    def create_category_group(self, category_name, color_keys, color_entries):
        """Create a group for a color category"""
        group_box = QGroupBox(f"{category_name} ({len(color_keys)})")
        layout = QGridLayout(group_box)

        for i, key in enumerate(color_keys):
            # Label
            label = QLabel(self.format_key_name(key))
            label.setToolTip(key)
            layout.addWidget(label, i, 0)

            # Color button
            color_btn = QPushButton()
            color_btn.setFixedSize(25, 25)
            color_btn.clicked.connect(lambda checked, k=key: self.pick_color(k))
            layout.addWidget(color_btn, i, 1)

            # Color value
            value_edit = QLineEdit()
            value_edit.setMaximumWidth(80)
            value_edit.textChanged.connect(lambda text, k=key: self.on_color_value_changed(k, text))
            layout.addWidget(value_edit, i, 2)

            # Get original color value - ADD SAFETY CHECK
            original_color = color_entries.get(key, '#000000')

            # Only create the mapping if the key exists in color_entries
            if key in color_entries:
                # Set initial values
                color_btn.setStyleSheet(f"background-color: {original_color}; border: 1px solid #ccc;")
                value_edit.setText(original_color)

                # Store reference
                self.color_mappings[key] = {
                    'button': color_btn,
                    'edit': value_edit,
                    'original': original_color
                }
            else:
                # Handle missing key - disable the controls
                color_btn.setEnabled(False)
                value_edit.setEnabled(False)
                color_btn.setStyleSheet("background-color: #cccccc; border: 1px solid #ccc;")
                value_edit.setText("#000000")
                print(f"DEBUG: Key '{key}' not found in color_entries")

        return group_box

    def format_key_name(self, key):
        """Format key for display"""
        return key.replace('_', ' ').title()[:25]

    def pick_color(self, key):
        """Pick color for a key"""
        if key not in self.color_mappings:
            print(f"DEBUG: Key '{key}' not found in color_mappings")
            return

        current_color = self.color_mappings[key]['edit'].text()

        # Preservar o alpha channel se existir
        if current_color.startswith('#') and len(current_color) == 9:  # #RRGGBBAA
            alpha = current_color[7:9]  # Preservar os últimos 2 dígitos (alpha)
            rgb_color = current_color[:7]  # Pegar apenas #RRGGBB
            initial_color = QColor(rgb_color) if rgb_color else QColor('#000000')
        else:
            alpha = None
            initial_color = QColor(current_color) if current_color.startswith('#') else QColor('#000000')

        color = QColorDialog.getColor(initial_color, self, f"Select color for {key}")
        if color.isValid():
            hex_color = color.name().upper()  # Isso retorna #RRGGBB

            # Adicionar alpha channel de volta se existia originalmente
            if alpha:
                hex_color += alpha  # Adicionar os dígitos alpha: #RRGGBB + AA

            self.color_mappings[key]['button'].setStyleSheet(f"background-color: {hex_color}; border: 1px solid #ccc;")
            self.color_mappings[key]['edit'].setText(hex_color)

    def on_color_value_changed(self, key, text):
        """Handle manual text input changes"""
        # Add safety check for key existence
        if key not in self.color_mappings:
            print(f"DEBUG: Key '{key}' not found in color_mappings")
            return

        if text.startswith('#') and len(text) in [7, 9]:  # #RRGGBB or #RRGGBBAA
            self.color_mappings[key]['button'].setStyleSheet(f"background-color: {text}; border: 1px solid #ccc;")

    def apply_all_colors(self):
        """Apply all color changes to the plist file"""
        if not self.current_plist_path:
            QMessageBox.warning(self, "Error", "No plist file loaded")
            return

        try:
            # Load current plist data
            with open(self.current_plist_path, 'rb') as f:
                plist_data = plistlib.load(f)

            changes = {}

            # Apply changes to gColors section if it exists
            if 'gColors' in plist_data:
                for key, mapping in self.color_mappings.items():
                    current_color = mapping['edit'].text().strip()
                    # Aceitar cores de 7 ou 8 dígitos
                    if (current_color and current_color.startswith('#') and
                            len(current_color) in [7, 9] and  # 7 ou 9 caracteres (incluindo #)
                            current_color != mapping['original']):

                        # Update in gColors
                        if key in plist_data['gColors']:
                            plist_data['gColors'][key] = current_color
                            changes[key] = current_color

            # Also check root level for color entries
            for key, mapping in self.color_mappings.items():
                current_color = mapping['edit'].text().strip()
                # Aceitar cores de 7 ou 8 dígitos
                if (current_color and current_color.startswith('#') and
                        len(current_color) in [7, 9] and  # 7 ou 9 caracteres (incluindo #)
                        current_color != mapping['original'] and
                        key in plist_data):  # Key exists at root level

                    plist_data[key] = current_color
                    changes[key] = current_color

            if changes:
                # Save the modified plist
                with open(self.current_plist_path, 'wb') as f:
                    plistlib.dump(plist_data, f)

                # Update original colors to reflect new state
                for key, new_color in changes.items():
                    if key in self.original_colors:
                        self.original_colors[key] = new_color
                    if key in self.color_mappings:
                        self.color_mappings[key]['original'] = new_color

                self.colorsChanged.emit(changes)
                QMessageBox.information(self, "Success", f"Applied {len(changes)} color changes to plist file")

                # Update status
                self.status_label.setText(f"Applied {len(changes)} changes - {Path(self.current_plist_path).name}")
                self.status_label.setStyleSheet(
                    "color: #28a745; padding: 5px; background-color: #f8f9fa; border-radius: 5px;")
            else:
                QMessageBox.information(self, "Info", "No changes to apply")

        except Exception as e:
            error_msg = f"Error applying color changes: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            print(f"DEBUG: {error_msg}")
            print(traceback.format_exc())

    def reset_colors(self):
        """Reset to original colors"""
        reply = QMessageBox.question(self, "Confirm Reset",
                                     "Are you sure you want to reset all colors to their original values?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            for key, mapping in self.color_mappings.items():
                original_color = self.original_colors.get(key, mapping['original'])
                mapping['edit'].setText(original_color)
                mapping['button'].setStyleSheet(f"background-color: {original_color}; border: 1px solid #ccc;")

            QMessageBox.information(self, "Reset Complete", "All colors have been reset to their original values")