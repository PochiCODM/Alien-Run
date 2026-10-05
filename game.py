import pygame
import sys
from enum import Enum
from random import randint, choice

pygame.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Alien Run")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)
tiny_font = pygame.font.Font(None, 24)
score_font = pygame.font.Font(None, 60)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_BLUE = (15, 25, 50)
CYAN = (0, 255, 255)
RED = (255, 100, 100)


# Game states
class GameState(Enum):
    START = 1
    RUNNING = 2
    DEAD = 3


# Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.stand_image = pygame.image.load("GRAPHICS/Player/player_stand.png").convert_alpha()
        self.walk1_image = pygame.image.load("GRAPHICS/Player/player_walk_1.png").convert_alpha()
        self.walk2_image = pygame.image.load("GRAPHICS/Player/player_walk_2.png").convert_alpha()
        self.jump_image = pygame.image.load("GRAPHICS/Player/jump.png").convert_alpha()

        self.image = self.stand_image
        self.rect = self.image.get_rect(bottomleft=(80, 300))

        # Physics
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_power = -12
        self.is_jumping = False

        # Animation
        self.animation_frame = 0
        self.animation_counter = 0

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True

    def update(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        if self.rect.bottom >= 300:
            self.rect.bottom = 300
            self.velocity_y = 0
            self.is_jumping = False

        if not self.is_jumping:
            self.animation_counter += 1
            if self.animation_counter > 5:
                self.animation_frame = (self.animation_frame + 1) % 2
                self.animation_counter = 0
            self.image = self.walk1_image if self.animation_frame == 0 else self.walk2_image
        else:
            self.image = self.jump_image


# Enemy
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type, speed):
        super().__init__()
        self.enemy_type = enemy_type
        self.speed = speed
        self.animation_frame = 0
        self.animation_counter = 0

        if enemy_type == "snail":
            self.image1 = pygame.image.load("GRAPHICS/snail/snail1.png").convert_alpha()
            self.image2 = pygame.image.load("GRAPHICS/snail/snail2.png").convert_alpha()
            self.image = self.image1
            self.rect = self.image.get_rect(bottomleft=(SCREEN_WIDTH, 300))
        else:
            self.image1 = pygame.image.load("GRAPHICS/Fly/Fly1.png").convert_alpha()
            self.image2 = pygame.image.load("GRAPHICS/Fly/Fly2.png").convert_alpha()
            self.image = self.image1
            self.rect = self.image.get_rect(topleft=(SCREEN_WIDTH, 150))

    def update(self):
        # Animation
        self.animation_counter += 1
        if self.animation_counter > 8:
            self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_counter = 0
        self.image = self.image1 if self.animation_frame == 0 else self.image2

        # Movement
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


