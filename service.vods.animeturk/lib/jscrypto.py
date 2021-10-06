'''
Created on Feb 16, 2021

@author: boogie
'''
import hashlib
import ghub

ghub.load("ricmoo", "pyaes", None)
import pyaes


def evpKDF(passwd, salt, key_size=8, iv_size=4, iterations=1, hash_algorithm="md5"):
    target_key_size = key_size + iv_size
    derived_bytes = b""
    number_of_derived_words = 0
    block = None
    hasher = hashlib.new(hash_algorithm)
    while number_of_derived_words < target_key_size:
        if block is not None:
            hasher.update(block)
        hasher.update(passwd.encode())
        hasher.update(salt)
        block = hasher.digest()
        hasher = hashlib.new(hash_algorithm)
        for _ in range(1, iterations):
            hasher.update(block)
            block = hasher.digest()
            hasher = hashlib.new(hash_algorithm)
        derived_bytes += block[0: min(len(block), (target_key_size - number_of_derived_words) * 4)]
        number_of_derived_words += len(block) / 4
    return derived_bytes[0: key_size * 4], derived_bytes[key_size * 4:]


def decrypt(data, password, salt):
    key, _ = evpKDF(password, salt, key_size=12)
    iv = key[len(key) - 16:]
    key = key[:len(key) - 16]
    decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv))
    decryptedData = decrypter.feed(data)
    decryptedData += decrypter.feed()
    return decryptedData
