# parks/templatetags/query_transform.py
from django import template

register = template.Library()

@register.simple_tag
def url_replace(request, **kwargs):
    """
    Return encoded GET parameters after replacing/updating keys with kwargs.
    Usage in template: ?{% url_replace request page=3 %}
    """
    query = request.GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    # remove empty keys
    for k in list(query.keys()):
        if query.get(k) == '':
            query.pop(k)
    return query.urlencode()
