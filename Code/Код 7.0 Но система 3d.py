from ursina import * 
from ursina.prefabs.first_person_controller import FirstPersonController
import os
import ast
import time

app = Ursina()
window.color = color.black
position_player = (0, 0, 0)

scene.ambient_color = color.rgb(5, 5, 5)
scene.fog_density = 0.08
scene.fog_color = color.black

base_dir = os.path.dirname(os.path.abspath(__file__))
textures_dir = os.path.join(base_dir, 'Textures')
sounds_dir = os.path.join(base_dir, 'Music and Sounds')
wall_tex = load_texture(os.path.join(textures_dir, 'wall.jpg')) or 'white_cube'
floor_tex = load_texture(os.path.join(textures_dir, 'floor.jpg')) or 'white_cube'
potolock = load_texture(os.path.join(textures_dir, 'potolock.jpg')) or 'white_cube'
door_texture = load_texture(os.path.join(textures_dir, 'door.png')) or 'white_cube'
door_open_texture = load_texture(os.path.join(textures_dir, 'door_open.png')) or 'white_cube'

Entity(model='plane', collider='box', scale=150, texture=floor_tex, texture_scale=(50, 50), position=(75, 0, 75), shadows=True)
Entity(model='plane', collider='box', scale=150, texture=potolock, texture_scale=(50, 50), position=(75, 4.5, 75), rotation_x=180, shadows=True)

sound = Audio(sound_file_name=os.path.join(sounds_dir, 'Stone Abyss.mp3'), volume=0.5, loop=False, autoplay=True)
step_sound = Audio(os.path.join(sounds_dir, 'echo-footsteps.mp3'), autoplay=False, loop=False)

vignette1 = Entity(parent=camera.ui, model='quad', texture=os.path.join(textures_dir, 'hi.png'), scale=(1.8, 1.5), color=color.white, always_on_top=True)
vignette2 = Entity(parent=camera.ui, model='quad', texture=os.path.join(textures_dir, 'cursor.png'), scale=(1, 1), color=color.white, always_on_top=True)
vignette3 = Entity(parent=camera.ui, model='quad', texture=os.path.join(textures_dir, 'inv.png'), scale=(0.5, 0.11), position=(-0.64, -0.45, 0), color=color.white, always_on_top=True)

keys_in_world = []
has_key = False
level_start_time = time.perf_counter()
level_completed = False

key_icon = Entity(parent=camera.ui, model='quad', texture=os.path.join(textures_dir, 'key.png'), scale=(0.1, 0.1), position=(-0.83, -0.45, -0.1), visible=False, always_on_top=True)
exit_door = None 

timer_text = Text(text='Время: 0.0 с', position=(-0.64, 0.45), scale=1.4, color=color.white)
finish_text = Text(text='', position=(0, 0), origin=(0, 0), scale=2, color=color.azure, visible=False)

def complete_level():
    global level_completed
    if level_completed: return
    level_completed = True
    elapsed = time.perf_counter() - level_start_time
    finish_text.text = f'Уровень пройден за {elapsed:.1f} сек'
    finish_text.visible = True
    player.speed = 0

def load_level():
    global position_player, exit_door
    level_path = os.path.join(os.path.dirname(__file__), 'level.txt')
    
    if not os.path.exists(level_path):
        print("Файл level.txt не найден!")
        return

    with open(level_path) as f:
        for line in f:
            if not line.strip(): continue
            t, x, z = ast.literal_eval(line)

            world_x = (x + 0.5) * 3
            world_z = (z + 0.5) * 3

            if t == 'spawn': 
                position_player = (world_x, 1.5, world_z)
            elif t == 'exit': 
                exit_door = Entity(model='cube', collider='box', position=(world_x, 2.25, world_z), scale=(3, 4.5, 3), texture=door_texture, shadows=True)
            elif t == 'key':
                k = Entity(model='quad', texture=os.path.join(textures_dir, 'key.png'), position=(world_x, 1.5, world_z), scale=(1,1), billboard=True, double_sided=True)
                keys_in_world.append(k)
            elif t == 'wall': 
                Entity(model='cube', collider='box', position=(world_x, 2.25, world_z), scale=(3, 4.5, 3), texture=wall_tex, texture_scale=(2, 2), shadows=True)

load_level()

player = FirstPersonController(position=position_player, speed=10, jump_height=0)
player.cursor.visible = False
player_light = PointLight(parent=player, position=(0, 1, 0), color=color.rgb(220, 200, 160), shadows=True)

def update():
    global has_key
    if not level_completed:
        elapsed = time.perf_counter() - level_start_time
        timer_text.text = f'Время: {elapsed:.1f} с'

    if held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']:
        if not step_sound.playing: step_sound.play()
    else:
        step_sound.stop()

    for k in keys_in_world:
        if k.enabled and distance(player.position, k.position) < 3:
            k.enabled = False
            has_key = True
            key_icon.visible = True

    if exit_door and exit_door.collider is None and distance(player.position, exit_door.position) < 1.8:
        complete_level()

def input(key):
    if key == 'e' or key == 'left mouse down':
        if exit_door and distance(player.position, exit_door.position) < 4:
            if has_key:
                exit_door.texture = door_open_texture
                exit_door.collider = None 
                print('Дверь открыта!')
            else:
                print('Нужен ключ!')

app.run()
