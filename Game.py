import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Set up the game window
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 700
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Memory Game")

# Load sound effect
match_sound = pygame.mixer.Sound("sound/match.wav")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (50, 205, 50)
RESET_BUTTON_COLOR = (255, 0, 0)  # Red color for the reset button

# Define card properties
CARD_WIDTH = 100
CARD_HEIGHT = 100
CARD_SPACING = 20
CARD_SYMBOLS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
NUM_CARDS = len(CARD_SYMBOLS) * 2
cards = [(symbol, False) for symbol in CARD_SYMBOLS * 2]
random.shuffle(cards)

# Game state variables
selected_cards = []
matched_cards = []
game_over = False
start_time = None

# Reset button properties
RESET_BUTTON_WIDTH = 200
RESET_BUTTON_HEIGHT = 50
RESET_BUTTON_X = WINDOW_WIDTH // 2 - RESET_BUTTON_WIDTH // 2
RESET_BUTTON_Y = WINDOW_HEIGHT - 100

# Function to reset the game
def reset_game():
    global cards, selected_cards, matched_cards, game_over, start_time
    cards = [(symbol, False) for symbol in CARD_SYMBOLS * 2]
    random.shuffle(cards)
    selected_cards = []
    matched_cards = []
    game_over = False
    start_time = None

# Function to draw the reset button
def draw_reset_button():
    pygame.draw.rect(window, RESET_BUTTON_COLOR, (RESET_BUTTON_X, RESET_BUTTON_Y, RESET_BUTTON_WIDTH, RESET_BUTTON_HEIGHT))
    font = pygame.font.Font(None, 36)
    text = font.render("Reset", True, WHITE)
    text_rect = text.get_rect(center=(RESET_BUTTON_X + RESET_BUTTON_WIDTH // 2, RESET_BUTTON_Y + RESET_BUTTON_HEIGHT // 2))
    window.blit(text, text_rect)

# Function to draw the cards
def draw_cards():
    for i, card in enumerate(cards):
        symbol, is_revealed = card
        x = (i % 4) * (CARD_WIDTH + CARD_SPACING) + CARD_SPACING
        y = ((i // 4) * (CARD_HEIGHT + CARD_SPACING)) + CARD_SPACING + 80  # Adjust card position
        if is_revealed or (len(selected_cards) == 2 and card in selected_cards):
            pygame.draw.rect(window, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT))
            font = pygame.font.Font(None, 72)
            text = font.render(symbol, True, BLACK)
            text_rect = text.get_rect(center=(x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2))
            window.blit(text, text_rect)
        else:
            pygame.draw.rect(window, GRAY, (x, y, CARD_WIDTH, CARD_HEIGHT))

# Function to draw the timer
def draw_timer():
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    timer_text = f"Time: {minutes:02d}:{seconds:02d}"
    font = pygame.font.Font(None, 60)
    text = font.render(timer_text, True, WHITE)
    window.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, 40))  # Center the timer text

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Check if the reset button is clicked
            if RESET_BUTTON_X <= mouse_x <= RESET_BUTTON_X + RESET_BUTTON_WIDTH and RESET_BUTTON_Y <= mouse_y <= RESET_BUTTON_Y + RESET_BUTTON_HEIGHT:
                reset_game()
            elif not game_over:
                clicked_card = None
                for i, card in enumerate(cards):
                    symbol, is_revealed = card
                    x = (i % 4) * (CARD_WIDTH + CARD_SPACING) + CARD_SPACING
                    y = ((i // 4) * (CARD_HEIGHT + CARD_SPACING)) + CARD_SPACING + 80
                    if x <= mouse_x <= x + CARD_WIDTH and y <= mouse_y <= y + CARD_HEIGHT and not is_revealed:
                        clicked_card = i
                        break

                if clicked_card is not None:
                    if len(selected_cards) < 2:
                        cards[clicked_card] = (cards[clicked_card][0], True)
                        selected_cards.append(clicked_card)
                    if len(selected_cards) == 2:
                        card1, card2 = selected_cards
                        if cards[card1][0] == cards[card2][0]:
                            matched_cards.extend(selected_cards)
                            selected_cards = []
                            # Play the match sound effect
                            match_sound.play()
                        else:
                            pygame.time.delay(1000)  # Delay for 1 second
                            cards[card1] = (cards[card1][0], False)
                            cards[card2] = (cards[card2][0], False)
                            selected_cards = []

                    if len(matched_cards) == NUM_CARDS:
                        game_over = True

    if not start_time:
        start_time = time.time()

    window.fill(BLACK)
    draw_timer()  # Draw the timer first
    draw_cards()
    draw_reset_button()  # Draw the reset button

    if game_over:
        font = pygame.font.Font(None, 72)
        text = font.render("Well done!", True, GREEN)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        window.blit(text, text_rect)

    pygame.display.update()

pygame.quit()