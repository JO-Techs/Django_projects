import base64
import os

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class DecryptAndVerifyData(APIView):
    def post(self, request):
        # Retrieve data from request
        encrypted_data_b64 = request.data.get('encrypted_data')
        signature_b64 = request.data.get('signature')
        public_key_b64 = request.data.get('public_key')

        # Missing data check
        if not all([encrypted_data_b64, signature_b64, public_key_b64]):
            return Response({'error': 'Missing encrypted_data, signature, or public_key'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode base64 encoded data
            def base64_decode_padded(data: str) -> bytes:
                data = data.strip()
                missing_padding = len(data) % 4
                if missing_padding:
                    data += '=' * (4 - missing_padding)
                return base64.b64decode(data)

            encrypted_data = base64_decode_padded(encrypted_data_b64)
            signature = base64_decode_padded(signature_b64)
            public_key_pem = base64_decode_padded(public_key_b64)

            # Load public key
            public_key = serialization.load_pem_public_key(public_key_pem, backend=None)

            # Verify the signature
            try:
                public_key.verify(signature, encrypted_data,  # Verify the encrypted data itself
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                print("Signature is valid.")
            except InvalidSignature:
                return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': f'Error during signature verification: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

            # Load private key for decryption
            key_path = 'rsaapi/keys/partner_private_key.pem'
            if not os.path.exists(key_path):
                return Response({'error': 'Private key file not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            with open(key_path, 'rb') as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None
                )

            # Decrypt the data
            plaintext_bytes = private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            plaintext = plaintext_bytes.decode()
            partner_id, customer_id, auth_token = plaintext.split(',')

            return Response({
                'partner_id': partner_id,
                'customer_id': customer_id,
                'auth_token': auth_token
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)