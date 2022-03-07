from typing import Iterator, List

from engine import WordleEngine
from solver.constraints import Constraints
from solver.wordle_solver import WordleSolver


class SimplifiedEntropySolver(WordleSolver):

    def __init__(self, engine: WordleEngine, allowed_words: List[str]):
        self.engine = engine
        self.allowed_words = allowed_words

    def get_engine(self) -> WordleEngine:
        return self.engine

    def iter_first_guesses(self) -> Iterator[str]:
        pass

    def iter_guesses(self, current_guesses: Iterator[str], constraints: Constraints) -> Iterator[str]:
        pass