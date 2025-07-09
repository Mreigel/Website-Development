import boto3
import base64
import logging
import os

REGION = "us-west-1"
KMS_KEY_ALIAS = "alias/pii-key"
kms = boto3.client("kms", region_name=REGION)

class EncryptionError(Exception):
    pass

def encrypt_field(plaintext: str) -> str:
    if not plaintext:
        return ""
    try:
        response = kms.encrypt(
            KeyId=KMS_KEY_ALIAS,
            Plaintext=plaintext.encode()
        )
        return base64.b64encode(response["CiphertextBlob"]).decode()
    except Exception as e:
        logging.error(f"❌ KMS encryption failed: {e}")
        raise EncryptionError("KMS encryption failed")

def decrypt_field(ciphertext_b64: str) -> str:
    if not ciphertext_b64:
        return ""
    try:
        decoded = base64.b64decode(ciphertext_b64.encode())
        response = kms.decrypt(CiphertextBlob=decoded)
        return response["Plaintext"].decode()
    except Exception as e:
        logging.error(f"❌ KMS decryption failed: {e}")
        raise EncryptionError("KMS decryption failed")
