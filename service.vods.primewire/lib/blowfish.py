'''
Created on Dec 29, 2021

@author: boogie
'''
from js2py import EvalJs
import os
import base64
import time
import six

test = "QIVWpVFA_6Lf0JioSrp0uUvySzR5YCDpXK20PwRIyWtnmspeRVUfmGXV9yxp8xRw41raZwBw/+1dOaOTcaJlxxcPecrPppOciGCRLL+lGVW85LdmmEsLWWHVZ7jsR2l33mrwQ9HDcq+zAvJICYrwJCyLSdL3Qx6H0/MI0RP2/LUYfbMm76rtCzxSkHQ0b9+xD1mF53Ry4DFy5d3uxW7GAy4eHNYto2fSrjg5B3mSyFJv+7ueArl2wL1/4hfJvQpZwO7oj1LZS55AgGwOnRNr63KfBdzz3VJhvUyg0EKwIe9lKK3tmovJIhO1i0gBRrA58PSlTds//ZOr9EArCNB3w4yTY/C/3D5SVEMwhPRmopShIsytN6+yoPbZq+6qH4bAtoiipegIaBixiISpwkSE="


def decrypt(data):
    if six.PY2:
        with open(os.path.join(os.path.dirname(__file__), "primewire.js")) as f:
            code = f.read()
        jscntx = EvalJs()
        jscntx.execute(code)
        return jscntx.decode(data)
    else:
        from bfish import Cipher
        from textwrap import wrap
        e = data[:9].encode()
        t = data[9:]
        bd = base64.b64decode(t)
        bf = Cipher(bytearray(e))
        out = b""
        for chunk in bf.decrypt_ecb(bd):
            out += chunk
        return wrap(out.decode(), 5)


if __name__ == "__main__":
    t1 = time.time()
    print(decrypt(test))
    print(time.time() - t1)
