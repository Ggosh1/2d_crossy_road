# -*- coding: utf8 -*-

import pygame
import math
import os
import sys
import random
from pygame.locals import * #это добавляет обработку клавиш


pygame.init()
running = True
size = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
rocks_sprites = pygame.sprite.Group()
tree_sprites = pygame.sprite.Group()
timer_event = pygame.USEREVENT + 1

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, *group):
        super().__init__(*group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, scale):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = pygame.transform.scale(self.frames[self.cur_frame], scale)


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 0
        self.top = 0
        self.cell_size = 100
        self.chance_safe_line = 90
        self.chance_tree_spawn = 10
        self.chance_rock_spawn = 5
        self.generate_area()
        print(self.board)

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        for i in range(self.height):
            for j in range(self.width):
                if i * self.cell_size + self.top + self.cell_size <= screen.get_size()[
                    1] and j * self.cell_size + self.left + self.cell_size <= screen.get_size()[0]:
                    pygame.draw.rect(screen, pygame.Color(255, 255, 255),
                                     (j * self.cell_size + self.left, i * self.cell_size + self.top, self.cell_size,
                                      self.cell_size), 1)

    def get_cell(self, mouse_pos):
        if self.left < mouse_pos[0] < self.left + self.cell_size * self.width and self.top < mouse_pos[
            1] < self.top + self.cell_size * self.height:
            column = (mouse_pos[0] - self.left) // self.cell_size
            row = (mouse_pos[1] - self.top) // self.cell_size
            return column, row
        else:
            return None

    def get_coords_by_cell(self, cell):
        if self.width >= cell[0] and self.height >= cell[1]:
            return self.left + self.cell_size * (cell[0]), self.height + self.cell_size * (cell[1])


    def on_click(self, cell_coords):
        pass

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def generate_area(self):
        self.road_lines = []
        self.list_ticks = []
        is_last_line_safe = False # не должно быть 2 линии безопасности подряд
        for i in range(0, self.height - 1):
            line = []
            type_line = random.choices(['safe', 'unsafe'], weights=[self.chance_safe_line, 100 - self.chance_safe_line],
                                       k=1)
            if type_line[0] == 'safe' and not is_last_line_safe: # 20% шанс, что линия станет безопасной
                is_last_line_safe = True
                for j in range(self.width):
                    if 100 - random.randint(0, 100) < self.chance_tree_spawn: # 10% шанс для каждой клетки, что заспавнится дерево
                        pos = self.get_coords_by_cell((j, i))[0], self.get_coords_by_cell((j, i))[1] - self.cell_size
                        line.append(Tree(tree_sprites, pos))
                    elif 100 - random.randint(0, 100) < self.chance_rock_spawn:
                        pos = self.get_coords_by_cell((j, i))[0], self.get_coords_by_cell((j, i))[1] - self.cell_size
                        line.append(Rock(rocks_sprites, pos))
                    else:
                        line.append(0)
            else:
                is_last_line_safe = False
                for j in range(self.width):
                    pos = self.get_coords_by_cell((j, i))[0], self.get_coords_by_cell((j, i))[1]
                    line.append(Road(all_sprites, pos))
                line_speed = random.randint(-15, -5) * random.choice([-1, 1])
                timer_interval = 5000 // abs(line_speed) + random.randint(100, 200)
                self.road_lines.append((i, line_speed, timer_interval))
            self.board[i] = line





class Road(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('road2.jpg'), (100, 100))
    def __init__(self, group, pos):
        super().__init__(group)
        self.image = Road.image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1] - 10


class Hero(AnimatedSprite):
    hero_image = load_image('ch.png')

    def __init__(self, pos, *group):
        super().__init__(Hero.hero_image, 4, 4, pos[0], pos[1], *group)

    def move(self, x, y):
        self.rect = self.rect.move(x, y)

    def update(self):
        super().update((100, 100))


class Tree(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('tree4.png'), (95, 190))
    def __init__(self, group, pos):
        super().__init__(group)
        self.image = Tree.image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1] - 2


class Rock(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('rock2.png'), (85, 70))
    def __init__(self, group, pos):
        super().__init__(group)
        self.image = Rock.image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] + random.randint(1, 23)
        self.rect.y = pos[1] + random.randint(-9, 14)


class Car(pygame.sprite.Sprite):
    image_list = [pygame.transform.scale(load_image('car.png', -1), (200, 150)), pygame.transform.scale(load_image('car2.png', -1), (200, 150)),
                           pygame.transform.scale(load_image('car3.png', -1), (200, 150)), pygame.transform.scale(load_image('car4.png', -1), (200, 120)),
                           pygame.transform.scale(load_image('car5.png', -1), (200, 120)), pygame.transform.scale(load_image('car6.png', -1), (200, 120))]
    def __init__(self, group, pos, speed):
        super().__init__(group)
        if speed >= 0:
            self.image = pygame.transform.flip(random.choice(Car.image_list), True, False)
        else:
            self.image = random.choice(Car.image_list)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.speed = speed

    def update(self):
        self.rect = self.rect.move(self.speed, 0)




board = Board(size[0] // 100, size[1] // 100)
hero_pos = board.get_coords_by_cell((board.width // 2, board.height))
hero = Hero((hero_pos[0], hero_pos[1] - board.cell_size - 10), all_sprites)
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(board.get_cell(event.pos))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                hero.move(0, -board.cell_size)
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                hero.move(-board.cell_size, 0)
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                hero.move(0, board.cell_size)
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                hero.move(board.cell_size, 0)
    for i, speed, ticks in board.road_lines:
        if 0 <= pygame.time.get_ticks() % ticks <= 5:
            if speed >= 0:
                Car(all_sprites, (-400, board.board[i][0].rect.y - 45), speed)
            else:
                Car(all_sprites, (screen.get_width(), board.board[i][0].rect.y - 45), speed)



    screen.fill((0, 255, 0))
    board.render(screen)
    rocks_sprites.draw(screen)
    all_sprites.draw(screen)
    all_sprites.update()
    tree_sprites.draw(screen)
    clock.tick(50)
    pygame.display.flip()
