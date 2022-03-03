from collections import Counter
from typing import List, Iterable, NamedTuple

import numpy as np

from worlde.letters_stats import get_sorted_words
from worlde.utils import load_wordslist, WordLettersAnnotations
from worlde.wordle_solver import Constraints


class MaxTriesExceededError(Exception):
    def __init__(self):
        super(self, MaxTriesExceededError).__init__("You've exceeded the maximal number of tries")


class GuessFeedback(NamedTuple):
    word: str
    target: str
    labels: List[WordLettersAnnotations]
    is_solved: bool

    @staticmethod
    def create_solved_feedback(target: str):
        return GuessFeedback(
            target,
            target,
            [WordLettersAnnotations.EXACT_POS for _ in range(len(target))],
            True
        )

    @staticmethod
    def create_feedback(word: str, target: str) -> 'GuessFeedback':
        if word == target:
            return GuessFeedback.create_solved_feedback(target)

        letters_counts = Counter(target)
        labels: List[WordLettersAnnotations] = [None for _ in range(len(target))]

        for index, letter in enumerate(word):
            if letter == target[index]:
                labels[index] = WordLettersAnnotations.EXACT_POS
                letters_counts[letter] -= 1

        for index, letter in enumerate(word):
            if labels[index] is not None:
                continue

            if letters_counts[letter] > 0:
                labels[index] = WordLettersAnnotations.FALSE_POS
                letters_counts[letter] -= 1

        for i in range(len(labels)):
            if labels[i] is None:
                labels[i] = WordLettersAnnotations.FALSE_LETTER

        return GuessFeedback(word, target, labels, False)


class WordleEngine:

    def __init__(self, possible_answers: List[str], allowed_guesses: List[str], max_tries: int = 6,
                 random_seed: int = 1919):
        self.possible_answers = possible_answers
        self.allowed_guesses = allowed_guesses
        self.max_tries = max_tries

        self.rng = np.random.default_rng(seed=random_seed)
        self.answers_indices = list(range(len(self.possible_answers)))
        self.rng.shuffle(self.answers_indices)
        self.__answers_indices = iter(self.answers_indices)

        self.__next_target: int = None
        self.__target: str = None

        self.__n_tries: int = 0
        self.guesses: List[str] = []

    @property
    def target(self):
        return self.__target

    def new_session(self):
        self.__n_tries = 0
        self.guesses = []
        self.__target = self.possible_answers[self.__next_target]
        self.__next_target: str = None

    def has_next_word(self):
        try:
            self.__next_target = self.__next_answer_word()
            return True
        except StopIteration:
            return False

    def __next_answer_word(self) -> str:
        return next(self.__answers_indices)

    def has_more_guess(self) -> bool:
        return self.__n_tries < self.max_tries

    def guess(self, word: str) -> GuessFeedback:
        assert self.__n_tries < self.max_tries
        self.__n_tries += 1
        self.guesses.append(word)
        return GuessFeedback.create_feedback(word, self.__target)
