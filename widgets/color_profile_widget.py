from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QLineEdit)
from PyQt5.QtCore import pyqtSignal

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