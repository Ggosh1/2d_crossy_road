# -*- coding: utf8 -*-

import pygame
import math
import os
import sys
import random
from pygame.locals import *  # это добавляет обработку клавиш

pygame.init()
running = True
size = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode(size)
enviroment_sprites = pygame.sprite.Group()
hero_sprites = pygame.sprite.Group()
rocks_sprites = pygame.sprite.Group()
tree_sprites = pygame.sprite.Group()
car_sprites = pygame.sprite.Group()
train_sprites = pygame.sprite.Group()
log_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
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
        self.chance_safe_line = 25
        self.chance_tree_spawn = 10
        self.chance_rock_spawn = 5
        self.chance_road_line = 55
        self.chance_train_line = 10
        self.chance_water_line = 100 - self.chance_safe_line - self.chance_road_line - self.chance_train_line
        self.generate_area()

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

    def generate_line(self, i, add_offset):
        line = []
        type_line = random.choices(['safe', 'road', 'train', 'water'],
                                   weights=[self.chance_safe_line, self.chance_road_line,
                                            self.chance_train_line, self.chance_train_line],
                                   k=1)
        if type_line[0] == 'safe':  # 20% шанс, что линия станет безопасной
            for j in range(self.width):
                if 100 - random.randint(0,
                                        100) < self.chance_tree_spawn:  # 10% шанс для каждой клетки, что заспавнится дерево
                    pos = self.get_coords_by_cell((j, i))[0], self.get_coords_by_cell((j, i))[1] - self.cell_size - add_offset
                    tree = Tree(tree_sprites, pos)
                    all_sprites.add(tree)
                    line.append(tree)
                elif 100 - random.randint(0, 100) < self.chance_rock_spawn:
                    pos = self.get_coords_by_cell((j, i))[0], self.get_coords_by_cell((j, i))[1] - add_offset
                    rock = Rock(rocks_sprites, pos)
                    all_sprites.add(rock)
                    line.append(rock)
                else:
                    line.append(0)
        elif type_line[0] == 'road':
            for j in range(self.width):
                pos = self.get_coords_by_cell((j, i))[0], self.get_coords_by_cell((j, i))[1] - add_offset
                road = Road(enviroment_sprites, pos)
                all_sprites.add(road)
                line.append(road)
            line_speed = random.randint(-15, -3) * random.choice([-1, 1])
            timer_interval = 6000 // abs(line_speed) + random.randint(100, 200)
            self.road_lines.append([i, line_speed, timer_interval])
        elif type_line[0] == 'train':
            for j in range(self.width):
                pos = self.get_coords_by_cell((j, i))[0], self.get_coords_by_cell((j, i))[1] - add_offset
                rails = Rails(enviroment_sprites, pos)
                all_sprites.add(rails)
                line.append(rails)
            line_speed = random.randint(-30, -14) * random.choice([-1, 1])
            timer_interval = 25000 // abs(line_speed)
            self.train_lines.append([i, line_speed, timer_interval])
        elif type_line[0] == 'water':
            for j in range(self.width):
                pos = self.get_coords_by_cell((j, i))[0], self.get_coords_by_cell((j, i))[1] - add_offset
                water = Water(enviroment_sprites, pos)
                all_sprites.add(water)
                line.append(water)
            line_speed = random.randint(-8, -4) * random.choice([-1, 1])
            timer_interval = 3000 // abs(line_speed) + random.randint(100, 200)
            self.water_lines.append([i, line_speed, timer_interval])
        return line

    def generate_area(self):
        self.road_lines = []
        self.train_lines = []
        self.water_lines = []
        for i in range(0, self.height - 1):
            line = self.generate_line(i, 0)
            self.board[i] = line

    def regenerate(self, shift):
        for i in range(self.height - 1, 0, -1):
            self.board[i] = self.board[i - shift]
        i = 0
        while i < len(self.road_lines):
            if self.road_lines[i][0] == self.height - 1:
                self.road_lines.pop(i)
            else:
                self.road_lines[i][0] += 1
                i += 1
        i = 0
        while i < len(self.train_lines):
            if self.train_lines[i][0] == self.height - 1:
                self.train_lines.pop(i)
            else:
                self.train_lines[i][0] += 1
                i += 1
        i = 0
        while i < len(self.water_lines):
            if self.water_lines[i][0] == self.height - 1:
                self.water_lines.pop(i)
            else:
                self.water_lines[i][0] += 1
                i += 1
        line = self.generate_line(0, self.cell_size)
        self.board[0] = line


class Rails(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('rails.jpg', -1), (110, 120))

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = Rails.image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1] - 22


class Road(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('road2.jpg'), (100, 100))

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = Road.image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1] - 10

class Water(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('water.png'), (100, 100))

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = Water.image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1] - 10


