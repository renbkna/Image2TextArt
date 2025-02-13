import numpy as np
from PIL import Image, ImageOps, ImageFilter
from .characters import CharacterSet


class AsciiArtGenerator:
    def __init__(
        self,
        image_path,
        output_width=100,
        color_mode="ansi",  # options: "grayscale", "ansi", "truecolor", "html", "braille"
        dithering=False,
        edge_detect=False,
        preset="classic",
        enhance_contrast=True,
        aspect_ratio_correction=0.55,
    ):
        self.image = Image.open(image_path)
        self.output_width = output_width
        self.color_mode = color_mode
        self.dithering = dithering
        self.edge_detect = edge_detect
        self.preset = preset
        self.enhance_contrast = enhance_contrast
        self.aspect_ratio_correction = aspect_ratio_correction
        self.aspect_ratio = self.image.height / self.image.width
        self.characters = self._get_character_set()

    def _get_character_set(self):
        try:
            return CharacterSet.get_preset(self.preset)
        except ValueError:
            # Fallback to classic if preset not found
            return CharacterSet.get_preset("classic")

    def _preprocess_image(self):
        # Optionally apply edge detection
        if self.edge_detect:
            self.image = self.image.filter(ImageFilter.FIND_EDGES)

        # Always convert to RGB (even for grayscale we'll convert later)
        img = self.image.convert("RGB")

        # Enhance contrast for better clarity if requested
        if self.enhance_contrast:
            img = ImageOps.autocontrast(img)

        # If the user wants grayscale output, convert the image
        if self.color_mode == "grayscale":
            img = ImageOps.grayscale(img)

        target_width = max(1, self.output_width)
        target_height = max(
            1, int(target_width * self.aspect_ratio * self.aspect_ratio_correction)
        )
        img = img.resize((target_width, target_height))

        # If dithering is enabled and we are in grayscale, apply dithering
        if self.dithering and self.color_mode == "grayscale":
            img = img.convert("1", dither=Image.FLOYDSTEINBERG).convert("L")

        return np.array(img)

    def _map_to_ascii(self, luminance):
        max_brightness = 255
        index = round((luminance / max_brightness) * (len(self.characters) - 1))
        index = min(max(index, 0), len(self.characters) - 1)
        return self.characters[index]

    def _get_ansi_color(self, r, g, b):
        return f"\033[38;2;{r};{g};{b}m"

    def _generate_braille_art(self):
        # For braille art, work in grayscale
        img = self.image.convert("L")
        if self.enhance_contrast:
            img = ImageOps.autocontrast(img)

        # For braille, each character represents a block of 2 columns x 4 rows
        target_width = max(1, self.output_width * 2)  # scale width accordingly
        new_height = int(
            target_width * self.aspect_ratio * self.aspect_ratio_correction
        )
        # Make sure height is a multiple of 4 for even blocks
        new_height = (new_height + 3) // 4 * 4
        img = img.resize((target_width, new_height))
        arr = np.array(img)

        rows, cols = arr.shape
        braille_lines = []
        threshold = 128  # adjust threshold as needed

        # Iterate over blocks (each block is 4 rows x 2 columns)
        for row in range(0, rows, 4):
            line_chars = []
            for col in range(0, cols, 2):
                braille_dot = 0
                # Map positions within the 2x4 block to braille dot bits:
                # (0,0): dot 1 (0x01)
                # (1,0): dot 2 (0x02)
                # (2,0): dot 3 (0x04)
                # (3,0): dot 7 (0x40)
                # (0,1): dot 4 (0x08)
                # (1,1): dot 5 (0x10)
                # (2,1): dot 6 (0x20)
                # (3,1): dot 8 (0x80)
                for dy in range(4):
                    for dx in range(2):
                        pixel_row = row + dy
                        pixel_col = col + dx
                        if pixel_row < rows and pixel_col < cols:
                            # For braille art, darker pixels are “on”
                            if arr[pixel_row, pixel_col] < threshold:
                                if dx == 0 and dy == 0:
                                    braille_dot |= 0x01
                                elif dx == 0 and dy == 1:
                                    braille_dot |= 0x02
                                elif dx == 0 and dy == 2:
                                    braille_dot |= 0x04
                                elif dx == 0 and dy == 3:
                                    braille_dot |= 0x40
                                elif dx == 1 and dy == 0:
                                    braille_dot |= 0x08
                                elif dx == 1 and dy == 1:
                                    braille_dot |= 0x10
                                elif dx == 1 and dy == 2:
                                    braille_dot |= 0x20
                                elif dx == 1 and dy == 3:
                                    braille_dot |= 0x80
                braille_char = chr(0x2800 + braille_dot)
                line_chars.append(braille_char)
            braille_lines.append("".join(line_chars))
        return "\n".join(braille_lines)

    def generate_ascii(self):
        if self.color_mode == "braille":
            return self._generate_braille_art()

        img_array = self._preprocess_image()
        output_lines = []
        is_grayscale = len(img_array.shape) == 2

        for row in img_array:
            line = []
            for pixel in row:
                if is_grayscale:
                    char = self._map_to_ascii(pixel)
                    line.append(char)
                else:
                    r, g, b = pixel[:3]
                    luminance = 0.299 * r + 0.587 * g + 0.114 * b
                    char = self._map_to_ascii(luminance)
                    if self.color_mode == "truecolor":
                        line.append(f"{self._get_ansi_color(r, g, b)}{char}\033[0m")
                    elif self.color_mode == "ansi":
                        ansi_code = 16 + (36 * (r // 51)) + (6 * (g // 51)) + (b // 51)
                        line.append(f"\033[38;5;{ansi_code}m{char}\033[0m")
                    else:
                        line.append(char)
            output_lines.append("".join(line))

        return "\n".join(output_lines)
