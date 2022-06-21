from io import BufferedReader
import struct
from typing import Literal, Tuple, Union
import math

def writeint(
    stream: BufferedReader,
    value: int,
    size: int,
    endian: Literal["little", "big"] = "little",
    signed: bool = False,
) -> int:
    return stream.write(value.to_bytes(size, endian, signed=signed))

def writeintoffset(
    stream: BufferedReader,
    offset: int,
    value: int,
    size: int,
    endian: Literal["little", "big"] = "little",
    signed: bool = False,
) -> int:
    return_offset = stream.tell()
    stream.seek(offset)
    written_length = writeint(stream, value, size, endian, signed)
    stream.seek(return_offset)
    return written_length

    

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

	#I realized later that there was no padding in t_place, but I keep it as it might be useful (you can also remove it if you want)
    to_be_aligned = False
    if datatype.startswith("aligned_"):
        to_be_aligned = True
        datatype = datatype[8:]
        
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
    elif datatype.endswith(("byte", "short", "int", "long", "float")):
        pack_number(stream, datatype[1:], data, datatype.startswith("u"))
    elif datatype.startswith("toffset"):
        writeint(stream, extra_data_idx, 8)
        if datatype == "toffset":
            extra_data_idx += writetextoffset(stream, data, extra_data_idx)
        else:
            extra_data_idx += writetextoffset(
                stream, data, extra_data_idx, encoding=datatype[7:]
            )
    elif datatype == "u16array":
        writeint(stream, extra_data_idx, 8)
        
        writeint(stream, len(data), 4)
        for i_u16 in range(0, len(data)):
            writeintoffset(stream, extra_data_idx + 2 * i_u16, data[i_u16], 2)
        extra_data_idx = extra_data_idx + 2 * len(data)
        
    #padding zeros to match the original file (essentially as safety measure)    
    if (to_be_aligned):
        to_be_padded = math.ceil(extra_data_idx / 4) * 4 - extra_data_idx 
        writeintoffset(stream, extra_data_idx, 0, to_be_padded)
        extra_data_idx = extra_data_idx + to_be_padded
        
    return extra_data_idx
