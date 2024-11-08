import pygame
import random

# Initializing pygame
pygame.mixer.init()
pygame.init()

# Setting up the Screen
SCR_WIDTH = 800
SCR_HEIGHT = 750
SCREEN = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
pygame.display.set_caption("Space Invaders")

# Setting up the Clock
CLOCK = pygame.time.Clock()
FPS = 60

# Setting up the Font
pygame.font.init()
font = pygame.font.SysFont("comicsans", 36)


# Loading Images
BG = pygame.image.load("assets/background-black.png").convert()
BG = pygame.transform.scale(BG, (SCR_WIDTH, SCR_HEIGHT))

PLAYER_IMG = pygame.image.load("assets/pixel_ship_yellow.png").convert_alpha()
PLAYER_BULLET_IMG = pygame.image.load("assets/pixel_laser_yellow.png").convert_alpha()

ENEMY_IMG = pygame.image.load("assets/pixel_ship_red_small.png").convert_alpha()
ENEMY_BULLET_IMG = pygame.image.load("assets/pixel_laser_red.png").convert_alpha()


# Loading Sounds
SHOOT_SOUND = pygame.mixer.Sound("assets/laser.wav")


class Laser:
    def __init__(self, img, x, y, vel):
        self.img = img
        self.x = x
        self.y = y
        self.vel = vel
    
    def update(self):
        # Move the laser
        self.y += self.vel
    
    def draw(self):
        SCREEN.blit(self.img, (self.x, self.y))

    def off_screen(self):
        # Check if the laser goes off-screen
        return self.y < 0 or self.y > SCR_HEIGHT

    def collision(self, obj):
        # Creating masks for pixel-perfect collision
        bullet_mask = pygame.mask.from_surface(self.img)
        obj_mask = pygame.mask.from_surface(obj.img)
        offset = (int(obj.x - self.x), int(obj.y - self.y))
        return bullet_mask.overlap(obj_mask, offset) is not None


class Player:
    def __init__(self, img, x, y):
        self.img = img
        self.x = x
        self.y = y
        self.displacement = 5
        self.bullets = []

    def draw(self):
        SCREEN.blit(self.img, (self.x, self.y))

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.displacement
        elif keys[pygame.K_RIGHT] and self.x < SCR_WIDTH - self.img.get_width():
            self.x += self.displacement
        elif keys[pygame.K_UP] and self.y > 0:
            self.y -= self.displacement
        elif keys[pygame.K_DOWN] and self.y < SCR_HEIGHT - self.img.get_height():
            self.y += self.displacement

    def shoot(self):
        SHOOT_SOUND.play()
        bullet_x = self.x + self.img.get_width() / 2 - PLAYER_BULLET_IMG.get_width() / 2
        bullet_y = self.y
        new_bullet = Laser(PLAYER_BULLET_IMG, bullet_x, bullet_y, vel=-10)
        self.bullets.append(new_bullet)

    def collision(self, obj):
        player_mask = pygame.mask.from_surface(self.img)
        obj_mask = pygame.mask.from_surface(obj.img)
        offset = (int(obj.x - self.x), int(obj.y - self.y))
        return player_mask.overlap(obj_mask, offset) is not None


class Enemy:
    def __init__(self, img, x, y, vel=3):
        self.img = img
        self.x = x
        self.y = y
        self.vel = vel       
        self.bullets = []
        self.shoot_delay = random.randint(60, 150)  # Frames between shots

    def update(self):
        self.y += self.vel
        # Shooting bullets periodically
        if random.randint(0, self.shoot_delay) == 0:
            self.shoot()

    def draw(self):
        SCREEN.blit(self.img, (self.x, self.y))

    def off_screen(self):
        return self.y > SCR_HEIGHT

    def shoot(self):
        bullet_x = self.x + self.img.get_width() / 2 - ENEMY_BULLET_IMG.get_width() / 2
        bullet_y = self.y + self.img.get_height()
        new_bullet = Laser(ENEMY_BULLET_IMG, bullet_x, bullet_y, vel=7)
        self.bullets.append(new_bullet)

# Function to regenerate enemies 
def spawn_enemy():
    x = random.randint(0, SCR_WIDTH - ENEMY_IMG.get_width())
    y = random.randint(-150, -50)
    return Enemy(ENEMY_IMG, x, y)


# Function to display text
def text_screen(text, font, color, x, y):
    # Render the text
    screen_text = font.render(text, True, color)
    # Blit the text onto the screen at (x, y) position
    SCREEN.blit(screen_text, (x-screen_text.get_rect().width/2, y-screen_text.get_rect().width/2)) # Centeralizing the text

# Home Screen
def home_screen():
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                return
        
        SCREEN.blit(BG, (0, 0))
        text_screen("Click to Play", font, (255, 255, 255), SCR_WIDTH/2, SCR_HEIGHT/2)
        pygame.display.update()
        CLOCK.tick(FPS)
    
    pygame.quit()
    quit()


# Game Over Screen
def game_over_screen():
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            # Restart the game
            if event.type == pygame.MOUSEBUTTONDOWN:
                home_screen()
                main()

        SCREEN.blit(BG, (0, 0))
        text_screen("You died !", font, (255, 255, 255), SCR_WIDTH/2, SCR_HEIGHT/2)
        pygame.display.update()
        CLOCK.tick(FPS)
    
    pygame.quit()
    quit()

#Main Game Window
def main():
    game_over = False
    score = 0

    player = Player(PLAYER_IMG, SCR_WIDTH / 2 - PLAYER_IMG.get_width() / 2, 600)
    enemies = [spawn_enemy() for _ in range(5)]

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # Shoot bullets based on keyboard input
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.shoot()

        # Update player position
        keys = pygame.key.get_pressed()
        player.update(keys)

        # Update player's bullets
        for bullet in player.bullets[:]:
            bullet.update()
            if bullet.off_screen():
                player.bullets.remove(bullet)

            # Check collision with enemies
            for enemy in enemies[:]:
                if bullet.collision(enemy):
                    score += 10 # Increase the score
                    player.bullets.remove(bullet)
                    enemies.remove(enemy)
                    enemies.append(spawn_enemy())  # Respawn new enemy
                    break

        # Update enemies and their bullets
        for enemy in enemies[:]:
            enemy.update()

            # Check collision between enemy and player
            if player.collision(enemy):
                game_over = True
                break

            # Remove enemy if off-screen
            if enemy.off_screen():
                enemies.remove(enemy)
                enemies.append(spawn_enemy())

            # Update and check enemy bullets
            for bullet in enemy.bullets[:]:
                bullet.update()
                if bullet.off_screen():
                    enemy.bullets.remove(bullet)
                elif bullet.collision(player):
                    game_over = True
                    break

        # Blitting all images on Screen
        SCREEN.blit(BG, (0, 0))
        player.draw()
        for bullet in player.bullets:
            bullet.draw()
        for enemy in enemies:
            enemy.draw()
            for bullet in enemy.bullets:
                bullet.draw()
        
        # Blitting score
        text_screen(f"Score : {score}", font, (255, 255, 255), 100, 100)
        pygame.display.update()
        CLOCK.tick(FPS)

    # Go to the game over screen after the main loop ends
    game_over_screen()


if __name__ == '__main__':
    home_screen()
    main()
    game_over_screen()