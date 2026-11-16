import binascii
import hashlib
from Crypto.Cipher import AES
import json

class AESCipher:

    def __init__(self):
        self.bs = AES.block_size
        config = json.loads(open('config/secrets.json').read())
        self.key = hashlib.sha256(config["encryptionkey"].encode()).digest()
        self.iv = b"YOUR_SALT_HERE"

    def encrypt(self, raw):
        raw = self._pad(str(raw))
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return str(binascii.hexlify(self.iv + cipher.encrypt(raw.encode())).decode())

    def decrypt(self, enc):
        enc = binascii.unhexlify(str(enc))
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return str(self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8'))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
