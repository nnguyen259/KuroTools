from io import BufferedReader
import struct
from typing import Any, Literal, Tuple


def readint(stream: BufferedReader, size: int, endian: Literal['little', 'big'] = 'little', signed: bool = False) -> int:
    return int.from_bytes(stream.read(size), byteorder=endian, signed=signed)


def readfloat(stream: BufferedReader) -> float:
    return struct.unpack('f', stream.read(4))[0]


def readtext(stream: BufferedReader, encoding: str = 'utf-8', raw: bool = False) -> str | bytes:
    output = b''
    char = stream.read(1)
    while char != b'\0':
        output += char
        char = stream.read(1)

    if raw:
        return output
    else:
        return output.decode(encoding)


def readtextoffset(stream: BufferedReader, offset: int, encoding: str = 'utf-8') -> str:
    return_offset = stream.tell()
    stream.seek(offset)
    output = readtext(stream, raw=True)
    stream.seek(return_offset)
    return output.decode(encoding)


def process_data(stream: BufferedReader, datatype: str | dict, max_length: int) -> Tuple[Any, int]:
    processed = 0
    if isinstance(datatype, dict):
        data = []
        for _ in range(int(datatype['size'])):
            inner_data = {}
            for key, value in datatype['schema'].items():
                inner_value, data_processed = process_data(
                    stream, value, max_length - processed)
                inner_data[key] = inner_value
                processed += data_processed
            data.append(inner_data)
    elif datatype == 'byte':
        data = readint(stream, 1, signed=True)
        processed += 1
    elif datatype == 'ubyte':
        data = readint(stream, 1)
        processed += 1
    elif datatype == 'short':
        data = readint(stream, 2, signed=True)
        processed += 2
    elif datatype == 'ushort':
        data = readint(stream, 2)
        processed += 2
    elif datatype == 'int':
        data = readint(stream, 4, signed=True)
        processed += 4
    elif datatype == 'uint':
        data = readint(stream, 4)
        processed += 4
    elif datatype == 'long':
        data = readint(stream, 8, signed=True)
        processed += 8
    elif datatype == 'ulong':
        data = readint(stream, 8)
        processed += 8
    elif datatype == 'float':
        data = readfloat(stream)
        processed += 4
    elif datatype == 'toffset':
        data = readtextoffset(
            stream,
            readint(stream, 8)
        )
        processed += 8
    elif datatype.startswith('data'):
        if len(datatype) <= 4:
            hex_text = stream.read(max_length - processed).hex()
        else:
            length = int(datatype[4:])
            hex_text = stream.read(length).hex()
            processed += length
        hex_text = ' '.join(hex_text[j:j+2]
                            for j in range(0, len(hex_text), 2)).upper()
        data = hex_text
    else:
        raise Exception(
            f'Unknown data type {datatype}')

    return (data, processed)
