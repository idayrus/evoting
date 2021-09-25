from app import app
from app.helper.preference import number_style
from re import sub as re_sub
from math import modf as MathModf


def terbilang(bil):
    angka = ["", "Satu ", "Dua ", "Tiga ", "Empat ", "Lima ", "Enam ", "Tujuh ", "Delapan ", "Sembilan ", "Sepuluh ", "Sebelas "]
    hasil = ""
    n = int(bil)
    if n >= 0 and n <= 11:
        hasil = angka[n]
    elif n < 20:
        hasil = terbilang(n-10) + " Belas "
    elif n < 100:
        hasil = terbilang(n/10) + " Puluh " + terbilang(n % 10)
    elif n < 200:
        hasil = " Seratus " + terbilang(n-100)
    elif n < 1000:
        hasil = terbilang(n/100) + " Ratus " + terbilang(n % 100)
    elif n < 2000:
        hasil = " Seribu " + terbilang(n-1000)
    elif n < 1000000:
        hasil = terbilang(n/1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000:
        hasil = terbilang(n/1000000) + " Juta " + terbilang(n % 1000000)
    elif n < 1000000000000:
        hasil = terbilang(n/1000000000) + " Milyar " + terbilang(n % 1000000000)
    elif n == 1000000000000:
        hasil = 'Satu Triliun'
    elif n > 1000000000000:
        hasil = 'Maaf, program tidak membaca angka lebih dari Satu Triliun'
    return hasil


def _convert_number(value, scale, endpoint):
    value = float(value) / scale
    value = int(value)
    output = f"{value}{endpoint}"
    output = str(output)
    # End
    return output


def convert_number(value):
    value = str(value)
    value = re_sub("[^0-9]", "", value)
    value = int(value)
    if value >= 1000 and value < 1000000:  # k
        output = _convert_number(value, 1000, "k")
    elif value >= 1000000 and value < 1000000000:  # m
        output = _convert_number(value, 1000000, "M")
    elif value >= 1000000000:  # B
        output = _convert_number(value, 1000000000, "B")
    else:
        output = str(value)
    # End
    return output


def convert_thousand(value, thou=None):
    if not thou:
        thou = number_style().number_group_separator
    output = str(value)
    output = re_sub(r"\B(?=(?:\d{3})+$)", thou, output)
    # End
    return output


def clean_number(value, to_int=True):
    output = str(value)
    output = re_sub("[^0-9]", "", output)
    if not output:
        # End
        output = "0"
    # End
    if to_int:
        return int(output)
    else:
        return output


def clean_decimal(value):
    # Config
    decimal = number_style().number_decimal_separator
    precision = 7

    # Split
    split = str(value).split(decimal)
    right = "0"
    left = str(clean_number(split[0]))
    if len(split) >= 2:
        right = str(clean_number(split[1], to_int=False))

    # Output
    output = left
    output += "."

    # Precision
    if right:
        if len(right) >= precision:
            output += right[:precision]
        else:
            missing = precision - len(right)
            output += right
            output += "0" * missing
    else:
        output += "0" * precision

    # End
    return output


def clean_money(value):
    return clean_decimal(value)


def mask_decimal(value, precision=None):
    # Var
    style = number_style()
    thousand = style.number_group_separator
    decimal = style.number_decimal_separator
    output = ""

    if precision is None:
        precision = style.number_precision

    # Process
    if value:
        # Split
        split = str(value).split(".")
        right = "0"
        left = str(clean_number(split[0]))
        if len(split) >= 2:
            right = str(clean_number(split[1], to_int=False))

        # Value
        output += convert_thousand(left, thousand)

        # Precision
        if precision > 0:
            output += decimal
            if len(right) >= precision:
                output += right[:precision]
            else:
                missing = precision - len(right)
                output += right
                output += "0" * missing

    else:
        output += "0"
        if precision > 0:
            output += decimal
        output += "0" * precision

    return output


def mask_money(value):
    # Config
    style = number_style()
    prefix = style.money_prefix
    suffix = style.money_suffix
    precision = style.money_precision

    # Output
    output = prefix
    output += mask_decimal(value, precision=precision)
    output += suffix

    return output


def format_bytes(size):
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{mask_decimal(str(size))}{(power_labels[n]+'b')}"


def jinja_shorthand(value):
    return convert_number(value)


def total_tagihan(tagihan_data):
    # Data
    dpp_a = 0
    pph_d = 0
    potongan_lain_e = 0
    if tagihan_data.dpp:
        dpp_a = float(tagihan_data.dpp)
    if tagihan_data.ppn:
        ppn_b = float(tagihan_data.ppn)
    if tagihan_data.pph:
        pph_d = float(tagihan_data.pph)
    if tagihan_data.potongan_lain:
        potongan_lain_e = float(tagihan_data.potongan_lain)
    pembayaran = dpp_a - pph_d - potongan_lain_e
    return mask_money(pembayaran)


# Register
app.add_template_filter(mask_decimal, 'mask_decimal')
app.add_template_filter(mask_money, 'mask_money')
app.add_template_filter(jinja_shorthand, 'number_shorthand')
app.add_template_filter(convert_thousand, 'number_thousand')
app.add_template_filter(format_bytes, 'format_bytes')
app.jinja_env.globals.update(total_tagihan=total_tagihan)
