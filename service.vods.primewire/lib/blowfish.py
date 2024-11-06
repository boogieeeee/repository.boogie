'''
Created on Dec 29, 2021

@author: boogie
'''
import base64
import time
from bfish import Cipher

test="O6abwC5Q+uhwn9gzoVJemlrkyosblvcVFsKMpxqQBXf5uwEbGJjwxl4LPd7ODQJlvkPYvVZIPlVnc5Xg32fVMw01wZE/ZKsuz7rjPA90JUE=tiP-_38hwe"

def decrypt(data):

    e = data[-10:].encode()
    t = data[:-10]
    bd = base64.b64decode(t)
    bf = Cipher(bytearray(e))
    out = b""
    for chunk in bf.decrypt_ecb(bd):
        out += chunk
    out = out.decode()
    codes = []
    code_size = 5
    for i in range(int(len(out) / code_size)):
        offset = i * code_size
        codes.append(out[offset: offset + code_size])
    return codes


if __name__ == "__main__":
    t1 = time.time()
    print(decrypt(test))
    print(time.time() - t1)
