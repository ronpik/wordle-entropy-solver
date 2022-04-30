from collections import Counter
from typing import List, Iterable, NamedTuple, Union, Optional

import numpy as np

from engine.wordle_engine import GuessFeedback, WordleEngine, WordLettersAnnotations, WordleSessionEngine, T


class MaxTriesExceededError(Exception):
    def __init__(self, max_tries: int):
        super().__init__(f"You've exceeded the maximal number of tries: {max_tries}")


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

    return GuessFeedback(word, labels)


class PredefinedWordleSession(WordleSessionEngine):

    def __init__(self, target: str, max_tries: int = 6):
        self.__target: str = target
        self.max_tries = max_tries
        self.__n_tries: int = 0
        self.guesses: List[str] = []

        self.__solved = False
        self.__failed = False

    @property
    def target(self) -> Optional[str]:
        if not self.is_closed():
            return None

        return self.__target

    def giveup_and_get_target(self) -> str:
        self.give_up()
        return self.target

    def has_more_guess(self) -> bool:
        return self.__n_tries < self.max_tries

    def is_solved(self) -> bool:
        return self.__solved

    def is_failed(self) -> bool:
        return self.__failed

    def give_up(self) -> str:
        self.__failed = True
        return self.target

    def is_closed(self) -> bool:
        return self.is_solved() or self.is_failed()

    def guess(self, word: str) -> GuessFeedback:
        if self.__n_tries >= self.max_tries:
            raise MaxTriesExceededError(self.max_tries)

        self.__n_tries += 1
        self.guesses.append(word)
        feedback = create_feedback(word, self.__target)
        if (not self.__solved) and feedback.is_solved():
            self.__solved = True
        elif self.__n_tries == self.max_tries:
            self.__failed = True

        return feedback


class AutoWordleEngine(WordleEngine[PredefinedWordleSession]):

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

    def new_session(self) -> PredefinedWordleSession:
        target = self.possible_answers[self.__next_target]
        self.__next_target: str = None
        return PredefinedWordleSession(target, self.max_tries)

    def has_next_word(self):
        try:
            self.__next_target = self.__next_answer_word()
            return True
        except StopIteration:
            return False

    def __next_answer_word(self) -> str:
        return next(self.__answers_indices)
