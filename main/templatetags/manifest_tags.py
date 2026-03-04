from django import template
from django.utils.safestring import mark_safe
from ..manifest_client import get_js_files, get_css_files

register = template.Library()


@register.simple_tag
def manifest_js(entry):
    """
    Template tag to get JavaScript files for an entry point.
    Usage: {% manifest_js "main" %}
    """
    files = get_js_files(entry)
    html_tags = []
    for file_path in files:
        html_tags.append(f'<script src="{file_path}"></script>')
    return mark_safe('\n'.join(html_tags))


@register.simple_tag
def manifest_css(entry):
    """
    Template tag to get CSS files for an entry point.
    Usage: {% manifest_css "main" %}
    """
    files = get_css_files(entry)
    html_tags = []
    for file_path in files:
        html_tags.append(f'<link rel="stylesheet" href="{file_path}">')
    return mark_safe('\n'.join(html_tags))


@register.simple_tag
def manifest_js_files(entry):
    """
    Template tag to get just the list of JavaScript file paths.
    Usage: {% manifest_js_files "main" as js_files %}
    """
    return get_js_files(entry)


@register.simple_tag
def manifest_css_files(entry):
    """
    Template tag to get just the list of CSS file paths.
    Usage: {% manifest_css_files "main" as css_files %}
    """
    return get_css_files(entry)
