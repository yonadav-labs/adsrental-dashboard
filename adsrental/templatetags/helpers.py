from django import template

register = template.Library()


@register.simple_tag
def relative_url(urlencode, field_name, value):
    url = '?{}={}'.format(field_name, value)
    querystring = urlencode.split('&')
    filtered_querystring = filter(lambda p: p.split('=')[0] != field_name, querystring)
    filtered_querystring = filter(lambda p: p.split('=')[-1] != '', filtered_querystring)
    encoded_querystring = '&'.join(filtered_querystring)
    url = '{}&{}'.format(url, encoded_querystring)
    return url


@register.filter
def ordinal(value):
    if value % 10 == 1 and value != 11:
        return '{}st'.format(value)
    if value % 10 == 2 and value != 12:
        return '{}nd'.format(value)
    if value % 10 == 3 and value != 13:
        return '{}rd'.format(value)

    return '{}th'.format(value)
