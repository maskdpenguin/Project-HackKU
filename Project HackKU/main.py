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
pygame.display.set_caption("Turn-based PvP Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

bridge_images = ["sky bridge.png", "castle bridge.png", "forest bridge.png", "bamboo bridge.png"]

# Randomly select one of the bridge images
selected_bridge = random.choice(bridge_images)

# Load the selected bridge image
background_arena = pygame.image.load(os.path.join("arenas", selected_bridge))

king_attack = [pygame.image.load(f"king/attack/image_0-{i}.png").convert_alpha() for i in range(0, 12)]
king_death = [pygame.image.load(f"king/death/image_0-{i}.png").convert_alpha() for i in range(0, 6)]
king_idle = [pygame.image.load(f"king/idle/image_0-{i}.png").convert_alpha() for i in range(0, 8)]
king_take_hit = [pygame.image.load(f"king/take hit/image_0-{i}.png").convert_alpha() for i in range(0, 4)]

shogun_attack = [pygame.image.load(f"shogun/attack/image_0-{i}.png").convert_alpha() for i in range(0, 12)]
shogun_death = [pygame.image.load(f"shogun/death/image_0-{i}.png").convert_alpha() for i in range(0, 6)]
shogun_idle = [pygame.image.load(f"shogun/idle/image_0-{i}.png").convert_alpha() for i in range(0, 8)]
shogun_take_hit = [pygame.image.load(f"shogun/take hit/image_0-{i}.png").convert_alpha() for i in range(0, 4)]

current_frame_king = 0
current_frame_shogun = 0

king_is_attacking = False
shogun_is_attacking = False
king_attack_frames = 0
shogun_takehit_frame = 0
shogun_attack_frames = 0
king_takehit_frame = 0


def animate_characters(screen):
    global king_is_attacking, shogun_is_attacking, king_attack_frames, shogun_takehit_frame, shogun_attack_frames, king_takehit_frame, current_frame_king, current_frame_shogun

    if king_is_attacking:
        king_is_attacking, king_attack_frames, shogun_takehit_frame, current_frame_king, current_frame_shogun = king_attack_animation(
            screen, king_attack_frames, shogun_takehit_frame, current_frame_king, current_frame_shogun)

    elif shogun_is_attacking:
        shogun_is_attacking, shogun_attack_frames, king_takehit_frame, current_frame_king, current_frame_shogun = shogun_attack_animation(
            screen, shogun_attack_frames, king_takehit_frame, current_frame_king, current_frame_shogun)

    else:
        screen.blit(king_idle[current_frame_king], (0, 70))
        current_frame_king = (current_frame_king + 1) % len(king_idle)
        screen.blit(shogun_idle[current_frame_shogun], (400, 50))
        current_frame_shogun = (current_frame_shogun + 1) % len(shogun_idle)


def king_attack_animation(screen, king_attack_frames, shogun_takehit_frame, current_frame_king, current_frame_shogun):
    if king_attack_frames < len(king_attack):
        screen.blit(king_attack[king_attack_frames], (0, 70))
        king_attack_frames += 1
        if king_attack_frames % 3 == 0:
            screen.blit(shogun_take_hit[shogun_takehit_frame], (400, 50))
            shogun_takehit_frame += 1
            if shogun_takehit_frame == len(shogun_take_hit):
                shogun_takehit_frame = 2
        if king_attack_frames == len(king_attack):
            return False, 0, 0, 0, 0  # Attack animation finished, reset variables
    else:
        screen.blit(king_idle[current_frame_king], (0, 70))
        current_frame_king = (current_frame_king + 1) % len(king_idle)
        screen.blit(shogun_idle[current_frame_shogun], (400, 50))
        current_frame_shogun = (current_frame_shogun + 1) % len(shogun_idle)
    return True, king_attack_frames, shogun_takehit_frame, current_frame_king, current_frame_shogun


def shogun_attack_animation(screen, shogun_attack_frames, king_takehit_frame, current_frame_king, current_frame_shogun):
    if shogun_attack_frames < len(shogun_attack):
        screen.blit(shogun_attack[shogun_attack_frames], (400, 50))
        shogun_attack_frames += 1
        if shogun_attack_frames % 3 == 0:
            screen.blit(king_take_hit[king_takehit_frame], (0, 70))
            king_takehit_frame += 1
            if king_takehit_frame == len(king_take_hit):
                king_takehit_frame = 0
        if shogun_attack_frames == len(shogun_attack):
            return False, 0, 0, 0, 0  # Attack animation finished, reset variables
    else:
        screen.blit(king_idle[current_frame_king], (0, 70))
        current_frame_king = (current_frame_king + 1) % len(king_idle)
        screen.blit(shogun_idle[current_frame_shogun], (400, 50))
        current_frame_shogun = (current_frame_shogun + 1) % len(shogun_idle)
    return True, shogun_attack_frames, king_takehit_frame, current_frame_king, current_frame_shogun


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
        self.health = 75
        self.key_attack = key_attack
        self.key_special = key_special
        self.shield_active = False
        self.shield_hits = 0  # Counter for tracking shield hits
        self.special_used = False  # Flag to track if special ability has been used
        self.animation_timer = pygame.time.get_ticks()

    def attack(self):
        return random.randint(5, 20)  # Random damage between 5 and 20

    def special_ability(self, target):
        pass  # Placeholder for special ability implementation


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
# all_sprites.add(player1, player2)

# Group for projectiles
projectile_group = pygame.sprite.Group()

# Main game loop
running = True
turn = 1  # Player 1 starts
MAIN_MENU = 0
GAMEPLAY = 1
PLAYER1_DEATH = 2
PLAYER2_DEATH = 3
RESTART_MENU = 4
# Initialize game state
game_state = MAIN_MENU
clock = pygame.time.Clock()  # Clock for controlling FPS
keywords = ["attack", "special", "begin", "quit", "restart", "continue"]
attack_detected = False
special_detected = False
shield_detected = False
start_detected = False
quit_detected = False
restart_detected = False
continue_detected = False
special_message_displayed = False
special_message_timer = 0
depleted_message_displayed = False
depleted_message_timer = 0

def run_keyword_detection():
    global attack_detected
    global special_detected
    global start_detected
    global quit_detected
    global restart_detected
    global continue_detected
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
        elif value == "continue":
            continue_detected = True


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
music_file = os.path.join("music/Epic Battle Music No Copyright Dragon Castle by Makaisymphony   (1).mp3")
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
        # Draw background image
        screen.blit(background_arena, (0, 0))
        if attack_detected:
            attack_detected = False
            if turn == 1:
                king_is_attacking = True
                damage = player1.attack()
                if player2.shield_active:
                    damage //= 2  # Reduce damage by half if shield is active
                player2.health -= damage
                print("Player 1 attacks Player 2 for", damage, "damage.")
                print("Player 2's health:", player2.health)
                turn = 2  # Switch to player 2's turn
            elif turn == 2:
                shogun_is_attacking = True
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
                        depleted_message_displayed = True
                        depleted_message_timer = pygame.time.get_ticks()
                turn = 1

        if special_detected:
            special_detected = False
            if turn == 1 and not player1.special_used:
                king_is_attacking = True
                damage = random.randint(15, 25)
                if player2.shield_active:
                    damage //= 2  # Reduce damage by half if shield is active
                player2.health -= damage
                player1.health -= 10
                print("Player 1 does special attack on Player 2 for", damage, "damage.")
                print("Player 2's health:", player2.health)
                special_message_displayed = True
                special_message_timer = pygame.time.get_ticks()
                player1.special_used = True  # Set special ability flag
                turn = 2  # Switch to player 2's turn
            elif turn == 2 and not player2.special_used:
                shogun_is_attacking = True
                # Player 2's special ability: Shield
                print("Player 2 uses special ability: Shield.")
                print("Player 2 gains temporary shield!")
                special_message_displayed = True
                player2.shield_active = True
                player2.special_used = True  # Set special ability flag
                special_message_timer = pygame.time.get_ticks()
                turn = 1  # Switch to player 1's turn

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == player1.key_attack and turn == 1:
                    king_is_attacking = True
                    damage = player1.attack()
                    if player2.shield_active:
                        damage //= 2  # Reduce damage by half if shield is active
                    player2.health -= damage
                    print("Player 1 attacks Player 2 for", damage, "damage.")
                    print("Player 2's health:", player2.health)
                    turn = 2  # Switch to player 2's turn
                elif event.key == player2.key_attack and turn == 2:
                    shogun_is_attacking = True
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
                            depleted_message_displayed = True
                            depleted_message_timer = pygame.time.get_ticks()

                    turn = 1

                elif event.key == player1.key_special and turn == 1 and not player1.special_used:
                    king_is_attacking = True
                    damage = random.randint(15, 25)
                    if player2.shield_active:
                        damage //= 2  # Reduce damage by half if shield is active
                    player2.health -= damage
                    player1.health -= 10
                    print("Player 1 does special attack on Player 2 for", damage, "damage.")
                    print("Player 2's health:", player2.health)
                    special_message_displayed = True
                    special_message_timer = pygame.time.get_ticks()
                    player1.special_used = True  # Set special ability flag
                    turn = 2  # Switch to player 2's turn

                elif event.key == player2.key_special and turn == 2 and not player2.special_used:
                    shogun_is_attacking = True
                    # Player 2's special ability: Shield
                    print("Player 2 uses special ability: Shield.")
                    print("Player 2 gains temporary shield!")
                    special_message_displayed = True
                    player2.shield_active = True
                    player2.special_used = True  # Set special ability flag
                    special_message_timer = pygame.time.get_ticks()
                    turn = 1  # Switch to player 1's turn
        pygame.draw.rect(screen, RED, (20, 20, player1.health * 2, 20))
        pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH - 20 - player2.health * 2, 20, player2.health * 2, 20))
        animate_characters(screen)

        if turn == 2:
            render_text(f"Player 1 attacks Player 2 for {damage} damage.", SCREEN_WIDTH // 4, SCREEN_HEIGHT - 50)
            render_text(f"Player 2's health: {player2.health}", SCREEN_WIDTH // 4, SCREEN_HEIGHT - 30)
        elif turn == 1:
            render_text(f"Player 2 attacks Player 1 for {damage} damage.", SCREEN_WIDTH // 4, SCREEN_HEIGHT - 50)
            render_text(f"Player 1's health: {player1.health}", SCREEN_WIDTH // 4, SCREEN_HEIGHT - 30)

        if special_message_displayed:
            # Duration to display the special message (in milliseconds)
            special_message_duration = 2000  # Adjust as needed
            if pygame.time.get_ticks() - special_message_timer >= special_message_duration:
                special_message_displayed = False

        if special_message_displayed and turn == 2:
            render_text("Player 1 engages special ability - Multi-Attack Combo!", SCREEN_WIDTH // 2 - 230,
                        SCREEN_HEIGHT // 2)
        elif special_message_displayed and turn == 1:
            render_text("Player 2 engages special ability - Temporary Shield!", SCREEN_WIDTH // 2 - 210,
                        SCREEN_HEIGHT // 2)

        if depleted_message_displayed:
            depleted_message_duration = 2000
            if pygame.time.get_ticks() - depleted_message_timer >= depleted_message_duration:
                depleted_message_displayed = False
            render_text("Shogun's shield has been depleted!", SCREEN_WIDTH // 2 - 150,
                        SCREEN_HEIGHT // 2)
        if player1.health <= 0:
            game_state = PLAYER1_DEATH
        elif player2.health <= 0:
            game_state = PLAYER2_DEATH

        pygame.display.flip()

    elif game_state == PLAYER1_DEATH:
        game_over_text = pygame_font.render("Player 1 is defeated! Player 2 wins!", True, BLACK)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, game_over_rect)
        if continue_detected:
            game_state = RESTART_MENU
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = RESTART_MENU
        # Update the display
        pygame.display.flip()

        # Change game state to RESTART_MENU

    elif game_state == PLAYER2_DEATH:
        game_over_text = pygame_font.render("Player 2 is defeated! Player 1 wins!", True, BLACK)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, game_over_rect)
        if continue_detected:
            game_state = RESTART_MENU
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = RESTART_MENU
        # Update the display
        pygame.display.flip()

        # Change game state to RESTART_MENU
    elif game_state == RESTART_MENU:
        screen.fill(WHITE)
        restart_text = pygame_font.render("Press ENTER to Restart", True, BLACK)
        quit_text = pygame_font.render("Press ESCAPE to Quit", True, BLACK)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_rect)
        screen.blit(quit_text, quit_rect)
        if quit_detected:
            quit_detected = False
            running = False
        elif restart_detected:
            restart_detected = False
            game_state = GAMEPLAY
            player1.health = 75
            player2.health = 75
            damage = 0
            turn = 1
            special_message_displayed = False
            special_message_timer = 0
            player1.special_used = False
            player2.special_used = False
            depleted_message_displayed = False
            depleted_message_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = GAMEPLAY
                    player1.health = 75
                    player2.health = 75
                    damage = 0
                    turn = 1
                    special_message_displayed = False
                    special_message_timer = 0
                    player1.special_used = False
                    player2.special_used = False
                    depleted_message_displayed = False
                    depleted_message_timer = 0
                    # Reset player health and other game variables here if needed
                elif event.key == pygame.K_ESCAPE:
                    running = False
        pygame.display.flip()

    clock.tick(10)  # Cap FPS at 60

    # Quit Pygame
pygame.quit()
sys.exit()
