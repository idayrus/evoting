from app import app
from app.helper.number import clean_number

operator_prefix = {
    "Telkomsel": [
        "0811",
        "0812",
        "0813",
        "0852",
        "0853",
        "0821",
        "0822",
        "0823",
    ],
    "Indosat": [
        "0814",
        "0815",
        "0816",
        "0855",
        "0856",
        "0857",
        "0858",
    ],
    "XL": [
        "0817",
        "0818",
        "0819",
        "0859",
        "0877",
        "0878",
    ],
    "Axis": [
        "0831",
        "0832",
        "0838",
    ],
    "Tri": [
        "0896",
        "0897",
        "0898",
    ],
    "Bolt": [
        "0998",
        "0999",
    ],
    "Smartfren": [
        "0881",
        "0882",
        "0883",
        "0884",
        "0885",
        "0886",
        "0887",
        "0888",
        "0889",
    ],
    "Ceria": [
        "0828",
    ]
}


def _filter_phone(number):
    number = str(number)
    first = number[:1]
    second = number[:2]
    third = number[:3]

    if first == '8':
        return '0' + number
    elif second == '08':
        return number
    elif second == '62':
        return "0%s" % (number[2:])
    elif third == '+62':
        return "0%s" % (number[3:])

    return number


def filter_phone(number, country_code=True):
    number = str(number)
    if not number or len(number) <= 6:
        return number
    number = _filter_phone(number)
    number = clean_number(number, to_int=False)
    if country_code:
        number = "628%s" % (number[2:])
    return number


def is_valid_phone(number, min_number=8):
    total_number = 0
    for i in str(number):
        if i.isdigit():
            total_number += 1
    return total_number >= min_number


def gsm_operator(number):
    number = filter_phone(number, False)
    prefix = number[:4]
    for i in operator_prefix:
        data = operator_prefix.get(i)
        if prefix in data:
            return i
    # End
    return "GSM"


app.jinja_env.globals.update(gsm_operator=gsm_operator)
