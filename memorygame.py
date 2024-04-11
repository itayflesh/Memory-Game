import pygame
import random
import time
import pyaudio
import json
from vosk import Model, KaldiRecognizer
import threading
import sounddevice as sd
import numpy as np
import threading
import queue

stop_audio_thread = False
audio_queue = queue.Queue()

def audio_listener_thread():
    global stop_audio_thread

    while not stop_audio_thread:
        speech = talk()
        audio_queue.put(speech)

# Dictionary mapping words to their numeric values
word_to_number = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "for": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16 , 
    "play again": 17

}


# Initialize Pygame
pygame.init()

# Set up the game window
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 700
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Memory Game")

# Load background image
background_image = pygame.image.load("photos/background.jpeg")
background_image = pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (30, 132, 73)
RED = (152, 104, 104)
HINT_COLOR = (145, 56, 49)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (200, 200, 0)
Board = (139, 0, 0)
player_1_color = (136, 8, 8)
player_1_voice_color = (165, 42, 42)
player_2_color = (128, 0, 32)
attack_color = (196, 30, 58)
play_again_color = (123, 36, 28)

# Define card properties
CARD_WIDTH = 100
CARD_HEIGHT = 100
CARD_SPACING = 20
CARD_SYMBOLS = ['A', 'B' , 'C' , 'D', 'E' , 'F' ,'G', 'H']
NUM_CARDS = len(CARD_SYMBOLS) * 2
cards = [(symbol, False) for symbol in CARD_SYMBOLS * 2]
random.shuffle(cards)

# Load card back image
card_back_image = pygame.image.load("photos/card_back.png")
card_back_image = pygame.transform.scale(card_back_image, (CARD_WIDTH, CARD_HEIGHT))
card_back_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
card_back_surface.blit(card_back_image, (0, 0))

# Load card photo images
card_images = {}
for symbol in CARD_SYMBOLS:
    card_image = pygame.image.load(f"photos/{symbol}.png")
    card_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
    card_images[symbol] = card_image

# Game state variables
revealed_cards = []
matched_cards = []
game_over = False
start_time = None
# countdown_time = 60  # Initial countdown time for Attack Mode
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


countdown_time = 61

# Initialize Vosk model
model = Model("vosk-model-small-en-us-0.15")

# Initialize Vosk recognizer
rec = KaldiRecognizer(model, 16000)
# Initialize PyAudio
p = pyaudio.PyAudio()

# Function to convert word to number
def word_to_int(word):
    return word_to_number.get(word, None)


# Function to capture and process audio
def talk():
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    audio_data = b""
    data = stream.read(30000)  # Read audio data from microphone
    audio_data += data
    rec.AcceptWaveform(audio_data)
    result = rec.Result()
    result_dict = json.loads(result)
    recognized_text = result_dict.get("text", "").strip().lower()
    return recognized_text
    

def reset_game():
    global cards, revealed_cards, matched_cards, game_over, start_time, countdown_time, flip_back_timer, hint_button_clicked, current_player, hint_used
    cards = [(symbol, False) for symbol in CARD_SYMBOLS * 2]
    random.shuffle(cards)
    revealed_cards = []
    matched_cards = []
    game_over = False
    start_time = time.time()
    flip_back_timer = 0
    hint_button_clicked = False
    current_player = 1
    hint_used = False

def reset_game_attack():
    global cards, revealed_cards, matched_cards, game_over, start_time, countdown_time, flip_back_timer, hint_button_clicked, current_player, hint_used
    cards = [(symbol, False) for symbol in CARD_SYMBOLS * 2]
    random.shuffle(cards)
    revealed_cards = []
    matched_cards = []
    game_over = False
    start_time = time.time()
    flip_back_timer = 0
    hint_button_clicked = False
    current_player = 1
    hint_used = False
    
    
