# -*- coding: utf8 -*-

import pygame
import math


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
                if i * self.cell_size + self.top + self.cell_size <= screen.get_size()[1] and j * self.cell_size + self.left + self.cell_size <= screen.get_size()[0]:
                    pygame.draw.rect(screen, pygame.Color(255, 255, 255),
                                     (j * self.cell_size + self.left, i * self.cell_size + self.top, self.cell_size,
                                      self.cell_size), 1)


    def get_cell(self, mouse_pos):
        if self.left < mouse_pos[0] < self.left + self.cell_size * self.width and self.top < mouse_pos[1] < self.top + self.cell_size * self.height:
            column = (mouse_pos[0] - self.left) // self.cell_size
            row = (mouse_pos[1] - self.top) // self.cell_size
            return column, row
        else:
            return None

    def on_click(self, cell_coords):
        pass

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)


pygame.init()
running = True
size = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode(size)
print(size)
board = Board(size[0] // 100, size[1] // 100)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(board.get_cell(event.pos))
    screen.fill((0, 0, 0))
    board.render(screen)
    pygame.display.flip()