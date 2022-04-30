from math import log2
from operator import itemgetter
from typing import Iterator, List, Tuple

from engine.wordle_engine import WordleSessionEngine
from solver.constraints import Constraints
from solver.entropy.letters_stats import sort_by_info_gain
from solver.wordle_solver import WordleSolver

DEFAULT_MIN_INFORMATION_GAIN_DIFF = 0.5


def max_entropy(n: int) -> float:
    return -log2(1. / n)


def binary_entropy(split_size: int, total: int) -> float:
    split_prob = float(split_size) / total
    return -((split_prob * log2(split_prob)) + ((1 - split_prob) * log2(1 - split_prob)))


def has_information_gain(
        remained_words: List[str],
        guesses_entropies: List[Tuple[str, float]],
        min_gain_diff: float
) -> bool:
    remained_words_set = set(remained_words)
    min_entropy = min(map(itemgetter(1), filter(lambda t: t[0] in remained_words_set, guesses_entropies)))
    max_entropy = max(map(itemgetter(1), filter(lambda t: t[0] in remained_words_set, guesses_entropies)))
    return (max_entropy - min_entropy) > min_gain_diff


class SimplifiedEntropySolver(WordleSolver):

    def __init__(self, allowed_guesses: List[str], max_guesses: int):
        self.allowed_guesses = allowed_guesses
        self.n_guesses = 0
        self.max_guesses = max_guesses
        self.initial_sorted_guesses = sort_by_info_gain(allowed_guesses)

    def reset(self):
        self.n_guesses = 0

    def solve(self, session: WordleSessionEngine) -> int:
        self.reset()
        return super().solve(session)

    def iter_first_guesses(self) -> Iterator[str]:
        self.n_guesses = 1
        return iter(map(itemgetter(0), self.initial_sorted_guesses))

    def iter_guesses(self, guesses_iter: Iterator[str], constraints: Constraints) -> Iterator[str]:
        self.n_guesses += 1
        guesses_iter = list(constraints.filter_words(guesses_iter))
        sorted_guesses = sort_by_info_gain(guesses_iter)
        if self.__might_fail(guesses_iter, sorted_guesses):
            print("*", end="")
            sorted_guesses = sort_by_info_gain(self.allowed_guesses, guesses_iter)

        return iter(map(itemgetter(0), sorted_guesses))

    def __might_fail(self, remained_words: List[str], guesses_entropies: List[Tuple[str, float]]) -> bool:
        if len(remained_words) <= 2:
            return False

        if len(remained_words) <= (self.max_guesses - self.n_guesses + 1):
            return False

        return True

        # return guesses_entropies[0][1] < 1 or \
        #        (not has_information_gain(remained_words, guesses_entropies, DEFAULT_MIN_INFORMATION_GAIN_DIFF))
