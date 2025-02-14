import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import re
from PIL import ImageTk, Image
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
        master.title("ASCII Art Generator")
        self.create_widgets()
        self.image_path = None
        self.ascii_art = None

    def create_widgets(self):
        # Control panel frame
        controls = ttk.Frame(self.master)
        controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(controls, text="Open Image", command=self.load_image).grid(
            row=0, column=0, padx=2
        )
        ttk.Button(controls, text="Generate", command=self.generate_ascii).grid(
            row=0, column=1, padx=2
        )
        ttk.Button(controls, text="Save", command=self.save_output).grid(
            row=0, column=2, padx=2
        )

        # Settings row 1
        ttk.Label(controls, text="Width:").grid(row=1, column=0, padx=2, sticky="e")
        self.width = ttk.Spinbox(controls, from_=10, to=500, width=5)
        self.width.grid(row=1, column=1, padx=2)

        ttk.Label(controls, text="Color Mode:").grid(
            row=1, column=2, padx=2, sticky="e"
        )
        self.color_mode = ttk.Combobox(
            controls,
            values=["grayscale", "ansi", "truecolor", "html", "braille"],
            state="readonly",
            width=10,
        )
        self.color_mode.grid(row=1, column=3, padx=2)
        self.color_mode.set("braille")

        # Preset selection
        ttk.Label(controls, text="Preset:").grid(row=1, column=4, padx=2, sticky="e")
        self.preset = ttk.Combobox(
            controls,
            values=CharacterSet.get_preset_names(),
            state="readonly",
            width=10,
        )
        self.preset.grid(row=1, column=5, padx=2)
        self.preset.set("classic")

        # Checkboxes for options
        self.dither = tk.BooleanVar()
        ttk.Checkbutton(controls, text="Dither", variable=self.dither).grid(
            row=2, column=0, padx=2
        )

        self.edges = tk.BooleanVar()
        ttk.Checkbutton(controls, text="Edge Detect", variable=self.edges).grid(
            row=2, column=1, padx=2
        )

        self.enhance = tk.BooleanVar(value=True)
        ttk.Checkbutton(controls, text="Enhance Contrast", variable=self.enhance).grid(
            row=2, column=2, padx=2
        )

        # Preview areas
        self.image_preview = ttk.Label(self.master)
        self.image_preview.pack(side=tk.LEFT, padx=5, pady=5)

        self.ascii_preview = tk.Text(
            self.master, wrap=tk.NONE, font=("DejaVu Sans Mono", 10)
        )
        self.ascii_preview.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

    def load_image(self):
        self.image_path = filedialog.askopenfilename()
        if not self.image_path:
            return
        try:
            img = Image.open(self.image_path)
            img.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(img)
            self.image_preview.config(image=photo)
            self.image_preview.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def generate_ascii(self):
        if not self.image_path:
            messagebox.showwarning("Warning", "Please load an image first!")
            return

        try:
            generator = AsciiArtGenerator(
                self.image_path,
                output_width=max(10, int(self.width.get())),
                color_mode=self.color_mode.get(),
                dithering=self.dither.get(),
                edge_detect=self.edges.get(),
                preset=self.preset.get(),
                enhance_contrast=self.enhance.get(),
            )
            self.ascii_art = generator.generate_ascii()
            self.ascii_preview.delete(1.0, tk.END)

            # For both truecolor and ANSI (256-color) modes, parse ANSI codes.
            if self.color_mode.get() in ("truecolor", "ansi"):
                insert_ansi_text(self.ascii_preview, self.ascii_art)
            else:
                self.ascii_preview.insert(tk.END, self.ascii_art)
        except Exception as e:
            messagebox.showerror("Error", f"Generation failed: {str(e)}")

    def save_output(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not file_path:
            return

        try:
            if self.color_mode.get() == "html":
                image_to_html(self.ascii_art, self.image_path, file_path)
            else:
                with open(file_path, "w") as f:
                    f.write(self.ascii_art)
            messagebox.showinfo("Success", f"Saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")


def run_gui():
    root = tk.Tk()
    app = AsciiArtGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
