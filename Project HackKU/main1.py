import os
import pygame
import sys
import random
import threading
from pygame import font
import speechRecognition as sr

# Initialize Pygame
pygame.init()

# Set up the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('King vs Shogun')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


# Define player class
class Player(pygame.sprite.Sprite):
    def __init__(self, directory, num_frames, x, y, key_attack, key_special):
        super().__init__()
        self.images = [pygame.image.load(os.path.join(directory, f"image_0-{i}.png")).convert_alpha() for i in
                       range(0, num_frames + 1)]
        self.image_index = 0  # Index of the current image in the animation
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.health = 100
        self.key_attack = key_attack
        self.key_special = key_special
        self.shield_active = False
        self.shield_hits = 0  # Counter for tracking shield hits
        self.special_used = False  # Flag to track if special ability has been used
        self.animation_timer = pygame.time.get_ticks()

    def attack(self):
        if self == player1:
            self.images = [pygame.image.load(os.path.join("king/attack", f"image_0-{i}.png")).convert_alpha() for i in
                           range(0, 12)]
            self.image_index = 0 # Reset animation index
            self.image = self.images[self.image_index]
            self.update_animation()
            attack_images = [pygame.image.load(os.path.join("king/attack", f"image_0-{i}.png")).convert_alpha() for i in
                             range(0, 12)]
            self.image_index = 0  # Reset animation index
            for image in attack_images:
                self.image = image
                self.update_animation()  # Update animation

            # Reset to idle animation
            self.images = [pygame.image.load(os.path.join("king/idle", f"image_0-{i}.png")).convert_alpha() for i in
                           range(0, 8)]
        if self == player2:
            self.images = [pygame.image.load(os.path.join("shogun/attack", f"image_0-{i}.png")).convert_alpha() for i in
                           range(0, 12)]
            self.image_index = 0  # Reset animation index
            self.image = self.images[self.image_index]
            self.update_animation()  # Update animation
            attack_images = [pygame.image.load(os.path.join("shogun/attack", f"image_0-{i}.png")).convert_alpha() for i in
                             range(0, 12)]
            self.image_index = 0  # Reset animation index
            for image in attack_images:
                self.image = image
                self.update_animation()  # Update animation

            # Reset to idle animation
            self.images = [pygame.image.load(os.path.join("shogun/idle", f"image_0-{i}.png")).convert_alpha() for i in
                           range(0, 8)]
        return random.randint(5, 20)  # Random damage between 5 and 20

    def special_ability(self, target):
        pass  # Placeholder for special ability implementation

    def update_animation(self):
        # Update animation frame based on elapsed time
        now = pygame.time.get_ticks()
        if now - self.animation_timer > 100:  # Change 100 to adjust animation speed
            self.animation_timer = now
            self.image_index = (self.image_index + 1) % len(self.images)
            self.image = self.images[self.image_index]


# Define projectile class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, color, start_pos, direction):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = start_pos
        self.direction = direction
        self.speed = 5

    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed


# Create players
player1 = Player("king/idle", 7, 100, 300, pygame.K_SPACE, pygame.K_q)
player2 = Player("shogun/idle", 7, 700, 375, pygame.K_RETURN, pygame.K_LSHIFT)

# Group for all sprites
all_sprites = pygame.sprite.Group()
all_sprites.add(player1, player2)

# Group for projectiles
projectile_group = pygame.sprite.Group()

# Main game loop
running = True
turn = 1  # Player 1 starts
MAIN_MENU = 0
GAMEPLAY = 1
PLAYER1_DEATH = 2
PLAYER2_DEATH = 3

# Initialize game state
game_state = MAIN_MENU
clock = pygame.time.Clock()  # Clock for controlling FPS
keywords = ["attack", "special", "begin", "quit", "restart"]
attack_detected = False
special_detected = False
shield_detected = False
start_detected = False
quit_detected = False
restart_detected = False


def run_keyword_detection():
    global attack_detected
    global special_detected
    global start_detected
    global quit_detected
    global restart_detected
    while True:
        value = sr.detect_keyword(keywords)
        if value == "attack":
            attack_detected = True
        elif value == "special":
            special_detected = True
        elif value == "begin":
            start_detected = True
        elif value == "quit":
            quit_detected = True
        elif value == "restart":
            restart_detected = True