# Game
class AlienRun:
    def __init__(self):
        self.state = GameState.START
        self.score = 0
        self.start_time = 0
        self.elapsed_time = 0

        self.player = pygame.sprite.GroupSingle()
        self.enemies = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        self.ground_image = pygame.image.load("GRAPHICS/ground.png").convert()
        self.sky_image = pygame.image.load("GRAPHICS/Sky.png").convert()

        # Load audio
        try:
            self.jump_sound = pygame.mixer.Sound("audio/jump.mp3")
            self.music = pygame.mixer.music.load("audio/music.wav")
            pygame.mixer.music.play(-1)
        except:
            pass

        self.enemy_spawn_timer = 0
        self.base_spawn_rate = 120
        self.base_speed = 6
        self.pulse = 0

    def start_game(self):
        self.state = GameState.RUNNING
        self.score = 0
        self.start_time = pygame.time.get_ticks()

        self.player.empty()
        self.enemies.empty()
        self.all_sprites.empty()

        player = Player()
        self.player.add(player)
        self.all_sprites.add(player)

    def get_current_difficulty(self):
        difficulty = self.elapsed_time / 8
        return difficulty

    def spawn_enemy(self):
        difficulty = self.get_current_difficulty()
        speed = self.base_speed + (difficulty * 1.2)

        enemy_type = choice(["snail", "bird"])
        enemy = Enemy(enemy_type, speed)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)

    def update(self):
        if self.state == GameState.RUNNING:
            self.all_sprites.update()

            difficulty = self.get_current_difficulty()
            spawn_rate = max(40, self.base_spawn_rate - int(difficulty * 15))

            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer > spawn_rate:
                self.spawn_enemy()
                self.enemy_spawn_timer = 0

            if pygame.sprite.spritecollide(self.player.sprite, self.enemies, False):
                self.state = GameState.DEAD

            self.score += 1
            self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000

        # Pulse for start screen effect
        self.pulse = (self.pulse + 1) % 60

    def draw(self):
        screen.fill(BLACK)

        if self.state == GameState.START:
            screen.blit(self.sky_image, (0, 0))
            screen.blit(self.ground_image, (0, 300))

            # Dark overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(80)
            overlay.fill(DARK_BLUE)
            screen.blit(overlay, (0, 0))

            # Title with glow effect
            title = font.render("ALIEN RUN", True, CYAN)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
            screen.blit(title, title_rect)

            # Subtitle
            subtitle = tiny_font.render("Survive the invaders", True, WHITE)
            subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 110))
            screen.blit(subtitle, subtitle_rect)

            # Player stand
            stand = pygame.image.load("GRAPHICS/Player/player_stand.png").convert_alpha()
            stand_rect = stand.get_rect(center=(SCREEN_WIDTH // 2, 220))
            screen.blit(stand, stand_rect)

            # Pulsing start text
            if self.pulse % 60 < 30:
                start_text = small_font.render("CLICK or SPACE to Start", True, CYAN)
            else:
                start_text = small_font.render("CLICK or SPACE to Start", True, WHITE)
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
            screen.blit(start_text, start_rect)

        elif self.state == GameState.RUNNING:
            screen.blit(self.sky_image, (0, 0))
            screen.blit(self.ground_image, (0, 300))

            self.all_sprites.draw(screen)

            score_surf = score_font.render(f"{self.score // 10}", True, CYAN)
            score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
            screen.blit(score_surf, score_rect)

        elif self.state == GameState.DEAD:
            screen.blit(self.sky_image, (0, 0))
            screen.blit(self.ground_image, (0, 300))

            # Dark overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(100)
            overlay.fill(DARK_BLUE)
            screen.blit(overlay, (0, 0))

            # Game Over box
            box_width = 500
            box_height = 250
            box_x = (SCREEN_WIDTH - box_width) // 2
            box_y = (SCREEN_HEIGHT - box_height) // 2
            pygame.draw.rect(screen, CYAN, (box_x, box_y, box_width, box_height), 3)

            dead_text = font.render("GAME OVER", True, RED)
            dead_rect = dead_text.get_rect(center=(SCREEN_WIDTH // 2, box_y + 40))
            screen.blit(dead_text, dead_rect)

            final_score = small_font.render(f"Score: {self.score // 10}", True, CYAN)

            score_rect = final_score.get_rect(center=(SCREEN_WIDTH // 2, box_y + 120))

            screen.blit(final_score, score_rect)

            # Pulsing restart text
            if self.pulse % 60 < 30:
                restart = small_font.render("CLICK or SPACE to Restart", True, WHITE)
            else:
                restart = small_font.render("CLICK or SPACE to Restart", True, CYAN)
            restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, box_y + 210))
            screen.blit(restart, restart_rect)

        pygame.display.flip()


# Main loop
game = AlienRun()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game.state == GameState.START:
                game.start_game()
            elif game.state == GameState.DEAD:
                game.start_game()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game.state == GameState.START:
                    game.start_game()
                elif game.state == GameState.DEAD:
                    game.start_game()
                elif game.state == GameState.RUNNING:
                    game.player.sprite.jump()

            if event.key in [pygame.K_UP, pygame.K_w]:
                if game.state == GameState.RUNNING:
                    game.player.sprite.jump()

    game.update()
    game.draw()
    clock.tick(60)

pygame.quit()
sys.exit()