import json
import math
from collections import Counter, defaultdict
from operator import itemgetter
from typing import Iterable, NamedTuple, Dict, List, Tuple, Sequence

import numpy as np
from tqdm.auto import tqdm


from worlde.utils import load_words, load_wordslist, load_freqs


class LetterStats(NamedTuple):
    occur_prob: List[float]
    position_probs: List[float]

    @staticmethod
    def from_counts(position_counts: Sequence[int], repeat_counts: Sequence[int], words_count: int) -> 'LetterStats':
        occur_count = repeat_counts[0]
        return LetterStats(
            [count / words_count for count in repeat_counts],
            [count / occur_count for count in position_counts]
        )


def compute_letters_stats(words: List[str], weights: Dict[str, float] = None) -> Dict[str, LetterStats]:
    weights = weights or {}
    words_count = 0
    letters_position_counts: Dict[str, List[int]] = {}
    letters_repeat_counts: Dict[str, List[int]] = {}
    all_letters = set(c for word in words for c in word)
    for letter in all_letters:
        letters_position_counts[letter] = [0 for _ in range(5)]
        letters_repeat_counts[letter] = [0 for _ in range(3)]

    for word in words:
        weight = weights.get(word, 1)
        words_count += weight
        letters_counter = Counter()
        for pos, letter in enumerate(word):
            # count this letter in the specific position, independently
            letters_position_counts[letter][pos] += weight
            # count with considering letter repetitions
            count = letters_counter[letter]
            letters_repeat_counts[letter][count] += weight
            letters_counter[letter] += 1

    letters_stats = {
        letter: LetterStats.from_counts(letters_position_counts[letter], letters_repeat_counts[letter], words_count)
        for letter in all_letters
    }
    return letters_stats


def compute_match_log_prob(word: str, letter_stats: Dict[str, LetterStats]) -> float:
    log_prob = 0
    for i, letter in enumerate(word):
        occur_log_prob, position_log_prob = letter_stats[letter]
        log_prob += occur_log_prob + position_log_prob[i]

    return log_prob


def compute_entropy(*probabilities: float) -> float:
    entropy = 0
    for p in probabilities:
        if (p == 0): continue
        if (p < 0): print(p)
        entropy += p * np.log2(p)

    return -entropy


def compute_word_letter_entropy(letter: str, position: int, repeat: int, letters_stats: Dict[str, LetterStats]) -> float:
    stats =  letters_stats.get(letter)
    if stats is None:
        return 0

    (repeat_probs, position_probs) = stats
    position_prob = position_probs[position]
    repeat_prob = repeat_probs[repeat]
    exact_prob = repeat_probs[0] * position_prob
    other_pos_prob = repeat_prob - repeat_prob * position_prob
    not_exist_prob = 1 - repeat_probs[repeat]
    return compute_entropy(exact_prob, other_pos_prob, not_exist_prob)


def compute_word_entropy_sum(word: str, letters_stats: Dict[str, LetterStats]) -> float:
    letters_counter = Counter()
    entropy_sum = 0
    for index, letter in enumerate(word):
        entropy_sum += compute_word_letter_entropy(letter, index, letters_counter[letter], letters_stats)
        letters_counter[letter] += 1

    return entropy_sum


def get_sorted_words(allowed_words: List[str], target_words: List[str] = None, weights: Dict[str, float] = None) -> List[Tuple[str, float]]:
    weights = weights or {}
    target_words = target_words or allowed_words
    letters_stats = compute_letters_stats(target_words, weights)
    words_log_prob = [(word, compute_word_entropy_sum(word, letters_stats)) for word in allowed_words]
    sorted_words = sorted(words_log_prob, key=itemgetter(1), reverse=True)
    return sorted_words


def load_word_probs(path: str) -> Iterable[Tuple[str, List[float]]]:
    with open(path, 'r') as f:
        for line in f:
            line_split = line.strip().split(" ")
            word = line_split[0]
            probs = list(map(float, line_split[1:]))
            yield word, probs


def load_word_entropies(word_probs_path: str) -> List[Tuple[str, float]]:
    word_entropies = []
    for word, probs in load_word_probs(word_probs_path):
        entropy = compute_entropy(*probs)
        word_entropies.append((word, entropy))

    return sorted(word_entropies, key=itemgetter(1), reverse=True)



if __name__ == "__main__":
    POSSIBLE_ANSWERS_FILEPATH = "possible_words.txt"
    ALLOWED_GUESSES_FILEPATH = "allowed_words.txt"
    WORDS_GUESS_PROBS_PATH = "wordle_words_freqs_full.txt"
    FREQS_PATH = "freq_map.json"

    possible_answers = set(load_wordslist(POSSIBLE_ANSWERS_FILEPATH))
    allowed_guesses = load_wordslist(ALLOWED_GUESSES_FILEPATH)
    freqs = load_freqs(FREQS_PATH)

    possible_ranks = []
    for i, (word, _) in enumerate(freqs):
        if word in possible_answers:
            possible_ranks.append(i)

    top_freqs = set(map(itemgetter(0), freqs[:len(possible_answers)]))

    overlap = top_freqs.intersection(possible_answers)
    outer_possible = possible_answers - overlap
    print(len(overlap, outer_possible))


    print(possible_ranks)


    all_allowed_words = load_wordslist(ALLOWED_GUESSES_FILEPATH)
    sorted_words = get_sorted_words(all_allowed_words)
    freqs = load_freqs(FREQS_PATH)
    word_entropies = load_word_entropies(WORDS_GUESS_PROBS_PATH)
    print(freqs[:10])
    print(sorted_words[:10])
    print(word_entropies[:10])

