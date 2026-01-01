# Download fonts script
import requests

fonts_urls = {
    'DejaVuSans.ttf': 'https://sourceforge.net/projects/dejavu/files/dejavu/2.37/dejavu-fonts-ttf-2.37.zip/download',
}

# Alternative: Use system fonts if available
import os
import shutil

# Check for system fonts (macOS)
system_font_paths = [
    '/System/Library/Fonts',
    '/Library/Fonts',
    '~/Library/Fonts'
]

vietnamese_fonts = [
    'Arial Unicode.ttf',
    'Arial.ttf',
    'Helvetica.ttc',
]

print("Searching for Vietnamese-compatible fonts on system...")
for font_dir in system_font_paths:
    font_dir = os.path.expanduser(font_dir)
    if os.path.exists(font_dir):
        for font_file in os.listdir(font_dir):
            if 'arial' in font_file.lower() or 'helvetica' in font_file.lower():
                print(f"Found: {os.path.join(font_dir, font_file)}")
