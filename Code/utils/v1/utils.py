import chardet
import datetime
from decimal import Decimal


# Dict str to boolean
strToBoolean = {
    'true': True,
    't': True,
    '1': True,
    1: True,
    'y': True,
    's': True,
    'n': False,
    'none': False,
    'false': False,
    'f': False,
    '0': False,
    0: False,
}


def str_to_boolean(value):

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value = value.lower()

    if value in strToBoolean.keys():
        return strToBoolean[value]


def get_headers(headers, filter=None):
    filter = headers.keys() if filter is None else filter
    filter = [key.upper() for key in filter]

    return {key: value for (key, value) in headers.get_all() if key.upper() in filter}


def to_string(text):
    if text is None:
        return None

    if isinstance(text, str):
        return text.strip()

    if isinstance(text, bytes):
        char = chardet.detect(text)
        if char['encoding'] is None:
            return text.decode('UTF-8').strip()
        return text.decode(char['encoding']).strip()

    if isinstance(text, list):
        return to_string(text[0])

    if isinstance(text, datetime.date):
        return text.strftime('%d/%m/%Y %H:%M:%S')

    if isinstance(text, Decimal):
        return '%.2f' % text

    raise ValueError


def to_json_able(text):
    if not text:
        return ""

    if isinstance(text, str):
        return text.strip()

    if isinstance(text, bytes):
        char = chardet.detect(text)
        if char['encoding'] is None:
            return text.decode('UTF-8').strip()
        return text.decode(char['encoding']).strip()

    if isinstance(text, list):
        return to_string(text[0])

    if isinstance(text, datetime.date):
        return text.strftime('%d/%m/%Y %H:%M:%S')

    if isinstance(text, Decimal):
        return "{:.2f}".format(text)

    return text
