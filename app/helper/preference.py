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
USER_ROLE = [
    {
        'group': 'Laporan',
        'value': [
            ('report_result_read', 'Lihat Hasil Pemilihan', [])
        ]
    },
    {
        'group': 'Data Calon',
        'value': [
            ('candidate_read', 'Lihat', []),
            ('candidate_create', 'Tambah', ['candidate_read']),
            ('candidate_update', 'Edit', ['candidate_read']),
            ('candidate_delete', 'Hapus', ['candidate_read', 'candidate_update'])
        ]
    },
    {
        'group': 'Data Pemilih',
        'value': [
            ('voter_read', 'Lihat', []),
            ('voter_create', 'Tambah', ['voter_read']),
            ('voter_update', 'Edit', ['voter_read']),
            ('voter_delete', 'Hapus', ['voter_read', 'voter_update']),
            ('voter_pin', 'Lihat PIN', ['voter_read']),
            ('voter_refresh', 'Ubah PIN', ['voter_read', 'voter_update', 'voter_pin']),
            ('voter_confirm', 'Konfirmasi Data', ['voter_read'])
        ]
    },
    {
        'group': 'Pengguna',
        'value': [
            ('user_read', 'Lihat', []),
            ('user_create', 'Tambah', ['user_read']),
            ('user_update', 'Edit', ['user_read']),
            ('user_delete', 'Hapus', ['user_read', 'user_update'])
        ]
    },
    {
        'group': 'Pengaturan',
        'value': [
            ('setting_update', 'Ubah Pengaturan', [])
        ]
    }
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
