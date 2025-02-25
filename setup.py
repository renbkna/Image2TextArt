from setuptools import setup, find_packages

setup(
    name="ansi_ascii_art_generator",
    version="2.0.0",  # Updated to match __init__.py version
    packages=find_packages(),
    install_requires=["Pillow>=11.1.0", "numpy>=2.2.3", "colorama>=0.4.6"],
    description="A powerful ASCII art generator with multiple modes and advanced features",
    author="Berkan",
    entry_points={
        "console_scripts": [
            "asciigen = ansi_ascii_art_generator.cli:main",
            "asciigen-gui = ansi_ascii_art_generator.gui:run_gui",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Artistic Software",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
    keywords="ascii, art, image, conversion, braille, ansi, terminal",
    python_requires=">=3.7",
)
