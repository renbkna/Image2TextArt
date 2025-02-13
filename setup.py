from setuptools import setup, find_packages

setup(
    name="ansi_ascii_art_generator",
    version="1.3.0",
    packages=find_packages(),
    install_requires=["Pillow>=9.0.0", "numpy>=1.22.0", "colorama>=0.4.4"],
    entry_points={
        "console_scripts": [
            "asciigen = ansi_ascii_art_generator.cli:main",
            "asciigen-gui = ansi_ascii_art_generator.gui:run_gui",
        ]
    },
)
