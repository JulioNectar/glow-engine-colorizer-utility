import colorsys

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

def rgb_to_hex(r, g, b):
    """Convert RGB values to HEX string"""
    return f"#{r:02x}{g:02x}{b:02x}"