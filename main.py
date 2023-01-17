# -*- coding: utf8 -*-
# 2d_crossy_road

import os
import random
import sys

import pygame

pygame.init()
running = True
moving = True
w, h = pygame.display.Info().current_w, pygame.display.Info().current_h
w -= w % 100
h -= h % 100
size = w, h
main_screen = pygame.display.set_mode(size)
pygame.display.set_caption('2d_crossy_road')


def load_image(name, colorkey=None):  # загрузка изображения спрайта
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


class AnimatedSprite(pygame.sprite.Sprite):  # загрузка изображений анимированного спрайта
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
            for x in range(columns):
                frame_location = (self.rect.w * x, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, scale):
        if moving:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], scale)


class Board:  # класс поля, необходим для хранения информации о объектах на поле и их состоянии
    def __init__(self, width, height):
        self.water_lines = None
        self.train_lines = None
        self.road_lines = None
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

    def get_cell(self, mouse_pos):
        if self.left < mouse_pos[0] < self.left + self.cell_size * self.width \
                and self.top < mouse_pos[1] < self.top + self.cell_size * self.height:
            column = (mouse_pos[0] - self.left) // self.cell_size
            row = (mouse_pos[1] - self.top) // self.cell_size
            return column, row
        else:
            return None

    def get_coords_by_cell(self, given_cell):
        if self.width >= given_cell[0] and self.height >= given_cell[1]:
            return self.left + self.cell_size * (given_cell[0]), self.height + self.cell_size * (given_cell[1])

    def on_click(self, cell_coords):
        pass

    def get_click(self, mouse_pos):
        new_cell = self.get_cell(mouse_pos)
        self.on_click(new_cell)

    def generate_line(self, x, add_offset):
        line = []
        type_line = random.choices(['safe', 'road', 'train', 'water'],
                                   weights=[self.chance_safe_line, self.chance_road_line,
                                            self.chance_train_line, self.chance_train_line],
                                   k=1)
        if type_line[0] == 'safe':
            for j in range(self.width):
                if 100 - random.randint(0,
                                        100) < self.chance_tree_spawn:

                    pos = self.get_coords_by_cell((j, x))[0], self.get_coords_by_cell((j, x))[
                                                                  1] - self.cell_size - add_offset
                    tree = Tree(tree_sprites, pos)
                    all_sprites.add(tree)
                    line.append(tree)
                elif 100 - random.randint(0, 100) < self.chance_rock_spawn:
                    pos = self.get_coords_by_cell((j, x))[0], self.get_coords_by_cell((j, x))[1] - add_offset
                    rock = Rock(rocks_sprites, pos)
                    all_sprites.add(rock)
                    line.append(rock)
                else:
                    line.append(0)
        elif type_line[0] == 'road':
            for j in range(self.width):
                pos = self.get_coords_by_cell((j, x))[0], self.get_coords_by_cell((j, x))[1] - add_offset
                road = Road(enviroment_sprites, pos)
                all_sprites.add(road)
                line.append(road)
            line_speed = random.randint(-15, -3) * random.choice([-1, 1])
            timer_interval = 6000 // abs(line_speed) + random.randint(100, 200)
            self.road_lines.append([x, line_speed, timer_interval])
        elif type_line[0] == 'train':
            for j in range(self.width):
                pos = self.get_coords_by_cell((j, x))[0], self.get_coords_by_cell((j, x))[1] - add_offset
                rails = Rails(enviroment_sprites, pos)
                all_sprites.add(rails)
                line.append(rails)
            line_speed = random.randint(-30, -14) * random.choice([-1, 1])
            timer_interval = 25000 // abs(line_speed)
            self.train_lines.append([x, line_speed, timer_interval])
        elif type_line[0] == 'water':
            for j in range(self.width):
                pos = self.get_coords_by_cell((j, x))[0], self.get_coords_by_cell((j, x))[1] - add_offset
                water = Water(enviroment_sprites, pos)
                all_sprites.add(water)
                line.append(water)
            line_speed = random.randint(-8, -4) * random.choice([-1, 1])
            timer_interval = 3000 // abs(line_speed) + random.randint(100, 200)
            self.water_lines.append([x, line_speed, timer_interval])
        return line

    def generate_area(self):
        self.road_lines = []
        self.train_lines = []
        self.water_lines = []
        for x in range(0, self.height - 1):
            line = self.generate_line(x, 0)
            self.board[x] = line

    def regenerate(self, shift):
        for x in range(self.height - 1, 0, -1):
            self.board[x] = self.board[x - shift]
        x = 0
        while x < len(self.road_lines):
            if self.road_lines[x][0] == self.height - 1:
                self.road_lines.pop(x)
            else:
                self.road_lines[x][0] += 1
                x += 1
        x = 0
        while x < len(self.train_lines):
            if self.train_lines[x][0] == self.height - 1:
                self.train_lines.pop(x)
            else:
                self.train_lines[x][0] += 1
                x += 1
        x = 0
        while x < len(self.water_lines):
            if self.water_lines[x][0] == self.height - 1:
                self.water_lines.pop(x)
            else:
                self.water_lines[x][0] += 1
                x += 1
        line = self.generate_line(0, self.cell_size)
        self.board[0] = line
        for el in all_sprites:
            if el.rect.y > main_screen.get_height() or el.rect.x < -3000 or el.rect.x > 3000:
                el.kill()


