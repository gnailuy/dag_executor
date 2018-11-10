from Crypto.Hash import SHA  # or SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from base64 import b64decode, b64encode


def sign_data(data, key_path):
    rsa_key = RSA.importKey(open(key_path, 'r').read())
    signer = PKCS1_v1_5.new(rsa_key)
    digest = SHA.new()
    digest.update(data)
    sign = signer.sign(digest)
    return b64encode(sign)


def verify_sign(signature, data, key_path):
    rsa_key = RSA.importKey(open(key_path, 'r').read())
    signer = PKCS1_v1_5.new(rsa_key)
    digest = SHA.new()
    digest.update(data)
    if signer.verify(digest, b64decode(signature)):
        return True
    return False


def test():
    text = 'Hello World!'
    print(text)

    sign = sign_data(text, './resources/rsa_private_key.pem')
    print(sign)

    ok = verify_sign(sign, text, './resources/rsa_public_key.pem')
    print(ok)


if __name__ == '__main__':
    test()

