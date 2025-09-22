from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGroupBox, QCheckBox, QSlider, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPixmap, QPainter
from utils.color_utils import adjust_color_hsv, hex_to_rgb, rgb_to_hex


class ColorVariationsWidget(QWidget):
    variationSelected = pyqtSignal(str)  # Emite a cor selecionada

    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_color = "#E6E0FF"
        self.variations = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Enable variations checkbox
        self.enable_variations = QCheckBox("Enable Color Variations")
        self.enable_variations.setChecked(False)
        layout.addWidget(self.enable_variations)

        # Variations intensity
        intensity_group = QGroupBox("Variation Intensity")
        intensity_layout = QHBoxLayout(intensity_group)

        intensity_layout.addWidget(QLabel("Intensity:"))
        self.variation_intensity = QSlider(Qt.Horizontal)
        self.variation_intensity.setRange(10, 100)
        self.variation_intensity.setValue(25)
        self.variation_intensity.valueChanged.connect(self.update_variations)
        intensity_layout.addWidget(self.variation_intensity)

        layout.addWidget(intensity_group)

        # Complementary color checkbox
        self.include_complementary = QCheckBox("Include Complementary Color")
        self.include_complementary.setChecked(True)
        self.include_complementary.stateChanged.connect(self.update_variations)
        layout.addWidget(self.include_complementary)

        # Variations preview
        self.variations_layout = QGridLayout()
        self.variations_widget = QWidget()
        self.variations_widget.setLayout(self.variations_layout)
        layout.addWidget(self.variations_widget)

        layout.addStretch()

    def set_base_color(self, hex_color):
        self.base_color = hex_color
        self.update_variations()

    def update_variations(self):
        # Clear previous variations
        for i in reversed(range(self.variations_layout.count())):
            self.variations_layout.itemAt(i).widget().setParent(None)

        if not self.enable_variations.isChecked():
            return

        intensity = self.variation_intensity.value() / 100.0
        self.variations = self.generate_color_variations(
            self.base_color,
            intensity,
            self.include_complementary.isChecked()
        )

        # Display variations
        for i, color in enumerate(self.variations):
            color_widget = ColorSwatchWidget(color)
            color_widget.colorSelected.connect(self.variationSelected.emit)
            self.variations_layout.addWidget(color_widget, i // 4, i % 4)

    def generate_color_variations(self, base_hex, intensity, include_complementary=True):
        """Generate color variations from base color"""
        r, g, b = hex_to_rgb(base_hex)
        variations = []

        # Original color
        variations.append(base_hex)

        # Light variations
        variations.append(rgb_to_hex(*adjust_color_hsv(r, g, b, 1.0, 1.0 + intensity)))
        variations.append(rgb_to_hex(*adjust_color_hsv(r, g, b, 1.0 - intensity, 1.0)))
        variations.append(rgb_to_hex(*adjust_color_hsv(r, g, b, 1.0 - intensity, 1.0 + intensity)))

        # Dark variations
        variations.append(rgb_to_hex(*adjust_color_hsv(r, g, b, 1.0, 1.0 - intensity)))
        variations.append(rgb_to_hex(*adjust_color_hsv(r, g, b, 1.0 + intensity, 1.0)))
        variations.append(rgb_to_hex(*adjust_color_hsv(r, g, b, 1.0 + intensity, 1.0 - intensity)))

        # Complementary (optional)
        if include_complementary:
            h, s, v = self.rgb_to_hsv(r, g, b)
            comp_h = (h + 0.5) % 1.0
            comp_r, comp_g, comp_b = self.hsv_to_rgb(comp_h, s, v)
            variations.append(rgb_to_hex(comp_r, comp_g, comp_b))

        return variations

    def rgb_to_hsv(self, r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        h, s, v = self._rgb_to_hsv(r, g, b)
        return h, s, v

    def hsv_to_rgb(self, h, s, v):
        r, g, b = self._hsv_to_rgb(h, s, v)
        return int(r * 255), int(g * 255), int(b * 255)

    def _rgb_to_hsv(self, r, g, b):
        # Simple RGB to HSV conversion
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val

        if max_val == min_val:
            h = 0
        elif max_val == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif max_val == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        else:
            h = (60 * ((r - g) / diff) + 240) % 360

        s = 0 if max_val == 0 else diff / max_val
        v = max_val

        return h / 360, s, v

    def _hsv_to_rgb(self, h, s, v):
        # Simple HSV to RGB conversion
        h = h * 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c

        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return r + m, g + m, b + m


class ColorSwatchWidget(QWidget):
    colorSelected = pyqtSignal(str)

    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(40, 40)
        self.setToolTip(color)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(self.color))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, self.width(), self.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.colorSelected.emit(self.color)