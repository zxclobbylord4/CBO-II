import pygame
import os
import random

pygame.init()


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("СВО II")

#частота кадров
clock = pygame.time.Clock()
FPS = 60

GRAVITY = 0.75
TILE_SIZE = 40


moving_left = False
moving_right = False
shoot = False


bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
bg = pygame.image.load('img/backgraund/0.png').convert_alpha()



back_gr = (144, 201, 120)
red_line = (255, 0, 0)

def draw_back_graund():
	screen.fill(back_gr)
	pygame.draw.line(screen, red_line, (0, 690), (SCREEN_WIDTH, 690))
	screen.blit(bg, (0, 0))

def bg_music():
  pygame.mixer.music.load('sound/Muz.mp3')
  pygame.mixer.music.play(-1)
  pygame.mixer.music.set_volume(0.2)
  
def sound_shoot():
  sound_shoot = pygame.mixer.Sound('sound/shoot.mp3')
  sound_shoot.set_volume(0.2)
  sound_shoot.play()



class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_type = char_type
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.health = 100
		self.max_health = self.health
		self.direction = 1
		self.speed_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()

		#переменные для ии
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling = False
		self.idling_counter = 0

		#загрузка всех изображений для персонажей
		animation_types = ['Idle', 'run', 'jump', 'death']
		for animation in animation_types:
			#обновляем временный список изображений
			temp_list = []
			#считываем кол-во изображений в папке
			num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)


	def update(self):
		self.update_animation()
		self.check_alive()
		#обновляем перезарядку
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1


	def move(self, moving_left, moving_right):
		#обновляем перемещение
		dx = 0
		dy = 0

		#перемещение при движении влево или вправо
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		#прыжок
		if self.jump == True and self.in_air == False:
			self.speed_y = -11
			self.jump = False
			self.in_air = True

		#сила гравитации
		self.speed_y += GRAVITY
		if self.speed_y > 10:
			self.speed_y
		dy += self.speed_y

		#ограничение по полу
		if self.rect.bottom + dy > 735:
			dy = 735 - self.rect.bottom
			self.in_air = False

		#обновление положения модельки
		self.rect.x += dx
		self.rect.y += dy


	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery - 10, self.direction)
			bullet_group.add(bullet)
			self.ammo -= 1

	
	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1, 200) == 1:
				self.update_action(0)   #стойка
				self.idling = True
				self.idling_counter = 50
			#если игрок находится в поле зрения врага
			if self.vision.colliderect(player.rect):
				self.update_action(0)  #стойка
				self.shoot()
				sound_shoot()
			else:
				if self.idling == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1)  #бег
					self.move_counter += 1
					#обновление зрения ии во время бега
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False


	def update_animation(self):
		#обновление анимации
		ANIMATION_COOLDOWN = 100
		#обновление изображения в зависимости от текущего кадра
		self.image = self.animation_list[self.action][self.frame_index]
		#проверка на необходимость обновления кадра
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#возвращение к началу, если анимация закончилась
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0



	def update_action(self, new_action):
		#проверка на новую анимацию
		if new_action != self.action:
			self.action = new_action
			#обновление настроек анимации
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()



	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)


	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)



class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		self.rect.x += (self.direction * self.speed)
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()

		#столкновение с персонажами
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 25
					self.kill()



enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()



player = Soldier('player', 200, 720, 1.5, 5, 30)
enemy = Soldier('enemy', 400, 680, 1.5, 5, 30)
enemy2 = Soldier('enemy', 600, 680, 1.5, 5, 30)
enemy_group.add(enemy)
enemy_group.add(enemy2)


run = True
bg_music()
while run:

	clock.tick(FPS)

	draw_back_graund()

	player.update()
	player.draw()

	for enemy in enemy_group:
		enemy.ai()
		enemy.update()
		enemy.draw()


	bullet_group.update()
	bullet_group.draw(screen)


	if player.alive:
		if shoot:
			player.shoot()
		if player.in_air:
			player.update_action(2)  #прыжок
		elif moving_left or moving_right:
			player.update_action(1)  #бег
		else:
			player.update_action(0)  #стойка
		player.move(moving_left, moving_right)


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_SPACE:
				shoot = True
				sound_shoot()
			if event.key == pygame.K_w and player.alive:
				player.jump = True
			if event.key == pygame.K_ESCAPE:
				run = False



		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot = False




	pygame.display.update()

pygame.quit()