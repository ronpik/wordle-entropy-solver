import abc
from typing import Iterator

from engine.wordle_engine import WordleSessionEngine
from solver.constraints import Constraints


class WordleSolver(abc.ABC):

    @abc.abstractmethod
    def iter_first_guesses(self) -> Iterator[str]:
        pass

    @abc.abstractmethod
    def iter_guesses(self, guesses_iter: Iterator[str], constraints: Constraints) -> Iterator[str]:
        pass

    def solve(self, session: WordleSessionEngine) -> int:
        guesses_it = self.iter_first_guesses()
        n_guesses = 0
        constraints = Constraints.create_empty()
        while not session.is_solved():
            n_guesses += 1
            next_word = next(guesses_it)
            feedback = session.guess(next_word)
            constraints = constraints.update(next_word, feedback.labels)
            guesses_it = self.iter_guesses(guesses_it, constraints)

        return n_guesses
