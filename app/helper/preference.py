from app import app
from flask import g

# Data
NUMBER_STYLE = {
    "IDR": {
        "money_nominal": [500.0, 1000.0, 2000.0, 5000.0, 10000.0, 20000.0, 50000.0, 100000.0],
        "money_prefix": "Rp ",
        "money_suffix": ",-",
        "money_with_decimal": False,
        "money_precision": 0,
        "number_decimal_separator": ",",
        "number_group_separator": ".",
        "number_precision": 2,
    },
    "USD": {
        "money_nominal": [],
        "money_prefix": "$",
        "money_suffix": "",
        "money_with_decimal": True,
        "money_precision": 2,
        "number_decimal_separator": ".",
        "number_group_separator": ",",
        "number_precision": 2,
    }
}
ALLOWED_CURRENCY = [
    ("IDR", "IDR - Indonesian Rupiah"),
    ("USD", "USD - United States Dollar")
]

#
# Function
#


class DataModel():
    def __init__(self, data=None):
        # Dict data
        if isinstance(data, dict):
            # Update data
            self.__dict__.update(data)

    def __getattr__(self, name):
        return None

    @property
    def to_dict(self):
        return dict(self.__dict__)


def get_number_style(currency):
    # Get data
    data = NUMBER_STYLE.get(currency)
    if data:
        return DataModel(data=data)
    else:
        return None


def get_preference(key):
    if key == "ALLOWED_CURRENCY":
        return ALLOWED_CURRENCY


def number_style():
    return get_number_style("IDR")


# Register
app.jinja_env.globals.update(get_preference=get_preference)