class Hero(AnimatedSprite):
    hero_image = load_image('ch.png')

    def __init__(self, pos, *group):
        super().__init__(Hero.hero_image, 4, 4, pos[0], pos[1], *group)
        self.life = True
        self.left = True

    def move(self, x, y):
        self.rect = self.rect.move(x, y)
        if x < 0:
            self.left = True
        elif x > 0:
            self.left = False

    def update(self):
        super().update((80, 80))
        if not self.left:
            self.image = pygame.transform.flip(self.image, True, False)
        if pygame.sprite.spritecollide(self, car_sprites, False) or pygame.sprite.spritecollide(self, train_sprites, False):
            self.life = False
        log = pygame.sprite.spritecollideany(self, log_sprites)
        if log:
            self.move(log.speed, 0)


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
    image_list = [(pygame.transform.scale(load_image('car.png', -1), (150, 100)), 0),
                  (pygame.transform.scale(load_image('car2.png', -1), (150, 100)), 1),
                  (pygame.transform.scale(load_image('car3.png', -1), (150, 100)), 2),
                  (pygame.transform.scale(load_image('car4.png', -1), (150, 80)), 3),
                  (pygame.transform.scale(load_image('car5.png', -1), (150, 80)), 4),
                  (pygame.transform.scale(load_image('car6.png', -1), (150, 80)), 5)
    ]

    def __init__(self, group, pos, speed):
        super().__init__(group)
        car_number = random.choice(Car.image_list)[1]
        if speed >= 0:
            self.image = pygame.transform.flip(Car.image_list[car_number][0], True, False)
        else:
            self.image = Car.image_list[car_number][0]
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1] + 10
        self.speed = speed

    def update(self):
        self.rect = self.rect.move(self.speed, 0)


class Log(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('log.png', -1), (300, 130))

    def __init__(self, group, pos, speed):
        super().__init__(group)
        self.image = pygame.transform.flip(Log.image, True, False)
        self.rect = self.image.get_rect()
        self.rect = pygame.Rect((self.rect.left + 180, self.rect.top, 200, 80))
        self.rect.x = pos[0]
        self.rect.y = pos[1] - 4
        self.speed = speed

    def update(self):
        self.rect = self.rect.move(self.speed, 0)


class Train(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('train.jpg', -1), (200, 90))

    def __init__(self, group, pos, speed):
        super().__init__(group)
        if speed >= 0:
            self.image = pygame.transform.flip(Train.image, True, False)
        else:
            self.image = Train.image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.speed = speed

    def update(self):
        self.rect = self.rect.move(self.speed, 0)


class Camera:

    def go(self, group, delt):
        for el in group:
            el.rect = el.rect.move(0, delt)


board = Board(size[0] // 100 + 1, size[1] // 100)
hero_pos = board.get_coords_by_cell((board.width // 2, board.height))
hero = Hero((hero_pos[0], hero_pos[1] - board.cell_size), hero_sprites)
all_sprites.add(hero)
clock = pygame.time.Clock()
camera = Camera()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(board.get_cell(event.pos))
        if event.type == pygame.KEYDOWN and hero.life:
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
                car = Car(car_sprites, (-400, board.board[i][0].rect.y), speed)
            else:
                car = Car(car_sprites, (screen.get_width(), board.board[i][0].rect.y), speed)
            all_sprites.add(car)
    for i, speed, ticks in board.train_lines:
        if 0 <= pygame.time.get_ticks() % ticks <= 2:
            if speed >= 0:
                cord1 = -400
                delta = -200
                for tr in range(random.randint(8, 16)):
                    train = Train(train_sprites, (cord1 + delta * tr, board.board[i][0].rect.y), speed)
                    all_sprites.add(train)
            else:
                cord1 = screen.get_width()
                delta = 200
                for tr in range(random.randint(8, 16)):
                    train = Train(train_sprites, (cord1 + delta * tr, board.board[i][0].rect.y), speed)
                    all_sprites.add(train)
    for i, speed, ticks in board.water_lines:
        if 0 <= pygame.time.get_ticks() % ticks <= 5:
            if speed >= 0:
                log = Log(log_sprites, (-400, board.board[i][0].rect.y), speed)
            else:
                log = Log(log_sprites, (screen.get_width(), board.board[i][0].rect.y), speed)
            all_sprites.add(log)
    if hero.rect.y <= board.get_coords_by_cell((0, 4))[1]:
        board.regenerate(1)
        camera.go(group=all_sprites, delt=board.cell_size)

    screen.fill((0, 255, 0))
    board.render(screen)
    rocks_sprites.draw(screen)
    enviroment_sprites.draw(screen)
    log_sprites.draw(screen)
    hero_sprites.draw(screen)
    car_sprites.draw(screen)
    tree_sprites.draw(screen)
    train_sprites.draw(screen)
    if hero.life:
        log_sprites.update()
        hero_sprites.update()
        car_sprites.update()
        train_sprites.update()
    clock.tick(50)
    pygame.display.flip()
