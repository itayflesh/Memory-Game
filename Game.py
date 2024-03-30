import pygame
import random
import time
import os

# Initialize Pygame
pygame.init()

# Set up the game window
WINDOW_WIDTH = 600  # Increased window width to accommodate the hint button
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
LIGHT_GRAY = (200, 200, 200)  # Background color for the game over message

# Define card properties
CARD_WIDTH = 100
CARD_HEIGHT = 100
CARD_SPACING = 20
CARD_SYMBOLS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
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

# Load sound effect
match_sound = None
try:
    match_sound = pygame.mixer.Sound("sound/match.wav")
except pygame.error:
    print("Sound file not found. Continuing without sound.")

# Reset game function
def reset_game():
    global cards, revealed_cards, matched_cards, game_over, start_time, final_time, flip_back_timer, hint_button_clicked
    cards = [(symbol, False) for symbol in CARD_SYMBOLS * 2]
    random.shuffle(cards)
    revealed_cards = []
    matched_cards = []
    game_over = False
    start_time = time.time()
    final_time = None
    flip_back_timer = 0
    hint_button_clicked = False  # Reset hint button status

reset_game()

# Draw reset button
reset_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 60, 200, 40)

# Draw hint button
hint_button_rect = pygame.Rect(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 60, 120, 40)
hint_button_clicked = False  # Flag to track if the hint button has been clicked

# Draw cards
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

# Draw timer
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

# Draw game over screen with a background rectangle
def draw_game_over_screen():
    if game_over:
        # Background rectangle
        bg_rect = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT // 2 - 60, 320, 140)
        pygame.draw.rect(window, LIGHT_GRAY, bg_rect)

        font = pygame.font.SysFont(None, 48)
        text = font.render("Well done!", True, GREEN)
        text_rect = text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 20))
        window.blit(text, text_rect)

        play_again_rect = pygame.Rect(WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2 + 20, 200, 40)
        pygame.draw.rect(window, BLUE, play_again_rect)
        play_again_text = font.render('Play again', True, WHITE)
        window.blit(play_again_text, (WINDOW_WIDTH / 2 - play_again_text.get_width() / 2, WINDOW_HEIGHT / 2 + 25))
        return play_again_rect
    return None

# Main game loop
running = True
play_again_rect = None
hint_timer = 0
hint_card_index = None

while running:
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
            elif hint_button_rect.collidepoint(mouse_x, mouse_y) and not hint_button_clicked:
                # Generate a hint if hint button is clicked and not already clicked before
                hint_button_clicked = True
                unrevealed_cards = [i for i, (symbol, is_revealed) in enumerate(cards) if not is_revealed]
                if unrevealed_cards:
                    hint_card_index = random.choice(unrevealed_cards)
                    cards[hint_card_index] = (cards[hint_card_index][0], True)
                    hint_timer = current_time + 2000  # Set hint timer for 2 seconds
            elif not game_over:
                # Card flip logic
                for i, card in enumerate(cards):
                    card_x = (i % 4) * (CARD_WIDTH + CARD_SPACING) + CARD_SPACING
                    card_y = (i // 4) * (CARD_HEIGHT + CARD_SPACING) + CARD_SPACING + 80
                    if card_x < mouse_x < card_x + CARD_WIDTH and card_y < mouse_y < card_y + CARD_HEIGHT:
                        if not card[1] and len(revealed_cards) < 2:
                            revealed_cards.append(i)
                            cards[i] = (card[0], True)
                            if len(revealed_cards) == 2:
                                flip_back_timer = current_time + flip_back_delay
                                if cards[revealed_cards[0]][0] == cards[revealed_cards[1]][0]:
                                    matched_cards += revealed_cards
                                    revealed_cards = []
                                    if match_sound:
                                        match_sound.play()
                                    if len(matched_cards) == NUM_CARDS:
                                        game_over = True
                                        final_time = time.time() - start_time
    if len(revealed_cards) == 2 and current_time >= flip_back_timer:
        if cards[revealed_cards[0]][0] != cards[revealed_cards[1]][0]:
            for i in revealed_cards:
                cards[i] = (cards[i][0], False)
        revealed_cards = []
    draw_cards()
    draw_timer()
    pygame.draw.rect(window, RED, reset_button_rect)
    font = pygame.font.SysFont(None, 36)
    text = font.render('Reset', True, WHITE)
    window.blit(text, [WINDOW_WIDTH // 2 - text.get_width() / 2, WINDOW_HEIGHT - 55])

    # Draw hint button only if it hasn't been clicked yet
    if not hint_button_clicked:
        pygame.draw.rect(window, BLUE, hint_button_rect)
        hint_text = font.render('Hint', True, WHITE)
        window.blit(hint_text, [WINDOW_WIDTH - 90, WINDOW_HEIGHT - 55])

    # Check if the hint timer has expired to hide the hinted card
    if hint_timer > 0 and current_time >= hint_timer:
        cards[hint_card_index] = (cards[hint_card_index][0], False)
        hint_timer = 0

    play_again_rect = draw_game_over_screen()
    pygame.display.update()

pygame.quit()
