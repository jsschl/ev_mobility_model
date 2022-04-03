import random
from variables import *


def generate_int_from_cumulative_distribution(
        cumulative_distribution: List[confloat(ge=0.0)],
) -> int:
    r = random.random()
    i = 0
    for value in cumulative_distribution:
        if r <= value:
            return i
        else:
            i += 1
    return len(cumulative_distribution) - 1


def get_purposes(purpose_chain: List[Purpose], index: int, last: bool):
    purpose = purpose_chain[index]
    if last:
        next_purpose = Purpose.UNKNOWN
    else:
        next_purpose = purpose_chain[index+1]
    return purpose, next_purpose


def stringify(number: conint(ge=0, le=99)) -> str:
    return f"{number:02d}"


