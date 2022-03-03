import random
from collections import Counter
from enum import Enum
from functools import partial
from itertools import starmap
from operator import itemgetter
from typing import Sequence, Callable, List, Tuple, NamedTuple, Iterable, Iterator, Any, TypeVar, Type

from worlde.letters_stats import get_sorted_words
from worlde.utils import load_wordslist, WordLettersAnnotations


T = TypeVar('T')


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

        new_must_exists_letter_set = set(map(itemgetter(1), new_constraints.must_exist))
        relevant_current_must_exist = [(letter, min_count) for (letter, min_count) in self.must_exist
                                       if letter not in new_must_exists_letter_set]

        must_exist = relevant_current_must_exist + new_constraints.must_exist

        false_positions = {letter: list(positions) for letter, positions in self.false_positions}
        for (letter, positions) in new_constraints.false_positions:
            false_positions.setdefault(letter, []).extend(positions)

        return Constraints(
            must_exist,
            must_not_exist,
            new_constraints.exact_positions,
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


def map_annotations(input: List[int]) -> List[WordLettersAnnotations]:
    return [WordLettersAnnotations(i) for i in input]


def load_words(path: str) -> List[str]:
        return get_sorted_words(load_wordslist(path))


def sample_word(words: List[str]) -> str:
    index = random.randrange(0, len(words))
    return words[index]


def is_solved(annotations: List[WordLettersAnnotations]) -> bool:
    return all(map(lambda a: a is WordLettersAnnotations.EXACT_POS, annotations))


if __name__ == "__main__":
    words_path = "allowed_words.txt"
    all_words = load_words(words_path)
    print(f"Starting with {len(all_words)} possible words")
    remained_words = iter(all_words)

    word = next(remained_words)
    print(f"First word: {word}")
    constraints: Constraints = None
    while word:
        print("Insert word annotations: (3 to take the next word, 4 to insert word of your own")
        raw_annotations = list(map(int, input()))
        if raw_annotations[0] == 3:
            word = next(remained_words)
            print(f"Next word: {word}")
            continue
        if raw_annotations[0] == 4:
            print("Insert the word you've used:")
            word = input()
            continue

        annotations = map_annotations(raw_annotations)
        if is_solved(annotations):
            break

        constraints = Constraints.create(word, annotations)
        remained_words = list(constraints.filter_words(remained_words))
        sorted_allowed_guesses = get_sorted_words(remained_words)
        # remained_words = get_sorted_words(list(constraints.filter_words(map(itemgetter(0), remained_words))))
        print(f"{len(remained_words)} words remained")
        print(remained_words[:10])

        remained_words = iter(remained_words)
        word = next(remained_words)
        print(f"Next word: {word}")

    print(f"Solved!! Daily word is: {word}")
