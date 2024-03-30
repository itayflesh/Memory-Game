import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Set up the game window
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Memory Game")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (50, 205, 50)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)

# Define card properties
CARD_WIDTH = 100
CARD_HEIGHT = 100
CARD_SPACING = 20
CARD_SYMBOLS = ['A', 'B']
# CARD_SYMBOLS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
NUM_CARDS = len(CARD_SYMBOLS) * 2
cards = [(symbol, False) for symbol in CARD_SYMBOLS * 2]
random.shuffle(cards)

# Game state variables
revealed_cards = []
matched_cards = []
game_over = False
start_time = None
final_time = None
flip_back_timer = 0
flip_back_delay = 1000
players_choice = None
current_player = 1
hint_used = False  # Variable to track if the hint has been used

# Load sound effect
match_sound = None
try:
    match_sound = pygame.mixer.Sound("sound/match.wav")
except pygame.error:
    print("Sound file not found. Continuing without sound.")

# Reset game function
def reset_game():
    global cards, revealed_cards, matched_cards, game_over, start_time, final_time, flip_back_timer, hint_button_clicked, current_player, hint_used
    cards = [(symbol, False) for symbol in CARD_SYMBOLS * 2]
    random.shuffle(cards)
    revealed_cards = []
    matched_cards = []
    game_over = False
    start_time = time.time()
    final_time = None
    flip_back_timer = 0
    hint_button_clicked = False
    current_player = 1
    hint_used = False  # Reset hint used status

reset_game()

# Draw reset button
reset_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 60, 200, 40)

# Draw hint button
hint_button_rect = pygame.Rect(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 60, 120, 40)
hint_button_clicked = False

