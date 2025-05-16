import base64
import datetime
import json
import os

import jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import rsa

# --- Keys ---
# Recipient's public key (for encryption)
RECIPIENT_PUBLIC_KEY_PATH = 'rsaapi/keys/partner_public_key.pem'
# Sender's private key (for signing)
SENDER_PRIVATE_KEY_PATH = 'rsaapi/keys/sender_private_key.pem' # You'll need to generate this key pair
# Sender's public key (to be sent to recipient for signature verification)
SENDER_PUBLIC_KEY_PATH = 'rsaapi/keys/sender_public_key.pem'  # You'll need to generate this key pair

# --- Helper function to generate sender keys if they don't exist (for demonstration) ---
def generate_and_save_sender_keys_if_needed():

    if not os.path.exists(SENDER_PRIVATE_KEY_PATH) or not os.path.exists(SENDER_PUBLIC_KEY_PATH):
        print("Sender keys not found, generating new ones...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        with open(SENDER_PRIVATE_KEY_PATH, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        public_key = private_key.public_key()
        with open(SENDER_PUBLIC_KEY_PATH, 'wb') as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        print(f"Sender keys generated and saved to {SENDER_PRIVATE_KEY_PATH} and {SENDER_PUBLIC_KEY_PATH}")

# Generate sender keys if they don't exist (you might do this once separately)
generate_and_save_sender_keys_if_needed()


# 1. Load Recipient's Public Key (for encryption)
with open(RECIPIENT_PUBLIC_KEY_PATH, 'rb') as f:
    recipient_public_key = serialization.load_pem_public_key(f.read())

# 2. Load Sender's Private Key (for signing)
with open(SENDER_PRIVATE_KEY_PATH, 'rb') as f:
    sender_private_key = serialization.load_pem_private_key(
        f.read(),
        password=None # Assuming no password on the private key for simplicity
    )

# 3. Load Sender's Public Key (to send to recipient)
with open(SENDER_PUBLIC_KEY_PATH, 'rb') as f:
    sender_public_key_pem = f.read() # Read as bytes to be base64 encoded later


# --- Data to encrypt ---
partner_id = "partner12520"*5
customer_id = 'customer456'
auth_token="a"*80
message = f'{partner_id},{customer_id},{auth_token}'.encode()
print(f'Message: {partner_id},{customer_id},{auth_token}')

# --- Encrypt with Recipient's RSA public key and OAEP padding ---
ciphertext = recipient_public_key.encrypt(
    message,
    asym_padding.OAEP( # Use the renamed import
        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# --- Sign the CIPHERTEXT with Sender's RSA private key and PSS padding ---
signature = sender_private_key.sign(
    ciphertext, # Sign the encrypted data
    asym_padding.PSS( # Use the renamed import
        mgf=asym_padding.MGF1(hashes.SHA256()),
        salt_length=asym_padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# --- Base64 encode data for transmission ---
encrypted_data_b64 = base64.b64encode(ciphertext).decode('utf-8')
signature_b64 = base64.b64encode(signature).decode('utf-8')
sender_public_key_b64 = base64.b64encode(sender_public_key_pem).decode('utf-8')


# --- Output ---
print("--- Data to be sent to the recipient ---")
print("\nBase64 Encrypted Data:")
print(encrypted_data_b64)

print("\nBase64 Signature of Encrypted Data:")
print(signature_b64)

print("\nBase64 Sender's Public Key (for signature verification):")
print(sender_public_key_b64)

# You would typically package this into a JSON object for an API call
payload_for_api = {
    "encrypted_data": encrypted_data_b64,
    "signature": signature_b64,
    "public_key": sender_public_key_b64 # This is the sender's public key
}

print("\nJSON Payload Example:")
print(json.dumps(payload_for_api, indent=2))