class Rails(pygame.sprite.Sprite):  # рельсы
    image = pygame.transform.scale(load_image('rails.jpg', -1), (110, 120))

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = Rails.image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1] - 22


class Road(pygame.sprite.Sprite):  # дорога
    image = pygame.transform.scale(load_image('road2.jpg'), (100, 100))

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = Road.image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1] - 10


class Water(pygame.sprite.Sprite):  # вода
    image = pygame.transform.scale(load_image('water.png'), (100, 100))

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = Water.image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1] - 10


class Hero(AnimatedSprite):  # персонаж
    hero_image = load_image('ch.png')

    def __init__(self, pos, *group):
        super().__init__(Hero.hero_image, 4, 4, pos[0], pos[1], *group)
        self.left = True
        self.alive = True
        self.count = 0
        self.movements = 0

    def move(self, x, y, do_flip):
        if moving and self.rect.top + y <= board.height * board.cell_size:
            self.rect = self.rect.move(x, y)
            if y < 0:
                hero.movements += 1
            elif y > 0:
                hero.movements -= 1
        if moving and self.rect.left < 0:
            self.rect = self.rect.move((board.width - 1) * board.cell_size, 0)
        elif moving and self.rect.left >= (board.width - 1) * board.cell_size:
            self.rect = self.rect.move((1 - board.width) * board.cell_size, 0)
        if moving and do_flip:
            if x < 0:
                self.left = True
            elif x > 0:
                self.left = False

    def game_end(self):
        self.alive = False

    def update(self):
        super().update((80, 80))
        cell = board.get_cell((main_screen.get_width() // 2, hero.rect.y))
        if cell is not None and board.board[cell[1]][0].__class__ == Water and (
                self.rect.x <= -80 or self.rect.x >= main_screen.get_width() - 10):
            hero.game_end()
        if not self.left and moving:
            self.image = pygame.transform.flip(self.image, True, False)
        new_log = pygame.sprite.spritecollideany(self, log_sprites)
        if moving and new_log and new_log.rect.x - self.rect.x <= -33:
            self.move(new_log.speed, 0, False)


class Tree(pygame.sprite.Sprite):  # дерево
    image = pygame.transform.scale(load_image('tree4.png'), (95, 190))

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = Tree.image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1] - 2


class Rock(pygame.sprite.Sprite):  # камень
    image = pygame.transform.scale(load_image('rock2.png'), (85, 70))

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = Rock.image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] + random.randint(1, 23)
        self.rect.y = pos[1] + random.randint(-9, 14)


