from typing import List

from engine import WordleEngine, GuessFeedback, WordLettersAnnotations
from engine.wordle_engine import WordleSessionEngine


ANNOTATION_INPUT_TEXT =\
    "Insert word annotations: [0] for NOT-EXIST, [1] for WRONG-POSITION, and [2] for EXACT-POSITION "


def is_valid_annotations_input(raw_annotations: str, word_len: int) -> bool:
    if len(raw_annotations) != word_len:
        return False

    return all(map(str.isdigit, raw_annotations))


def map_annotations(input: List[int]) -> List[WordLettersAnnotations]:
    return [WordLettersAnnotations(i) for i in input]


def map_annotations_from_str(s: str) -> List[WordLettersAnnotations]:
    raw_annotations = list(map(int, s))
    return map_annotations(raw_annotations)


class CliWordleSession(WordleSessionEngine):

    def __init__(self, word_len: int):
        self.solved = False
        self.word_len = word_len

    def guess(self, word: str) -> GuessFeedback:
        raw_input = ""
        while not is_valid_annotations_input(raw_input, self.word_len):
            print(ANNOTATION_INPUT_TEXT)
            raw_input = input()

        annotations = map_annotations_from_str(raw_input)
        feedback = GuessFeedback(word, annotations)
        if feedback.is_solved():
            self.solved = True

        return feedback

    def is_solved(self) -> bool:
        return self.solved


class CliWordleEngine(WordleEngine[CliWordleSession]):

    def __init__(self, word_len: int = 5):
        self.word_len = word_len

    def new_session(self) -> CliWordleSession:
        return CliWordleSession(self.word_len)
