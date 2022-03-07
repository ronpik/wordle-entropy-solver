import json
from enum import Enum
from operator import itemgetter
from typing import List, Iterable, Tuple, Dict

import numpy as np


def load_words(path: str) -> Iterable[str]:
    with open(path, 'r') as f:
        words = map(str.strip, f)
        words = filter(lambda w: len(w) == 5, words)
        words = filter(lambda w: all(map(str.isalpha, w)), words)
        yield from words


def load_wordslist(path: str) -> List[str]:
    return list(load_words(path))


def load_freqs(path: str) -> List[Tuple[str, float]]:
    with open(path, 'r') as f:
        return sorted(json.load(f).items(), key=itemgetter(1), reverse=True)


def compute_word_weights_from_freqs(words_freqs: List[Tuple[str, float]]) -> Dict[str, float]:
    max_rank = len(words_freqs)

    def compute_weight(rank: int) -> float:
        return (1 - (rank / max_rank)) ** 2

    return {word: compute_weight(i) for i, (word, _) in enumerate(words_freqs)}



def compute_word_weights_from_freqs1(words_freqs: List[Tuple[str, float]]) -> Dict[str, float]:
    min_freq = words_freqs[0][1]
    max_freq = min_freq
    for _, freq in words_freqs:
        if freq > 0:
            if freq < min_freq:
                min_freq = freq
            elif freq > max_freq:
                max_freq = freq

    # compute inverse of min-max normalization
    max_log_freq = -np.log(min_freq) ** 2
    min_log_freq = -np.log(max_freq) ** 2
    norm_factor = max_log_freq - min_log_freq

    def compute_weight(freq: float) -> float:
        return 1 - ((-np.log(freq) ** 2) - min_log_freq) / norm_factor

    return {word: (compute_weight(freq) if freq > 0 else 0) for word, freq in words_freqs}

