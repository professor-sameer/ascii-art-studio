
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import os

# ---------- Configuration ----------
DEFAULT_WIDTH = 180

STYLES = {
    "Classic": " .,:;irsXA253hMHGS#9B&@",
    "Dense": "  .,:-~=+*#%@",
    "Minimal": "  .'-:|/",
    "Block": "  ░▒▓█",
}


class ASCIIPortraitStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCII Portrait Studio")
        self.root.geometry("1200x800")
        self.root.minsize(800, 500)
        self.root.configure(bg="#111111")

        self.original_image = None
        self.photo_path = None
        self.ascii_output = ""

        self.width_var = tk.IntVar(value=DEFAULT_WIDTH)
        self.style_var = tk.StringVar(value="Classic")
        self.contrast_var = tk.DoubleVar(value=1.25)

        self.build_ui()

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#202020", padx=14, pady=12)
        header.pack(fill="x")

        tk.Label(
            header,
            text="ASCII PORTRAIT STUDIO",
            bg="#202020",
            fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(side="left")

        ttk.Button(
            header,
            text="Open Photo",
            command=self.open_photo
        ).pack(side="right")

        # Controls
        controls = tk.Frame(
            self.root, bg="#202020", padx=14, pady=12
        )
        controls.pack(fill="x")

        tk.Label(
            controls, text="Width:",
            bg="#202020", fg="white"
        ).pack(side="left")

        tk.Spinbox(
            controls,
            from_=80,
            to=320,
            increment=20,
            width=6,
            textvariable=self.width_var,
            font=("Segoe UI", 10)
        ).pack(side="left", padx=(6, 18))

        tk.Label(
            controls, text="Character style:",
            bg="#202020", fg="white"
        ).pack(side="left")

        ttk.Combobox(
            controls,
            textvariable=self.style_var,
            values=list(STYLES.keys()),
            state="readonly",
            width=12
        ).pack(side="left", padx=8)

        tk.Label(
            controls, text="Contrast:",
            bg="#202020", fg="white"
        ).pack(side="left", padx=(12, 4))

        ttk.Scale(
            controls,
            from_=0.8,
            to=2.0,
            variable=self.contrast_var,
            orient="horizontal",
            length=110
        ).pack(side="left", padx=4)

        ttk.Button(
            controls,
            text="Generate",
            command=self.generate
        ).pack(side="left", padx=12)

        ttk.Button(
            controls,
            text="Save TXT",
            command=self.save_text
        ).pack(side="left")

        # Status bar
        self.status = tk.Label(
            self.root,
            text="Open a photo to get started.",
            anchor="w",
            bg="#181818",
            fg="#cccccc",
            padx=12,
            pady=8
        )
        self.status.pack(fill="x")

        # Main preview
        preview = tk.Frame(self.root, bg="black")
        preview.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.output = tk.Text(
            preview,
            bg="black",
            fg="white",
            insertbackground="white",
            font=("Consolas", 6),
            wrap="none",
            borderwidth=0,
            padx=10,
            pady=10,
            undo=False
        )

        vertical = ttk.Scrollbar(
            preview, orient="vertical",
            command=self.output.yview
        )
        horizontal = ttk.Scrollbar(
            preview, orient="horizontal",
            command=self.output.xview
        )

        self.output.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set
        )

        self.output.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")

        preview.rowconfigure(0, weight=1)
        preview.columnconfigure(0, weight=1)

    def open_photo(self):
        path = filedialog.askopenfilename(
            title="Select a portrait",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.webp"),
                ("All files", "*.*")
            ]
        )

        if not path:
            return

        try:
            with Image.open(path) as image:
                self.original_image = ImageOps.exif_transpose(
                    image
                ).convert("RGB")

            self.photo_path = path
            self.generate()

        except Exception as error:
            messagebox.showerror(
                "Image Error",
                f"Could not open the image:\n{error}"
            )

    def generate(self):
        if self.original_image is None:
            messagebox.showinfo(
                "No Photo",
                "Please open a photo first."
            )
            return

        try:
            width = int(self.width_var.get())

            if not 80 <= width <= 320:
                raise ValueError(
                    "Width must be between 80 and 320."
                )

            image = self.original_image.copy()

            # Balanced contrast and gentle sharpening
            image = ImageEnhance.Contrast(image).enhance(
                self.contrast_var.get()
            )
            image = ImageEnhance.Sharpness(image).enhance(1.35)

            # Convert to grayscale
            image = ImageOps.grayscale(image)

            # Compensate for the shape of terminal characters.
            # Character cells are generally taller than they are wide.
            height = max(
                1,
                int(image.height / image.width * width * 0.48)
            )

            image = image.resize(
                (width, height),
                Image.Resampling.LANCZOS
            )

            # Slight smoothing reduces noisy pixel-level changes
            image = image.filter(ImageFilter.SMOOTH)

            pixels = list(image.getdata())
            characters = STYLES[self.style_var.get()]
            ramp_length = len(characters) - 1

            lines = []

            for y in range(height):
                row = []

                for x in range(width):
                    brightness = pixels[y * width + x]

                    index = round(
                        brightness / 255 * ramp_length
                    )

                    row.append(characters[index])

                lines.append("".join(row))

            self.ascii_output = "\n".join(lines)

            self.output.delete("1.0", "end")
            self.output.insert("1.0", self.ascii_output)
            self.output.xview_moveto(0)
            self.output.yview_moveto(0)

            filename = os.path.basename(self.photo_path)

            self.status.config(
                text=(
                    f"Generated: {width} columns x {height} rows"
                    f"  |  Style: {self.style_var.get()}"
                    f"  |  Photo: {filename}"
                )
            )

        except (ValueError, tk.TclError) as error:
            messagebox.showerror("Invalid Setting", str(error))

        except Exception as error:
            messagebox.showerror(
                "Generation Error",
                f"Could not generate ASCII art:\n{error}"
            )

    def save_text(self):
        if not self.ascii_output:
            messagebox.showinfo(
                "Nothing to Save",
                "Generate a portrait first."
            )
            return

        path = filedialog.asksaveasfilename(
            title="Save ASCII Portrait",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )

        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as file:
                file.write(self.ascii_output)

            messagebox.showinfo(
                "Saved",
                f"ASCII portrait saved successfully:\n{path}"
            )

        except OSError as error:
            messagebox.showerror("Save Error", str(error))


if __name__ == "__main__":
    root = tk.Tk()
    app = ASCIIPortraitStudio(root)
    root.mainloop()
