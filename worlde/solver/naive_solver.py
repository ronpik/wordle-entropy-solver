import random
from typing import List, Iterator

from solver.constraints import Constraints
from solver.wordle_solver import WordleSolver


class NaiveSolver(WordleSolver):

    def __init__(self, allowed_words: List[str], seed: int = 1919):
        self.allowed_words = allowed_words
        self.random = random.Random(seed)

    def iter_first_guesses(self) -> Iterator[str]:
        indices = list(range(len(self.allowed_words)))
        self.random.shuffle(indices)
        yield from iter(map(self.allowed_words.__getitem__, indices))

    def iter_guesses(self, current_guesses: Iterator[str], constraints: Constraints) -> Iterator[str]:
        return constraints.filter_words(current_guesses)
