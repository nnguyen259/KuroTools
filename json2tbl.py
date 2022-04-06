import json
import os
from pathlib import Path
from typing import Union

from lib.packer import pack_data, writehex, writeint, writetext


def pack(name: Union[str, bytes, os.PathLike]) -> None:
    filename = Path(name).stem
    with open(name, "r", encoding="utf-8") as inputfile:
        data = json.load(inputfile)

    with open(f"{filename}.tbl", "wb") as outputfile:
        outputfile.write(b"#TBL")
        writeint(outputfile, len(data["headers"]), 4)
        for header in data["headers"]:
            writetext(outputfile, header["name"], padding=64)
            writehex(outputfile, header["hash"])
            writeint(outputfile, header["start"], 4)
            writeint(outputfile, header["length"], 4)
            writeint(outputfile, header["count"], 4)

        extra_data_idx = header["start"] + header["length"] * header["count"]

        for i, header in enumerate(data["headers"]):
            if os.path.exists(f'schemas/headers/{header["name"]}.json'):
                with open(
                    f'schemas/headers/{header["name"]}.json', "r", encoding="utf-8"
                ) as schema_file:
                    schema: dict = json.load(schema_file)
            else:
                schema = {"data": "data"}
            all_header_data = data["data"][i]["data"]
            for header_data in all_header_data:
                header_data: dict
                for key, datatype in schema.items():
                    key_data = header_data[key]
                    extra_data_idx = pack_data(
                        outputfile, datatype, key_data, extra_data_idx
                    )

        if "data_dump" in data:
            writehex(outputfile, data["data_dump"])


if __name__ == "__main__":
    pack("t_place.json")