# Function to handle drawing of player choice screen
def draw_player_choice_screen():
    font = pygame.font.SysFont(None, 48)
    text_1 = font.render("1 Player", True, WHITE)
    text_2 = font.render("2 Players", True, WHITE)
    player_1_button = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 100, 300, 50)
    player_2_button = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2, 300, 50)
    pygame.draw.rect(window, RED, player_1_button)
    pygame.draw.rect(window, BLUE, player_2_button)
    window.blit(text_1, (WINDOW_WIDTH // 2 - text_1.get_width() / 2, WINDOW_HEIGHT // 2 - 90))
    window.blit(text_2, (WINDOW_WIDTH // 2 - text_2.get_width() / 2, WINDOW_HEIGHT // 2 + 10))
    return player_1_button, player_2_button

def draw_cards():
    for i, (symbol, is_revealed) in enumerate(cards):
        x = (i % 4) * (CARD_WIDTH + CARD_SPACING) + CARD_SPACING
        y = ((i // 4) * (CARD_HEIGHT + CARD_SPACING)) + CARD_SPACING + 80
        if is_revealed or i in matched_cards:
            pygame.draw.rect(window, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT))
            font = pygame.font.SysFont(None, 72)
            text = font.render(symbol, True, BLACK)
            window.blit(text, (x + (CARD_WIDTH - text.get_width()) / 2, y + (CARD_HEIGHT - text.get_height()) / 2))
        else:
            pygame.draw.rect(window, GRAY, (x, y, CARD_WIDTH, CARD_HEIGHT))

def draw_timer():
    if not game_over:
        elapsed_time = time.time() - start_time
    else:
        elapsed_time = final_time
    font = pygame.font.SysFont(None, 36)
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    timer_text = font.render(f"Time: {minutes:02}:{seconds:02}", True, WHITE)
    window.blit(timer_text, (5, 5))

def draw_game_over_screen():
    if game_over:
        bg_rect = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT // 2 - 60, 320, 120)
        pygame.draw.rect(window, LIGHT_GRAY, bg_rect)
        font = pygame.font.SysFont(None, 48)
        text = font.render("Game Over!", True, GREEN)
        window.blit(text, (WINDOW_WIDTH // 2 - text.get_width() / 2, WINDOW_HEIGHT // 2 - 20))
        if players_choice == '1':
            play_again_text = "Play Again"
        else:
            play_again_text = "Play Again"
        play_again_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 40, 200, 50)
        pygame.draw.rect(window, BLUE, play_again_rect)
        text = font.render(play_again_text, True, WHITE)
        window.blit(text, (WINDOW_WIDTH // 2 - text.get_width() / 2, WINDOW_HEIGHT // 2 + 50))
        return play_again_rect
    return None

def draw_player_indicator():
    if players_choice == '2':
        font = pygame.font.SysFont(None, 36)
        text = font.render(f"Player {current_player}'s Turn", True, YELLOW)
        window.blit(text, (5, WINDOW_HEIGHT - 100))

# Main game loop
running = True
play_again_rect = None
hint_timer = 0
hint_card_index = None

while running:
    if players_choice is None:
        window.fill(BLACK)
        player_1_button, player_2_button = draw_player_choice_screen()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if player_1_button.collidepoint(mouse_x, mouse_y):
                    players_choice = '1'
                    reset_game()
                elif player_2_button.collidepoint(mouse_x, mouse_y):
                    players_choice = '2'
                    reset_game()
        continue

    current_time = pygame.time.get_ticks()
    window.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if play_again_rect and play_again_rect.collidepoint(mouse_x, mouse_y):
                reset_game()
                play_again_rect = None
            elif reset_button_rect.collidepoint(mouse_x, mouse_y):
                reset_game()
            elif hint_button_rect.collidepoint(mouse_x, mouse_y) and not hint_used and players_choice == '1':
                hint_used = True  # Mark the hint as used
                hint_button_clicked = True
                unrevealed_cards = [i for i, (symbol, is_revealed) in enumerate(cards) if not is_revealed and i not in matched_cards]
                if unrevealed_cards:
                    hint_card_index = random.choice(unrevealed_cards)
                    cards[hint_card_index] = (cards[hint_card_index][0], True)
                    hint_timer = current_time + 2000
            elif not game_over:
                for i, (symbol, is_revealed) in enumerate(cards):
                    x = (i % 4) * (CARD_WIDTH + CARD_SPACING) + CARD_SPACING
                    y = ((i // 4) * (CARD_HEIGHT + CARD_SPACING)) + CARD_SPACING + 80
                    if x < mouse_x < x + CARD_WIDTH and y < mouse_y < y + CARD_HEIGHT and not is_revealed and len(revealed_cards) < 2:
                        revealed_cards.append(i)
                        cards[i] = (cards[i][0], True)
                        if len(revealed_cards) == 2:
                            if cards[revealed_cards[0]][0] == cards[revealed_cards[1]][0]:
                                matched_cards.extend(revealed_cards)
                                revealed_cards = []
                                if match_sound:
                                    match_sound.play()
                                if len(matched_cards) == NUM_CARDS:
                                    game_over = True
                                    final_time = time.time() - start_time
                            else:
                                flip_back_timer = current_time + flip_back_delay
                                if players_choice == '2':
                                    current_player = 2 if current_player == 1 else 1

    if len(revealed_cards) == 2 and current_time >= flip_back_timer:
        for i in revealed_cards:
            cards[i] = (cards[i][0], False)
        revealed_cards = []

    if hint_timer > 0 and current_time >= hint_timer:
        cards[hint_card_index] = (cards[hint_card_index][0], False)
        hint_timer = 0
        hint_button_clicked = False

    draw_cards()
    draw_timer()
    play_again_rect = draw_game_over_screen()
    pygame.draw.rect(window, RED, reset_button_rect)
    reset_text = pygame.font.SysFont(None, 36).render('Reset', True, WHITE)
    window.blit(reset_text, (reset_button_rect.x + (reset_button_rect.width - reset_text.get_width()) / 2, reset_button_rect.y + 5))

    if players_choice == '1' and not hint_button_clicked and not hint_used:
        pygame.draw.rect(window, BLUE, hint_button_rect)
        hint_text = pygame.font.SysFont(None, 36).render('Hint', True, WHITE)
        window.blit(hint_text, (hint_button_rect.x + (hint_button_rect.width - hint_text.get_width()) / 2, hint_button_rect.y + 5))

    draw_player_indicator()
    pygame.display.update()

pygame.quit()
