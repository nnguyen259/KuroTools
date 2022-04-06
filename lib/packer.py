from io import BufferedReader
import struct
from typing import Literal, Tuple, Union


def writeint(
    stream: BufferedReader,
    value: int,
    size: int,
    endian: Literal["little", "big"] = "little",
    signed: bool = False,
) -> int:
    return stream.write(value.to_bytes(size, endian, signed=signed))


def writefloat(stream: BufferedReader, value: float) -> int:
    return stream.write(struct.pack("<f", value))


def writetext(
    stream: BufferedReader,
    text: str,
    encoding: str = "utf-8",
    padding: Union[None, int] = None,
) -> Tuple[int, bytes]:
    output = text.encode(encoding) + b"\0"
    if padding is not None:
        while len(output) < padding:
            output += b"\0"
    return stream.write(output)


def writetextoffset(
    stream: BufferedReader, text: str, offset: int, encoding: str = "utf-8"
) -> int:
    return_offset = stream.tell()
    stream.seek(offset)
    written_length = writetext(stream, text, encoding=encoding)
    stream.seek(return_offset)
    return written_length


def writehex(stream: BufferedReader, hexstring: str) -> int:
    return stream.write(bytes.fromhex(hexstring))


def pack_number(
    stream: BufferedReader, datatype: str, data: int | float, signed: bool = False
) -> int:
    int_size = {"byte": 1, "short": 2, "int": 4, "long": 8}
    if datatype in int_size:
        return writeint(stream, data, int_size[datatype], signed=signed)
    else:
        return writefloat(stream, data)


def pack_data(
    stream: BufferedReader,
    datatype: str | dict,
    data: int | str | float,
    extra_data_idx: int,
):
    if isinstance(datatype, dict):
        schema: dict = datatype["schema"]
        for i in range(datatype["size"]):
            for key, sub_datatype in schema.items():
                key_data = data[i][key]
                extra_data_idx = pack_data(
                    stream, sub_datatype, key_data, extra_data_idx
                )
    elif datatype.startswith("data"):
        writehex(stream, data)
    elif datatype.startswith("u"):
        pack_number(stream, datatype[1:], data, True)
    elif datatype in ["byte", "short", "int", "long", "float"]:
        pack_number(stream, datatype, data, False)
    elif datatype == "toffset":
        writeint(stream, extra_data_idx, 8)
        extra_data_idx += writetextoffset(stream, data, extra_data_idx)
    return extra_data_idx
