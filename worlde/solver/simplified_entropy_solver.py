from typing import Iterator

from engine import WordleEngine
from solver.constraints import Constraints
from solver.wordle_solver import WordleSolver


class SimplifiedEntropySolver(WordleSolver):
    def get_engine(self) -> WordleEngine:
        pass

    def iter_first_guesses(self) -> Iterator[str]:
        pass

    def iter_guesses(self, current_guesses: Iterator[str], constraints: Constraints) -> Iterator[str]:
        pass