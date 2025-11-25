from typing import Generator, Sequence, TypeVar

T = TypeVar("T")
def distinct_pairs(seq : Sequence[T]) -> Generator[tuple[T, T]]:
    for i in range(len(seq)):
        for j in range(i+1, len(seq)):
            yield (seq[i], seq[j])
