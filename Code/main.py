from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import os
import ast
import time
import random

app = Ursina()
window.color = color.black
position_player = (0, 0, 0)

tex_wall = load_texture('Textures/wall.jpg') or 'white_cube'
tex_floor = load_texture('Textures/floor.jpg') or 'white_cube'
tex_ceiling = load_texture('Textures/potolock.jpg') or 'white_cube'
tex_door = load_texture('Textures/door.png') or 'white_cube'
tex_door_open = load_texture('Textures/door_open.png') or 'white_cube'

scene.ambient_color = color.black
scene.fog_density = 0.12
scene.fog_color = color.black

Entity(model='plane', collider='box', scale=150, texture=tex_floor, texture_scale=(30, 30), position=(75, 0, 75), shadows=True)
Entity(model='plane', collider='box', scale=150, texture=tex_ceiling, texture_scale=(25, 25), position=(75, 4.5, 75), rotation_x=180, shadows=True)

sound_ambient = Audio('Music and Sounds/Stone Abyss', volume=0.5, loop=False, autoplay=True)
sound_key = Audio('Music and Sounds/Key_up', volume=0.7, autoplay=False, loop=False)
step_sound = Audio('Music and Sounds/echo-footsteps', autoplay=False, loop=False)

vignette1 = Entity(parent=camera.ui, model='quad', texture='Textures/fog3.png', scale=(1.8, 1.5), color=color.white, always_on_top=True, transparent=True)
vignette3 = Entity(parent=camera.ui, model='quad', texture='Textures/inv.png', scale=(0.5, 0.11), position=(-0.64, -0.45, 0), color=color.white, always_on_top=True, transparent=True)
key_icon = Entity(parent=camera.ui, model='quad', texture='Textures/key.png', scale=(0.1, 0.1), position=(-0.83, -0.45, -0.1), visible=False, always_on_top=True, transparent=True)
crosshair = None

timer_text = Text(text='Время: 0.0 с', position=(-0.64, 0.45), scale=1.4, color=color.white)
finish_text = Text(text='', position=(0, 0), origin=(0, 0), scale=2, color=color.azure, visible=False)

keys_in_world = []
has_key = False
level_completed = False
time_limit = 60.0
level_start_time = 0.0
countdown_start_time = 0.0
exit_door = None
level_parent = None

main_menu = Entity(parent=camera.ui, enabled=True)
end_menu = Entity(parent=camera.ui, enabled=False)

main_bg = Sprite(texture=tex_wall, parent=main_menu, scale=(1.8, 1), unlit=True)
main_title = Text(text='ТАЙНА ТЕМНОГО ЛАБИРИНТА', parent=main_menu, y=0.3, origin=(0, 0), scale=3, color=color.red)
start_btn = Button(text='ИГРАТЬ', parent=main_menu, y=0, scale=(0.3, 0.08), color=color.gray, on_click=lambda: start_game())
exit_btn = Button(text='ВЫХОД', parent=main_menu, y=-0.1, scale=(0.3, 0.08), color=color.dark_gray, on_click=application.quit)

end_bg = Sprite(texture=tex_ceiling, parent=end_menu, scale=(1.8, 1), unlit=True)
restart_btn = Button(text='ИГРАТЬ СНОВА', parent=end_menu, y=-0.1, scale=(0.3, 0.08), color=color.orange, on_click=lambda: restart_game())

