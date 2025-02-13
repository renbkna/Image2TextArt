from PIL import Image


def image_to_html(ascii_art, original_image_path, output_path, font_size=8):
    """
    Generate an HTML file that displays the ASCII art with colored spans.
    For each character, the corresponding pixel in the original image (sampled proportionally)
    is used to set the text color.
    """
    img = Image.open(original_image_path).convert("RGB")
    ascii_lines = ascii_art.split("\n")
    num_lines = len(ascii_lines)
    html = f"""<pre style="font-size: {font_size}pt; line-height: 1em; letter-spacing: 0; font-family: monospace;">"""

    for j, line in enumerate(ascii_lines):
        if not line:
            html += "<br/>"
            continue
        num_chars = len(line)
        html_line = []
        for i, char in enumerate(line):
            x = int(i * img.width / num_chars)
            y = int(j * img.height / num_lines)
            pixel = img.getpixel((min(x, img.width - 1), min(y, img.height - 1)))
            r, g, b = pixel
            html_line.append(f"<span style='color: rgb({r},{g},{b})'>{char}</span>")
        html += "".join(html_line) + "<br/>"

    html += "</pre>"
    with open(output_path, "w") as f:
        f.write(html)


def calculate_best_width(image_path, terminal_width=100):
    with Image.open(image_path) as img:
        return min(terminal_width, img.width)
