from typing import List

from engine import WordleEngine, GuessFeedback, WordLettersAnnotations
from engine.wordle_engine import WordleSessionEngine, T


def map_annotations(input: List[int]) -> List[WordLettersAnnotations]:
    return [WordLettersAnnotations(i) for i in input]


class CliWordleSession(WordleSessionEngine):

    def __init__(self):
        self.solved = False

    def guess(self, word: str) -> GuessFeedback:
        print("Insert word annotations: [0] for NOT-EXIST, [1] for WRONG-POSITION, and [2] for EXACT-POSITION ")
        raw_annotations = list(map(int, input()))
        annotations = map_annotations(raw_annotations)
        feedback = GuessFeedback(word, annotations)
        if feedback.is_solved():
            self.solved = True

        return feedback

    def is_solved(self) -> bool:
        return self.solved


class CliWordleEngine(WordleEngine[CliWordleSession]):

    def new_session(self) -> CliWordleSession:
        return CliWordleSession()