def load_level():
    global position_player, exit_door

    level_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'level.txt')
    if not os.path.exists(level_path):
        print("Файл level.txt не найден!")
        return

    with open(level_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            t, x, z = ast.literal_eval(line)
            if t == 'spawn':
                position_player = ((x + 0.5) * 3, 1.5, (z + 0.5) * 3)
            elif t == 'exit':
                exit_door = Entity(model='cube', collider='box', position=((x + 0.5) * 3, 2.25, (z + 0.5) * 3), scale=(3, 4.5, 3), texture=tex_door, shadows=True)
            elif t == 'key':
                k = Entity(model='quad', texture='Textures/key.png', position=((x + 0.5) * 3, 1.5, (z + 0.5) * 3), scale=(1, 1), billboard=True, double_sided=True)
                keys_in_world.append(k)
            elif t == 'wall':
                Entity(model='cube', collider='box', position=((x + 0.5) * 3, 2.25, (z + 0.5) * 3), scale=(3, 4.5, 3), texture=tex_wall, shadows=True)

def generate_maze(width, height, seed):
    rng = random.Random(seed)
    maze = [[True] * width for _ in range(height)]
    
    def carve(x, y):
        maze[y][x] = False
        dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        rng.shuffle(dirs)
        
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 < nx < width - 1 and 0 < ny < height - 1 and maze[ny][nx]:
                maze[y + dy // 2][x + dx // 2] = False
                carve(nx, ny)

    carve(1, 1)
    return maze

def load_generated_level(seed, width=21, height=21):
    global position_player, exit_door, level_parent, keys_in_world
    
    if level_parent:
        destroy(level_parent)
    level_parent = Entity()
    keys_in_world = []
    
    maze = generate_maze(width, height, seed)
    
    possible_doors = []
    for z in range(1, height-1):
        if not maze[z][1]: possible_doors.append((0, z))
        if not maze[z][width-2]: possible_doors.append((width-1, z))
    for x in range(1, width-1):
        if not maze[1][x]: possible_doors.append((x, 0))
        if not maze[height-2][x]: possible_doors.append((x, height-1))
        
    possible_doors.sort(key=lambda p: p[0] + p[1])
    dx, dz = random.choice(possible_doors[:4])
    maze[dz][dx] = False
    
    for z in range(height):
        for x in range(width):
            if maze[z][x]:
                Entity(parent=level_parent, model='cube', collider='box', position=((x + 0.5) * 3, 2.25, (z + 0.5) * 3), scale=(3, 4.5, 3), texture=tex_wall, shadows=True, texture_scale=(4, 4))
    
    position_player = ((1 + 0.5) * 3, 1.5, (1 + 0.5) * 3)
    
    empty_cells = []
    for z in range(height):
        for x in range(width):
            if not maze[z][x] and (x, z) not in ((1, 1), (dx, dz)):
                empty_cells.append((x, z))
                
    if empty_cells:
        kx, kz = random.choice(empty_cells)
        k = Entity(parent=level_parent, model='quad', texture='Textures/key.png', position=((kx + 0.5) * 3, 1.5, (kz + 0.5) * 3), scale=(1, 1), billboard=True, double_sided=True)
        keys_in_world.append(k)

    exit_door = Entity(parent=level_parent, model='cube', collider='box', position=((dx + 0.5) * 3, 2.25, (dz + 0.5) * 3), scale=(3, 4.5, 3), texture=tex_door, shadows=True)

player = FirstPersonController(position=position_player, speed=10, jump_height=0)
player.enabled = False
mouse.locked = False
mouse.visible = True

player_light = PointLight(parent=player, position=(0, 1, 0), color=color.rgb(220, 200, 160), shadows=True)

def start_game():
    global level_start_time, crosshair
    
    if exit_door is None:
        load_generated_level(random.randint(1, 999999999))
        player.position = position_player

    main_menu.enabled = False
    player.enabled = True
    mouse.locked = True
    mouse.visible = False
    level_start_time = time.perf_counter()

    if crosshair is None:
        crosshair = Entity(parent=camera.ui, model='quad', texture='Textures/cursor.png', scale=(1, 1), color=color.white, always_on_top=True)
    else:
        crosshair.enabled = True

def restart_game():
    global level_completed, has_key, level_start_time
    level_completed = False
    has_key = False
    key_icon.visible = False
    finish_text.visible = False
    end_menu.enabled = False

    load_generated_level(random.randint(1, 999999999))

    player.position = position_player
    player.enabled = True
    mouse.locked = True
    mouse.visible = False
    level_start_time = time.perf_counter()

    sound_ambient.play()

def complete_level():
    global level_completed
    if level_completed:
        return
    level_completed = True
    elapsed = time.perf_counter() - level_start_time
    finish_text.text = f'Уровень пройден за {elapsed:.1f} сек'
    finish_text.visible = True

    end_menu.enabled = True
    player.enabled = False
    mouse.locked = False
    mouse.visible = True
    step_sound.stop()
    sound_key.stop()

def update():
    global has_key, countdown_start_time
    if main_menu.enabled or end_menu.enabled:
        return

    if not level_completed:
        if has_key:
            elapsed = time.perf_counter() - countdown_start_time
            time_left = max(0, time_limit - elapsed)
            timer_text.text = f'Время: {time_left:.1f} с'

            if time_left <= 0:
                finish_text.text = 'Время вышло!'
                finish_text.visible = True
                end_menu.enabled = True
                player.enabled = False
                mouse.locked = False
                mouse.visible = True
                step_sound.stop()
                return
        else:
            timer_text.text = f'Время: {time_limit:.1f} с'

    if held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']:
        if not step_sound.playing:
            step_sound.play()
    else:
        step_sound.stop()

    for k in keys_in_world:
        if k.enabled and distance(player.position, k.position) < 3:
            k.enabled = False
            has_key = True
            key_icon.visible = True
            sound_key.play()
            sound_ambient.stop()
            countdown_start_time = time.perf_counter()
            break

    if exit_door and exit_door.collider is None:
        dist = distance(Vec3(player.x, 0, player.z), Vec3(exit_door.x, 0, exit_door.z))
        if dist < 1.2:
            complete_level()

def input(key):
    if main_menu.enabled or end_menu.enabled:
        return

    if key == 'e' or key == 'left mouse down':
        if exit_door and distance(player.position, exit_door.position) < 4:
            if has_key:
                exit_door.collider = None
                exit_door.texture = tex_door_open
                print('Дверь открыта!')
            else:
                print('Нужен ключ!')

app.run()
