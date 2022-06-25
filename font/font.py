
import sys
import os 
import struct
from pathlib import Path
from lib.parser import readint

class character:
    def __init__(self, stream):
        self.addr = stream.tell()
        self.code = readint(stream, 4)
        self.int0 = readint(stream, 4)
        self.GNF_X = readint(stream, 2)
        self.GNF_Y = readint(stream, 2)
        self.half0 = readint(stream, 2)
        self.half1 = readint(stream, 2)
        self.half2 = readint(stream, 2)
        self.half3 = readint(stream, 2)
        self.half4 = readint(stream, 2)
        self.half5 = readint(stream, 2)

    def to_string(self)->str:
        print("Character at " + str(hex(self.addr)))
        pixel_nb = self.GNF_X + self.GNF_Y * 4096
        result = ""
        result = result + str(hex(self.addr)) + ";" + "\"" + chr(self.code) + "\"" + ";" + str(hex(self.int0)) + ";" + str((self.GNF_X)) + ";" + str((self.GNF_Y)) + ";" + str(pixel_nb) + ";" + str(hex(self.half0))+ ";"
        result = result + str(hex(self.half1)) + ";" + str(hex(self.half2)) + ";" + str(hex(self.half3)) + ";" + str(hex(self.half4))+ ";"
        result = result + str(hex(self.half5))+ ";"
        return result

def parse_font_file(font_file_path):
    filename = Path(font_file_path).stem
    filesize = os.path.getsize(font_file_path)
    with open(font_file_path, "rb") as fnt_file:
        fourCC = readint(fnt_file, 4)
        font_fcc = struct.unpack("<I",b'FCV\0')[0]
        
        if fourCC == font_fcc:
            half0 = readint(fnt_file, 2)
            half1 = readint(fnt_file, 2)
            char_count = readint(fnt_file, 4)
            half2 = readint(fnt_file, 2)
            half3 = readint(fnt_file, 2)
            half4 = readint(fnt_file, 2)
            half5 = readint(fnt_file, 2)
            int0 = readint(fnt_file, 4)
            int1 = readint(fnt_file, 4)
            int2 = readint(fnt_file, 4)
            fourcc2 = readint(fnt_file, 4)
            font_fcc2 = struct.unpack("<I",b'FLTI')[0]
            if fourcc2 == font_fcc2:
                size = readint(fnt_file, 4)
                current_addr = 0
                chr_list = []
                while(current_addr < size):
                    start = fnt_file.tell()
                    chr_list.append(character(fnt_file))
                    current_addr = current_addr + fnt_file.tell() - start
                
                with open('font.csv', 'w', encoding="utf-8") as f:
                    f.write("Address;Character;Int0;GNF_X_Origin;GNF_Y_Origin;Pixel_Nb;Width;Height;(Green = 0x100, Red = 0x200);Half0;Half1;Half2;"+"\n")
                    for chr in chr_list:

                        f.write(chr.to_string() + "\n")

if __name__ == "__main__":
    parse_font_file(sys.argv[1])