reset_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 60, 200, 40)
reset_button_rect_voice = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 60, 300, 40)
hint_button_rect = pygame.Rect(WINDOW_WIDTH // 2 -60, WINDOW_HEIGHT - 120, 120, 40)
hint_button_clicked = False

def draw_player_choice_screen():
    font = pygame.font.SysFont(None, 48)
    text_1 = font.render("1 Player", True, WHITE)
    text_2 = font.render("2 Players", True, WHITE)
    text_3 = font.render("Attack Mode", True, WHITE)
    text_4 = font.render("Voice Mode", True, WHITE)
    
    player_1_button = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 165, 300, 50)
    player_2_button = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2, 300, 50)
    attack_button = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 100, 300, 50)
    voice_control_button = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 100, 200, 50)
    
    border_width = 2

    # Draw player 1 button with border
    pygame.draw.rect(window, player_1_color, player_1_button)
    pygame.draw.rect(window, BLACK, player_1_button, border_width)

    # Draw player 2 button with border
    pygame.draw.rect(window, player_2_color, player_2_button)
    pygame.draw.rect(window, BLACK, player_2_button, border_width)

    # Draw attack button with border
    pygame.draw.rect(window, attack_color, attack_button)
    pygame.draw.rect(window, BLACK, attack_button, border_width)

    # Draw voice control button with border
    pygame.draw.rect(window, player_1_voice_color, voice_control_button)
    pygame.draw.rect(window, BLACK, voice_control_button, border_width)

    window.blit(text_1, (WINDOW_WIDTH // 2 - text_1.get_width() / 2, WINDOW_HEIGHT // 2 - 155))
    window.blit(text_2, (WINDOW_WIDTH // 2 - text_2.get_width() / 2, WINDOW_HEIGHT // 2 +10))
    window.blit(text_3, (WINDOW_WIDTH // 2 - text_3.get_width() / 2, WINDOW_HEIGHT // 2 + 110))
    window.blit(text_4, (WINDOW_WIDTH // 2 - text_4.get_width() / 2, WINDOW_HEIGHT // 2 - 90))
    
    return player_1_button, player_2_button, attack_button, voice_control_button


def draw_cards():
    for i, (symbol, is_revealed) in enumerate(cards):
        x = (i % 4) * (CARD_WIDTH + CARD_SPACING) + CARD_SPACING
        y = ((i // 4) * (CARD_HEIGHT + CARD_SPACING)) + CARD_SPACING + 80
        if is_revealed or i in matched_cards:
            pygame.draw.rect(window, GRAY, (x, y, CARD_WIDTH, CARD_HEIGHT))
            card_image = card_images[symbol]
            window.blit(card_image, (x, y))
        else:
            window.blit(card_back_surface, (x, y))
            font = pygame.font.SysFont(None, 36)
            text = font.render(str(i + 1), True, WHITE)
            window.blit(text, (x + (CARD_WIDTH - text.get_width()) / 2, y + (CARD_HEIGHT - text.get_height()) / 2))

def flip_card_animation(card_index, symbol):
    card_rect = pygame.Rect((card_index % 4) * (CARD_WIDTH + CARD_SPACING) + CARD_SPACING,
                            ((card_index // 4) * (CARD_HEIGHT + CARD_SPACING)) + CARD_SPACING + 80,
                            CARD_WIDTH, CARD_HEIGHT)
    
    animation_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
    
    for angle in range(0, 180, 10):
        animation_surface.fill((0, 0, 0, 0))  # Clear the animation surface
        
        rotated_card_back = pygame.transform.rotate(card_back_surface, angle)
        rotated_card_front = pygame.transform.rotate(card_images[symbol], angle)
        
        if angle < 90:
            animation_surface.blit(rotated_card_back, ((CARD_WIDTH - rotated_card_back.get_width()) // 2,
                                                       (CARD_HEIGHT - rotated_card_back.get_height()) // 2))
        else:
            animation_surface.blit(rotated_card_front, ((CARD_WIDTH - rotated_card_front.get_width()) // 2,
                                                        (CARD_HEIGHT - rotated_card_front.get_height()) // 2))
        
        window.blit(animation_surface, card_rect)
        pygame.display.update(card_rect)
        pygame.time.delay(20)

def draw_timer():
    global game_over
    if not game_over:
        if players_choice == 'attack':
            elapsed_time = max(countdown_time - (time.time() - start_time), 0)
            if elapsed_time == 0:   
                game_over = True
                return draw_game_over_message()
        else:
            elapsed_time = time.time() - start_time
    else:
        elapsed_time = countdown_time if players_choice == 'attack' else final_time
    font = pygame.font.SysFont(None, 50)
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    timer_text = font.render(f"Time: {minutes:02}:{seconds:02}", True, WHITE)
    window.blit(timer_text, (155, 40))

def draw_game_over_screen():
    if game_over:
        if players_choice == 'attack':
            return draw_game_over_message()
        else:
            return draw_game_well_done_message()
    return None

def draw_player_indicator():
    if players_choice == '2':
        if current_player == 1:
            font = pygame.font.SysFont(None, 35)

            bg_rect1 = pygame.Rect(WINDOW_WIDTH // 2 -150 , WINDOW_HEIGHT // 2 + 230, 120,50)
            pygame.draw.rect(window, GREEN, bg_rect1)
            text1 = font.render("player 1", True, BLACK)
            window.blit(text1, (WINDOW_WIDTH // 2 -135 , WINDOW_HEIGHT // 2 + 240))

            bg_rect2 = pygame.Rect(WINDOW_WIDTH // 2 + 100  , WINDOW_HEIGHT // 2 + 230, 120,50)
            pygame.draw.rect(window, Board, bg_rect2)
            text2 = font.render("player 2", True, BLACK)
            window.blit(text2, (WINDOW_WIDTH // 2 + 40 , WINDOW_HEIGHT // 2 + 240))
        else:
            font = pygame.font.SysFont(None, 35)

            bg_rect1 = pygame.Rect(WINDOW_WIDTH // 2 -150 , WINDOW_HEIGHT // 2 + 230, 120,50)
            pygame.draw.rect(window, Board, bg_rect1)
            text1 = font.render("player 1", True, BLACK)
            window.blit(text1, (WINDOW_WIDTH // 2 -135 , WINDOW_HEIGHT // 2 + 240))

            bg_rect2 = pygame.Rect(WINDOW_WIDTH // 2 + 30  , WINDOW_HEIGHT // 2 + 230, 120,50)
            pygame.draw.rect(window, GREEN, bg_rect2)
            text2 = font.render("player 2", True, BLACK)
            window.blit(text2, (WINDOW_WIDTH // 2 + 40 , WINDOW_HEIGHT // 2 + 240))
  

def draw_game_well_done_message():
    bg_rect = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT // 2 - 60, 320, 120)
    pygame.draw.rect(window, play_again_color, bg_rect)
    # Add black border to the background rectangle
    pygame.draw.rect(window, BLACK, bg_rect, 2)

    font = pygame.font.SysFont(None, 48)
    text = font.render("Well Done!", True, BLACK)
    window.blit(text, (WINDOW_WIDTH // 2 - text.get_width() / 2, WINDOW_HEIGHT // 2 - 45))

    play_again_text = "Play Again"
    play_again_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, 200, 50)
    pygame.draw.rect(window, HINT_COLOR, play_again_rect)
    # Add black border to the "Play Again" rectangle
    pygame.draw.rect(window, BLACK, play_again_rect, 2)

    text = font.render(play_again_text, True, WHITE)
    window.blit(text, (WINDOW_WIDTH // 2 - text.get_width() / 2, WINDOW_HEIGHT // 2 + 10))

    return play_again_rect

def draw_game_over_message():
    bg_rect = pygame.Rect(WINDOW_WIDTH // 2 - 160, WINDOW_HEIGHT // 2 - 60, 320, 120)
    pygame.draw.rect(window, play_again_color, bg_rect)
    pygame.draw.rect(window, BLACK, bg_rect, 2)

    font = pygame.font.SysFont(None, 48)
    text = font.render("Game Over!", True, BLACK)
    window.blit(text, (WINDOW_WIDTH // 2 - text.get_width() / 2, WINDOW_HEIGHT // 2 - 45))
    
    play_again_text = "Play Again"
    play_again_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 , 200, 50)
    pygame.draw.rect(window, HINT_COLOR, play_again_rect)
    pygame.draw.rect(window, BLACK, play_again_rect, 2)

    text = font.render(play_again_text, True, WHITE)
    window.blit(text, (WINDOW_WIDTH // 2 - text.get_width() / 2, WINDOW_HEIGHT // 2 + 10))
    return play_again_rect

running = True
play_again_rect = None
hint_timer = 0
hint_card_index = None
audio_listener = None

while running:
    if players_choice is None:
        window.blit(background_image, (0, 0))
        player_1_button, player_2_button, attack_button, voice_control_button = draw_player_choice_screen()
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
                elif attack_button.collidepoint(mouse_x, mouse_y):
                    players_choice = 'attack'
                    reset_game()
                elif voice_control_button.collidepoint(mouse_x, mouse_y):
                    players_choice = 'voice'
                    reset_game()
        continue

    if players_choice != 'voice':
        current_time = pygame.time.get_ticks()
        window.fill(Board)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if play_again_rect and play_again_rect.collidepoint(mouse_x, mouse_y):
                    countdown_time = 61
                    reset_game()
                    play_again_rect = None
                elif reset_button_rect.collidepoint(mouse_x, mouse_y):
                    reset_game()
                elif hint_button_rect.collidepoint(mouse_x, mouse_y) and not hint_used and players_choice == '1':
                    hint_used = True
                    hint_button_clicked = True
                    unrevealed_cards = [i for i, (symbol, is_revealed) in enumerate(cards) if not is_revealed and i not in matched_cards]
                    if unrevealed_cards:
                        hint_card_index = random.choice(unrevealed_cards)
                        cards[hint_card_index] = (cards[hint_card_index][0], True)
                        hint_timer = current_time + 2000
                else:
                    if not game_over:
                        for i, (symbol, is_revealed) in enumerate(cards):
                            x = (i % 4) * (CARD_WIDTH + CARD_SPACING) + CARD_SPACING
                            y = ((i // 4) * (CARD_HEIGHT + CARD_SPACING)) + CARD_SPACING + 80
                            if x < mouse_x < x + CARD_WIDTH and y < mouse_y < y + CARD_HEIGHT and not is_revealed and len(revealed_cards) < 2:
                                revealed_cards.append(i)
                                cards[i] = (cards[i][0], True)
                                flip_card_animation(i, symbol)  # Call the flip animation function
                                if len(revealed_cards) == 2:
                                    if cards[revealed_cards[0]][0] == cards[revealed_cards[1]][0]:
                                        matched_cards.extend(revealed_cards)
                                        revealed_cards = []
                                        if match_sound:
                                            match_sound.play()
                                        if len(matched_cards) == NUM_CARDS and players_choice != 'attack':
                                            game_over = True
                                            final_time = time.time() - start_time
                                        if len(matched_cards) == NUM_CARDS and players_choice == 'attack':
                                            countdown_time = countdown_time - 5
                                            reset_game_attack()
                                    else:
                                        flip_back_timer = current_time + flip_back_delay
                                        if players_choice == '2':
                                            current_player = 2 if current_player == 1 else 1
                    
    else:
        current_time = pygame.time.get_ticks()
        window.fill(Board)
        # for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            stop_audio_thread = True
        else:
            if not game_over:
                if audio_listener is None:
                    audio_listener = threading.Thread(target=audio_listener_thread)
                    audio_listener.start()

                while not audio_queue.empty():
                    speech = audio_queue.get()
                    # print(speech) // for debug
                    x = word_to_int(speech)
                    if isinstance(x, int):
                        if x == 17:
                            reset_game()
                        else:
                            i = x - 1
                            if i not in revealed_cards and len(revealed_cards) < 2:
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
    if players_choice != 'attack' and players_choice != 'voice' :
        pygame.draw.rect(window, RED, reset_button_rect)
        border_width = 2
        border_rect = pygame.Rect(reset_button_rect.left - border_width,
                                reset_button_rect.top - border_width,
                                reset_button_rect.width + border_width * 2,
                                reset_button_rect.height + border_width * 2)
        pygame.draw.rect(window, BLACK, border_rect, border_width)
        reset_text = pygame.font.SysFont(None, 36).render('Reset', True, WHITE)
        window.blit(reset_text, (reset_button_rect.x + (reset_button_rect.width - reset_text.get_width()) / 2, reset_button_rect.y + 10))

    if players_choice == 'voice' :
        pygame.draw.rect(window, RED, reset_button_rect_voice)
        reset_text = pygame.font.SysFont(None, 36).render('say "Play again" to reset', True, WHITE)
        window.blit(reset_text, (reset_button_rect.x + (reset_button_rect.width - reset_text.get_width()) / 2, reset_button_rect.y + 5))

    if players_choice == '1' and not hint_button_clicked and not hint_used:
        pygame.draw.rect(window, HINT_COLOR, hint_button_rect)
        border_width = 2
        border_rect = pygame.Rect(hint_button_rect.left - border_width,
                                hint_button_rect.top - border_width,
                                hint_button_rect.width + border_width * 2,
                                hint_button_rect.height + border_width * 2)
        pygame.draw.rect(window, BLACK, border_rect, border_width)
        hint_text = pygame.font.SysFont(None, 36).render('Hint', True, WHITE)
        window.blit(hint_text, (hint_button_rect.x + (hint_button_rect.width - hint_text.get_width()) / 2, hint_button_rect.y + 5))

    draw_player_indicator()
    pygame.display.update()

pygame.quit()
