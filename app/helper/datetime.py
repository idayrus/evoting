from flask import g
from app import app
from datetime import datetime, timezone
from calendar import monthrange
from pytz import timezone as pytz_tz
import arrow

#
# Utils
#


def get_month_name(number):
    data = {
        "1": "Januari",
        "2": "Februari",
        "3": "Maret",
        "4": "April",
        "5": "Mei",
        "6": "Juni",
        "7": "Juli",
        "8": "Agustus",
        "9": "September",
        "10": "Oktober",
        "11": "November",
        "12": "Desember"
    }
    return data.get(str(number))


def get_day_of_week(number):
    # The int value follows the ISO-8601 standard, from 1 (Monday) to 7 (Sunday)
    data = {
        "1": "Senin",
        "2": "Selasa",
        "3": "Rabu",
        "4": "Kamis",
        "5": "Jumat",
        "6": "Sabtu",
        "7": "Minggu",
    }
    return data.get(str(number))


def get_start_end_utc_datetime(start=None, end=None, replace_end=True):
    if not start:
        start = datetime.utcnow()
    if not end:
        end = datetime.utcnow()
    day_start = start.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    if replace_end:
        day_end = end.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
    else:
        day_end = end.replace(tzinfo=timezone.utc)
    return day_start, day_end


def get_start_end_utc_timestamp(start=None, end=None):
    # Convert to timestamp
    day_start = int(start.replace(tzinfo=timezone.utc).timestamp())
    day_end = int(end.replace(tzinfo=timezone.utc).timestamp())
    return day_start, day_end


def get_current_range_date(date, is_single=False):
    # Local
    if is_single:
        first_day_local = date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        first_day_local = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day_local = date.replace(hour=23, minute=59, second=59, microsecond=0)
    # To UTC
    first_day = DateTime().from_local(first_day_local).to_utc().as_datetime()
    last_day = DateTime().from_local(last_day_local).to_utc().as_datetime()
    # End
    return first_day, last_day


def get_month_name_abbr(number):
    month_name = get_month_name(number)
    return month_name[:3]


def get_month_first_last_date(date):
    first_day = date.replace(day=1)
    last_day = date.replace(day=monthrange(date.year, date.month)[1])
    return get_start_end_utc_datetime(first_day, last_day, replace_end=False)


def get_default_timezone():
    return app.config.get("DEFAULT_TIMEZONE")


def get_allowed_timezone():
    return app.config.get("ALLOWED_TIMEZONE")


def get_allowed_timezone_as_list():
    output = []
    for i in get_allowed_timezone():
        output.append(i[0])
    return output


# Load at startup
timezone_default = get_default_timezone()
timezone_allowed = get_allowed_timezone()
timezone_allowed_list = get_allowed_timezone_as_list()


def get_current_timezone():
    # Get from global variable
    timezone = "UTC"
    if g.get("auth"):
        timezone = g.auth.user_config.get("timezone")
    # Validate
    if not timezone in timezone_allowed_list:
        timezone = timezone_default
    # Return
    return timezone


def parse_query_date(query_data, is_single=False):
    # Query filter
    if query_data.from_date and query_data.to_date:
        # Parse
        try:
            date_format = "%d-%m-%Y %H:%M:%S"
            if is_single:
                start_text = "%s 00:00:00" % (query_data.to_date)
            else:
                start_text = "%s 00:00:00" % (query_data.from_date)
            end_txt = "%s 23:59:59" % (query_data.to_date)
            print(start_text, end_txt)
            start = DateTime().from_local(start_text, date_format).to_utc().as_datetime()
            end = DateTime().from_local(end_txt, date_format).to_utc().as_datetime()
            if not start > end:
                return start, end
            else:
                # End
                return None

        except Exception as e:
            # Log
            app.logger.error(e)
            # End
            return None
    else:
        # End
        return None


class DateTime():
    def __init__(self):
        self._arrow_datetime = None
        self._raw = None
        self._temp_dt = None
        self._target_timezone = "UTC"

    def _parse(self, value, format, tz):
        # Set to raw
        self._raw = value
        # If value is python datetime
        if isinstance(value, datetime):
            # End
            return arrow.get(value, tz)
        else:
            if isinstance(value, str):
                # Parse from string
                try:
                    # Set format if empty
                    if not format:
                        format = "%Y-%m-%d %H:%M:%S"
                    # End
                    return arrow.get(datetime.strptime(value, format), tz)
                except Exception as e:
                    raise e
            elif isinstance(value, int):
                return arrow.get(datetime.utcfromtimestamp(value), tz)

            else:
                # Raise error
                raise Exception("Unknown datetime format for %s" % str(value))

    def from_local(self, value, format=None):
        dt = self._parse(value, format, tz=get_current_timezone())
        dt = dt.to("UTC")
        self._arrow_datetime = dt
        return self

    def from_utc(self, value, format=None):
        dt = self._parse(value, format, tz="UTC")
        self._arrow_datetime = dt
        return self

    def to_local(self):
        if self._arrow_datetime:
            self._temp_dt = self._arrow_datetime.to(get_current_timezone())
            self._target_timezone = get_current_timezone()
        return self

    def to_utc(self):
        if self._arrow_datetime:
            self._temp_dt = self._arrow_datetime
            self._target_timezone = "UTC"
        return self

    def as_arrow(self):
        if self._temp_dt:
            return self._temp_dt
        else:
            return None

    def as_datetime(self):
        if self._temp_dt:
            return self._temp_dt.naive.replace(tzinfo=pytz_tz(self._target_timezone))
        else:
            return None

    def current_local(self):
        return self.from_utc(datetime.utcnow()).to_local().as_datetime()

    def humanize_datetime(self, abbr=False, with_time=True):
        # Get datetime
        dt = self.to_local().as_arrow()
        if not dt:
            return self._raw

        # Get day
        output = dt.format("DD")
        output += " "
        # Get month
        if abbr:
            output += get_month_name_abbr(dt.format("M"))
        else:
            output += get_month_name(dt.format("M"))
        output += " "
        output += dt.format("YYYY")

        # Time
        if with_time:
            output += ", "
            output += dt.format("HH:mm:ss")

        # End
        return output

    def humanize_date(self, abbr=False):
        return self.humanize_datetime(abbr, with_time=False)

# Function for jinja


def humanize_datetime(value, abbr=False, default="{invalid}"):
    if not value:
        return default
    return DateTime().from_utc(value).humanize_datetime(abbr)


def humanize_date(value, abbr=False, default="{invalid}"):
    if not value:
        return default
    return DateTime().from_utc(value).humanize_date(abbr)


def humanize_date_local(value, abbr=False, default="{invalid}"):
    if not value:
        return default
    return DateTime().from_local(value).humanize_date(abbr)


def datetime_local(value, default="{invalid}"):
    if not value:
        return default
    return DateTime().from_utc(value).to_local().as_datetime()


# Register to jinja
app.add_template_filter(humanize_datetime, 'humanize_datetime')
app.add_template_filter(humanize_date, 'humanize_date')
app.add_template_filter(humanize_date_local, 'humanize_date_local')
app.add_template_filter(get_month_name, 'month_name')
app.add_template_filter(get_day_of_week, 'day_of_week')
app.jinja_env.globals.update(datetime_local=datetime_local)
