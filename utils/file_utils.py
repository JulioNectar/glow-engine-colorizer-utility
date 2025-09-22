from pathlib import Path
import shutil

def get_all_image_files(directory, supported_extensions):
    """Get all image files from directory"""
    files = []
    for item in directory.iterdir():
        if item.name == 'backup':
            continue
        if item.is_file() and item.suffix.lower() in supported_extensions:
            files.append(item)
    return files

def get_top_level_files(directory, tint_checkboxes=True, tint_windowframes=True, supported_extensions=None):
    """Get files to process based on user preferences"""
    if supported_extensions is None:
        supported_extensions = ['.png', '.jpg', '.jpeg']

    files = []
    for item in directory.iterdir():
        if item.name == 'backup':
            continue
        if item.is_file() and item.suffix.lower() in supported_extensions:
            filename_lower = item.name.lower()

            # Always include Mica files regardless of other filters
            if 'mica' in filename_lower or item.name.startswith('Mica:'):
                files.append(item)
                continue

            if not tint_checkboxes and filename_lower.startswith('checkbox'):
                continue
            if not tint_windowframes and (filename_lower.startswith('windowframe') or filename_lower.startswith('frame')):
                continue
            files.append(item)
    return files