from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QGroupBox,
                             QLabel, QSpinBox, QCheckBox, QHBoxLayout, QLineEdit,
                             QScrollArea, QFrame)
from PyQt5.QtCore import Qt

class PlistSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # Main container widget
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)

        # Window Shadow Settings
        shadow_group = QGroupBox("Window Shadow Settings")
        shadow_layout = QGridLayout(shadow_group)

        shadow_layout.addWidget(QLabel("Active Window Shadow Radius:"), 0, 0)
        self.active_shadow_spin = QSpinBox()
        self.active_shadow_spin.setRange(-100, 300)
        self.active_shadow_spin.setValue(10)
        shadow_layout.addWidget(self.active_shadow_spin, 0, 1)

        shadow_layout.addWidget(QLabel("Inactive Window Shadow Radius:"), 1, 0)
        self.inactive_shadow_spin = QSpinBox()
        self.inactive_shadow_spin.setRange(-100, 300)
        self.inactive_shadow_spin.setValue(8)
        shadow_layout.addWidget(self.inactive_shadow_spin, 1, 1)

        layout.addWidget(shadow_group)

        # Dock Settings
        dock_group = QGroupBox("Dock Settings")
        dock_layout = QGridLayout(dock_group)

        self.dock_reflection_checkbox = QCheckBox("Dock Reflection")
        self.dock_reflection_checkbox.setChecked(True)
        dock_layout.addWidget(self.dock_reflection_checkbox, 0, 0)

        self.dock_touches_ground_checkbox = QCheckBox("Dock Touches Ground")
        self.dock_touches_ground_checkbox.setChecked(True)
        dock_layout.addWidget(self.dock_touches_ground_checkbox, 0, 1)

        dock_layout.addWidget(QLabel("Dock Slices:"), 1, 0)
        self.dock_slices_input = QLineEdit("{{0.25, 0.05},{0.5, 0.95}}")
        dock_layout.addWidget(self.dock_slices_input, 1, 1)

        layout.addWidget(dock_group)

        # Control Settings
        control_group = QGroupBox("Control Settings")
        control_layout = QGridLayout(control_group)

        control_layout.addWidget(QLabel("Control Spacing:"), 0, 0)
        self.control_spacing_spin = QSpinBox()
        self.control_spacing_spin.setRange(0, 20)
        self.control_spacing_spin.setValue(7)
        control_layout.addWidget(self.control_spacing_spin, 0, 1)

        self.hide_window_rim_checkbox = QCheckBox("Hide Window Rim")
        self.hide_window_rim_checkbox.setChecked(False)
        control_layout.addWidget(self.hide_window_rim_checkbox, 1, 0)

        self.mini_toolbar_checkbox = QCheckBox("Mini Toolbar")
        self.mini_toolbar_checkbox.setChecked(False)
        control_layout.addWidget(self.mini_toolbar_checkbox, 1, 1)

        self.patch_appearance_checkbox = QCheckBox("Patch Appearance")
        self.patch_appearance_checkbox.setChecked(True)
        control_layout.addWidget(self.patch_appearance_checkbox, 2, 0)

        layout.addWidget(control_group)

        # Mica Settings
        mica_group = QGroupBox("Mica Settings")
        mica_layout = QVBoxLayout(mica_group)

        self.mica_header_checkbox = QCheckBox("Enable Mica Header")
        self.mica_header_checkbox.setChecked(True)
        mica_layout.addWidget(self.mica_header_checkbox)

        self.mica_sidebar_checkbox = QCheckBox("Enable Mica Sidebar")
        self.mica_sidebar_checkbox.setChecked(True)
        mica_layout.addWidget(self.mica_sidebar_checkbox)

        self.mica_titlebar_checkbox = QCheckBox("Enable Mica Titlebar")
        self.mica_titlebar_checkbox.setChecked(True)
        mica_layout.addWidget(self.mica_titlebar_checkbox)

        self.mica_menu_checkbox = QCheckBox("Enable Mica Menu")
        self.mica_menu_checkbox.setChecked(True)
        mica_layout.addWidget(self.mica_menu_checkbox)

        self.mica_window_bg_checkbox = QCheckBox("Enable Mica Window Background")
        self.mica_window_bg_checkbox.setChecked(True)
        mica_layout.addWidget(self.mica_window_bg_checkbox)

        layout.addWidget(mica_group)

        # Asset Slice Settings
        asset_group = QGroupBox("Asset Slice Settings")
        asset_layout = QGridLayout(asset_group)

        asset_layout.addWidget(QLabel("Window Frame Mask (1x):"), 0, 0)
        self.window_frame_mask_1x = QLineEdit("{16,16,0,0}")
        asset_layout.addWidget(self.window_frame_mask_1x, 0, 1)

        asset_layout.addWidget(QLabel("Window Frame Base (1x):"), 1, 0)
        self.window_frame_base_1x = QLineEdit("{16,48,0,0}")
        asset_layout.addWidget(self.window_frame_base_1x, 1, 1)

        asset_layout.addWidget(QLabel("Window Frame Mask (2x):"), 2, 0)
        self.window_frame_mask_2x = QLineEdit("{32,32,0,0}")
        asset_layout.addWidget(self.window_frame_mask_2x, 2, 1)

        asset_layout.addWidget(QLabel("Window Frame Base (2x):"), 3, 0)
        self.window_frame_base_2x = QLineEdit("{32,96,0,0}")
        asset_layout.addWidget(self.window_frame_base_2x, 3, 1)

        layout.addWidget(asset_group)

        # Info label
        self.info_label = QLabel("These settings will be applied to the settings.plist file in the theme folder.")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.info_label)

        layout.addStretch()

        # Set scroll area widget
        scroll_area.setWidget(container)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)