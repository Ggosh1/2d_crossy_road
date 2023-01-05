# -*- coding: utf8 -*-

import pygame
import math
import os
import sys
from pygame.locals import * #это добавляет обработку клавиш


pygame.init()
running = True
size = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()

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

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = pygame.transform.scale(self.frames[self.cur_frame], (100, 100))


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 0
        self.top = 0
        self.cell_size = 100

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
            return self.left + self.cell_size * (cell[0]), self.height + self.cell_size * (cell[1] - 1)


    def on_click(self, cell_coords):
        pass

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)


class Hero(AnimatedSprite):
    hero_image = load_image('ch.png')

    def __init__(self, pos, *group):
        super().__init__(Hero.hero_image, 4, 4, pos[0], pos[1], *group)

    def move(self, x, y):
        self.rect = self.rect.move(x, y)

    def update(self):
        super().update()


board = Board(size[0] // 100, size[1] // 100)
hero = Hero(board.get_coords_by_cell((board.width // 2, board.height)), all_sprites)
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


    screen.fill((0, 0, 0))
    board.render(screen)
    all_sprites.draw(screen)
    all_sprites.update()
    clock.tick(50)
    pygame.display.flip()
