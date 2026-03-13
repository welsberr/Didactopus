from dataclasses import dataclass


@dataclass
class RubricScore:
    correctness: float
    clarity: float
    justification: float
    transfer: float

    def mean(self) -> float:
        return (self.correctness + self.clarity + self.justification + self.transfer) / 4.0


def score_simple_rubric(
    correctness: float,
    clarity: float,
    justification: float,
    transfer: float,
) -> RubricScore:
    return RubricScore(
        correctness=correctness,
        clarity=clarity,
        justification=justification,
        transfer=transfer,
    )
