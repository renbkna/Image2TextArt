# ANSI-ASCII Art Generator

## Overview

The ANSI-ASCII Art Generator is a powerful tool that transforms images into beautiful and highly detailed ASCII art. It supports multiple rendering modes, each optimized for maximum detail and precision. The tool features both a command-line interface and an enhanced graphical user interface with advanced customization options.

## Features

- **High-detail conversion** in all modes:
  - **Grayscale**: Rich tonal variation with optimized character mapping
  - **ANSI 256-color**: Detailed color representation with optimized palette
  - **Truecolor**: Full 24-bit color with precise character selection
  - **HTML**: Web-friendly colorized output with custom styling
  - **Unicode Braille**: High resolution dot-pattern representation
  
- **Intelligent image processing**:
  - Advanced detail enhancement with local contrast optimization
  - High-quality dithering with mode-specific algorithms
  - Sophisticated edge detection and enhancement
  - Adaptive threshold calculation
  - Dynamic character mapping based on visual density
  
- **Expanded character sets**:
  - 13+ optimized character presets for different visual styles
  - Dense gradient sets for smooth transitions
  - Specialized sets for photos, line art, geometric patterns, and more
  - Custom character set support
  
- **Enhanced GUI**:
  - Auto-fit feature that adjusts to window size
  - Image analysis with recommended settings
  - Advanced display options with zoom controls
  - Font size and family selection
  - Custom background and foreground colors
  
- **Advanced customization**:
  - Brightness, contrast, and saturation controls
  - Gamma correction and detail level adjustment
  - Blur and sharpen filters
  - Aspect ratio fine-tuning
  - Edge threshold control

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

For convenient command-line entry points:

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

| Option             | Short | Description                                              |
| ------------------ | ----- | -------------------------------------------------------- |
| `--width`          | `-w`  | Set output width (default: 100)                          |
| `--color`          | `-c`  | Color mode: grayscale, ansi, truecolor, html, braille   |
| `--dither`         | `-d`  | Enable dithering                                         |
| `--edges`          | `-e`  | Enable edge detection                                    |
| `--preset`         | `-p`  | Choose character set preset                              |
| `--output`         | `-o`  | Save output to a file                                    |
| `--no-enhance`     |       | Disable auto contrast enhancement                        |
| `--edge-threshold` |       | Set edge detection threshold (0-255)                     |
| `--invert`         |       | Invert image colors                                      |
| `--aspect-ratio`   |       | Adjust aspect ratio correction                           |
| `--blur`           |       | Apply blur (0.0-10.0)                                    |
| `--sharpen`        |       | Apply sharpening (0.0-10.0)                             |
| `--brightness`     |       | Adjust brightness (0.5-2.0)                              |
| `--saturation`     |       | Adjust saturation (0.0-2.0)                              |
| `--custom-chars`   |       | Specify custom character set                             |

#### Example Usage

Convert an image to grayscale ASCII art with enhanced detail:

```sh
python -m ansi_ascii_art_generator.cli /path/to/image.jpg -c grayscale --sharpen 2.0 --contrast 1.2
```

Create Braille art with dithering:

```sh
python -m ansi_ascii_art_generator.cli /path/to/image.jpg -c braille -d -w 120
```

Use edge detection with custom threshold:

```sh
python -m ansi_ascii_art_generator.cli /path/to/image.jpg -e --edge-threshold 50
```

### GUI Mode

#### Launch GUI

To run the enhanced graphical user interface, execute:

```sh
python -m ansi_ascii_art_generator.gui
```

If you've installed in editable mode, you can also launch it using:

```sh
asciigen-gui
```

#### GUI Features

The GUI provides access to all features through an intuitive interface:

- **Basic tab**: Width, color mode, character set, aspect ratio, and basic toggles
- **Advanced tab**: Fine-tuning controls for edge threshold, blur, sharpen, brightness, saturation, contrast, detail level, gamma, and custom character sets
- **Display tab**: Font controls, auto-fit toggle, and zoom buttons
- **Color controls**: Custom background and foreground colors
- **Recommended settings**: Automatic analysis of the image to suggest optimal settings

## Character Sets

The generator includes numerous character sets optimized for different purposes:

- `block`: Block characters for solid shapes
- `dense`: Smooth gradient transitions
- `lineart`: Line-drawing characters for diagrams
- `classic`: Traditional ASCII art characters
- `unicode`: Unicode block characters
- `detailed`: Extensive gradient for photographic detail
- `binary`: Simple high-contrast (just 0 and 1)
- `minimal`: Clean, simple gradient
- `circles`: Circle-based characters for organic shapes
- `shading`: Pure shading blocks
- `geometric`: Geometric shapes
- `dots`: Braille-like patterns
- `contrast`: High contrast (space and full block)
- `photo`: Optimized for photographs
- `pixel`: Retro-style pixelated look
- `ultra`: Maximum detail character set

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
README.md
requirements.txt
setup.py
```

### Key Components

- `core.py`: The heart of the conversion engine with image processing
- `characters.py`: Character set definitions and density mapping
- `gui.py`: Enhanced graphical interface
- `cli.py`: Command-line interface
- `utils.py`: Helper functions and HTML output

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For issues or feature requests, open an issue on GitHub.
