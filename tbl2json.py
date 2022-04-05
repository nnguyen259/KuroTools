import json
import os
from pathlib import Path
from typing import Union

from lib.parser import process_data, readint


def parse(name: Union[str, bytes, os.PathLike]) -> None:
    filename = Path(name).stem
    filesize = os.path.getsize(name)
    with open(name, "rb") as tbl_file:
        tbl_file.read(4)
        header_count = readint(tbl_file, 4)
        headers = []
        tbl_data = []
        schema_list = []
        output = {}
        has_extra = False
        has_schema = True

        if os.path.exists(f"schemas/{filename}.json"):
            with open(f"schemas/{filename}.json") as header_file:
                schemas = json.load(header_file)
                schema_list = schemas["headers"]
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
                "unknown": unknown,
                "start": start_offset,
                "length": entry_length,
                "count": entry_count,
            }
            print(header)
            headers.append(header)
        output["headers"] = headers

        if header["start"] + header["length"] * header["count"] < filesize:
            has_extra = True

        for header in headers:
            tbl_file.seek(header["start"])
            header_data = {"name": header["name"], "data": []}
            if has_schema and header["name"] in schema_list:
                with open(f'schemas/headers/{header["name"]}.json') as schema_file:
                    schema: dict
                    schema = json.load(schema_file)
                for _ in range(header["count"]):
                    processed = 0
                    data = {}
                    for key, datatype in schema.items():
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
        output["data"] = tbl_data

        if has_extra and not has_schema:
            hex_text = tbl_file.read().hex()
            hex_text = " ".join(
                hex_text[j : j + 2] for j in range(0, len(hex_text), 2)
            ).upper()
            output["data_dump"] = hex_text

        with open(f"{filename}.json", "w", encoding="utf-8") as output_file:
            json.dump(output, output_file, ensure_ascii=False, indent="\t")


if __name__ == "__main__":
    parse("tbl_files/t_skill.tbl")
