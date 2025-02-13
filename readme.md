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

# Installation

### Prerequisites

- Python 3.7 or later
- `pip` package manager

### Install Required Dependencies

Run the following command to install the required dependencies:

```sh
pip install -r requirements.txt
```

### Manual Installation

Alternatively, you can install the dependencies manually:

```sh
pip install Pillow numpy colorama
```

# Usage

## CLI Mode

### Basic Usage

To generate ASCII art from an image:

```sh
python -m ascii_art_generator.cli /path/to/image.jpg
```

### Options

| Option         | Short | Description                                                              |
| -------------- | ----- | ------------------------------------------------------------------------ |
| `--width`      | `-w`  | Set output width (default: 100)                                          |
| `--color`      | `-c`  | Color mode: grayscale, ansi, truecolor, html, braille (default: braille) |
| `--dither`     | `-d`  | Enable dithering                                                         |
| `--edges`      | `-e`  | Enable edge detection                                                    |
| `--preset`     | `-p`  | Choose character set preset                                              |
| `--output`     | `-o`  | Save output to a file                                                    |
| `--no-enhance` |       | Disable auto contrast enhancement                                        |

### Example Usage

Convert an image to grayscale ASCII art:

```sh
python -m ascii_art_generator.cli /path/to/image.jpg -c grayscale
```

Convert an image using ANSI color mode with 120-character width:

```sh
python -m ascii_art_generator.cli /path/to/image.jpg -c ansi -w 120
```

Save output to a file:

```sh
python -m ascii_art_generator.cli /path/to/image.jpg -o output.txt
```

## GUI Mode

### Launch GUI

To run the graphical user interface:

```sh
python -m ascii_art_generator.gui or simply run asciigen-gui
```

### GUI Features

- **Open Image:** Select an image from file explorer.
- **Generate ASCII:** Convert the loaded image into ASCII art.
- **Save Output:** Save the generated ASCII art to a text file.
- **Adjust Settings:** Modify width, color mode, character preset, and enhancement options.

# Development

### Repository Structure

```
ascii_art_generator/
├── __init__.py
├── characters.py
├── cli.py
├── core.py
├── gui.py
├── utils.py
├── requirements.txt
├── setup.py
```

### Running Tests

Tests are not included yet. To add test cases, consider using `pytest`.

# Contribution

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes and commit with a descriptive message
4. Push to your fork and submit a pull request

# License

This project is open-source under the MIT License.

# Contact

For issues or feature requests, open an issue on GitHub.
