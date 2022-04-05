from io import BufferedReader
from typing import Literal, Tuple, Union


def writeint(
    stream: BufferedReader,
    value: int,
    size: int,
    endian: Literal["little", "big"] = "little",
    signed: bool = False,
) -> int:
    return stream.write(value.to_bytes(size, endian, signed=signed))


def writetext(
    stream: BufferedReader,
    text: str,
    encoding: str = "utf-8",
    padding: Union[None, int] = None,
) -> Tuple[int, int, bytes]:
    output = text.encode(encoding) + b"\0"
    if padding is not None:
        while len(output) < padding:
            output += b"\0"
    return stream.write(output), len(output), output


def writehex(stream: BufferedReader, hexstring: str) -> int:
    return stream.write(bytes.fromhex(hexstring))
