import jwt
from cryptography.fernet import Fernet

from flexibees_candidate.settings import SECRET_CIPHER_KEY, SECRET_KEY

CIPHER = Fernet(SECRET_CIPHER_KEY)


def crypto_encode(value):
    """
    It take value and makes one 100 character token
    :param value: any value
    :return: token
    """
    if value == '':
        raise ValueError('Please add some value!!')
    value = str.encode(str(value))
    encrypted_text = CIPHER.encrypt(value).decode('utf-8')
    return encrypted_text


def crypto_decode(token):
    """
    It decode token to actual value
    :param token: token
    :return: it returns string value
    """
    if token == '':
        raise ValueError('Please add some value!!')
    token = str.encode(token)
    decrypted_text = CIPHER.decrypt(token)
    return decrypted_text.decode('utf-8')


def jwt_payload_handler(user, role):

    bi = crypto_encode(user.password) if user.password != '' else ''

    payload = {
        'ai': crypto_encode(user.pk),
        'bi': bi,
        'ci': role
    }
    return payload


def jwt_encode_handler(payload):
    return jwt.encode(
        payload,
        SECRET_KEY,
        'HS256'
    )


def jwt_decode_handler(token):
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=['HS256']
    )

def jwt_project_payload_handler(role, project):
            return {
                'bi': project,
                'ci': role
            } 

def jwt_email_change_payload_handler(email_change_id, user_id, role):
            return {
                'ai': email_change_id,
                'bi': user_id,
                'ci': role
            } 