import json
import os
import re
from pathlib import Path
from typing import Union, Optional
import argparse

from lib.parser import process_data, readint, get_size_from_schema
from processcle import processCLE


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Decompiles a .tbl file into JSON."
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version=f"{parser.prog} version 0.0"
    )
    parser.add_argument(
        "-g", "--game",
        help="Specify the game name to select a matching schema (e.g., 'Sora1')."
    )
    parser.add_argument('file', help="Input .tbl file to decompile")
    return parser


def parse(name: Union[str, bytes, os.PathLike], game: Optional[str] = None) -> None:
    true_filename = Path(name).stem
    # Replace digits in filename with %d to match generic schema names (e.g., "item01" → "item%d")
    filename = re.sub(r"\d", "%d", true_filename)
    filesize = os.path.getsize(name)

    tbl_file = None
    decrypted_temp = False

    try:
        with open(name, "rb") as f:
            magic = f.read(4)

        if magic != b"#TBL":
            # File appears encrypted — decrypt it
            with open(name, "rb") as encrypted_file:
                file_content = encrypted_file.read()
            decrypted_content = processCLE(file_content)

            # Write decrypted data back to the same file (or consider using a temp file)
            with open(name, "w+b") as output_file:
                output_file.write(decrypted_content)
            filesize = os.path.getsize(name)
            tbl_file = open(name, "rb")
            decrypted_temp = True  # Mark that we manually opened the file
        else:
            # File is not encrypted — open normally
            tbl_file = open(name, "rb")

        # Skip magic bytes if we're reading a decrypted file (already past 4 bytes in original logic)
        if decrypted_temp:
            tbl_file.seek(4)
        else:
            # For unencrypted files, we haven't read anything yet beyond magic check
            # But we opened fresh, so read magic again or skip
            magic_check = tbl_file.read(4)
            if magic_check != b"#TBL":
                raise ValueError("File does not start with expected magic '#TBL' after decryption.")

        header_count = readint(tbl_file, 4)
        headers = []
        tbl_data = []
        schema_list = []
        output = {}
        has_extra = False
        has_schema = True

        # Load schema metadata if available
        schema_meta_path = Path("schemas") / f"{filename}.json"
        if schema_meta_path.exists():
            with open(schema_meta_path, encoding="utf-8") as header_file:
                schemas_meta = json.load(header_file)
                schema_list = schemas_meta.get("headers", [])
        else:
            has_schema = False

        # Read all headers
        for _ in range(header_count):
            header_name_bytes = tbl_file.read(64)
            if len(header_name_bytes) < 64:
                raise ValueError("Unexpected end of file while reading header name.")
            header_name = header_name_bytes.replace(b"\0", b"").decode("utf-8")
            unknown = tbl_file.read(4).hex()  # Not used, but consumed
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

        # Check if there's trailing data beyond the declared tables
        if headers and headers[-1]["start"] + headers[-1]["length"] * headers[-1]["count"] < filesize:
            has_extra = True

        # Process each header's data
        for header in headers:
            tbl_file.seek(header["start"])
            header_data = {"name": header["name"], "data": []}

            if has_schema and header["name"] in schema_list:
                header_schema_path = Path("schemas") / "headers" / f"{header['name']}.json"
                if not header_schema_path.exists():
                    print(f"Warning: Schema file not found for header '{header['name']}'. Using raw hex.")
                    correct_schema = None
                else:
                    with open(header_schema_path, encoding="utf-8") as schema_file:
                        schemas: dict = json.load(schema_file)

                    actual_entry_size = header["length"]
                    correct_schema = None

                    # Try to find a matching schema by game and size
                    if game is not None:
                        for name, sch in schemas.items():
                            if sch.get("game") == game and get_size_from_schema(sch) == actual_entry_size:
                                correct_schema = (name, sch)
                                break
                    # Fallback: match by size only
                    if correct_schema is None:
                        for name, sch in schemas.items():
                            if get_size_from_schema(sch) == actual_entry_size:
                                correct_schema = (name, sch)
                                break

                if correct_schema is None:
                    print(f"Warning: No matching schema found for header '{header['name']}' "
                          f"(entry size = {actual_entry_size}). Using raw hex.")
                    for _ in range(header["count"]):
                        raw_bytes = tbl_file.read(header["length"])
                        if len(raw_bytes) != header["length"]:
                            raise ValueError(f"Unexpected end of file in header '{header['name']}'.")
                        hex_text = " ".join(
                            raw_bytes.hex()[j:j + 2] for j in range(0, len(raw_bytes.hex()), 2)
                        ).upper()
                        header_data["data"].append({"data": hex_text})
                else:
                    schema_dict = correct_schema[1]
                    header["schema"] = schema_dict.get("game", correct_schema[0])

                    for _ in range(header["count"]):
                        processed = 0
                        data = {}
                        schema = correct_schema[1]["schema"]
                        for key, datatype in schema.items():
                            # Handle composite types (e.g., "comp:Position")
                            if isinstance(datatype, str) and datatype.startswith("comp:"):
                                comp_key = datatype[5:]
                                if comp_key in schema:
                                    datatype = schema[comp_key]
                                else:
                                    raise KeyError(f"Composite reference '{datatype}' not found in schema.")
                            value, processed_bytes = process_data(
                                tbl_file, datatype, header["length"] - processed
                            )
                            data[key] = value
                            processed += processed_bytes
                        header_data["data"].append(data)
            else:
                # No schema available — dump raw hex
                for _ in range(header["count"]):
                    raw_bytes = tbl_file.read(header["length"])
                    if len(raw_bytes) != header["length"]:
                        raise ValueError(f"Unexpected end of file in header '{header['name']}'.")
                    hex_text = " ".join(
                        raw_bytes.hex()[j:j + 2] for j in range(0, len(raw_bytes.hex()), 2)
                    ).upper()
                    header_data["data"].append({"data": hex_text})

            tbl_data.append(header_data)
            print(header)

        output["data"] = tbl_data

        # Dump any trailing extra data if no schema is available
        if has_extra and not has_schema:
            remaining = tbl_file.read()
            if remaining:
                hex_text = " ".join(
                    remaining.hex()[j:j + 2] for j in range(0, len(remaining.hex()), 2)
                ).upper()
                output["data_dump"] = hex_text

        # Remove internal fields from headers in final output
        for header in output["headers"]:
            header.pop("count", None)
            header.pop("length", None)
            header.pop("start", None)

        # Write output JSON
        output_path = f"{true_filename}.json"
        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(output, output_file, ensure_ascii=False, indent="\t")

    finally:
        # Ensure file is closed if we opened it manually
        if tbl_file is not None and not tbl_file.closed:
            tbl_file.close()


def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()
    if not args.file:
        parser.error("A .tbl file is required.")
    parse(args.file, game=args.game)


if __name__ == "__main__":
    main()