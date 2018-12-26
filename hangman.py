import random

import hangman_helper
from hangman_gui import MAX_ERRORS, WIN_MSG, LOSS_MSG, ALREADY_CHOSEN_MSG, NON_VALID_MSG, HINT_MSG, DEFAULT_MSG, HINT, \
    LETTER


def load_words(file='resources/words.txt'):
    lines = open(file)
    words = [line.strip() for line in lines if line.strip().isalpha()]
    lines.close()
    return words


def get_random_word(words_list):
    return random.choice(words_list)


def update_word_pattern(word, pattern, letter):
    pattern_list = list(pattern)

    for i in range(len(word)):
        if word[i] == letter:
            pattern_list[i] = letter

    return ''.join(pattern_list)


def get_letter_indices_dict(word):
    letter_indices_dict = dict()
    for i in range(len(word)):
        if word[i] != '_':
            letter_indices_dict[word[i]] = letter_indices_dict.get(word[i], []) + [i]
    return letter_indices_dict


def filter_words_list(words, pattern, wrong_guesses):
    hints = list()
    wrong_guesses_set = set(wrong_guesses)
    letter_indices_dict = get_letter_indices_dict(pattern)

    for word in words:
        if len(word) != len(pattern):
            continue

        matches_pattern = True
        for letter, indices in letter_indices_dict.items():
            for index in indices:
                if word[index] != letter:
                    matches_pattern = False

        if matches_pattern and not wrong_guesses_set.intersection(set(word)):
            hints.append(word)

    return hints


def choose_hint(words, pattern):
    letter_count_dict = dict()

    for word in words:
        for letter in word:
            if letter not in pattern:
                letter_count_dict[letter] = letter_count_dict.get(letter, 0) + 1

    return max(letter_count_dict, key=letter_count_dict.get)


def is_input_valid(input_letter):
    return len(input_letter) != 1 or not input_letter.isalpha()


def run_single_game(words):
    word = get_random_word(words)
    pattern = '_' * len(word)

    wrong_guesses = list()
    used_letters = list()
    error_counter = 0

    hangman_helper.display_state(pattern, error_counter, wrong_guesses, DEFAULT_MSG)

    while True:
        input_action, input_letter = hangman_helper.get_input()

        if input_action == LETTER:
            if is_input_valid(input_letter):
                hangman_helper.display_state(pattern, error_counter, wrong_guesses, NON_VALID_MSG)
            elif input_letter in used_letters:
                hangman_helper.display_state(pattern, error_counter, wrong_guesses, ALREADY_CHOSEN_MSG + input_letter)
            elif input_letter in word:
                used_letters.append(input_letter)
                pattern = update_word_pattern(word, pattern, input_letter)
                if pattern == word:
                    hangman_helper.display_state(pattern, error_counter, wrong_guesses, WIN_MSG, ask_play=True)
                    break
                hangman_helper.display_state(pattern, error_counter, wrong_guesses, DEFAULT_MSG)
            elif input_letter not in word:
                wrong_guesses.append(input_letter)
                used_letters.append(input_letter)
                error_counter += 1
                if error_counter == MAX_ERRORS:
                    hangman_helper.display_state(pattern, error_counter, wrong_guesses, LOSS_MSG + word, ask_play=True)
                    break
                hangman_helper.display_state(pattern, error_counter, wrong_guesses, DEFAULT_MSG)

        if input_action == HINT:
            possible_words = filter_words_list(words, pattern, wrong_guesses)
            hint = choose_hint(possible_words, pattern)
            hangman_helper.display_state(pattern, error_counter, wrong_guesses, HINT_MSG + hint)


def main():
    words = load_words()

    while True:
        run_single_game(words)

        if not hangman_helper.get_input()[1]:
            break


if __name__ == "__main__":
    hangman_helper.start_gui()
    main()
    hangman_helper.close_gui()
