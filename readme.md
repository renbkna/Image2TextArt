# ANSI-ASCII Art Generator

## Overview

The ANSI-ASCII Art Generator is a tool that converts images into ASCII representations using various character sets and color modes. It supports both command-line and graphical interfaces and provides multiple customization options.

## Features

- Convert images to ASCII art
- Support for multiple color modes:
  - Grayscale
  - ANSI 256-color
  - Truecolor
  - HTML
  - Unicode Braille
- Adjustable output width
- Character set presets
- Edge detection and dithering options
- GUI and CLI modes

## Installation

### Prerequisites

- Python 3.7 or later
- `pip` package manager

### Install Required Dependencies

Clone the repository and install the required dependencies:

```sh
git clone https://github.com/renbkna/ansi-ascii-art-generator
cd ansi-ascii-art-generator
pip install -r requirements.txt
```

### Optional: Install in Editable Mode

If you want to use convenient command-line entry points or make development easier, install the app in editable mode:

```sh
pip install -e .
```

This registers the entry points defined in `setup.py`, allowing you to run the app with commands like `asciigen-gui`.

## Usage

### CLI Mode

#### Basic Usage

To generate ASCII art from an image using the command-line interface, run:

```sh
python -m ansi_ascii_art_generator.cli /path/to/image.jpg
```

#### Options

| Option         | Short | Description                                                              |
| -------------- | ----- | ------------------------------------------------------------------------ |
| `--width`      | `-w`  | Set output width (default: 100)                                          |
| `--color`      | `-c`  | Color mode: grayscale, ansi, truecolor, html, braille (default: braille) |
| `--dither`     | `-d`  | Enable dithering                                                         |
| `--edges`      | `-e`  | Enable edge detection                                                    |
| `--preset`     | `-p`  | Choose character set preset                                              |
| `--output`     | `-o`  | Save output to a file                                                    |
| `--no-enhance` |       | Disable auto contrast enhancement                                        |

#### Example Usage

Convert an image to grayscale ASCII art:

```sh
python -m ansi_ascii_art_generator.cli /path/to/image.jpg -c grayscale
```

Convert an image using ANSI color mode with 120-character width:

```sh
python -m ansi_ascii_art_generator.cli /path/to/image.jpg -c ansi -w 120
```

Save the output to a file:

```sh
python -m ansi_ascii_art_generator.cli /path/to/image.jpg -o output.txt
```

### GUI Mode

#### Launch GUI

To run the graphical user interface, execute:

```sh
python -m ansi_ascii_art_generator.gui
```

If you've installed in editable mode, you can also launch it using:

```sh
asciigen-gui
```

## Development

### Repository Structure

```plaintext
ansi_ascii_art_generator/
├── __init__.py
├── characters.py
├── cli.py
├── core.py
├── gui.py
├── utils.py
.gitignore
LICENSE
readme.md
requirements.txt
setup.py
```

### Running Tests

Tests are not included yet. To add test cases, consider using a framework like `pytest`.

## Contribution

1. Fork the repository
2. Create a feature branch
3. Make your changes and commit with a descriptive message
4. Push to your fork and submit a pull request

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For issues or feature requests, open an issue on GitHub.
