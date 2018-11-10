from Crypto.Cipher import DES
from base64 import b64decode, b64encode

BS = 8


def pad(s): return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)


def unpad(s): return s[0:-ord(s[-1])]


def encode_des(message, password):
    des = DES.new(password, DES.MODE_ECB)
    return b64encode(des.encrypt(pad(message)))


def decode_des(cipher_text, password):
    des = DES.new(password, DES.MODE_ECB)
    return unpad(des.decrypt(b64decode(cipher_text)))


def test():
    text = 'Hello World!'
    print(text)

    ct = encode_des(text, 'password')
    print(ct)

    dt = decode_des(ct, 'password')
    print(dt)


if __name__ == '__main__':
    test()

