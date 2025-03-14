import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageChops, ImageStat
import os
from .characters import CharacterSet
from ._colormap import ColorMapper

class AsciiArtGenerator:
    def __init__(
        self,
        image_input,
        output_width=100,
        color_mode="ansi",  # options: "grayscale", "ansi", "truecolor", "html", "braille"
        dithering=False,
        edge_detect=False,
        preset="classic",
        enhance_contrast=True,
        aspect_ratio_correction=0.55,
        invert=False,
        edge_threshold=75,
        blur=0,
        sharpen=0,
        brightness=1.0,
        saturation=1.0,
        contrast=1.0,
        detail_level=1.0,
        gamma=1.0,
    ):
        """
        Initialize the ASCII art generator with the given parameters.
        
        Args:
            image_input: Either a file path (str) or a PIL Image object
            output_width: Width of the ASCII art in characters
            color_mode: "grayscale", "ansi", "truecolor", "html", or "braille"
            dithering: Whether to apply dithering
            edge_detect: Whether to apply edge detection
            preset: Character set preset name
            enhance_contrast: Whether to enhance contrast
            aspect_ratio_correction: Aspect ratio correction factor
            invert: Whether to invert colors
            edge_threshold: Edge detection threshold (0-255)
            blur: Blur amount (0.0-10.0)
            sharpen: Sharpen amount (0.0-10.0)
            brightness: Brightness adjustment (0.5-2.0)
            saturation: Saturation adjustment (0.0-2.0)
            contrast: Contrast adjustment (0.5-2.0)
            detail_level: Detail level adjustment (0.1-2.0)
            gamma: Gamma correction (0.5-2.0)
        """
        # Handle input that can be either a file path or a PIL Image
        if isinstance(image_input, str):
            # It's a file path
            self.image_path = image_input
            self.image = Image.open(image_input)
        elif isinstance(image_input, Image.Image):
            # It's a PIL Image object
            self.image = image_input
            self.image_path = getattr(image_input, 'filename', None)
        else:
            raise TypeError("image_input must be a file path or a PIL Image object")
            
        self.output_width = output_width
        self.color_mode = color_mode
        self.dithering = dithering
        self.edge_detect = edge_detect
        self.preset = preset
        self.enhance_contrast = enhance_contrast
        self.aspect_ratio_correction = aspect_ratio_correction
        self.invert = invert
        self.edge_threshold = edge_threshold
        self.blur = blur
        self.sharpen = sharpen
        self.brightness = brightness
        self.saturation = saturation
        self.contrast = contrast
        self.detail_level = detail_level
        self.gamma = gamma
        self.aspect_ratio = self.image.height / self.image.width
        self.characters = self._get_character_set()
        
        # Character density is now cached at the class level in CharacterSet

    def _get_character_set(self):
        """Get the character set based on the selected preset."""
        try:
            return CharacterSet.get_preset(self.preset)
        except ValueError:
            # Fallback to classic if preset not found
            return CharacterSet.get_preset("classic")

    def _preprocess_image(self):
        """
        Apply preprocessing to the image before ASCII conversion.
        Optimized version with reduced intermediate image creation.
        """
        # Always convert to RGB (even for grayscale we'll convert later)
        img = self.image.convert("RGB")
        
        # Apply combined adjustments to reduce intermediate image creation
        adjustments = []
        
        # Stack adjustments that need to be applied
        if self.gamma != 1.0:
            # Using a lookup table is more efficient than a point operation
            gamma_map = [int(255 * (i / 255) ** (1.0 / self.gamma)) for i in range(256)]
            img = img.point(lambda p: gamma_map[p])
        
        # Group enhancers together for better performance
        if self.saturation != 1.0 or self.brightness != 1.0 or self.contrast != 1.0:
            if self.saturation != 1.0:
                adjustments.append((ImageEnhance.Color, self.saturation))
            
            if self.brightness != 1.0:
                adjustments.append((ImageEnhance.Brightness, self.brightness))
                
            if self.contrast != 1.0:
                adjustments.append((ImageEnhance.Contrast, self.contrast))
                
            # Apply all enhancers in sequence
            for enhancer_class, value in adjustments:
                img = enhancer_class(img).enhance(value)
        
        # Apply filters only if needed
        if self.blur > 0 or self.sharpen > 0 or self.edge_detect:
            if self.blur > 0:
                img = img.filter(ImageFilter.GaussianBlur(self.blur))
                
            if self.sharpen > 0:
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(1.0 + self.sharpen)
            
            if self.edge_detect:
                # Create a sophisticated edge detection algorithm
                # First, create an edge-detected version
                edge_img = img.filter(ImageFilter.FIND_EDGES)
                
                # Convert to grayscale for thresholding
                edge_img = edge_img.convert("L")
                
                # Apply adaptive thresholding based on image content
                stat = ImageStat.Stat(edge_img)
                edge_mean = stat.mean[0]
                adaptive_threshold = min(max(edge_mean * 0.7, self.edge_threshold), 200)
                
                # Apply threshold to make edges more distinct
                edge_img = edge_img.point(lambda p: 255 if p > adaptive_threshold else 0)
                
                # Convert back to RGB
                edge_img = edge_img.convert("RGB")
                
                # Blend original with edges based on detail level
                if self.detail_level < 1.0:
                    blend_factor = min(max(self.detail_level, 0.0), 1.0)
                    img = Image.blend(img, edge_img, blend_factor)
                else:
                    img = edge_img

        # Enhance contrast for better clarity if requested
        if self.enhance_contrast:
            img = ImageOps.autocontrast(img, cutoff=(2, 2))

        # Color mode conversions
        if self.color_mode == "grayscale" or self.color_mode == "braille":
            # For grayscale conversion, use a more sophisticated approach
            if self.color_mode == "grayscale":
                # Optimized grayscale conversion - use ImageOps directly
                img = ImageOps.grayscale(img)
            else:
                img = ImageOps.grayscale(img)
            
        # Invert if requested
        if self.invert:
            img = ImageOps.invert(img)

        # Calculate optimal dimensions based on ASCII aspect ratio correction
        target_width = max(1, self.output_width)
        height_correction = self.aspect_ratio_correction
        
        # Adjust ratio to account for the specific character set
        if len(self.characters) > 0:
            # Wide character sets need further correction
            avg_char_width = sum(1 for c in self.characters if ord(c) > 0x2500) / len(self.characters)
            if avg_char_width > 0.5:  # If many wide characters
                height_correction *= 1.2
        
        target_height = max(
            1, int(target_width * self.aspect_ratio * height_correction)
        )
        
        # Use high-quality resizing for better detail preservation
        img = img.resize((target_width, target_height), Image.LANCZOS)

        # Apply specialized dithering based on the mode
        if self.dithering:
            if self.color_mode == "grayscale" or self.color_mode == "braille":
                # For grayscale/braille modes, use Floyd-Steinberg dithering
                img = img.convert("1", dither=Image.FLOYDSTEINBERG).convert("L")
            elif self.color_mode in ["ansi", "truecolor", "html"]:
                # For color modes, apply optimized dithering
                if img.mode == "RGB":
                    r, g, b = img.split()
                    r = r.convert("1", dither=Image.FLOYDSTEINBERG).convert("L")
                    g = g.convert("1", dither=Image.FLOYDSTEINBERG).convert("L")
                    b = b.convert("1", dither=Image.FLOYDSTEINBERG).convert("L")
                    img = Image.merge("RGB", (r, g, b))

        return np.array(img)

    def _map_to_ascii(self, luminance, inverted=False):
        """
        Map a luminance value to an ASCII character from the selected character set.
        If inverted is True, dark pixels will be mapped to lighter characters and vice versa.
        Uses optimized character density lookup.
        """
        if not self.characters:
            return " "  # Return space if character set is empty
        
        # For aesthetics, map to characters based on their visual density
        max_brightness = 255
        relative_brightness = luminance / max_brightness
        
        # Invert the brightness-to-density mapping if requested
        if inverted:
            relative_brightness = 1.0 - relative_brightness
        
        # Use the density map for optimal character selection
        if hasattr(CharacterSet, 'DENSITY_MAP') and self.characters:
            # Target density equals brightness for standard mapping
            target_density = relative_brightness
                
            # Find best match using the class's optimized density lookup
            char_densities = [(c, CharacterSet.get_character_density(c)) for c in self.characters]
            closest_char = min(char_densities, key=lambda x: abs(x[1] - target_density))
            return closest_char[0]
        else:
            # Fallback to the original simple mapping if density info not available
            index = int(relative_brightness * (len(self.characters) - 1))
            index = min(max(index, 0), len(self.characters) - 1)
            return self.characters[index]

    def _get_ansi_color(self, r, g, b):
        """Get ANSI truecolor escape sequence for given RGB values."""
        return ColorMapper.get_ansi_truecolor(r, g, b)

    def _get_ansi_256_code(self, r, g, b):
        """Get optimized ANSI 256-color code for the given RGB values."""
        return ColorMapper.rgb_to_ansi_code(r, g, b)

    def _enhance_detail_standard(self, img):
        """Apply advanced detail enhancement for standard modes."""
        # Start with the original image
        enhanced = img.copy()
        
        # Apply unsharp mask for detail enhancement
        enhanced = enhanced.filter(ImageFilter.UnsharpMask(radius=1.5, percent=150, threshold=3))
        
        # Apply local contrast enhancement
        if self.enhance_contrast:
            # Create a blurred version for local contrast
            blurred = enhanced.filter(ImageFilter.GaussianBlur(2.0))
            # Blend to enhance local contrast
            enhanced = ImageChops.difference(enhanced, blurred)
            enhanced = ImageChops.invert(enhanced)
            # Normalize the result
            enhanced = ImageOps.autocontrast(enhanced, cutoff=1)
        
        # Apply edge enhancement
        if self.edge_detect:
            # Create edge-enhanced version
            edge = enhanced.filter(ImageFilter.EDGE_ENHANCE_MORE)
            # Blend with original
            enhanced = Image.blend(enhanced, edge, 0.4)
        
        return enhanced

    def _preprocess_standard_image(self):
        """
        Special preprocessing optimized for non-braille modes.
        Optimized version with fewer intermediate image creations.
        """
        # For non-braille modes, enhance details differently
        img = self.image
        
        # Convert to appropriate color space
        if self.color_mode == "grayscale":
            img = img.convert("L")
        else:
            img = img.convert("RGB")
        
        # Group image enhancements together
        enhancers = []
        
        # Add required enhancers to the list
        enhancers.append((ImageEnhance.Contrast, 1.2 * self.contrast))
        enhancers.append((ImageEnhance.Brightness, self.brightness))
        
        # Apply sharpening to improve details
        if self.sharpen > 0:
            enhancers.append((ImageEnhance.Sharpness, 1.0 + self.sharpen * 1.2))
        else:
            # Default sharpening for better detail
            enhancers.append((ImageEnhance.Sharpness, 1.3))
            
        # For color modes, enhance saturation
        if self.color_mode in ["ansi", "truecolor", "html"] and img.mode == "RGB":
            enhancers.append((ImageEnhance.Color, self.saturation * 1.2))
        
        # Apply all enhancers in sequence
        for enhancer_class, value in enhancers:
            img = enhancer_class(img).enhance(value)
        
        # Apply blur if needed
        if self.blur > 0:
            img = img.filter(ImageFilter.GaussianBlur(self.blur))
        
        # Apply advanced detail enhancement
        img = self._enhance_detail_standard(img)
            
        # Invert if requested
        if self.invert:
            img = ImageOps.invert(img)
            
        return img

    def _generate_braille_art(self):
        """
        Generate Unicode Braille pattern art from the image.
        Optimized version with improved memory usage.
        """
        # For braille art, work with special processing
        img = self.image
        
        # Apply image adjustments specific to braille
        img = self._preprocess_braille_image(img)
        
        # For braille, each character represents a block of 2 columns x 4 rows
        # Scale width accordingly for proper aspect ratio
        target_width = max(1, self.output_width * 2)
        
        # Calculate optimal height
        height_factor = 0.5 if self.aspect_ratio < 1.0 else 0.4  # Adjustment for different image shapes
        new_height = int(target_width * self.aspect_ratio * height_factor)
        
        # Make sure height is a multiple of 4 for even braille blocks
        new_height = (new_height + 3) // 4 * 4
        
        # High-quality resize
        img = img.resize((target_width, new_height), Image.LANCZOS)
        
        # Apply dithering optimized for braille
        if self.dithering:
            # Custom dithering parameters for braille
            img = img.convert("1", dither=Image.FLOYDSTEINBERG).convert("L")
        else:
            img = img.convert("L")
            
        # Convert to numpy array for faster processing
        arr = np.array(img)
        rows, cols = arr.shape
        
        # Calculate threshold once
        if self.dithering:
            threshold = 128  # Fixed threshold with dithering
        else:
            # Dynamic threshold calculation using Otsu's method
            # This is more efficient than the previous implementation
            hist = img.histogram()
            total_pixels = sum(hist)
            
            # Precompute histogram indexes and weights
            hist_indexes = np.arange(256)
            pixel_counts = np.array(hist)
            
            # Initialize variables for Otsu's method
            max_variance = 0
            threshold = 128  # Default
            
            # Compute cumulative sums
            cum_sum = np.cumsum(pixel_counts)
            cum_mean = np.cumsum(pixel_counts * hist_indexes)
            
            # Find threshold that maximizes between-class variance
            for t in range(1, 255):
                w0 = cum_sum[t]
                if w0 == 0 or w0 == total_pixels:
                    continue
                
                w1 = total_pixels - w0
                mu0 = cum_mean[t] / w0
                mu1 = (cum_mean[-1] - cum_mean[t]) / w1
                
                # Calculate between-class variance
                variance = w0 * w1 * ((mu0 - mu1) ** 2)
                
                if variance > max_variance:
                    max_variance = variance
                    threshold = t

        # Mapping of 2x4 dot positions to braille pattern bits
        # This lookup table is more efficient
        DOT_POSITION_MAP = {
            (0, 0): 0x01, (1, 0): 0x02, (2, 0): 0x04, (3, 0): 0x40,
            (0, 1): 0x08, (1, 1): 0x10, (2, 1): 0x20, (3, 1): 0x80
        }
        
        # Process the image in 2x4 blocks to create braille characters
        # Using list comprehension for better performance
        braille_lines = []
        
        for row in range(0, rows, 4):
            line_chars = []
            for col in range(0, cols, 2):
                braille_dot = 0
                
                # Process all dots in the 2x4 grid
                for dy in range(4):
                    for dx in range(2):
                        pixel_row = row + dy
                        pixel_col = col + dx
                        if pixel_row < rows and pixel_col < cols:
                            if arr[pixel_row, pixel_col] < threshold:
                                dot_pos = (dy, dx)
                                if dot_pos in DOT_POSITION_MAP:
                                    braille_dot |= DOT_POSITION_MAP[dot_pos]
                
                # Create the braille character and add to the current line
                braille_char = chr(0x2800 + braille_dot)
                line_chars.append(braille_char)
                
            braille_lines.append("".join(line_chars))
            
        return "\n".join(braille_lines)

    def _preprocess_braille_image(self, img):
        """
        Special preprocessing optimized for braille output.
        Optimized version with fewer intermediate images.
        """
        # Convert to grayscale
        img = img.convert("L")
        
        # Group the image enhancements for better performance
        enhancers = []
        
        # Edge enhancement for better detail in braille
        edge_img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        img = Image.blend(img, edge_img, 0.3)
        
        # Add required enhancers to the list
        enhancers.append((ImageEnhance.Contrast, 1.5 * self.contrast))
        enhancers.append((ImageEnhance.Brightness, self.brightness))
        
        if self.sharpen > 0:
            enhancers.append((ImageEnhance.Sharpness, 1.0 + self.sharpen * 1.5))
            
        # Apply all enhancers in sequence
        for enhancer_class, value in enhancers:
            img = enhancer_class(img).enhance(value)
        
        # Apply blur if needed
        if self.blur > 0:
            img = img.filter(ImageFilter.GaussianBlur(self.blur))
            
        # Invert if requested
        if self.invert:
            img = ImageOps.invert(img)
            
        return img

    def _optimize_resolution(self, mode, img):
        """Calculate optimal resolution based on mode."""
        # Calculate base dimensions
        base_width = self.output_width
        
        # For detailed character modes, increase effective resolution
        if mode in ["grayscale", "html"] and self.preset in ["detailed", "dense"]:
            # For detailed character sets, we need higher resolution
            effective_width = int(base_width * 1.5)
        elif mode in ["ansi", "truecolor"]:
            # Color modes can use slightly higher resolution
            effective_width = int(base_width * 1.2)
        else:
            effective_width = base_width
            
        # Calculate height based on aspect ratio
        aspect_correction = self.aspect_ratio_correction
        
        # Adjust for image type
        if self.aspect_ratio > 1.5:  # Tall image
            aspect_correction *= 0.8
        elif self.aspect_ratio < 0.7:  # Wide image
            aspect_correction *= 1.1
            
        effective_height = int(effective_width * self.aspect_ratio * aspect_correction)
        
        return effective_width, effective_height

    def _apply_dithering_standard(self, mode, img):
        """Apply optimized dithering for standard modes."""
        if not self.dithering:
            return img
            
        if mode == "grayscale" or img.mode == "L":
            # Special dithering for grayscale
            dithered = img.convert("1", dither=Image.FLOYDSTEINBERG).convert("L")
            
            # Enhance the dithering pattern by amplifying it
            # This makes the dithering more visible and effective
            blend_factor = 0.7
            return Image.blend(img, dithered, blend_factor)
        else:
            # For color images, dither each channel separately
            r, g, b = img.split()
            
            # Apply special dithering to each channel
            r_dither = r.convert("1", dither=Image.FLOYDSTEINBERG).convert("L")
            g_dither = g.convert("1", dither=Image.FLOYDSTEINBERG).convert("L")
            b_dither = b.convert("1", dither=Image.FLOYDSTEINBERG).convert("L")
            
            # For truecolor, make the dithering effect stronger
            if mode == "truecolor":
                blend_factor = 0.85
            else:
                blend_factor = 0.7
                
            # Blend original with dithered for each channel
            r_result = Image.blend(r, r_dither, blend_factor)
            g_result = Image.blend(g, g_dither, blend_factor)
            b_result = Image.blend(b, b_dither, blend_factor)
            
            # Merge channels back
            return Image.merge("RGB", (r_result, g_result, b_result))

    def _generate_standard_mode(self, mode):
        """
        Generate ASCII art for non-braille modes with high-detail optimizations.
        Optimized version with better memory usage and performance.
        """
        # Preprocess the image specially for standard modes
        img = self._preprocess_standard_image()
        
        # Convert to appropriate color space if needed
        if mode == "grayscale" and img.mode != "L":
            img = img.convert("L")
            
        # Calculate optimal dimensions for detail
        target_width, target_height = self._optimize_resolution(mode, img)
        
        # High-quality resize with detail preservation
        img = img.resize((target_width, target_height), Image.LANCZOS)
        
        # Apply improved dithering optimized for each mode
        img = self._apply_dithering_standard(mode, img)
        
        # Convert to numpy array for faster processing
        img_array = np.array(img)
        
        # Check if grayscale
        is_grayscale = len(img_array.shape) == 2 or mode == "grayscale"
        
        # Flag to indicate if we should invert the density mapping
        invert_mapping = mode in ["grayscale", "html"] and not self.invert
        
        # Use more efficient list comprehensions for line building
        if is_grayscale:
            # Process grayscale pixels
            if len(img_array.shape) == 2:
                # Already in grayscale format
                output_lines = [
                    "".join(self._map_to_ascii(pixel, invert_mapping) for pixel in row)
                    for row in img_array
                ]
            else:
                # Convert RGB to grayscale
                output_lines = [
                    "".join(self._map_to_ascii(
                        0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2], 
                        invert_mapping
                    ) for pixel in row)
                    for row in img_array
                ]
        else:
            # Process color pixels
            if mode == "truecolor":
                # Full 24-bit color with enhanced color accuracy
                output_lines = [
                    "".join(
                        f"{self._get_ansi_color(pixel[0], pixel[1], pixel[2])}"
                        f"{self._map_to_ascii(0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2], invert_mapping)}"
                        f"\033[0m"
                        for pixel in row
                    )
                    for row in img_array
                ]
            elif mode == "ansi":
                # Enhanced ANSI 256-color mapping
                output_lines = [
                    "".join(
                        f"\033[38;5;{self._get_ansi_256_code(pixel[0], pixel[1], pixel[2])}m"
                        f"{self._map_to_ascii(0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2], invert_mapping)}"
                        f"\033[0m"
                        for pixel in row
                    )
                    for row in img_array
                ]
            else:  # html or other modes
                output_lines = [
                    "".join(
                        self._map_to_ascii(0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2], invert_mapping)
                        for pixel in row
                    )
                    for row in img_array
                ]
        
        # Join the output lines into the final ASCII art
        return "\n".join(output_lines)

    def generate_ascii(self):
        """
        Generate ASCII art based on the selected mode, with all modes optimized for high detail.
        Main entry point for ASCII art generation.
        """
        # Special case for braille mode which has its own dedicated logic
        if self.color_mode == "braille":
            return self._generate_braille_art()
        
        # For all other modes (grayscale, ansi, truecolor, html)
        # Use the optimized high-detail standard processing pipeline
        return self._generate_standard_mode(self.color_mode)
