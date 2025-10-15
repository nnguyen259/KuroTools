import json
import os
import re
from pathlib import Path
from typing import Union

import argparse

from lib.parser import process_data, readint, get_size_from_schema
from processcle import processCLE


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Decompiles a tbl file into json."
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version=f"{parser.prog} version 0.0"
    )
    parser.add_argument(
        "-g", "--game",
        help="Specify the game name to select a matching schema (e.g., 'Sora1')."
    )
    parser.add_argument('file')
    return parser


def parse(name: Union[str, bytes, os.PathLike], game: Union[str, None] = None) -> None:
    true_filename = Path(name).stem
    filename = re.sub(r"\d", "%d", true_filename)
    filesize = os.path.getsize(name)
    with open(name, "rb") as tbl_file:
        magic = tbl_file.read(4)
        if magic != b"#TBL":
            with open(name, mode='rb') as encrypted_file: 
                fileContent = encrypted_file.read()
            decrypted_file = processCLE(fileContent)
            with open(name, "w+b") as outputfile:
                outputfile.write(decrypted_file)
            filesize = os.path.getsize(name)
            tbl_file = open(name, "rb")
            tbl_file.seek(4)

        header_count = readint(tbl_file, 4)
        headers = []
        tbl_data = []
        schema_list = []
        output = {}
        has_extra = False
        has_schema = True

        if os.path.exists(f"schemas/{filename}.json"):
            with open(f"schemas/{filename}.json") as header_file:
                schemas_meta = json.load(header_file)
                schema_list = schemas_meta["headers"]
        else:
            has_schema = False

        for _ in range(header_count):
            header_name = tbl_file.read(64).replace(b"\0", b"").decode("utf-8")
            unknown = tbl_file.read(4).hex()
            start_offset = readint(tbl_file, 4)
            entry_length = readint(tbl_file, 4)
            entry_count = readint(tbl_file, 4)
            header = {
                "name": header_name,
                "length": entry_length,
                "count": entry_count,
                "start": start_offset
            }
            headers.append(header)
        output["headers"] = headers

        if headers and headers[-1]["start"] + headers[-1]["length"] * headers[-1]["count"] < filesize:
            has_extra = True

        for header in headers:
            tbl_file.seek(header["start"])
            header_data = {"name": header["name"], "data": []}
            if has_schema and header["name"] in schema_list:
                with open(f'schemas/headers/{header["name"]}.json') as schema_file:
                    schemas: dict = json.load(schema_file)

                actual_entry_size = header["length"]
                correct_schema = None

                if game is not None:
                    
                    for name, sch in schemas.items():
                        if sch.get("game") == game and get_size_from_schema(sch) == actual_entry_size:
                            correct_schema = (name, sch)
                            break
                    
                    if correct_schema is None:
                        for name, sch in schemas.items():
                            if get_size_from_schema(sch) == actual_entry_size:
                                correct_schema = (name, sch)
                                break
                else:
                    
                    for name, sch in schemas.items():
                        if get_size_from_schema(sch) == actual_entry_size:
                            correct_schema = (name, sch)
                            break

                
                schema_dict = correct_schema[1]
                header["schema"] = schema_dict.get("game", correct_schema[0])

                for _ in range(header["count"]):
                    processed = 0
                    data = {}
                    for key, datatype in correct_schema[1]["schema"].items():
                        if isinstance(datatype, str) and datatype.startswith("comp:"):
                            datatype = correct_schema[1]["schema"][datatype[5:]]
                        value, processed_data = process_data(
                            tbl_file, datatype, header["length"] - processed
                        )
                        data[key] = value
                        processed += processed_data
                    header_data["data"].append(data)
            else:
                for _ in range(header["count"]):
                    data = {}
                    hex_text = tbl_file.read(header["length"]).hex()
                    hex_text = " ".join(
                        hex_text[j : j + 2] for j in range(0, len(hex_text), 2)
                    ).upper()
                    data["data"] = hex_text
                    header_data["data"].append(data)
            tbl_data.append(header_data)
            print(header)  

        output["data"] = tbl_data

        if has_extra and not has_schema:
            hex_text = tbl_file.read().hex()
            hex_text = " ".join(
                hex_text[j : j + 2] for j in range(0, len(hex_text), 2)
            ).upper()
            output["data_dump"] = hex_text

        for header in output["headers"]:
            header.pop("count", None)
            header.pop("length", None)
            header.pop("start", None)

        with open(f"{true_filename}.json", "w", encoding="utf-8") as output_file:
            json.dump(output, output_file, ensure_ascii=False, indent="\t")


def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()
    if not args.file:
        raise Exception("tbl2json needs a table to decompile!")
    else:
        parse(args.file, game=args.game)


if __name__ == "__main__":
    main()