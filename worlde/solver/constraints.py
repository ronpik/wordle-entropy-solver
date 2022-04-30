from collections import Counter
from enum import Enum
from functools import partial
from itertools import starmap
from operator import itemgetter
from typing import Sequence, Tuple, Callable, List, NamedTuple, Iterable, Iterator

from engine import WordLettersAnnotations


def make_constraints_must_exist(letters_min_count: Sequence[Tuple[str, int]]) -> Callable[[str], bool]:

    def constraint(word: str) -> bool:
        letters_counter = Counter(word)
        return all(starmap(lambda letter, min_count: letters_counter[letter] >= min_count, letters_min_count))

    return constraint


def make_constraints_must_not_exist(letters_max_count: Sequence[Tuple[str, int]]) -> Callable[[str], bool]:

    def constraint(word: str) -> bool:
        letters_counter = Counter(word)
        return all(starmap(lambda letter, max_count: letters_counter[letter] <= max_count, letters_max_count))

    return constraint


def make_constraints_in_position(letter_positions: List[Tuple[str, int]]) -> Callable[[str], bool]:

    def constraint(word: str) -> bool:
        for letter, position in letter_positions:
            if word[position] != letter:
                return False

        return True

    return constraint


def make_constraints_not_in_positions(letters_positions: List[Tuple[str, Sequence[int]]]) -> Callable[[str], bool]:

    def constraint(word: str) -> bool:
        for letter, positions in letters_positions:
            for position in positions:
                if word[position] == letter:
                    return False

        return True

    return constraint


def apply_constraints(word: str, constraints: List[Callable[[str], bool]]) -> bool:
    return all(map(lambda c: c(word), constraints))


class Constraints(NamedTuple):
    must_exist: List[Tuple[str, int]]
    must_not_exist: List[Tuple[str, int]]
    exact_positions: List[Tuple[str, int]]
    false_positions: List[Tuple[str, Sequence[int]]]

    def filter_words(self, words: Iterable[str]) -> Iterator[str]:
        constraints = [
            make_constraints_in_position(self.exact_positions),
            make_constraints_must_exist(self.must_exist),
            make_constraints_must_not_exist(self.must_not_exist),
            make_constraints_not_in_positions(self.false_positions)
        ]
        is_valid_word = partial(apply_constraints, constraints=constraints)
        yield from filter(is_valid_word, words)

    def update(self, word: str, annotations: List[WordLettersAnnotations]) -> 'Constraints':
        new_constraints = self.create(word, annotations)

        must_not_exist = self.must_not_exist + new_constraints.must_not_exist

        new_must_exists_letter_set = set(map(itemgetter(0), new_constraints.must_exist))
        relevant_current_must_exist = [(letter, min_count) for (letter, min_count) in self.must_exist
                                       if letter not in new_must_exists_letter_set]

        must_exist = relevant_current_must_exist + new_constraints.must_exist

        current_exact_positions_letter_set = set(map(itemgetter(0), self.exact_positions))
        exact_positions = self.exact_positions + [(letter, pos) for letter, pos in new_constraints.exact_positions
                                                  if letter not in current_exact_positions_letter_set]

        false_positions = {letter: list(positions) for letter, positions in self.false_positions}
        for (letter, positions) in new_constraints.false_positions:
            false_positions.setdefault(letter, []).extend(positions)

        return Constraints(
            must_exist,
            must_not_exist,
            exact_positions,
            list(false_positions.items())
        )

    @staticmethod
    def create_empty() -> 'Constraints':
        return Constraints([], [], [], [])

    @staticmethod
    def create(
            word: str,
            annotations: List[WordLettersAnnotations],
    ) -> 'Constraints':

        must_exist = Counter()
        must_not_exist = Counter()
        exact_positions = []
        false_positions = {}

        for index, letter in enumerate(word):
            annotation = annotations[index]
            if annotation == WordLettersAnnotations.FALSE_LETTER:
                must_not_exist[letter] += 1
                if must_exist[letter] >= 1:
                    false_positions.setdefault(letter, []).append(index)
            elif annotation == WordLettersAnnotations.FALSE_POS:
                false_positions.setdefault(letter, []).append(index)
                must_exist[letter] += 1
            elif annotation == WordLettersAnnotations.EXACT_POS:
                exact_positions.append((letter, index))
                must_exist[letter] += 1
            else:
                raise AssertionError(f"Unsupported annotation in index {index} for word {word}: {annotation}")

        letters_counts = Counter(word)
        must_not_exist = [(letter, letters_counts[letter] - false_count) for letter, false_count in must_not_exist.items()]

        return Constraints(
            list(must_exist.items()),
            must_not_exist,
            exact_positions,
            list(false_positions.items())
        )