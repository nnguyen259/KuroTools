import json
import os
from pathlib import Path
from typing import Union

from lib.packer import writehex, writeint, writetext


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


if __name__ == "__main__":
    pack("t_skill.json")
