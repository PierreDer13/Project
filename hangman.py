import pygame
import random
import string
from english_words import english_words_lower_set
import os
import json
from datetime import datetime


pygame.init()

# Window settings
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
RED = (200, 40, 40)
GREEN = (30, 150, 60)
BLUE = (40, 90, 180)

# Fonts
title_font = pygame.font.Font(None, 64)
word_font = pygame.font.Font(None, 58)
text_font = pygame.font.Font(None, 34)
small_font = pygame.font.Font(None, 28)
hangman_font = pygame.font.Font(None, 36)

# Hangman drawings
hangman = [
    """
-----
|   |

|
|
|
=========
""",
    """
-----
|   |
O   |
|
|
=========
""",
    """
-----
|   |
O   |
|   |
|
=========
""",
    """
-----
|   |
O   |
/|\\  |
|
=========
""",
    """
-----
|   |
O   |
/|\\  |
/    |
=========
""",
    """
-----
|   |
O   |
/|\\  |
/ \\  |
=========
"""
]


# Remove accidental spaces from the example words
word_set = [word.strip().lower() for word in english_words_lower_set]

# ScoreBoard
SCORES_FILE = "hangman_scores.json"
def load_scores():
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as file:
            scores = json.load(file)

            # Make sure the JSON contains a list
            if isinstance(scores, list):
                return scores

            return []

    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        # The file is empty or contains invalid JSON
        return []

def save_score(attempts):
    print("save_score() was called")

    scores = []

    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r", encoding="utf-8") as file:
            scores = json.load(file)
    new_score = {
        "attempts": attempts,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    scores.append(new_score)
    scores.sort(key=lambda score: score["attempts"])    #Least attempts in first
    scores = scores[:10]                                #Keep 10 best

    with open(SCORES_FILE, "w", encoding="utf-8") as file:
       json.dump(scores, file, indent=4)

    return scores
def draw_leaderboard(scores, x, y):
    draw_text("BEST SCORERS", text_font, BLUE, x, y)

    if not isinstance(scores, list) or len(scores) == 0:
        draw_text("No scores yet", small_font, BLACK, x, y + 40)
        return
    for index, score in enumerate(scores[:5]):
            text = (
                f"{index + 1}. "
                f"{score['attempts']} wrong guesses - " 
                f"{score['date']}"
            )

            draw_text(
                text,
                small_font,
                BLACK,
                x,
                y + 40 + index * 30
            )

    
def new_game():
    word = random.choice(word_set)
    guessed_word = ["_"] * len(word)
    guessed_letters = set()
    wrong_guesses = 0
    message = "Guess a letter"
    game_over = False
    won = False

    return (
        word,
        guessed_word,
        guessed_letters,
        wrong_guesses,
        message,
        game_over,
        won,
    )


def draw_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)

    if center:
        rect = surface.get_rect(center=(x, y))
    else:
        rect = surface.get_rect(topleft=(x, y))

    screen.blit(surface, rect)


def draw_hangman(drawing, x, y):
    lines = drawing.strip("\n").split("\n")

    for number, line in enumerate(lines):
        draw_text(line, hangman_font, BLACK, x, y + number * 32)


# Start game
(
    word,
    guessed_word,
    guessed_letters,
    wrong_guesses,
    message,
    game_over,
    won,
) = new_game()

clock = pygame.time.Clock()
running = True
score_saved = False
Scores = load_scores
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # Start a new game after win/loss
            if game_over:
                if event.key == pygame.K_r:
                    (
                        word,
                        guessed_word,
                        guessed_letters,
                        wrong_guesses,
                        message,
                        game_over,
                        won,
                    ) = new_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False

            # Process letter guesses
            elif event.unicode.lower() in string.ascii_lowercase:
                letter = event.unicode.lower()

                if letter in guessed_letters:
                    message = f"You already guessed '{letter}'"

                else:
                    guessed_letters.add(letter)

                    if letter in word:
                        for index, character in enumerate(word):
                            if character == letter:
                                guessed_word[index] = letter

                        message = "Correct!"

                        if "_" not in guessed_word:
                            message = f"You won! The word was: {word}"
                            message = f"You guessed {word} in {wrong_guesses} attempts but in {save_score}"
                            game_over = True
                            won = True
                            if not score_saved:
                                scores = save_score(wrong_guesses)
                                score_saved = True

                    else:
                        wrong_guesses += 1
                        remaining = 5 - wrong_guesses
                        message = f"Wrong! Attempts remaining: {remaining}"

                        if wrong_guesses >= 5:
                            message = f"Game over! The word was: {word}"
                            game_over = True
                            won = False

    # Background
    screen.fill(WHITE)

    # Title
    draw_text("HANGMAN", title_font, BLUE, WIDTH // 2, 55, center=True)

    # Hangman drawing
    draw_hangman(hangman[wrong_guesses], 80, 130)
    draw_leaderboard(Scores, 500, 130)
    # Word display
    word_display = " ".join(guessed_word)
    draw_text(word_display, word_font, BLACK, WIDTH // 2, 280, center=True)

    # Guessed letters
    guessed_display = ", ".join(sorted(guessed_letters))
    draw_text(
        f"Guessed letters: {guessed_display}",
        text_font,
        BLACK,
        WIDTH // 2,
        360,
        center=True,
    )

    # Attempts
    draw_text(
        f"Wrong guesses: {wrong_guesses}/5",
        text_font,
        RED if wrong_guesses >= 3 else BLACK,
        WIDTH // 2,
        410,
        center=True,
    )

    # Status message
    message_color = GREEN if won else RED if game_over else BLACK
    draw_text(
        message,
        text_font,
        message_color,
        WIDTH // 2,
        480,
        center=True,
    )

    # Instructions
    if game_over:
        draw_text(
            "Press R to play again or ESC to quit",
            small_font,
            GRAY,
            WIDTH // 2,
            550,
            center=True,
        )
    else:
        draw_text(
            "Type a letter using your keyboard",
            small_font,
            GRAY,
            WIDTH // 2,
            550,
            center=True,
        )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
