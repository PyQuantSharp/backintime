from typing import Generator, TypeVar


FloatGenerator = TypeVar(
    'FloatGenerator',
    bound=Generator[float, None, None])
