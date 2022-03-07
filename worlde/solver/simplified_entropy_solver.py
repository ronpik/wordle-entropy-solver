from operator import itemgetter
from typing import Iterator, List, Tuple

from solver.constraints import Constraints
from solver.entropy.letters_stats import sort_by_info_gain
from solver.wordle_solver import WordleSolver


def has_information_gain(remained_words: List[str], guesses_entropies: List[Tuple[str, float]]) -> bool:
    remained_words_set = set(remained_words)
    min_entropy = min(map(itemgetter(1), filter(lambda t: t[0] in remained_words_set, guesses_entropies)))
    max_entropy = max(map(itemgetter(1), filter(lambda t: t[0] in remained_words_set, guesses_entropies)))
    return max_entropy > min_entropy + 0.5


class SimplifiedEntropySolver(WordleSolver):

    def __init__(self, allowed_guesses: List[str], max_guesses: int):
        self.allowed_guesses = allowed_guesses
        self.n_guesses = 0
        self.max_guesses = max_guesses

    def iter_first_guesses(self) -> Iterator[str]:
        self.n_guesses = 1
        sorted_guesses = sort_by_info_gain(self.allowed_guesses)
        return iter(map(itemgetter(0), sorted_guesses))

    def iter_guesses(self, current_guesses: Iterator[str], constraints: Constraints) -> Iterator[str]:
        self.n_guesses += 1
        remained_words = list(constraints.filter_words(current_guesses))
        sorted_guesses = sort_by_info_gain(remained_words)
        if self.__might_fail(remained_words, sorted_guesses):
            sorted_guesses = sort_by_info_gain(self.allowed_guesses, remained_words)

        return iter(map(itemgetter(0), sorted_guesses))

    def __might_fail(self, remained_words: List[str], guesses_entropies: List[Tuple[str, float]]) -> bool:
        if len(remained_words) <= 2:
            return False

        if len(remained_words) <= (self.max_guesses - self.n_guesses + 1):
            return False

        return not has_information_gain(remained_words, guesses_entropies)
