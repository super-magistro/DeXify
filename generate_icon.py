#!/usr/bin/env python3
"""
Standalone icon generator for DeXtop Mode.
Used by GitHub Actions CI (headless, no display/tkinter required).
Generates icon.png in CONFIG_DIR and optionally icon.ico in the current directory.
"""
import os
import sys
from PIL import Image, ImageDraw

CONFIG_DIR = os.path.expanduser("~/.config/dextop")
ICON_FILE = os.path.join(CONFIG_DIR, "icon.png")


def generate_icon_png(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    pixels = img.load()
    for y in range(512):
        for x in range(512):
            ratio = (x + y) / 1024.0
            pixels[x, y] = (
                int(15 + 73 * ratio),
                int(23 + 5 * ratio),
                int(42 + 93 * ratio),
                255
            )
    mask = Image.new("L", (512, 512), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([20, 20, 492, 492], radius=100, fill=255)
    img.putalpha(mask)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([100, 110, 412, 310], radius=20, outline=(255, 255, 255, 255), width=16)
    draw.rectangle([236, 310, 276, 360], fill=(255, 255, 255, 255))
    draw.rounded_rectangle([180, 360, 332, 385], radius=8, fill=(255, 255, 255, 255))
    draw.rounded_rectangle([310, 180, 420, 390], radius=15, fill=(15, 23, 42, 255), outline=(0, 240, 255, 255), width=12)
    draw.rounded_rectangle([345, 370, 385, 375], radius=2, fill=(0, 240, 255, 255))
    draw.ellipse([358, 192, 372, 206], fill=(0, 240, 255, 255))
    img.save(output_path)
    return img


def generate_icon_ico(png_path, ico_path):
    img = Image.open(png_path).convert("RGBA")
    img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"[OK] icon.ico saved to: {ico_path}")


if __name__ == "__main__":
    # Always generate the base PNG
    generate_icon_png(ICON_FILE)
    print(f"[OK] icon.png saved to: {ICON_FILE}")

    # If --ico flag is passed, also generate icon.ico in current directory
    if "--ico" in sys.argv:
        generate_icon_ico(ICON_FILE, "icon.ico")
