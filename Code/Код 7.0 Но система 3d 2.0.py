from ursina import destroy
from ursina import destroy
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import os
import ast
import time

app = Ursina()
window.color = color.black
position_player = (0, 0, 0)

wall_tex = load_texture('Textures/wall.jpg')
floor_tex = load_texture('Textures/floor.jpg')
ceiling_tex = load_texture('Textures/potolock.jpg')
door_texture = load_texture('Textures/door.png')
door_open_texture = load_texture('Textures/door_open.png')

if not wall_tex:
    wall_tex = 'white_cube'
if not floor_tex:
    floor_tex = 'white_cube'
if not ceiling_tex:
    ceiling_tex = 'white_cube'
if not door_texture:
    door_texture = 'white_cube'
if not door_open_texture:
    door_open_texture = 'white_cube'

scene.ambient_color = color.rgb(5, 5, 5)
scene.fog_density = 0.08
scene.fog_color = color.black

Entity(model='plane', collider='box', scale=150, texture=floor_tex, texture_scale=(50, 50), position=(75, 0, 75), shadows=True)
Entity(model='plane', collider='box', scale=150, texture=ceiling_tex, texture_scale=(50, 50), position=(75, 4.5, 75), rotation_x=180, shadows=True)

sound_ambient = Audio('Music and Sounds/Stone Abyss', volume=0.5, loop=False, autoplay=True)
sound_key = Audio('Music and Sounds/Key_up', volume=0.7, autoplay=False, loop=False)
step_sound = Audio('Music and Sounds/echo-footsteps', autoplay=False, loop=False)

vignette1 = Entity(parent=camera.ui, model='quad', texture='Textures/fog3.png', scale=(1.8, 1.5), color=color.white, always_on_top=True)
vignette3 = Entity(parent=camera.ui, model='quad', texture='Textures/inv.png', scale=(0.5, 0.11), position=(-0.64, -0.45, 0), color=color.white, always_on_top=True)
key_icon = Entity(parent=camera.ui, model='quad', texture='Textures/key.png', scale=(0.1, 0.1), position=(-0.83, -0.45, -0.1), visible=False, always_on_top=True)
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

main_menu = Entity(parent=camera.ui, enabled=True)
end_menu = Entity(parent=camera.ui, enabled=False)

main_bg = Sprite(texture='Textures/wall.jpg', parent=main_menu, scale=(1.8, 1), unlit=True)
main_title = Text(text='ТАЙНА ТЕМНОГО ЛАБИРИНТА', parent=main_menu, y=0.3, origin=(0, 0), scale=3, color=color.red)
start_btn = Button(text='ИГРАТЬ', parent=main_menu, y=0, scale=(0.3, 0.08), color=color.gray, on_click=lambda: start_game())
exit_btn = Button(text='ВЫХОД', parent=main_menu, y=-0.1, scale=(0.3, 0.08), color=color.dark_gray, on_click=application.quit)

end_bg = Sprite(texture='Textures/potolock.jpg', parent=end_menu, scale=(1.8, 1), unlit=True)
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
            world_x = (x + 0.5) * 3
            world_z = (z + 0.5) * 3

            if t == 'spawn':
                position_player = (world_x, 1.5, world_z)
            elif t == 'exit':
                exit_door = Entity(model='cube', collider='box', position=(world_x, 2.25, world_z), scale=(3, 4.5, 3), texture=door_texture, shadows=True)
            elif t == 'key':
                k = Entity(model='quad', texture='Textures/key.png', position=(world_x, 1.5, world_z), scale=(1, 1), billboard=True, double_sided=True)
                keys_in_world.append(k)
            elif t == 'wall':
                Entity(model='cube', collider='box', position=(world_x, 2.25, world_z), scale=(3, 4.5, 3), texture=wall_tex, texture_scale=(2, 2), shadows=True)

import random

def generate_maze(width, height, seed):
    random.seed(seed)
    
    # Сетка: True = стена, False = проход
    maze = [[True] * width for _ in range(height)]
    
    # Стартуем с клетки (1, 1)
    stack = [(1, 1)]
    maze[1][1] = False
    
    while stack:
        x, y = stack[-1]
        # Соседи через одну клетку (чтобы стены оставались между проходами)
        neighbors = []
        for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
            nx, ny = x + dx, y + dy
            if 0 < nx < width - 1 and 0 < ny < height - 1 and maze[ny][nx]:
                neighbors.append((nx, ny, dx, dy))
        
        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            # Убираем стену между текущей и соседней клеткой
            maze[y + dy // 2][x + dx // 2] = False
            maze[ny][nx] = False
            stack.append((nx, ny))
        else:
            stack.pop()  # тупик — откатываемся
    
    return maze


def load_generated_level(seed, width=21, height=21):
    global position_player, exit_door
    
    maze = generate_maze(width, height, seed)
    
    for z in range(height):
        for x in range(width):
            world_x = (x + 0.5) * 3
            world_z = (z + 0.5) * 3
            
            if maze[z][x]:  # стена
                Entity(model='cube', collider='box',
                       position=(world_x, 2.25, world_z),
                       scale=(3, 4.5, 3), texture=wall_tex,
                       texture_scale=(2, 2), shadows=True)
    
    # Спавн в (1,1), выход в дальнем углу
    position_player = ((1 + 0.5) * 3, 1.5, (1 + 0.5) * 3)
    
    # Ищем самую дальнюю проходимую клетку для выхода
    ex, ez = width - 2, height - 2
    exit_door = Entity(model='cube', collider='box',
                       position=((ex + 0.5) * 3, 2.25, (ez + 0.5) * 3),
                       scale=(3, 4.5, 3), texture=door_texture, shadows=True)


player = FirstPersonController(position=position_player, speed=10, jump_height=0)
player.enabled = False
mouse.locked = False
mouse.visible = True

player_light = PointLight(parent=player, position=(0, 1, 0), color=color.rgb(220, 200, 160), shadows=True)

def start_game():
    global level_start_time, crosshair

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

    player.position = position_player
    player.enabled = True
    mouse.locked = True
    mouse.visible = False
    level_start_time = time.perf_counter()

    for k in keys_in_world:
        k.enabled = True

    if exit_door:
        exit_door.texture = door_texture
        exit_door.collider = 'box'

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
                exit_door.texture = door_open_texture
                exit_door.collider = None
                print('Дверь открыта!')
            else:
                print('Нужен ключ!')

load_generated_level(seed=123451231232131312)


app.run()
