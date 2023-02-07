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
        version = f"{parser.prog} version 0.0"
    )
    parser.add_argument('file')
    return parser

def pack(name: Union[str, bytes, os.PathLike]) -> None:
    filename = Path(name).stem
    with open(name, "r", encoding="utf-8") as inputfile:
        data = json.load(inputfile)
    
    #First, for each header we need to get the size of each entry and the number of entries so that each starting address can be computed
    #And for that we need to assign a schema to each header

    current_addr = 8 + len(data["headers"]) * 0x50

    for i, header in enumerate(data["headers"]):
        if os.path.exists(f'schemas/headers/{header["name"]}.json'):
                with open(
                    f'schemas/headers/{header["name"]}.json', "r", encoding="utf-8"
                ) as schema_file:
                    schemas: dict
                    schemas = json.load(schema_file)
        
        all_header_data = data["data"][i]["data"]
        header["count"] = len(all_header_data)
        #for each header data, we need to find the corresponding schema version
        if "schema" not in header.keys():
            #means there was no schema, we will have to dump the whole hex string
            #we get the size of each entry with the size of the first one
            if len(all_header_data) > 0:
                header["length"] = len(bytes.fromhex(all_header_data[0]["data"]))
            else:
                header["length"] = 0

            schema = ("data_schema",{"game":"???","schema":{"data": "data"}})
        else:
            header["length"] = get_size_from_schema(schemas[header["schema"]])
            schema = schemas[header["schema"]]["schema"]
        
        header["start"] = current_addr 
        current_addr = current_addr + header["length"] * header["count"]
        #Not the best thing to do, but here header["schema"] goes from the name of the schema (if it existed) to the actual schema data
        header["schema"] = schema




    with open(f"{filename}.tbl", "w+b") as outputfile:
        outputfile.write(b"#TBL")
        writeint(outputfile, len(data["headers"]), 4)
        for header in data["headers"]:
            writetext(outputfile, header["name"], padding=64)
            writeint(outputfile, compute_crc32(header["name"]),4)
            writeint(outputfile, header["start"], 4)  #This should be recomputed
            writeint(outputfile, header["length"], 4) #Same here
            writeint(outputfile, header["count"], 4)  #Same here

        extra_data_idx = header["start"] + header["length"] * header["count"]

        for i, header in enumerate(data["headers"]):
            all_header_data = data["data"][i]["data"]
            schema = header["schema"]
            for header_data in all_header_data:
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
