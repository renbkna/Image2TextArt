from PIL import Image, ImageOps
import numpy as np
import os


def image_to_html(ascii_art, original_image_path, output_path, font_size=8, font_family="monospace", background_color="#000000"):
    """
    Generate an HTML file that displays the ASCII art with colored spans.
    For each character, the corresponding pixel in the original image (sampled proportionally)
    is used to set the text color.
    
    Args:
        ascii_art: The ASCII art string
        original_image_path: Path to the original image
        output_path: Path to save the HTML file
        font_size: Font size in points
        font_family: Font family to use
        background_color: Background color in hex format
    """
    img = Image.open(original_image_path).convert("RGB")
    ascii_lines = ascii_art.split("\n")
    num_lines = len(ascii_lines)
    
    # Create a more sophisticated HTML template with better styling
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASCII Art Visualization</title>
    <style>
        body {{
            background-color: {background_color};
            margin: 0;
            padding: 20px;
        }}
        .ascii-art {{
            font-size: {font_size}pt;
            line-height: 1em;
            letter-spacing: 0;
            font-family: {font_family}, "Courier New", Courier, monospace;
            white-space: pre;
            text-align: center;
            padding: 20px;
            display: inline-block;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
            background-color: {background_color};
        }}
        .container {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 90vh;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="ascii-art">"""

    # Process the ASCII art and map colors from original image
    for j, line in enumerate(ascii_lines):
        if not line:
            html += "<br/>"
            continue
        num_chars = len(line)
        html_line = []
        for i, char in enumerate(line):
            # Sample the original image at proportionally mapped coordinates
            x = int(i * img.width / num_chars)
            y = int(j * img.height / num_lines)
            pixel = img.getpixel((min(x, img.width - 1), min(y, img.height - 1)))
            r, g, b = pixel
            
            # Apply color to the character
            html_line.append(f"<span style='color: rgb({r},{g},{b})'>{char}</span>")
        html += "".join(html_line) + "<br/>"

    # Complete the HTML template
    html += """
        </div>
    </div>
</body>
</html>"""

    # Write the HTML file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def calculate_best_width(image_path, terminal_width=100):
    """
    Calculate the optimal width for ASCII art based on image dimensions and terminal width.
    
    Args:
        image_path: Path to the input image
        terminal_width: Available width in the terminal
        
    Returns:
        The optimal width for the ASCII art
    """
    with Image.open(image_path) as img:
        img_width, img_height = img.size
        
        # For very wide or panoramic images, scale down further
        aspect_ratio = img_width / img_height
        
        if aspect_ratio > 2.5:  # Very wide image
            return min(terminal_width, int(terminal_width * 0.8))
        elif aspect_ratio < 0.5:  # Very tall image
            return min(terminal_width, int(terminal_width * 1.2))
        else:
            return min(terminal_width, img_width)


def detect_image_edges(image_path, threshold=30, sigma=2.0):
    """
    Perform edge detection on an image using Sobel filters.
    
    Args:
        image_path: Path to the input image
        threshold: Edge detection threshold (0-255)
        sigma: Gaussian blur sigma before edge detection
        
    Returns:
        PIL Image with detected edges
    """
    from PIL import ImageFilter, ImageEnhance
    
    img = Image.open(image_path).convert('L')  # Convert to grayscale
    
    # Apply Gaussian blur to reduce noise
    if sigma > 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=sigma))
    
    # Apply edge detection
    img = img.filter(ImageFilter.FIND_EDGES)
    
    # Apply threshold
    img = img.point(lambda p: p > threshold and 255)
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    
    return img


def optimize_character_contrast(ascii_art, min_darkness=0.1, max_darkness=0.9):
    """
    Optimize the contrast in ASCII art by stretching the distribution of character densities.
    
    Args:
        ascii_art: The ASCII art string
        min_darkness: Minimum darkness value (0.0-1.0)
        max_darkness: Maximum darkness value (0.0-1.0)
        
    Returns:
        Optimized ASCII art string
    """
    from .characters import CharacterSet
    
    lines = ascii_art.split('\n')
    unique_chars = set(''.join(lines))
    
    # Get character densities
    densities = {char: CharacterSet.get_character_density(char) for char in unique_chars}
    
    # Find current min and max densities
    current_min = min(densities.values())
    current_max = max(densities.values())
    
    # Skip optimization if there's not enough variation
    if current_max - current_min < 0.1:
        return ascii_art
    
    # Create a mapping function to stretch contrast
    def remap_density(val):
        if current_max == current_min:
            return val
        return min_darkness + (val - current_min) * (max_darkness - min_darkness) / (current_max - current_min)
    
    # Create a dictionary to map characters to their new densities
    new_densities = {char: remap_density(density) for char, density in densities.items()}
    
    # Sort characters by their new densities
    sorted_chars = sorted(new_densities.keys(), key=lambda c: new_densities[c])
    
    # Create a mapping from old to new characters
    char_map = {}
    num_chars = len(sorted_chars)
    for i, char in enumerate(sorted_chars):
        new_idx = int(i / num_chars * len(sorted_chars))
        char_map[char] = sorted_chars[new_idx]
    
    # Apply mapping to ASCII art
    optimized_lines = []
    for line in lines:
        optimized_line = ''.join(char_map.get(c, c) for c in line)
        optimized_lines.append(optimized_line)
    
    return '\n'.join(optimized_lines)


def save_as_ansi_text(ascii_art, output_path):
    """
    Save ASCII art with ANSI color codes to a text file.
    
    Args:
        ascii_art: The ASCII art string with ANSI color codes
        output_path: Path to save the text file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ascii_art)
