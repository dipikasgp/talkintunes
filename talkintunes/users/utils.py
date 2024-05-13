import binascii
import os
import secrets

from PIL import Image
from flask import url_for
from flask_mail import Message
from flask import current_app
from talkintunes import mail

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_tokens()
    msg = Message('Password reset request', sender='dipika.sengupta3012@outlook.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)


# Generate RSA key pair for a user
def generate_rsa_key():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )


# Encrypt message with recipient's public key
def encrypt_message(message, recipient_public_key):
    public_key = serialization.load_pem_public_key(recipient_public_key, backend=default_backend())
    # message = message.decode('utf-8')
    try:

        encrypted_message = public_key.encrypt(
            message.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_message
    except Exception as e:
        print("Encryption failed:", e)


# Decrypt message with recipient's private key
def decrypt_message(encrypted_message, private_key):
    # encrypted_message_bytes = encrypted_message.encode('utf-8')
    private_key = serialization.load_pem_private_key(private_key, password=None, backend=default_backend())
    decrypted_message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ).decode()
    return decrypted_message


# Serialize RSA private key to PEM format
def serialize_rsa_key_to_pem(private_key, username):
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    private_key_file = f'{username}_private_key.pem'
    private_key_filepath = os.path.join(os.getcwd(), ' \\private_keys', private_key_file)
    with open(private_key_filepath, 'wb') as f:
        f.write(private_key_pem)

    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    return private_key_filepath, public_key_pem


# Deserialize RSA private key from PEM format
def deserialize_private_key_from_pem(pem_data):
    private_key = serialization.load_pem_private_key(
        pem_data,
        password=None,
        backend=default_backend()
    )
    return private_key
