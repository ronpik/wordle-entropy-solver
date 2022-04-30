from engine import CliWordleEngine
from engine.auto_wordle_engine import PredefinedWordleSession
from solver.cli_solver_wrapper import CliSolverWrapper
from solver.simplified_entropy_solver import SimplifiedEntropySolver
from utils import load_words


if __name__ == "__main__":
    words_path = "../resources/allowed_words.txt"
    all_words = list(load_words(words_path))
    session = PredefinedWordleSession("hover", 6)
    # solver = CliSolverWrapper(SimplifiedEntropySolver(all_words, max_guesses=6))
    solver = SimplifiedEntropySolver(all_words, max_guesses=6)
    solver.solve(session)
    if session.is_solved():
        print("Solved!")
    else:
        print("Failed!")
