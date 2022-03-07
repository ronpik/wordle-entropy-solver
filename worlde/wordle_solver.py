import random
from collections import Counter
from enum import Enum
from functools import partial
from itertools import starmap
from operator import itemgetter
from typing import Sequence, Callable, List, Tuple, NamedTuple, Iterable, Iterator, Any, TypeVar, Type

from solver.constraints import WordLettersAnnotations, Constraints
from solver.entropy.letters_stats import sort_by_info_gain
from utils import load_wordslist

T = TypeVar('T')





def load_words(path: str) -> List[str]:
        return sort_by_info_gain(load_wordslist(path))



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
        sorted_allowed_guesses = sort_by_info_gain(remained_words)
        # remained_words = get_sorted_words(list(constraints.filter_words(map(itemgetter(0), remained_words))))
        print(f"{len(remained_words)} words remained")
        print(remained_words[:10])

        remained_words = iter(remained_words)
        word = next(remained_words)
        print(f"Next word: {word}")

    print(f"Solved!! Daily word is: {word}")
