import lib.blowfish as blowfish
import struct
import operator
import math
try:
    import zstandard
except ImportError:
    import pip
    pip.main(['install', '--user', 'zstandard'])
    try:
        import zstandard
    except ImportError:
        #print("zstandard might not be installed with the Python version you are currently using")
        pass #At least when not needed you should be able to decompile scripts

key = b"\x16\x4B\x7D\x0F\x4F\xA7\x4C\xAC\xD3\x7A\x06\xD9\xF8\x6D\x20\x94"
IV = b"\x9D\x8F\x9D\xA1\x49\x60\xCC\x4C"
cipher = blowfish.Cipher(key, byte_order = "big")
iv = struct.unpack(">Q", IV)
dec_counter = blowfish.ctr_counter(iv[0], f = operator.add)


def processCLE(file_content):
    result = file_content
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

def compressCLE(file_content):
    compressor = zstandard.ZstdCompressor(level=9, write_checksum=True)
    result = compressor.compress(file_content)
    filesize=len(result)
    a = 8*math.ceil(filesize/8) - filesize
    for x in range (a):
        result = result + b"0"
    filesize=len(result)
    result=b"D9BA"+filesize.to_bytes(4,'little')+result    

    return result

def encryptCLE(file_content):
    result = b"".join(cipher.encrypt_ctr(file_content, dec_counter))
    filesize=len(result)
    a = 8*math.ceil(filesize/8) - filesize
    for x in range (a):
        result = result + b"0"
    filesize=len(result)
    result=b"F9BA"+filesize.to_bytes(4,'little')+result

    return result


