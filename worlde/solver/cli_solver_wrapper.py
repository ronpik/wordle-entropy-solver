from typing import Iterator

from engine import WordleEngine
from solver.constraints import Constraints
from solver.wordle_solver import WordleSolver


VALID_INPUTS = {'c', 'n', 'i'}


def get_user_selection(next_word: str, default_selection: str = None) -> str:
    default_selection = default_selection or 'c'
    while True:
        print(f"The next word is: {next_word}")
        print("Type ['c'] to continue with the above word, ['n'] to take the next word, ['i'] to insert word of your own")
        raw_input = input(f"Please type your selection: [{default_selection}]")
        if len(raw_input) == 0:
            return default_selection

        if len(raw_input) > 1 or (raw_input not in VALID_INPUTS):
            print("Invalid input")
            continue

        return raw_input


def select_first_then_iter(guesses: Iterator[str]) -> Iterator[str]:
    while True:
        next_word = next(guesses)
        selection = get_user_selection(next_word)

        if selection == 'n':
            continue

        if selection == 'c':
            yield next_word

        elif selection == 'i':
            print("Insert the word you've used:")
            word = input()
            yield word

        break

    yield from guesses


class CliSolverWrapper(WordleSolver):

    def __init__(self, solver: WordleSolver):
        self.solver = solver

    def iter_first_guesses(self) -> Iterator[str]:
        guesses = self.solver.iter_first_guesses()
        return select_first_then_iter(guesses)

    def iter_guesses(self, current_guesses: Iterator[str], constraints: Constraints) -> Iterator[str]:
        guesses = self.solver.iter_guesses(current_guesses, constraints)
        return select_first_then_iter(guesses)

