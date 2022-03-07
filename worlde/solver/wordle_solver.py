import abc
from typing import Iterator

from engine import WordleEngine
from solver.constraints import Constraints


class WordleSolver(abc.ABC):

    @abc.abstractmethod
    def get_engine(self) -> WordleEngine:
        pass

    @abc.abstractmethod
    def iter_first_guesses(self) -> Iterator[str]:
        pass

    @abc.abstractmethod
    def iter_guesses(self, current_guesses: Iterator[str], constraints: Constraints) -> Iterator[str]:
        pass

    def solve(self) -> int:
        engine = self.get_engine()
        guesses_it = self.iter_first_guesses()
        n_guesses = 0
        while True:
            n_guesses += 1
            next_word = next(guesses_it)
            feedback = engine.guess(next_word)
            if feedback.is_solved():
                break

            constraints = Constraints.create(next_word, feedback.labels)
            guesses_it = self.iter_guesses(guesses_it, constraints)

        return n_guesses


# speak with Avi
# speak with Ronen
# speak with Benny





