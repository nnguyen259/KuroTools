import lib.blowfish as blowfish
import struct
import operator
import zstandard

key = b"\x16\x4B\x7D\x0F\x4F\xA7\x4C\xAC\xD3\x7A\x06\xD9\xF8\x6D\x20\x94"
IV = b"\x9D\x8F\x9D\xA1\x49\x60\xCC\x4C"
cipher = blowfish.Cipher(key, byte_order = "big")
iv = struct.unpack(">Q", IV)
dec_counter = blowfish.ctr_counter(iv[0], f = operator.add)


def processCLE(file_content):
    magic = file_content[0:4]
    to_decrypt = [b"F9BA", b"C9BA"]
    to_decompress = [b"D9BA"]
    while (magic in to_decrypt) or (magic in to_decompress):
        if (magic in to_decrypt):
            result = b"".join(cipher.decrypt_ctr(file_content[8:], dec_counter))
        elif(magic in to_decompress):
            decompressor = zstandard.ZstdDecompressor()
            result = decompressor.decompress(file_content[8:])
        file_content = result
        magic = file_content[0:4]

    return result


