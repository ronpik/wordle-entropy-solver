import json
from operator import itemgetter
from typing import List, Tuple

from worlde.letters_stats import get_sorted_words
from worlde.utils import load_wordslist, compute_word_weights_from_freqs, load_freqs
from worlde.wordle_engine import WordleEngine
from worlde.wordle_solver import Constraints


def result_to_json(target: str, session_guesses: List[Tuple[str, int, List[str]]], solved: bool, ignored: bool) -> dict:
    return {
        "target": target,
        "guesses": [{"guess": guess, "n_remained": n_remained, "remained": remained}
                    for guess, n_remained, remained in session_guesses],
        "solved": solved,
        "ignored": ignored
    }


def has_information_gain(remained_words: List[str], guesses_entropies: List[Tuple[str, float]]) -> bool:
    remained_words_set = set(remained_words)
    min_entropy = min(map(itemgetter(1), filter(lambda t: t[0] in remained_words_set, guesses_entropies)))
    max_entropy = max(map(itemgetter(1), filter(lambda t: t[0] in remained_words_set, guesses_entropies)))
    return max_entropy > min_entropy + 0.5


if __name__ == "__main__":
    POSSIBLE_ANSWERS_FILEPATH = "possible_words.txt"
    ALLOWED_GUESSES_FILEPATH = "allowed_words.txt"
    FREQS_PATH = "freq_map.json"

    freqs = load_freqs(FREQS_PATH)
    freqs_map = dict(freqs)
    guesses_weights = compute_word_weights_from_freqs(freqs)

    possible_answers = load_wordslist(POSSIBLE_ANSWERS_FILEPATH)
    allowed_guesses = sorted(load_wordslist(ALLOWED_GUESSES_FILEPATH), key=freqs_map.get, reverse=True)

    wordle_engine = WordleEngine(possible_answers, allowed_guesses)

    initial_sorted_allowed_guesses = get_sorted_words(allowed_guesses, weights=guesses_weights)
    # initial_sorted_possible_guesses = get_sorted_words(possible_answers)

    possible_answers = set(possible_answers)

    results = []
    avg_n_guesses = 0
    while wordle_engine.has_next_word():
        print(len(results), end=") ")
        # prepare for guessing session
        guesses = []
        wordle_engine.new_session()
        sorted_allowed_guesses = initial_sorted_allowed_guesses
        remained_words = allowed_guesses
        constraints = Constraints.create_empty()
        solved, ignored = False, False
        while wordle_engine.has_more_guess():
            word = sorted_allowed_guesses[0][0] if (len(remained_words) > 1) else remained_words[0]
            feedback = wordle_engine.guess(word)
            guesses.append((word, len(remained_words), [] if len(remained_words) > 10 else remained_words))
            print(word, end=" -> ")
            if feedback.is_solved:
                solved = True
                print(f"Solved! (in {len(guesses)} tries)")
                break

            # constraints.update(word, feedback.labels)
            constraints = Constraints.create(word, feedback.labels)
            remained_words = list(constraints.filter_words(remained_words))
            sorted_allowed_guesses = get_sorted_words(remained_words, weights=guesses_weights)
            if (len(remained_words) > 2) and (len(guesses) < 5) and (not has_information_gain(remained_words, sorted_allowed_guesses)):
                sorted_allowed_guesses = get_sorted_words(allowed_guesses, remained_words, weights=guesses_weights)
                # ignored = True

        results.append(result_to_json(wordle_engine.target, guesses, False, ignored))

        if ignored:
            print("O", wordle_engine.target, "Ignored")
            continue

        if not solved:
            print("X", wordle_engine.target, "Failed!")

        avg_n_guesses = ((avg_n_guesses * (len(results) - 1)) + len(guesses)) / (len(results))
        print(avg_n_guesses)

    with open("wordle-results.jsonl", 'w') as f:
        results_str = "\n".join(map(json.dumps, results))
        f.write(results_str)


