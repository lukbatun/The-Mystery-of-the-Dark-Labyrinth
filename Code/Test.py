from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Создаем объект с коллайдером
player = Entity(model='cube', collider='box', position=(0, 0, 0))
wall = Entity(model='cube', collider='box', position=(0, 0, 0), color=color.red)

def update():
    # Проверяем пересечение
    hit_info = player.intersects()
    if hit_info.hit:
        print(f"Столкновение с: {hit_info.entity}")

app.run()