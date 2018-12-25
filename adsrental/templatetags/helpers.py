import datetime

from django import template

register = template.Library()


@register.simple_tag
def relative_url(urlencode: str, field_name: str, value: str) -> str:
    url = '?{}={}'.format(field_name, value)
    querystring = urlencode.split('&')
    filtered_querystring = filter(lambda p: p.split('=')[0] != field_name, querystring)
    filtered_querystring = filter(lambda p: p.split('=')[-1] != '', filtered_querystring)
    encoded_querystring = '&'.join(filtered_querystring)
    url = '{}&{}'.format(url, encoded_querystring)
    return url


@register.filter
def ordinal(value: int) -> str:
    if value % 10 == 1 and value != 11:
        return '{}st'.format(value)
    if value % 10 == 2 and value != 12:
        return '{}nd'.format(value)
    if value % 10 == 3 and value != 13:
        return '{}rd'.format(value)

    return '{}th'.format(value)

@register.filter()
def humanize_timedelta(timedeltaobj: datetime.timedelta) -> str:
    secs = timedeltaobj.total_seconds()
    timetot = ""
    if secs < 60:
        return 'Now'

    if secs > 86400: # 60sec * 60min * 24hrs
        days = secs // 86400
        timetot += "{} days".format(int(days))
        secs = secs - days*86400

    if secs > 3600:
        hrs = secs // 3600
        timetot += " {} hours".format(int(hrs))
        secs = secs - hrs*3600

    if secs > 60:
        mins = secs // 60
        timetot += " {} minutes".format(int(mins))
        secs = secs - mins*60

    return timetot

@register.filter()
def humanize_timedelta_hours(timedeltaobj: datetime.timedelta) -> str:
    secs = timedeltaobj.total_seconds()
    timetot = ""
    if secs < 3600:
        return 'Now'

    if secs > 86400: # 60sec * 60min * 24hrs
        days = secs // 86400
        timetot += "{} days".format(int(days))
        secs = secs - days*86400

    if secs > 3600:
        hrs = secs // 3600
        timetot += " {} hours".format(int(hrs))
        secs = secs - hrs*3600

    return timetot
