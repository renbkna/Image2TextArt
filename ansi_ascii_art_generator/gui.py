import tkinter as tk
from tkinter import filedialog, ttk, messagebox, colorchooser, font
import re
from PIL import ImageTk, Image, ImageOps
from .core import AsciiArtGenerator
from .utils import image_to_html
from .characters import CharacterSet

# Regular expressions for ANSI truecolor and ANSI 256-color sequences, and the reset code.
ANSI_TRUECOLOR_RE = re.compile(r"\x1b\[38;2;(\d+);(\d+);(\d+)m")
ANSI_256_RE = re.compile(r"\x1b\[38;5;(\d+)m")
ANSI_RESET_RE = re.compile(r"\x1b\[0m")


def convert_ansi256_to_rgb(code):
    """
    Convert a 256-color ANSI code to an RGB tuple.
    """
    if 16 <= code <= 231:
        code -= 16
        r = (code // 36) * 51
        g = ((code % 36) // 6) * 51
        b = (code % 6) * 51
        return r, g, b
    elif 232 <= code <= 255:
        gray = (code - 232) * 10 + 8
        return gray, gray, gray
    else:
        # For codes 0-15, use a simple mapping.
        ansi_0_15 = [
            (0, 0, 0),
            (128, 0, 0),
            (0, 128, 0),
            (128, 128, 0),
            (0, 0, 128),
            (128, 0, 128),
            (0, 128, 128),
            (192, 192, 192),
            (128, 128, 128),
            (255, 0, 0),
            (0, 255, 0),
            (255, 255, 0),
            (0, 0, 255),
            (255, 0, 255),
            (0, 255, 255),
            (255, 255, 255),
        ]
        if code < len(ansi_0_15):
            return ansi_0_15[code]
        return (255, 255, 255)


def insert_ansi_text(text_widget, ansi_text):
    """
    Parse a string containing ANSI escape codes (both truecolor and 256-color)
    and insert the text into a Tkinter Text widget with the appropriate color tags.
    """
    text_widget.delete("1.0", tk.END)
    pos = 0
    current_tag = None

    while pos < len(ansi_text):
        m_true = ANSI_TRUECOLOR_RE.match(ansi_text, pos)
        m_256 = ANSI_256_RE.match(ansi_text, pos)
        m_reset = ANSI_RESET_RE.match(ansi_text, pos)

        if m_true:
            r, g, b = m_true.groups()
            color = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            tag_name = f"fg_{r}_{g}_{b}"
            if tag_name not in text_widget.tag_names():
                text_widget.tag_config(tag_name, foreground=color)
            current_tag = tag_name
            pos = m_true.end()
            continue
        elif m_256:
            code = int(m_256.group(1))
            r, g, b = convert_ansi256_to_rgb(code)
            color = f"#{r:02x}{g:02x}{b:02x}"
            tag_name = f"fg_{r}_{g}_{b}"
            if tag_name not in text_widget.tag_names():
                text_widget.tag_config(tag_name, foreground=color)
            current_tag = tag_name
            pos = m_256.end()
            continue
        elif m_reset:
            current_tag = None
            pos = m_reset.end()
            continue

        next_ansi = ansi_text.find("\x1b", pos)
        if next_ansi == -1:
            next_ansi = len(ansi_text)
        segment = ansi_text[pos:next_ansi]
        text_widget.insert(tk.END, segment, current_tag)
        pos = next_ansi


class AsciiArtGUI:
    def __init__(self, master):
        self.master = master
        master.title("Enhanced ASCII Art Generator")
        
        # Initialize all variables first
        self.image_path = None
        self.ascii_art = None
        self.bg_color = "#000000"
        self.fg_color = "#FFFFFF"
        self.font_size = 10
        self.auto_fit = tk.BooleanVar(value=True)
        
        # Create the widgets
        self.create_widgets()
        self.setup_styles()
        
        # Configure the preview area with default colors
        if self.ascii_preview:
            self.ascii_preview.config(bg=self.bg_color, fg=self.fg_color)
        
        # Bind window resize event to adjust text when auto-fit is enabled
        self.master.bind("<Configure>", self.on_window_resize)
        
    def setup_styles(self):
        """Set up ttk styles for a more modern look"""
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=3)
        style.configure("TFrame", padding=5)
        
    def create_widgets(self):
        # Main container with two frames
        main_container = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side: controls and image preview
        left_frame = ttk.Frame(main_container)
        main_container.add(left_frame, weight=1)
        
        # Right side: ASCII preview
        right_frame = ttk.Frame(main_container)
        main_container.add(right_frame, weight=2)
        
        # Control panel frame on left
        controls = ttk.LabelFrame(left_frame, text="Controls")
        controls.pack(fill=tk.X, padx=5, pady=5)
        
        # Image preview area on left
        preview_frame = ttk.LabelFrame(left_frame, text="Image Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.image_preview = ttk.Label(preview_frame)
        self.image_preview.pack(padx=5, pady=5)
        
        # Button row
        button_frame = ttk.Frame(controls)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Open Image", command=self.load_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Generate", command=self.generate_ascii).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Save", command=self.save_output).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Set Colors", command=self.set_colors).pack(side=tk.RIGHT, padx=2)
        
        # Create a notebook for tabbed settings
        settings_notebook = ttk.Notebook(controls)
        settings_notebook.pack(fill=tk.X, padx=5, pady=5)
        
        # Basic settings tab
        basic_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(basic_tab, text="Basic")
        
        # Advanced settings tab
        advanced_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(advanced_tab, text="Advanced")
        
        # Display settings tab
        display_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(display_tab, text="Display")
        
        # Basic settings content
        row = 0
        
        # Width setting
        ttk.Label(basic_tab, text="Width:").grid(row=row, column=0, padx=2, sticky="e")
        self.width = ttk.Spinbox(basic_tab, from_=10, to=500, width=5)
        self.width.grid(row=row, column=1, padx=2)
        self.width.set("100")
        
        # Color mode setting
        ttk.Label(basic_tab, text="Color Mode:").grid(row=row, column=2, padx=2, sticky="e")
        self.color_mode = ttk.Combobox(
            basic_tab,
            values=["grayscale", "ansi", "truecolor", "html", "braille"],
            state="readonly",
            width=10,
        )
        self.color_mode.grid(row=row, column=3, padx=2)
        self.color_mode.set("braille")
        
        row += 1
        
        # Preset selection
        ttk.Label(basic_tab, text="Character Set:").grid(row=row, column=0, padx=2, sticky="e")
        self.preset = ttk.Combobox(
            basic_tab,
            values=CharacterSet.get_preset_names(),
            state="readonly",
            width=12,
        )
        self.preset.grid(row=row, column=1, padx=2)
        self.preset.set("classic")
        
        # Aspect ratio
        ttk.Label(basic_tab, text="Aspect Ratio:").grid(row=row, column=2, padx=2, sticky="e")
        self.aspect_ratio = ttk.Spinbox(basic_tab, from_=0.1, to=2.0, increment=0.05, width=5)
        self.aspect_ratio.grid(row=row, column=3, padx=2)
        self.aspect_ratio.set("0.55")
        
        row += 1
        
        # Checkboxes for options
        self.dither = tk.BooleanVar()
        ttk.Checkbutton(basic_tab, text="Dithering", variable=self.dither).grid(
            row=row, column=0, padx=2, sticky="w"
        )
        
        self.edges = tk.BooleanVar()
        ttk.Checkbutton(basic_tab, text="Edge Detection", variable=self.edges).grid(
            row=row, column=1, padx=2, sticky="w"
        )
        
        self.enhance = tk.BooleanVar(value=True)
        ttk.Checkbutton(basic_tab, text="Enhance Contrast", variable=self.enhance).grid(
            row=row, column=2, padx=2, sticky="w"
        )
        
        self.invert = tk.BooleanVar(value=False)
        ttk.Checkbutton(basic_tab, text="Invert Colors", variable=self.invert).grid(
            row=row, column=3, padx=2, sticky="w"
        )
        
        # Advanced settings content
        row = 0
        
        # Edge threshold
        ttk.Label(advanced_tab, text="Edge Threshold:").grid(row=row, column=0, padx=2, sticky="e")
        self.edge_threshold = ttk.Scale(advanced_tab, from_=0, to=255, orient=tk.HORIZONTAL)
        self.edge_threshold.grid(row=row, column=1, padx=2, sticky="ew")
        self.edge_threshold.set(75)
        
        row += 1
        
        # Blur
        ttk.Label(advanced_tab, text="Blur:").grid(row=row, column=0, padx=2, sticky="e")
        self.blur = ttk.Scale(advanced_tab, from_=0, to=10, orient=tk.HORIZONTAL)
        self.blur.grid(row=row, column=1, padx=2, sticky="ew")
        self.blur.set(0)
        
        # Sharpen
        ttk.Label(advanced_tab, text="Sharpen:").grid(row=row, column=2, padx=2, sticky="e")
        self.sharpen = ttk.Scale(advanced_tab, from_=0, to=10, orient=tk.HORIZONTAL)
        self.sharpen.grid(row=row, column=3, padx=2, sticky="ew")
        self.sharpen.set(0)
        
        row += 1
        
        # Brightness
        ttk.Label(advanced_tab, text="Brightness:").grid(row=row, column=0, padx=2, sticky="e")
        self.brightness = ttk.Scale(advanced_tab, from_=0.5, to=2.0, orient=tk.HORIZONTAL)
        self.brightness.grid(row=row, column=1, padx=2, sticky="ew")
        self.brightness.set(1.0)
        
        # Saturation
        ttk.Label(advanced_tab, text="Saturation:").grid(row=row, column=2, padx=2, sticky="e")
        self.saturation = ttk.Scale(advanced_tab, from_=0, to=2.0, orient=tk.HORIZONTAL)
        self.saturation.grid(row=row, column=3, padx=2, sticky="ew")
        self.saturation.set(1.0)
        
        row += 1
        
        # Contrast
        ttk.Label(advanced_tab, text="Contrast:").grid(row=row, column=0, padx=2, sticky="e")
        self.contrast = ttk.Scale(advanced_tab, from_=0.5, to=2.0, orient=tk.HORIZONTAL)
        self.contrast.grid(row=row, column=1, padx=2, sticky="ew")
        self.contrast.set(1.0)
        
        # Detail level
        ttk.Label(advanced_tab, text="Detail Level:").grid(row=row, column=2, padx=2, sticky="e")
        self.detail_level = ttk.Scale(advanced_tab, from_=0.1, to=1.0, orient=tk.HORIZONTAL)
        self.detail_level.grid(row=row, column=3, padx=2, sticky="ew")
        self.detail_level.set(1.0)
        
        row += 1
        
        # Gamma
        ttk.Label(advanced_tab, text="Gamma:").grid(row=row, column=0, padx=2, sticky="e")
        self.gamma = ttk.Scale(advanced_tab, from_=0.5, to=2.0, orient=tk.HORIZONTAL)
        self.gamma.grid(row=row, column=1, padx=2, sticky="ew")
        self.gamma.set(1.0)
        
        row += 1
        
        # Custom character set
        ttk.Label(advanced_tab, text="Custom Characters:").grid(row=row, column=0, padx=2, sticky="e")
        self.custom_chars = ttk.Entry(advanced_tab, width=30)
        self.custom_chars.grid(row=row, column=1, columnspan=3, padx=2, sticky="ew")
        
        # Display settings tab
        row = 0
        
        # Create and initialize text widget first before connecting to font controls
        # Right side - ASCII preview in frame with scrollbars
        preview_frame = ttk.Frame(right_frame)
        preview_frame.grid(row=0, column=0, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Create vertical scrollbar
        v_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create preview text widget
        self.ascii_preview = tk.Text(
            preview_frame, 
            wrap=tk.NONE, 
            font=("Courier New", 10),
            bg="#000000",  # Default to black background
            fg="#FFFFFF",  # Default to white text
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set
        )
        self.ascii_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Connect scrollbars to the text widget
        v_scrollbar.config(command=self.ascii_preview.yview)
        h_scrollbar.config(command=self.ascii_preview.xview)
        
        # Font size slider
        ttk.Label(display_tab, text="Font Size:").grid(row=row, column=0, padx=2, sticky="e")
        self.font_size_slider = ttk.Scale(display_tab, from_=4, to=24, orient=tk.HORIZONTAL, command=self.update_font_size)
        self.font_size_slider.grid(row=row, column=1, padx=2, sticky="ew")
        self.font_size_slider.set(10)  # Default font size
        
        # Font family dropdown
        ttk.Label(display_tab, text="Font Family:").grid(row=row, column=2, padx=2, sticky="e")
        # Check available monospace fonts or use fallbacks
        try:
            available_fonts = sorted([f for f in font.families() if f.lower().find('mono') >= 0 or f == 'Courier'])
            if not available_fonts:
                available_fonts = ['Courier', 'Courier New', 'Consolas', 'DejaVu Sans Mono']
        except Exception:
            available_fonts = ['Courier', 'Courier New', 'Consolas', 'DejaVu Sans Mono']
            
        self.font_family = ttk.Combobox(display_tab, values=available_fonts, state="readonly", width=15)
        self.font_family.grid(row=row, column=3, padx=2, sticky="ew")
        self.font_family.set("Courier New")  # Use a reliable default
        self.font_family.bind("<<ComboboxSelected>>", self.update_font)
        
        row += 1
        
        # Auto-fit checkbox
        ttk.Checkbutton(
            display_tab, 
            text="Auto-fit to Window", 
            variable=self.auto_fit,
            command=self.toggle_auto_fit
        ).grid(row=row, column=0, columnspan=2, padx=2, sticky="w")
        
        # Zoom buttons
        zoom_frame = ttk.Frame(display_tab)
        zoom_frame.grid(row=row, column=2, columnspan=2, sticky="e")
        ttk.Button(zoom_frame, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="Zoom Out", command=self.zoom_out).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="Reset Zoom", command=self.reset_zoom).pack(side=tk.LEFT, padx=2)

    def load_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
                ("All files", "*.*")
            ]
        )
        if not self.image_path:
            return
        try:
            img = Image.open(self.image_path)
            img.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(img)
            self.image_preview.config(image=photo)
            self.image_preview.image = photo  # Keep a reference to avoid garbage collection
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def set_colors(self):
        """Set custom background and foreground colors for the ASCII preview"""
        # Background color picker
        bg_color = colorchooser.askcolor(
            title="Choose Background Color", 
            initialcolor=self.bg_color
        )
        if bg_color[1]:  # If user selected a color
            self.bg_color = bg_color[1]
            self.ascii_preview.config(bg=self.bg_color)
        
        # Foreground color picker (for non-colored modes)
        fg_color = colorchooser.askcolor(
            title="Choose Text Color", 
            initialcolor=self.fg_color
        )
        if fg_color[1]:  # If user selected a color
            self.fg_color = fg_color[1]
            self.ascii_preview.config(fg=self.fg_color)
        
        # If we have ASCII art, reapply it with the new colors
        if self.ascii_art and self.color_mode.get() not in ("ansi", "truecolor"):
            self.ascii_preview.delete(1.0, tk.END)
            self.ascii_preview.insert(tk.END, self.ascii_art)

    def update_font_size(self, value=None):
        """Update font size based on slider value"""
        try:
            if value is not None:
                self.font_size = int(float(value))
            
            # Get current font family
            current_font = self.ascii_preview.cget("font")
            if isinstance(current_font, str):
                family = current_font
            else:
                family = current_font[0]
                
            # Update font
            new_font = (family, self.font_size)
            self.ascii_preview.configure(font=new_font)
            
            # If auto-fit is enabled, adjust text to fit
            if self.auto_fit.get() and self.ascii_art:
                self.fit_text_to_window()
        except Exception as e:
            print(f"Error updating font size: {e}")

    def update_font(self, event=None):
        """Update font family"""
        try:
            family = self.font_family.get()
            new_font = (family, self.font_size)
            self.ascii_preview.configure(font=new_font)
            
            # If auto-fit is enabled, adjust text to fit
            if self.auto_fit.get() and self.ascii_art:
                self.fit_text_to_window()
        except Exception as e:
            print(f"Error updating font family: {e}")

    def zoom_in(self):
        """Increase font size"""
        self.font_size = min(24, self.font_size + 1)
        self.font_size_slider.set(self.font_size)
        self.update_font_size()

    def zoom_out(self):
        """Decrease font size"""
        self.font_size = max(4, self.font_size - 1)
        self.font_size_slider.set(self.font_size)
        self.update_font_size()

    def reset_zoom(self):
        """Reset to default font size"""
        self.font_size = 10
        self.font_size_slider.set(self.font_size)
        self.update_font_size()

    def toggle_auto_fit(self):
        """Toggle auto-fit functionality"""
        if self.auto_fit.get() and self.ascii_art:
            self.fit_text_to_window()

    def on_window_resize(self, event=None):
        """Handle window resize event"""
        if self.auto_fit.get() and self.ascii_art:
            # Use after to avoid multiple calls during resize
            self.master.after(100, self.fit_text_to_window)

    def fit_text_to_window(self):
        """Adjust font size to make ASCII art fit in the window"""
        if not self.ascii_art:
            return
            
        try:
            # Calculate max line length
            lines = self.ascii_art.split('\n')
            max_length = max(len(line) for line in lines)
            
            # Get available width
            available_width = self.ascii_preview.winfo_width() - 20  # subtract some padding
            if available_width <= 0:
                available_width = self.master.winfo_width() * 0.7  # fallback estimation
            
            # Use a temporary font for measurement
            temp_font = font.Font(family=self.font_family.get(), size=10)
            char_width = temp_font.measure('m')  # measure width of 'm' as reference
            
            # Calculate optimal font size
            if char_width > 0 and max_length > 0:
                optimal_font_size = available_width / (max_length * char_width/10)
            else:
                optimal_font_size = 10  # fallback
            
            # Limit font size to reasonable range
            new_font_size = max(4, min(24, int(optimal_font_size)))
            
            # Only update if significantly different
            if abs(new_font_size - self.font_size) > 1:
                self.font_size = new_font_size
                self.font_size_slider.set(self.font_size)
                self.update_font_size()
        except Exception as e:
            print(f"Error in fit_text_to_window: {e}")

    def suggest_optimal_settings(self, image_path):
        """Suggest optimal settings based on image characteristics"""
        try:
            img = Image.open(image_path)
            width, height = img.size
            aspect_ratio = height / width
            
            # Calculate optimal width based on image size
            suggested_width = min(150, max(50, int(width / 10)))
            self.width.set(suggested_width)
            
            # Detect if it's a photo or graphic
            is_photo = False
            
            # Convert to grayscale for analysis
            img_gray = img.convert('L')
            
            # Get histogram
            hist = img_gray.histogram()
            
            # Check for unique colors (approximation using histogram)
            unique_tones = sum(1 for count in hist if count > 0)
            if unique_tones > 100:
                is_photo = True
            
            # Suggest character set
            if is_photo:
                # Photos work better with more gradients
                if aspect_ratio > 1.5:  # Tall image
                    self.preset.set("detailed")
                    self.aspect_ratio.set(0.5)
                    self.color_mode.set("braille")
                elif aspect_ratio < 0.7:  # Wide image
                    self.preset.set("dense")
                    self.aspect_ratio.set(0.4)
                    self.color_mode.set("ansi")
                else:  # Normal aspect ratio
                    self.preset.set("dense")
                    self.aspect_ratio.set(0.55)
                    self.color_mode.set("braille")
                    
                # Enable dithering for photos
                self.dither.set(True)
                # Enhance contrast for photos
                self.enhance.set(True)
                
            else:
                # Graphics/drawings work better with cleaner output
                if aspect_ratio > 1.5:  # Tall image
                    self.preset.set("block")
                    self.aspect_ratio.set(0.6)
                    self.color_mode.set("grayscale")
                elif aspect_ratio < 0.7:  # Wide image
                    self.preset.set("block") 
                    self.aspect_ratio.set(0.45)
                    self.color_mode.set("ansi")
                else:  # Normal aspect ratio
                    self.preset.set("lineart")
                    self.aspect_ratio.set(0.55)
                    self.color_mode.set("grayscale")
                    
                # Disable dithering for graphics
                self.dither.set(False)
                # Maybe enable edge detection for better graphics
                self.edges.set(True)
                
            return True
        except Exception as e:
            print(f"Error suggesting settings: {e}")
            return False

    def generate_ascii(self):
        if not self.image_path:
            messagebox.showwarning("Warning", "Please load an image first!")
            return

        try:
            # Get custom character set if provided
            custom_chars = self.custom_chars.get().strip()
            
            # Suggest optimal settings for the image
            if messagebox.askyesno("Optimize Settings", 
                                  "Would you like to use recommended settings for this image?"):
                self.suggest_optimal_settings(self.image_path)
            
            # Create the generator with all the options
            generator = AsciiArtGenerator(
                self.image_path,
                output_width=max(10, int(self.width.get())),
                color_mode=self.color_mode.get(),
                dithering=self.dither.get(),
                edge_detect=self.edges.get(),
                preset=self.preset.get(),
                enhance_contrast=self.enhance.get(),
                aspect_ratio_correction=float(self.aspect_ratio.get()),
                invert=self.invert.get(),
                edge_threshold=int(self.edge_threshold.get()),
                blur=float(self.blur.get()),
                sharpen=float(self.sharpen.get()),
                brightness=float(self.brightness.get()),
                saturation=float(self.saturation.get()),
                contrast=float(self.contrast.get()),
                detail_level=float(self.detail_level.get()),
                gamma=float(self.gamma.get()),
            )
            
            # If custom characters were provided, use them
            if custom_chars:
                try:
                    generator.characters = CharacterSet.create_custom_set(custom_chars)
                except ValueError as e:
                    messagebox.showwarning("Warning", f"Custom character set error: {str(e)}")
            
            # Generate the ASCII art
            self.ascii_art = generator.generate_ascii()
            
            # Display in the preview area
            if self.color_mode.get() in ("truecolor", "ansi"):
                insert_ansi_text(self.ascii_preview, self.ascii_art)
            else:
                self.ascii_preview.delete(1.0, tk.END)
                self.ascii_preview.insert(tk.END, self.ascii_art)
            
            # If auto-fit is enabled, adjust text to fit
            if self.auto_fit.get():
                self.fit_text_to_window()
                
        except Exception as e:
            messagebox.showerror("Error", f"Generation failed: {str(e)}")

    def save_output(self):
        """Save the generated ASCII art to a file"""
        if not self.ascii_art:
            messagebox.showwarning("Warning", "Please generate ASCII art first!")
            return
        
        # Determine default extension based on color mode
        default_ext = ".txt"
        if self.color_mode.get() == "html":
            default_ext = ".html"
            
        file_types = [
            ("Text files", "*.txt"),
            ("HTML files", "*.html"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=file_types
        )
        
        if not file_path:
            return

        try:
            # Handle HTML output
            if self.color_mode.get() == "html" or file_path.lower().endswith(".html"):
                image_to_html(
                    self.ascii_art, 
                    self.image_path, 
                    file_path,
                    font_size=self.font_size,
                    font_family=self.font_family.get(),
                    background_color=self.bg_color,
                )
            else:
                # Normal text output
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.ascii_art)
                    
            messagebox.showinfo("Success", f"Saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")


def run_gui():
    """Run the GUI application"""
    root = tk.Tk()
    root.title("Enhanced ASCII Art Generator")
    
    # Set minimum window size
    root.minsize(800, 600)
    
    # Set initial window size and position
    window_width = 1000
    window_height = 700
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    app = AsciiArtGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
