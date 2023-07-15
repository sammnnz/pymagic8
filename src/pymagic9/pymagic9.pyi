from types import CodeType, FrameType
from typing import Any, Callable, Generator, List, Optional, Sequence, Tuple, Union

__all__: List[str]

# noinspection SpellCheckingInspection
def _getframe(__depth: int) -> Optional[FrameType]: ...

# noinspection SpellCheckingInspection
getframe: Callable[[int],  Optional[FrameType]]

# noinspection SpellCheckingInspection
def isfunctionincallchain(o: Union[Callable[[Any], Any], CodeType], __depth: int = ...) -> bool: ...

# noinspection SpellCheckingInspection
def nameof(o: Any) -> Optional[str]: ...

_ArgVal = Optional[Union[int, str, Sequence[str], Tuple[Any, bool]]]
_Bytes = Union[bytes, bytearray]

# noinspection SpellCheckingInspection
def _get_argval(offset: int,
                op: int,
                arg: int,
                varnames: Tuple[_ArgVal] = ...,
                names: Tuple[_ArgVal] = ...,
                constants: Tuple[_ArgVal] = ...,
                cells: Tuple[_ArgVal] = ...) -> _ArgVal: ...

def _get_last_name(code: _Bytes, names: Tuple[str]) -> Optional[str]: ...

# noinspection SpellCheckingInspection
def _unpack_opargs(code: _Bytes) -> Generator[Tuple[int, int, Optional[int]], None, None]: ...