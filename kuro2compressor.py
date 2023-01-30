import os
import sys
from processcle import compressCLE
from processcle import encryptCLE

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    if os.path.exists(sys.argv[1]):
        with open(sys.argv[1], 'rb') as decrypted_file:
            compressedfile = compressCLE(decrypted_file.read())
        with open(sys.argv[1], 'wb') as out:
            out.write(compressedfile)
