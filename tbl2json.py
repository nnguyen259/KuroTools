import json
import os
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
        version = f"{parser.prog} version 0.0"
    )
    parser.add_argument('file')
    return parser

def parse(name: Union[str, bytes, os.PathLike]) -> None:
    filename = Path(name).stem
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
                "length": entry_length,
                "count": entry_count,
                "start": start_offset
            }
            
            headers.append(header)
        output["headers"] = headers

        if header["start"] + header["length"] * header["count"] < filesize:
            has_extra = True

        for header in headers:
            
            tbl_file.seek(header["start"])
            header_data = {"name": header["name"], "data": []}
            if has_schema and header["name"] in schema_list:
                with open(f'schemas/headers/{header["name"]}.json') as schema_file:
                    schemas: dict
                    schemas = json.load(schema_file)

                schemas_by_size: dict

                #First we get all versions of the schema (Falcom? CLE?)
                #Then we sort them by entry size in a dict called schemas_by_size
                schemas_by_size = {}
                for sch in schemas.items():
                    current_schema = sch[1]
                    variant_name = sch[0]
                    sz = get_size_from_schema(current_schema)
                    schemas_by_size[sz] = sch
                #once the sorting is done, we grab the actual entry size from the input tbl
                actual_entry_size = header["length"]
                #finally we select the correct schema corresponding to the size specified in the input tbl
                correct_schema = schemas_by_size[actual_entry_size]
                header["schema"] = correct_schema[0]

                for _ in range(header["count"]):
                    
                    
                    #and now we process the data specified in that schema.
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
                #print("No schema available for this TBL, please open an issue on github if you want this schema to be added to the tool.")
                for _ in range(header["count"]):
                    data = {}
                    hex_text = tbl_file.read(header["length"]).hex()
                    hex_text = " ".join(
                        hex_text[j : j + 2] for j in range(0, len(hex_text), 2)
                    ).upper()
                    data["data"] = hex_text
                    header_data["data"].append(data)
            tbl_data.append(header_data)
            print(header) #Moved the print here so that the schema version is apparent in the console
        output["data"] = tbl_data

        if has_extra and not has_schema:
            hex_text = tbl_file.read().hex()
            hex_text = " ".join(
                hex_text[j : j + 2] for j in range(0, len(hex_text), 2)
            ).upper()
            output["data_dump"] = hex_text
        for header in output["headers"]:
            #removing those as they could confuse the user
            header.pop("count")
            header.pop("length")
            header.pop("start")
        with open(f"{filename}.json", "w", encoding="utf-8") as output_file:
            json.dump(output, output_file, ensure_ascii=False, indent="\t")


def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()
    if not args.file:
        raise Exception("tbl2json needs a table to decompile!")
    else:
        parse(args.file)

if __name__ == "__main__":
    main()