class Car(pygame.sprite.Sprite):  # машина
    image_list = [(pygame.transform.scale(load_image('car.png', -1), (150, 100)), 0),
                  (pygame.transform.scale(load_image('car2.png', -1), (150, 100)), 1),
                  (pygame.transform.scale(load_image('car3.png', -1), (150, 100)), 2),
                  (pygame.transform.scale(load_image('car4.png', -1), (150, 80)), 3),
                  (pygame.transform.scale(load_image('car5.png', -1), (150, 80)), 4),
                  (pygame.transform.scale(load_image('car6.png', -1), (150, 80)), 5)
                  ]

    def __init__(self, group, pos, given_speed):
        super().__init__(group)
        car_number = random.choice(Car.image_list)[1]
        if given_speed >= 0:
            self.image = pygame.transform.flip(Car.image_list[car_number][0], True, False)
        else:
            self.image = Car.image_list[car_number][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1] + 10
        self.speed = given_speed

    def update(self):
        if not pygame.sprite.collide_mask(self, hero) and moving:
            self.rect = self.rect.move(self.speed, 0)
        else:
            hero.count += 1
            hero.game_end()


class Log(pygame.sprite.Sprite):  # бревно
    image = pygame.transform.scale(load_image('log.png', -1), (300, 130))

    def __init__(self, group, pos, speed_given):
        super().__init__(group)
        self.image = pygame.transform.flip(Log.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.size = (185, 80)
        self.rect.x = pos[0]
        self.rect.y = pos[1] - 4
        self.speed = speed_given

    def update(self):
        if moving:
            self.rect = self.rect.move(self.speed, 0)


class Train(pygame.sprite.Sprite):  # поезд
    image = pygame.transform.scale(load_image('train.jpg', -1), (200, 90))

    def __init__(self, group, pos, speed_given):
        super().__init__(group)
        if speed_given >= 0:
            self.image = pygame.transform.flip(Train.image, True, False)
        else:
            self.image = Train.image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.speed = speed_given

    def update(self):
        if not pygame.sprite.collide_mask(self, hero) and moving:
            self.rect = self.rect.move(self.speed, 0)
        else:
            hero.count += 1
            hero.game_end()


class Camera:  # камера

    @staticmethod
    def go(group, delt):
        for el in group:
            el.rect = el.rect.move(0, delt)


enviroment_sprites = pygame.sprite.Group()
hero_sprites = pygame.sprite.Group()
rocks_sprites = pygame.sprite.Group()
tree_sprites = pygame.sprite.Group()
car_sprites = pygame.sprite.Group()
train_sprites = pygame.sprite.Group()
log_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
timer_event = pygame.USEREVENT + 1
board = Board(size[0] // 100 + 1, size[1] // 100)
hero_pos = board.get_coords_by_cell((board.width // 2, board.height))
hero = Hero((hero_pos[0], hero_pos[1] - board.cell_size), hero_sprites)
all_sprites.add(hero)
clock = pygame.time.Clock()
camera = Camera()
should_update = True
show_start_screen = True
while running:
    if not hero.alive:
        if should_update:
            pygame.time.wait(300)
            moving = False
            copy_score = hero.movements
            best_score = str(open('data\\best_score.txt', 'r').readline().strip('\n'))
            if best_score == '':
                best_score = '0'
            largeFont = pygame.font.SysFont('comicsans', 80)
            lastScore = largeFont.render(f'Best Score: {max(int(best_score), copy_score)}', 1,
                                         (255, 255, 255))
            currentScore = largeFont.render(f'Score: {copy_score}', 1, (255, 255, 255))
            help_label = largeFont.render('Press "space" to restart', 1, (255, 255, 255))
            main_screen.fill((0, 0, 0))
            main_screen.blit(lastScore, ((board.width * board.cell_size) / 2 - lastScore.get_width() / 2, 150))
            main_screen.blit(currentScore, ((board.width * board.cell_size) / 2 - currentScore.get_width() / 2, 240))
            main_screen.blit(help_label, ((board.width * board.cell_size) / 2 - help_label.get_width() / 2, 330))
            if hero.movements > int(best_score):
                file = open('data\\best_score.txt', 'r+')
                file.truncate(0)
                file.write(str(hero.movements))
                file.close()

            hero.movements = 0
            pygame.display.update()
            should_update = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        moving = True
                        should_update = True
                        enviroment_sprites = pygame.sprite.Group()
                        hero_sprites = pygame.sprite.Group()
                        rocks_sprites = pygame.sprite.Group()
                        tree_sprites = pygame.sprite.Group()
                        car_sprites = pygame.sprite.Group()
                        train_sprites = pygame.sprite.Group()
                        log_sprites = pygame.sprite.Group()
                        all_sprites = pygame.sprite.Group()
                        timer_event = pygame.USEREVENT + 1
                        board = Board(size[0] // 100 + 1, size[1] // 100)
                        hero_pos = board.get_coords_by_cell((board.width // 2, board.height))
                        hero = Hero((hero_pos[0], hero_pos[1] - board.cell_size), hero_sprites)
                        all_sprites.add(hero)
                        clock = pygame.time.Clock()
                        camera = Camera()
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and not show_start_screen:
                    hero.move(0, -board.cell_size, True)
                if event.key == pygame.K_a and not show_start_screen:
                    hero.move(-board.cell_size, 0, True)
                if event.key == pygame.K_s and not show_start_screen:
                    hero.move(0, board.cell_size, True)
                if event.key == pygame.K_d and not show_start_screen:
                    hero.move(board.cell_size, 0, True)
                if event.key == pygame.K_SPACE and show_start_screen:
                    show_start_screen = False
        for i, speed, ticks in board.road_lines:
            if 0 <= pygame.time.get_ticks() % ticks <= 5:
                if speed >= 0:
                    car = Car(car_sprites, (-400, board.board[i][0].rect.y), speed)
                else:
                    car = Car(car_sprites, (main_screen.get_width(), board.board[i][0].rect.y), speed)
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
                    cord1 = main_screen.get_width()
                    delta = 200
                    for tr in range(random.randint(8, 16)):
                        train = Train(train_sprites, (cord1 + delta * tr, board.board[i][0].rect.y), speed)
                        all_sprites.add(train)
        for i, speed, ticks in board.water_lines:
            if 0 <= pygame.time.get_ticks() % ticks <= 5:
                if speed >= 0:
                    log = Log(log_sprites, (-400, board.board[i][0].rect.y), speed)
                else:
                    log = Log(log_sprites, (main_screen.get_width(), board.board[i][0].rect.y), speed)
                all_sprites.add(log)
        if hero.rect.y <= board.get_coords_by_cell((0, 4))[1]:
            board.regenerate(1)
            camera.go(group=all_sprites, delt=board.cell_size)

        cell = board.get_cell((hero.rect.x, hero.rect.y))

        if cell is \
                not None and board.board[cell[1]][0].__class__ == Water and \
                pygame.sprite.spritecollideany(hero, log_sprites) is None:
            hero.game_end()

        main_screen.fill((0, 255, 0))
        rocks_sprites.draw(main_screen)
        enviroment_sprites.draw(main_screen)
        log_sprites.draw(main_screen)
        hero_sprites.draw(main_screen)
        car_sprites.draw(main_screen)
        tree_sprites.draw(main_screen)
        train_sprites.draw(main_screen)
        log_sprites.update()
        hero_sprites.update()
        car_sprites.update()
        train_sprites.update()
        if show_start_screen:
            best_score = str(open('data\\best_score.txt', 'r').readline().strip('\n'))
            if best_score == '':
                best_score = '0'
            largeFont = pygame.font.SysFont('comicsans', 80)
            lastScore = largeFont.render(f'Best Score: {best_score}', 1,
                                         (0, 0, 0))
            help_label = largeFont.render('Press "space" to start', 1, (0, 0, 0))
            main_screen.blit(lastScore, ((board.width * board.cell_size) / 2 - lastScore.get_width() / 2, 150))
            main_screen.blit(help_label, ((board.width * board.cell_size) / 2 - help_label.get_width() / 2, 330))
        clock.tick(50)
        pygame.display.flip()
