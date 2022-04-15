

import sys
import argparse
import ED9Disassembler

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Disassembles and reassembles ED9 script files (EXPERIMENTAL)."
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version = f"{parser.prog} version 0.0"
    )
    
    parser.add_argument('--markers', nargs='?', type=bool)
    parser.add_argument('--decompile', nargs='?', type=bool)
    parser.add_argument('--debug', nargs='?', type=bool)
    parser.add_argument('file')
    return parser

def main() -> None:

    global smallest_data_ptr

    parser = init_argparse()
    args = parser.parse_args()
    if args.markers is None:
        args.markers = False
    if args.decompile is None:
        args.decompile = False
    if args.debug is None:
        args.debug = False
    if not args.file:
        raise Exception("ED9Disassembler needs a file to disassemble!")
    else:
        disasm = ED9Disassembler.ED9Disassembler(args.markers, args.decompile, args.debug)
        disasm.parse(args.file)
    
        


if __name__ == "__main__":
    main()
