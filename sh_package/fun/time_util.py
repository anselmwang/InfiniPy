import datetime

import pytz


def _str_time(date_object):
    return date_object.strftime("%Y-%m-%d %H:%M:%S")

def cur_time():
    local_time = datetime.datetime.now()
    utc_time = datetime.datetime.utcnow()
    beijing_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
    return f"""Local: {_str_time(local_time)}
Beijing: {_str_time(beijing_time)}
UTC: {_str_time(utc_time)}"""