from tkinter import *
import os 

GRID_SIZE = 50 
CHAR_SIZE = 10
CANVAS_SIZE = GRID_SIZE * CHAR_SIZE

squares_coords = []
square_ids = []
spawn_coords = []
spawn_ids = []
exit_coords = []
exit_ids = []
key_coords = []
key_ids = []
spawn = 0
mode = "none"

def set_mode(new_mode):
    global mode
    mode = new_mode
    print(f"Режим: {mode}")

colors = ['Black', 'Brown', 'Cyan', 'Yellow', 'Purple', 'Blue', 'Green', 'Red']
current_color_index = 0
color_button_ref = None 

def create_square_at(x, y):
    global current_color_index
    if mode == "block":
        if (x, y) in squares_coords: return False
        current_color = colors[current_color_index]
        square_id = canvas.create_rectangle(x, y, x + CHAR_SIZE, y + CHAR_SIZE, fill=current_color, outline="")
        squares_coords.append((x, y))
        square_ids.append(square_id)
        return True

    if mode == "spawn":
        if len(spawn_coords) > 0: return False
        spawn_id = canvas.create_rectangle(x, y, x + CHAR_SIZE, y + CHAR_SIZE, fill="red", outline="")
        spawn_coords.append((x, y))
        spawn_ids.append(spawn_id)
        return True
    
    if mode == "exit":
        if len(exit_coords) > 0: return False
        exit_id = canvas.create_rectangle(x, y, x + CHAR_SIZE, y + CHAR_SIZE, fill="orange", outline="")
        exit_coords.append((x, y))
        exit_ids.append(exit_id)
        return True
    
    if mode == "key":
        if len(key_coords) > 0: return False
        key_id = canvas.create_rectangle(x, y, x + CHAR_SIZE, y + CHAR_SIZE, fill="purple", outline="")
        key_coords.append((x, y))
        key_ids.append(key_id)
        return True

def clear_canvas_and_lists():
    global squares_coords, square_ids, spawn_coords, spawn_ids, exit_coords, exit_ids, key_coords, key_ids, spawn
    canvas.delete("all") 
    squares_coords, square_ids = [], []
    spawn_coords, spawn_ids = [], []
    exit_coords, exit_ids = [], []
    key_coords, key_ids = [], []
    spawn = 0
    print("Холст очищен.")

def on_draw(event):
    x = event.x // CHAR_SIZE * CHAR_SIZE
    y = event.y // CHAR_SIZE * CHAR_SIZE
    if 0 <= x < CANVAS_SIZE and 0 <= y < CANVAS_SIZE:
        if create_square_at(x, y):
            print(f"Блок создан в клетке ({x//CHAR_SIZE}, {y//CHAR_SIZE}).")

def on_delete(event):
    x = event.x // CHAR_SIZE * CHAR_SIZE
    y = event.y // CHAR_SIZE * CHAR_SIZE
    if 0 <= x < CANVAS_SIZE and 0 <= y < CANVAS_SIZE:
        for coords, ids, name in [(spawn_coords, spawn_ids, "Спавн"), (squares_coords, square_ids, "Стена"), (exit_coords, exit_ids, "Выход"), (key_coords, key_ids, "Ключ")]:
            if (x, y) in coords:
                idx = coords.index((x, y))
                canvas.delete(ids[idx])
                del coords[idx]
                del ids[idx]
                print(f"{name} удален.")
                return

def on_save(event=None):
    with open("level.txt", "w") as file:
        for x, y in spawn_coords: file.write(f"('spawn', {x//CHAR_SIZE}, {y//CHAR_SIZE})\n")
        for x, y in squares_coords: file.write(f"('wall', {x//CHAR_SIZE}, {y//CHAR_SIZE})\n")
        for x, y in exit_coords: file.write(f"('exit', {x//CHAR_SIZE}, {y//CHAR_SIZE})\n")
        for x, y in key_coords: file.write(f"('key', {x//CHAR_SIZE}, {y//CHAR_SIZE})\n")
    print("Уровень успешно сохранен!")

def switch_color():
    global current_color_index
    current_color_index = (current_color_index + 1) % len(colors)
    if color_button_ref: color_button_ref.config(bg=colors[current_color_index], text=colors[current_color_index])

def show_settings_window():
    global color_button_ref
    top = Toplevel(tk) 
    top.title("Настройки")
    top.geometry("250x250")
    top.resizable(False, False)
    Label(top, text="Инструменты:", font=("Arial", 12)).pack(pady=10)
    color_button_ref = Button(top, width=20, height=2, bg=colors[current_color_index], fg="white", text=colors[current_color_index], command=switch_color)
    color_button_ref.pack(pady=5)
    Button(top, text="Сохранить", width=20, height=2, bg="blue", fg="white", command=on_save).pack(pady=5)
    Button(top, text="Стереть всё поле", width=20, height=2, bg="red", fg="white", command=clear_canvas_and_lists).pack(pady=5)

tk = Tk()
tk.title("Редактор Лабиринта")
tk.geometry("610x550")
tk.resizable(False, False)

canvas = Canvas(tk, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white")
canvas.place(x=100, y=0)

canvas.bind("<Button-1>", on_draw)     
canvas.bind("<B1-Motion>", on_draw)    
canvas.bind("<Button-3>", on_delete) 
canvas.bind("<B3-Motion>", on_delete) 

Button(tk, text="Открыть Настройки", width=20, bg="green", fg="white", command=show_settings_window).pack(pady=5, side=BOTTOM) 
Button(tk, text="Сохранить", width=10, bg="blue", fg="white", command=on_save).pack(side=TOP, anchor="nw", pady=(10, 0), padx=10)
Button(tk, text="Блоки", width=10, bg="black", fg="white", command=lambda: set_mode("block")).pack(side=TOP, anchor="nw", pady=(10, 0), padx=10)
Button(tk, text="Спавн", width=10, bg="red", fg="white", command=lambda: set_mode("spawn")).pack(side=TOP, anchor="nw", pady=(10, 0), padx=10)
Button(tk, text="Лестница", width=10, bg="orange", fg="white", command=lambda: set_mode("exit")).pack(side=TOP, anchor="nw", pady=(10, 0), padx=10)
Button(tk, text="Ключ", width=10, bg="purple", fg="white", command=lambda: set_mode("key")).pack(side=TOP, anchor="nw", pady=(10, 0), padx=10)

tk.mainloop()