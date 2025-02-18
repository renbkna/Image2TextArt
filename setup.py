from setuptools import setup, find_packages

setup(
    name="ansi_ascii_art_generator",
    version="1.3.0",
    packages=find_packages(),
    install_requires=["Pillow>=11.1.0", "numpy>=2.2.3", "colorama>=0.4.6"],
    entry_points={
        "console_scripts": [
            "asciigen = ansi_ascii_art_generator.cli:main",
            "asciigen-gui = ansi_ascii_art_generator.gui:run_gui",
        ]
    },
)
