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
