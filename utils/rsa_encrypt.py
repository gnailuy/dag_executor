from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from base64 import b64decode, b64encode


def encode_rsa(message, key_path):
    key = RSA.importKey(open(key_path).read())
    cipher = PKCS1_OAEP.new(key)
    cipher_text = cipher.encrypt(message)
    return b64encode(cipher_text)


def decode_rsa(cipher_text, key_path):
    key = RSA.importKey(open(key_path).read())
    cipher = PKCS1_OAEP.new(key)
    message = cipher.decrypt(b64decode(cipher_text))
    return message


def test():
    text = 'Hello World!'  # No longer than 214 bytes
    print(text)

    ct = encode_rsa(text, './resources/rsa_public_key.pem')
    print(ct)

    dt = decode_rsa(ct, './resources/rsa_private_key.pem')
    print(dt)


if __name__ == '__main__':
    test()

