from engine.auto_wordle_engine import AutoWordleEngine, MaxTriesExceededError
from solver.simplified_entropy_solver import SimplifiedEntropySolver
from utils import load_words, load_wordslist

if __name__ == "__main__":
    words_path = "../resources/allowed_words.txt"
    POSSIBLE_ANSWERS_FILEPATH = "../resources/possible_words.txt"
    FREQS_PATH = "freq_map.json"
    max_guesses = 6

    all_words = list(load_words(words_path))
    possible_answers = load_wordslist(POSSIBLE_ANSWERS_FILEPATH)

    wordle_engine = AutoWordleEngine(possible_answers, all_words)
    solver = SimplifiedEntropySolver(all_words, max_guesses=6)

    results = []
    avg_n_guesses = 0
    while wordle_engine.has_next_word():
        session = wordle_engine.new_session()
        try:
            n_guesses = solver.solve(session)
        except MaxTriesExceededError:
            n_guesses = max_guesses + 1

        results.append(n_guesses)
        avg_n_guesses = ((avg_n_guesses * (len(results) - 1)) + n_guesses) / len(results)

        # status_str = "Solved" if session.is_solved() else "Failed"
        status_str = "Solved" if n_guesses <= max_guesses else "Failed"
        print(f"{len(results)}) {session.target}\t{status_str}!\t{n_guesses}\t({avg_n_guesses})")


