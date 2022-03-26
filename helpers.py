import random
from pydantic import confloat
from typing import Union


def generate_int_from_cumulative_distribution(
        cumulative_distribution: [confloat(ge=0.0)],
        seed: Union[int, None] = None
) -> int:
    if seed is not None:
        random.seed(seed)
    r = random.random()
    i = 0
    for value in cumulative_distribution:
        if r <= value:
            return i
        else:
            i += 1
    return len(cumulative_distribution) - 1


