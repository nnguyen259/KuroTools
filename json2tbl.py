import json
import os
from pathlib import Path
from typing import Union
import argparse
from lib.packer import pack_data, writehex, writeint, writetext
from lib.parser import get_size_from_schema
from lib.crc32 import compute_crc32


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Compiles a json file into tbl."
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version=f"{parser.prog} version 0.0"
    )
    parser.add_argument('file')
    return parser


def pack(name: Union[str, bytes, os.PathLike]) -> None:
    filename = Path(name).stem
    with open(name, "r", encoding="utf-8") as inputfile:
        data = json.load(inputfile)
    
    current_addr = 8 + len(data["headers"]) * 0x50

    for i, header in enumerate(data["headers"]):
        all_header_data = data["data"][i]["data"]
        header["count"] = len(all_header_data)

        if "schema" not in header or header["schema"] == "data_schema":
            # Hex dump mode (no real schema)
            if len(all_header_data) > 0:
                header["length"] = len(bytes.fromhex(all_header_data[0]["data"]))
            else:
                header["length"] = 0
            schema_content = {"data": "data"}
        else:
            # New format: header["schema"] = game name (e.g., "Sora1")
            schema_game = header["schema"]
            schema_file_path = f'schemas/headers/{header["name"]}.json'
            
            if not os.path.exists(schema_file_path):
                raise FileNotFoundError(f"Schema file not found: {schema_file_path}")

            with open(schema_file_path, "r", encoding="utf-8") as schema_file:
                schemas = json.load(schema_file)

            found_schema_name = None
            found_schema_data = None

            # First pass: try to match by "game" and length
            for sch_name, sch_data in schemas.items():
                if not isinstance(sch_data, dict) or "schema" not in sch_data:
                    continue
                if sch_data.get("game") == schema_game:
                    try:
                        computed_size = get_size_from_schema(sch_data)
                    except Exception as e:
                        print(f"Warning: failed to compute size for schema {sch_name}: {e}")
                        continue
                    if "length" in header:
                        if computed_size == header["length"]:
                            found_schema_name = sch_name
                            found_schema_data = sch_data
                            break
                    else:
                        found_schema_name = sch_name
                        found_schema_data = sch_data
                        header["length"] = computed_size
                        break

            # Fallback: if not found by game, try to match by length only
            if found_schema_data is None and "length" in header:
                expected_length = header["length"]
                for sch_name, sch_data in schemas.items():
                    if not isinstance(sch_data, dict) or "schema" not in sch_data:
                        continue
                    try:
                        if get_size_from_schema(sch_data) == expected_length:
                            found_schema_name = sch_name
                            found_schema_data = sch_data
                            break
                    except Exception:
                        continue

            if found_schema_data is None:
                raise ValueError(
                    f"Could not find a valid schema for header '{header['name']}' "
                    f"with game='{schema_game}' and length={header.get('length')}."
                )

            schema_content = found_schema_data["schema"]

        header["start"] = current_addr
        current_addr += header["length"] * header["count"]
        header["schema"] = schema_content  # Store actual schema dict for packing


    # Write TBL file
    with open(f"{filename}.tbl", "w+b") as outputfile:
        outputfile.write(b"#TBL")
        writeint(outputfile, len(data["headers"]), 4)
        
        for header in data["headers"]:
            writetext(outputfile, header["name"], padding=64)
            writeint(outputfile, compute_crc32(header["name"]), 4)
            writeint(outputfile, header["start"], 4)
            writeint(outputfile, header["length"], 4)
            writeint(outputfile, header["count"], 4)

        extra_data_idx = current_addr

        for i, header in enumerate(data["headers"]):
            all_header_data = data["data"][i]["data"]
            schema = header["schema"]
            for header_data in all_header_data:
                offsets = {}
                for key, datatype in schema.items():
                    offsets[key] = outputfile.tell()
                    key_data = header_data[key]
                    extra_data_idx = pack_data(
                        outputfile, datatype, key_data, extra_data_idx
                    )

        if "data_dump" in data:
            writehex(outputfile, data["data_dump"])


def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()
    if not args.file:
        raise Exception("json2tbl needs a json to compile!")
    else:
        pack(args.file)


if __name__ == "__main__":
    main()