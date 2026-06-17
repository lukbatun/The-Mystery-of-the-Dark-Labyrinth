import os
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

files = []

def add_files():
    paths = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")])
    for p in paths:
        if p not in files:
            files.append(p)
            box.insert(tk.END, os.path.basename(p))

def clear_files():
    files.clear()
    box.delete(0, tk.END)

def build_atlas():
    if not files:
        return

    try:
        size = int(size_entry.get())
    except ValueError:
        size = 512

    save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
    if not save_path:
        return

    n = len(files)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    atlas = Image.new('RGBA', (cols * size, rows * size), (0, 0, 0, 0))
    code = f"TILE_SCALE = ({round(1/cols, 4)}, {round(1/rows, 4)})\n"

    for i, path in enumerate(files):
        img = Image.open(path).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
        c, r = i % cols, i // cols
        atlas.paste(img, (c * size, r * size))

        u = c / cols
        v = (rows - 1 - r) / rows
        name = os.path.splitext(os.path.basename(path))[0].upper()
        code += f"{name}_OFFSET = ({round(u, 4)}, {round(v, 4)})\n"

    atlas.save(save_path)
    
    code_out.delete(1.0, tk.END)
    code_out.insert(tk.END, code)
    messagebox.showinfo("Успех", "Атлас готов!")

root = tk.Tk()
root.title("Atlas Maker")
root.geometry("650x400")

left_side = tk.Frame(root)
left_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

box = tk.Listbox(left_side)
box.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

tk.Button(left_side, text="Добавить картинки", command=add_files).pack(fill=tk.X, pady=2)
tk.Button(left_side, text="Очистить список", command=clear_files).pack(fill=tk.X, pady=2)

size_frame = tk.Frame(left_side)
size_frame.pack(fill=tk.X, pady=5)
tk.Label(size_frame, text="Размер тайла:").pack(side=tk.LEFT)
size_entry = tk.Entry(size_frame, width=8)
size_entry.insert(0, "512")
size_entry.pack(side=tk.LEFT, padx=5)

tk.Button(left_side, text="СОХРАНИТЬ АТЛАС", bg="#2e7d32", fg="white", command=build_atlas).pack(fill=tk.X, pady=5)

code_out = tk.Text(root, width=40, bg="#1a1a1a", fg="#00ff00", font=("Consolas", 10))
code_out.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

root.mainloop()