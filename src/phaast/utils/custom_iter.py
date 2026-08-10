from typing import Generator, Sequence

def distinct_pairs[T](seq : Sequence[T]) -> Generator[tuple[T, T]]:
    """
    Iter over distinct pairs of all elements of seq
    (If seq has duplicate elements, the pairs might also contain redundancy)
    """
    for i in range(len(seq)):
        for j in range(i+1, len(seq)):
            yield (seq[i], seq[j])
