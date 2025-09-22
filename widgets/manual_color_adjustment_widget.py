from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QGroupBox, QLabel, QPushButton, QColorDialog,
                             QScrollArea, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor


class ManualColorAdjustmentWidget(QWidget):
    colorChanged = pyqtSignal(str, str)  # Emits (item_name, color)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_color = "#E6E0FF"
        self.item_colors = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Info label
        info_label = QLabel("Manually adjust colors for specific image items. "
                            "Changes will be applied during theme processing.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 5px; background-color: #f8f9fa; border-radius: 5px;")
        layout.addWidget(info_label)

        # Create scroll area for the color controls
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # Container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)

        # Define the item groups
        item_groups = [
            {
                "name": "Mica Header Items",
                "items": [
                    "Mica/ Header_Active_Normal_Off_Base0@2x.png",
                    "Mica/ Header_Inactive_Normal_Off_Base0@2x.png",
                    "Mica/ Header-Opaque_Active_Normal_Off_Base0@2x.png",
                    "Mica/ Header-Opaque_Inactive_Normal_Off_Base0@2x.png",
                    "Mica/ InlineTitlebar_Active_Normal_Off_Base0@2x.png",
                    "Mica/ InlineTitlebar_Inactive_Normal_Off_Base0@2x.png",
                    "Mica/ InlineTitlebar-Opaque_Active_Normal_Off_Base0@2x.png",
                    "Mica/ InlineTitlebar-Opaque_Inactive_Normal_Off_Base0@2x.png"
                ]
            },
            {
                "name": "Mica Selection Items",
                "items": [
                    "Mica/ Selection_Active_Normal_Off_Base0@2x.png",
                    "Mica/ Selection_Active_Pressed_Off_Base0@2x.png",
                    "Mica/ Selection_Inactive_Normal_Off_Base0@2x.png",
                    "Mica/ Selection-Opaque_Active_Normal_Off_Base0@2x.png",
                    "Mica/ Selection-Opaque_Active_Pressed_Off_Base0@2x.png",
                    "Mica/ Selection-Opaque_Inactive_Normal_Off_Base0@2x.png"
                ]
            },
            {
                "name": "Mica Sidebar Items",
                "items": [
                    "Mica/ Sidebar_Active_Normal_Off_Base0@2x.png",
                    "Mica/ Sidebar_Inactive_Normal_Off_Base0@2x.png",
                    "Mica/ Sidebar-Opaque_Active_Normal_Off_Base0@2x.png",
                    "Mica/ Sidebar-Opaque_Inactive_Normal_Off_Base0@2x.png"
                ]
            },
            {
                "name": "Mica Titlebar Items",
                "items": [
                    "Mica/ Titlebar_Active_Normal_Off_Base0@2x.png",
                    "Mica/ Titlebar_Inactive_Normal_Off_Base0@2x.png",
                    "Mica/ Titlebar-Opaque_Active_Normal_Off_Base0@2x.png",
                    "Mica/ Titlebar-Opaque_Inactive_Normal_Off_Base0@2x.png"
                ]
            },
            {
                "name": "Mica Window Background Items",
                "items": [
                    "Mica/ WindowBackground_Active_Normal_Off_Base0@2x.png",
                    "Mica/ WindowBackground_Inactive_Normal_Off_Base0@2x.png",
                    "Mica/ WindowBackground-Opaque_Active_Normal_Off_Base0@2x.png",
                    "Mica/ WindowBackground-Opaque_Inactive_Normal_Off_Base0@2x.png"
                ]
            },
            {
                "name": "Progress Indicator Items",
                "items": [
                    "ProgressIndicatorBar_Fill_Regular_Active_Normal_Off_Base0@2x.png",
                    "ProgressIndicatorBar_Fill_Regular_Inactive_Normal_Off_Base0@2x.png",
                    "ProgressIndicatorBar_Track_Regular_Active_Normal_Off_Base0@2x.png"
                ]
            }
        ]

        # Create color controls for each group
        self.color_controls = {}
        for group in item_groups:
            group_box = QGroupBox(group["name"])
            group_layout = QGridLayout(group_box)

            for i, item_name in enumerate(group["items"]):
                # Shorten the display name
                display_name = item_name.split('/')[-1] if '/' in item_name else item_name
                display_name = display_name.replace('@2x.png', '').replace('.png', '')

                # Label
                label = QLabel(display_name)
                group_layout.addWidget(label, i, 0)

                # Color preview button
                color_btn = QPushButton()
                color_btn.setFixedSize(30, 30)
                color_btn.setStyleSheet(f"background-color: {self.base_color}; border: 1px solid #ccc;")
                color_btn.clicked.connect(lambda checked, name=item_name: self.pick_color_for_item(name))
                group_layout.addWidget(color_btn, i, 1)

                # Store the control
                self.color_controls[item_name] = color_btn
                self.item_colors[item_name] = self.base_color

            container_layout.addWidget(group_box)

        # Reset button
        reset_btn = QPushButton("Reset All to Base Color")
        reset_btn.setStyleSheet(
            "QPushButton { font-weight: bold; padding: 10px; background-color: #dc3545; color: white; }")
        reset_btn.clicked.connect(self.reset_all_colors)
        container_layout.addWidget(reset_btn)

        container_layout.addStretch()

        # Set up scroll area
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)

    def set_base_color(self, color):
        """Set the base color and update all controls"""
        self.base_color = color
        for item_name, color_btn in self.color_controls.items():
            color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid #ccc;")
            self.item_colors[item_name] = color

    def pick_color_for_item(self, item_name):
        """Open color picker for a specific item"""
        current_color = QColor(self.item_colors.get(item_name, self.base_color))
        color = QColorDialog.getColor(current_color, self, f"Select color for {item_name}")

        if color.isValid():
            hex_color = color.name()
            self.color_controls[item_name].setStyleSheet(f"background-color: {hex_color}; border: 1px solid #ccc;")
            self.item_colors[item_name] = hex_color
            self.colorChanged.emit(item_name, hex_color)

    def reset_all_colors(self):
        """Reset all colors to the base color"""
        for item_name, color_btn in self.color_controls.items():
            color_btn.setStyleSheet(f"background-color: {self.base_color}; border: 1px solid #ccc;")
            self.item_colors[item_name] = self.base_color
            self.colorChanged.emit(item_name, self.base_color)

    def get_item_color(self, item_name):
        """Get the color for a specific item"""
        return self.item_colors.get(item_name, self.base_color)

    def get_all_colors(self):
        """Get all custom colors"""
        return self.item_colors.copy()