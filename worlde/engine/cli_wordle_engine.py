from typing import List

from engine import WordleEngine, GuessFeedback, WordLettersAnnotations


def map_annotations(input: List[int]) -> List[WordLettersAnnotations]:
    return [WordLettersAnnotations(i) for i in input]


class CliWordleEngine(WordleEngine):

    def guess(self, word: str) -> GuessFeedback:
        print("Insert word annotations: [0] for NOT-EXIST, [1] for WRONG-POSITION, and [2] for EXACT-POSITION ")
        raw_annotations = list(map(int, input()))
        annotations = map_annotations(raw_annotations)
        return GuessFeedback(word, annotations)
