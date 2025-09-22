from pathlib import Path
from PIL import Image, ImageOps
from .color_utils import hex_to_rgb, adjust_color_hsv, is_white_pixel, is_black_pixel

def colorize_enhanced(file_path, color, intensity, saturation, brightness,
                      out_folder, input_dir, preserve_transparency=True,
                      preserve_whites=True, preserve_blacks=True,
                      white_threshold=245, black_threshold=30,
                      pattern_path=None, pattern_blend=0,
                      convert_to_grayscale=False):
    """Enhanced colorization with optional grayscale pre-processing"""
    img = Image.open(file_path).convert("RGBA")

    if convert_to_grayscale:
        # Convert to grayscale but keep alpha
        gray = ImageOps.grayscale(img)
        img = Image.merge("RGBA", (gray, gray, gray, img.getchannel("A")))

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
