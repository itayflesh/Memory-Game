# Memory Game

## Description

https://drive.google.com/file/d/1V3sOVXkO_T1NppGZghjS09gNF2jazwDO/view?usp=share_link

This project is a Python-based memory game created as part of a programming assignment. The game features a classic memory card-matching mechanic with additional modes and features to enhance gameplay.

Key features include:
- Single-player mode
- Two-player mode
- Time Attack mode
- Voice Control mode
- Hint system
- Card flip animations
- Sound effects for matches

## Installation

To run this game, you'll need to have Python installed on your system. The game uses several libraries that you'll need to install:

1. Install Python (version 3.6 or higher) from [python.org](https://www.python.org/downloads/)

2. Install the required libraries using pip:

```
pip install pygame pyaudio vosk sounddevice numpy
```

3. Download the Vosk model for voice recognition:
   - Go to the [Vosk Models page](https://alphacephei.com/vosk/models)
   - Download the `vosk-model-small-en-us-0.15` model
   - Extract the model files into a folder named `vosk-model-small-en-us-0.15` in the same directory as the game script

4. Prepare the game assets:
   - Create a `photos` folder in the game directory
   - Add card images named A.png, B.png, C.png, etc., for each card symbol
   - Add a `card_back.png` image for the back of the cards
   - Add a `background.jpeg` image for the game background

5. Add a sound effect:
   - Create a `sound` folder in the game directory
   - Add a `match.wav` sound file for the card match effect

## How to Play

1. Run the Python script to start the game.
2. Choose a game mode from the main menu:
   - 1 Player: Standard single-player memory game
   - 2 Players: Take turns matching cards
   - Attack Mode: Race against the clock to match all cards
   - Voice Mode: Control the game using voice commands

3. Click on cards to reveal them and find matching pairs.
4. In single-player mode, use the hint button for assistance (one-time use).
5. In voice mode, say the number of the card you want to flip.
6. Match all pairs to win the game.

## Technologies Used

- Python: The core programming language
- Pygame: For game graphics and window management
- PyAudio: For audio input processing
- Vosk: For speech recognition in voice control mode
- Sounddevice: For audio device handling
- NumPy: For numerical operations
- Threading: For concurrent execution in voice control mode

This project demonstrates the use of various Python libraries to create an interactive game with multiple features and modes of play.
