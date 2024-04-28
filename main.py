from typing import Any
import pygame

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("СВО II")

#частота кадров
clock = pygame.time.Clock()
FPS = 60

moving_right = False
moving_left = False

back_gr = (144, 201, 120)

def draw_back_graund():
    screen.fill(back_gr)

class Soldier(pygame.sprite.Sprite):
    def __init__(self, pers_type, x ,y , scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.pers_type = pers_type
        self.speed = speed
        self.direction = 1
        self.jump = False
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        temp_list = []
        for i in range(1):
            img = pygame.image.load(f"img/{pers_type}/Idle/{i}.png")
            self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        temp_list = []
        for i in range(5):
            img = pygame.image.load(f"img/{pers_type}/run/{i}.png")
            self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        #выделяем место для персонажа на экране и ставим его в начальную точку
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0
        if moving_left:
            dx = -self.speed
            self.direction = -1
            self.flip = True
        if moving_right:
            dx = self.speed
            self.direction = 1
            self.flip = False
        #двигаем прямоугольник
        self.rect.x += dx
        self.rect.y += dy

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        #изображение меняется в зависимости от текущего кадра
        self.image = self.animation_list[self.action][self.frame_index]
        #прошло ли достаточно времени с последнего обновления
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1 
        #если анимация закончилась - возвращаемся
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            #обновляем настройки анимации
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()


    #выводим персонажа на экран
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
    

player = Soldier("player", 200, 700, 4, 5)
enemy = Soldier("enemy", 400, 700, 4, 5)


run = True
while run:

    clock.tick(FPS)

    draw_back_graund()

    player.update_animation()
    player.draw()
    enemy.draw()

    if player.alive:
        if moving_left or moving_right:
            player.update_action(1) #run
        else:
            player.update_action(0)
        player.move(moving_left, moving_right) 
    
    for event in pygame.event.get():
        #выходи из игры
        if event.type == pygame.QUIT:
            run = False
        #нажатие клавиш
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False

    pygame.display.update()


pygame.quit()
