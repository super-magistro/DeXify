import re
from setuptools import setup, find_packages

with open("dextop.py", "r", encoding="utf-8") as f:
    match = re.search(r'__version__\s*=\s*"([^"]+)"', f.read())
    version = match.group(1) if match else "1.0.20"

setup(
    name="dextop-mode",
    version=version,
    py_modules=["dextop"],
    install_requires=[
        "customtkinter>=5.2.0",
        "Pillow",
        "qrcode",
        "zeroconf>=0.13.0",
    ],
    entry_points={
        "console_scripts": [
            "dextop-mode=dextop:main",
            "dextop=dextop:main",
        ],
    },
)
