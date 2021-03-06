import json
import os
from pathlib import Path
from typing import Union
import argparse
from lib.packer import pack_data, writehex, writeint, writetext

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Compiles a json file into tbl."
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version = f"{parser.prog} version 0.0"
    )
    parser.add_argument('file')
    return parser

def pack(name: Union[str, bytes, os.PathLike]) -> None:
    filename = Path(name).stem
    with open(name, "r", encoding="utf-8") as inputfile:
        data = json.load(inputfile)
    with open(f"{filename}.tbl", "w+b") as outputfile:
        outputfile.write(b"#TBL")
        writeint(outputfile, len(data["headers"]), 4)
        for header in data["headers"]:
            writetext(outputfile, header["name"], padding=64)
            writehex(outputfile, header["hash"])
            writeint(outputfile, header["start"], 4)  #This should be recomputed
            writeint(outputfile, header["length"], 4) #Same here
            writeint(outputfile, header["count"], 4)  #Same here

        extra_data_idx = header["start"] + header["length"] * header["count"]

        for i, header in enumerate(data["headers"]):
            if os.path.exists(f'schemas/headers/{header["name"]}.json'):
                with open(
                    f'schemas/headers/{header["name"]}.json', "r", encoding="utf-8"
                ) as schema_file:
                    schemas: dict
                    schemas = json.load(schema_file)
            else:
                schemas = ("data_schema",{"game":"???","schema":{"data": "data"}})

            all_header_data = data["data"][i]["data"]
            for header_data in all_header_data:
                #for each header data, we need to find the corresponding schema version
                if "schema" not in header.keys():
                    #means there was no schema, we will have to dump the whole hex string
                    schema = schemas[1]["schema"]
                else:
                    schema = schemas[header["schema"]]["schema"]



                header_data: dict
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
