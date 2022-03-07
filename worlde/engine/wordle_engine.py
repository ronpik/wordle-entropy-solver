from typing import NamedTuple, List, TypeVar, Generic

import abc
from enum import Enum


class WordLettersAnnotations(Enum):
    EXACT_POS = 2
    FALSE_POS = 1
    FALSE_LETTER = 0


class GuessFeedback(NamedTuple):
    word: str
    labels: List[WordLettersAnnotations]

    def is_solved(self) -> bool:
        return all(label is WordLettersAnnotations.EXACT_POS for label in self.labels)

    @staticmethod
    def create_solved_feedback(target: str):
        return GuessFeedback(
            target,
            [WordLettersAnnotations.EXACT_POS for _ in range(len(target))]
        )


class WordleSessionEngine(abc.ABC):
    @abc.abstractmethod
    def guess(self, word: str) -> GuessFeedback:
        pass

    @abc.abstractmethod
    def is_solved(self) -> bool:
        pass


T = TypeVar("T", bound=WordleSessionEngine)


class WordleEngine(Generic[T], abc.ABC):

    @abc.abstractmethod
    def new_session(self) -> T:
        pass


