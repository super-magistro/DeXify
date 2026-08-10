from setuptools import setup, find_packages

setup(
    name="dextop-mode",
    version="1.0.10",
    py_modules=["dextop"],
    install_requires=[
        "customtkinter>=5.2.0",
        "pillow>=9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "dextop-mode=dextop:main",
            "dextop=dextop:main",
        ],
    },
)
