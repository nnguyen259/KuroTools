import json
import os
from io import BufferedReader
from pathlib import Path
import struct
from typing import Any, Tuple, Union


def readint(stream: BufferedReader, size: int, endian='little', signed=False) -> int:
    return int.from_bytes(stream.read(size), byteorder=endian, signed=signed)


def readfloat(stream: BufferedReader) -> float:
    return struct.unpack('f', stream.read(4))[0]


def readtext(stream: BufferedReader, encoding='utf-8', raw=False) -> str | bytes:
    output = b''
    char = stream.read(1)
    while char != b'\0':
        output += char
        char = stream.read(1)

    if raw:
        return output
    else:
        return output.decode(encoding)


def readtextoffset(stream: BufferedReader, offset: int, encoding='utf-8') -> str:
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


def parse(name: Union[str, bytes, os.PathLike]):
    filename = Path(name).stem
    filesize = os.path.getsize(name)
    with open(name, 'rb') as tbl_file:
        tbl_file.read(4)
        header_count = readint(tbl_file, 4)
        headers = []
        schema_list = []
        output = {}
        has_extra = False
        has_schema = True

        if os.path.exists(f'schemas/{filename}.json'):
            with open(f'schemas/{filename}.json') as header_file:
                schemas = json.load(header_file)
                schema_list = schemas['headers']
        else:
            has_schema = False

        for _ in range(header_count):
            header_name = tbl_file.read(64).replace(b'\0', b'').decode('utf-8')
            unknown = tbl_file.read(4).hex()
            start_offset = readint(tbl_file, 4)
            entry_length = readint(tbl_file, 4)
            entry_count = readint(tbl_file, 4)
            header = {
                'name': header_name,
                'unknown': unknown,
                'start': start_offset,
                'length': entry_length,
                'count': entry_count
            }
            print(header)
            headers.append(header)
        output['headers'] = headers

        if header['start'] + header['length'] * header['count'] < filesize:
            has_extra = True

        for header in headers:
            tbl_file.seek(header['start'])
            header_data = []
            if has_schema and header['name'] in schema_list:
                with open(f'schemas/headers/{header["name"]}.json') as schema_file:
                    schema: dict
                    schema = json.load(schema_file)
                for _ in range(header['count']):
                    processed = 0
                    data = {}
                    for key, datatype in schema.items():
                        value, processed_data = process_data(
                            tbl_file, datatype, header['length'] - processed)
                        data[key] = value
                        processed += processed_data
                    header_data.append(data)
            else:
                for _ in range(header['count']):
                    data = {}
                    hex_text = tbl_file.read(header['length']).hex()
                    hex_text = ' '.join(hex_text[j:j+2]
                                        for j in range(0, len(hex_text), 2)).upper()
                    data['data'] = hex_text
                    header_data.append(data)
            output[header['name']] = header_data

        if has_extra and not has_schema:
            hex_text = tbl_file.read().hex()
            hex_text = ' '.join(hex_text[j:j+2]
                                for j in range(0, len(hex_text), 2)).upper()
            output['data_dump'] = hex_text

        with open(f'{filename}.json', 'w', encoding='utf-8') as output_file:
            json.dump(output, output_file, ensure_ascii=False, indent='\t')


if __name__ == '__main__':
    parse('tbl_files/t_item.tbl')
