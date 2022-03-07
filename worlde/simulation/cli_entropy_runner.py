from engine import CliWordleEngine
from solver.cli_solver_wrapper import CliSolverWrapper
from solver.simplified_entropy_solver import SimplifiedEntropySolver
from utils import load_words


if __name__ == "__main__":
    words_path = "../resources/allowed_words.txt"
    all_words = list(load_words(words_path))
    engine = CliWordleEngine()
    solver = CliSolverWrapper(SimplifiedEntropySolver(all_words, max_guesses=6))
    solver.solve(engine.new_session())