def render_text(text, x, y):
    text_surface = pygame_font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect.midtop)


keyword_thread = threading.Thread(target=run_keyword_detection)
keyword_thread.daemon = True  # Set the thread as daemon so it will exit when the main program exits
keyword_thread.start()

font.init()  # Initialize Pygame's font module
font_path = pygame.font.match_font('arial')  # Choose a font
pygame_font = pygame.font.Font(font_path, 24)  # Create a Pygame font object
damage = 0

pygame.mixer.init()

# Load Background Music
music_file = os.path.join("music", "Epic Battle Music No Copyright Dragon Castle by Makaisymphony.mp3")
pygame.mixer.music.load(music_file)

# Play Background Music (Loop Continuously)
pygame.mixer.music.play(loops=-1)

while running:
    if game_state == MAIN_MENU:
        title_text = pygame_font.render("Turn-based PvP Game", True, WHITE)
        start_text = pygame_font.render("Press ENTER to Begin", True, WHITE)
        quit_text = pygame_font.render("Press ESCAPE to Quit", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(title_text, title_rect)
        screen.blit(start_text, start_rect)
        screen.blit(quit_text, quit_rect)
        # Handle input to start the game or quit
        if start_detected:
            start_detected = False
            game_state = GAMEPLAY
        if quit_detected:
            quit_detected = False
            running = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = GAMEPLAY
                elif event.key == pygame.K_ESCAPE:
                    running = False
        # Update the display
        pygame.display.flip()
    elif game_state == GAMEPLAY:
        if attack_detected:
            attack_detected = False
            if turn == 1:
                damage = player1.attack()
                if player2.shield_active:
                    damage //= 2  # Reduce damage by half if shield is active
                player2.health -= damage
                print("Player 1 attacks Player 2 for", damage, "damage.")
                print("Player 2's health:", player2.health)
                turn = 2  # Switch to player 2's turn
            elif turn == 2:
                damage = player2.attack()
                if player1.shield_active:
                    damage //= 2  # Reduce damage by half if shield is active
                player1.health -= damage
                print("Player 2 attacks Player 1 for", damage, "damage.")
                print("Player 1's health:", player1.health)

                # Increase shield hits counter for Player 2
                if player2.shield_active:
                    player2.shield_hits += 1
                    if player2.shield_hits >= 3:  # Deactivate shield after 3 hits
                        player2.shield_active = False
                        print("Player 2's shield has been depleted!")
                turn = 1


        if special_detected:
            special_detected = False
            if turn == 1 and not player1.special_used:
                damage = random.randint(15, 25)
                if player2.shield_active:
                    damage //= 2  # Reduce damage by half if shield is active
                player2.health -= damage
                player1.health -= 10
                print("Player 1 does special attack on Player 2 for", damage, "damage.")
                print("Player 2's health:", player2.health)
                player1.special_used = True  # Set special ability flag
                turn = 2  # Switch to player 2's turn
            if turn == 2 and not player2.special_used:
                # Player 2's special ability: Shield
                print("Player 2 uses special ability: Shield.")
                print("Player 2 gains temporary shield!")
                player2.shield_active = True
                player2.special_used = True  # Set special ability flag
                turn = 1  # Switch to player 1's turn


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == player1.key_attack and turn == 1:
                    damage = player1.attack()
                    if player2.shield_active:
                        damage //= 2  # Reduce damage by half if shield is active
                    player2.health -= damage
                    print("Player 1 attacks Player 2 for", damage, "damage.")
                    print("Player 2's health:", player2.health)
                    turn = 2  # Switch to player 2's turn
                elif event.key == player2.key_attack and turn == 2:
                    damage = player2.attack()
                    if player1.shield_active:
                        damage //= 2  # Reduce damage by half if shield is active
                    player1.health -= damage
                    print("Player 2 attacks Player 1 for", damage, "damage.")
                    print("Player 1's health:", player1.health)
                    # Increase shield hits counter for Player 2
                    if player2.shield_active:
                        player2.shield_hits += 1
                        if player2.shield_hits >= 3:  # Deactivate shield after 3 hits
                            player2.shield_active = False
                            print("Player 2's shield has been depleted!")
                    turn = 1


                elif event.key == player1.key_special and turn == 1 and not player1.special_used:
                    damage = random.randint(15, 25)
                    if player2.shield_active:
                        damage //= 2  # Reduce damage by half if shield is active
                    player2.health -= damage
                    player1.health -= 10
                    print("Player 1 does special attack on Player 2 for", damage, "damage.")
                    print("Player 2's health:", player2.health)
                    player1.special_used = True  # Set special ability flag
                    turn = 2  # Switch to player 2's turn


                elif event.key == player2.key_special and turn == 2 and not player2.special_used:
                    # Player 2's special ability: Shield
                    print("Player 2 uses special ability: Shield.")
                    print("Player 2 gains temporary shield!")
                    player2.shield_active = True
                    player2.special_used = True  # Set special ability flag
                    turn = 1  # Switch to player 1's turn
        player1.update_animation()
        player2.update_animation()
        screen.fill(WHITE)
        pygame.draw.rect(screen, RED, (20, 20, player1.health * 2, 20))
        pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH - 20 - player2.health * 2, 20, player2.health * 2, 20))
        all_sprites.draw(screen)
        if turn == 2:
            render_text(f"Player 1 attacks Player 2 for {damage} damage.", SCREEN_WIDTH // 4, SCREEN_HEIGHT - 50)
            render_text(f"Player 2's health: {player2.health}", SCREEN_WIDTH // 4, SCREEN_HEIGHT - 30)
        elif turn == 1:
            render_text(f"Player 2 attacks Player 1 for {damage} damage.", SCREEN_WIDTH // 4, SCREEN_HEIGHT - 50)
            render_text(f"Player 1's health: {player1.health}", SCREEN_WIDTH // 4, SCREEN_HEIGHT - 30)
        if player1.health <= 0:
            game_state = PLAYER1_DEATH
        elif player2.health <= 0:
            game_state = PLAYER2_DEATH
        pygame.display.flip()

    elif game_state == PLAYER1_DEATH:
        screen.fill(WHITE)  # Clear the screen
        # Draw player 1 death screen text
        game_over_text = pygame_font.render("Player 1 is defeated! Player 2 wins!", True, BLACK)
        restart_text = pygame_font.render("Press ENTER to Restart", True, BLACK)
        quit_text = pygame_font.render("Press ESCAPE to Quit", True, BLACK)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(game_over_text, game_over_rect)
        screen.blit(restart_text, restart_rect)
        screen.blit(quit_text, quit_rect)
        # Handle input to restart the game or quit
        if quit_detected:
            quit_detected = False
            running = False
        if restart_detected:
            restart_detected = False
            game_state = GAMEPLAY
            player1.health = 100
            player2.health = 100
            damage = 0
            turn = 1
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = GAMEPLAY
                    player1.health = 100
                    player2.health = 100
                    damage = 0
                    turn = 1
                    # Reset player health and other game variables here if needed
                elif event.key == pygame.K_ESCAPE:
                    running = False
        # Update the display
        pygame.display.flip()

    elif game_state == PLAYER2_DEATH:
        screen.fill(WHITE)  # Clear the screen
        # Draw player 1 death screen text
        game_over_text = pygame_font.render("Player 2 is defeated! Player 1 wins!", True, BLACK)
        restart_text = pygame_font.render("Press ENTER to Restart", True, BLACK)
        quit_text = pygame_font.render("Press ESCAPE to Quit", True, BLACK)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(game_over_text, game_over_rect)
        screen.blit(restart_text, restart_rect)
        screen.blit(quit_text, quit_rect)
        if quit_detected:
            quit_detected = False
            running = False
        elif restart_detected:
            restart_detected = False
            game_state = GAMEPLAY
            player1.health = 100
            player2.health = 100
            damage = 0
            turn = 2
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = GAMEPLAY
                    player1.health = 100
                    player2.health = 100
                    damage = 0
                    turn = 2
                    # Reset player health and other game variables here if needed
                elif event.key == pygame.K_ESCAPE:
                    running = False
        # Update the display
        pygame.display.flip()
    clock.tick(60)  # Cap FPS at 60

    # Quit Pygame
pygame.quit()
sys.exit()