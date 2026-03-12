from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from ..manifest_client import get_js_files, get_css_files

register = template.Library()


def _resolve_path(file_path: str) -> str:
    """Prepend STATIC_URL to relative paths; leave absolute URLs (http/https) untouched."""
    if file_path.startswith(('http://', 'https://', '//')):
        return file_path
    return f"{settings.STATIC_URL}{file_path}"


@register.simple_tag
def manifest_js(entry):
    files = get_js_files(entry)
    tags = [f'<script src="{_resolve_path(f)}"></script>' for f in files]
    return mark_safe('\n'.join(tags))


@register.simple_tag
def manifest_css(entry):
    files = get_css_files(entry)
    tags = [f'<link rel="stylesheet" href="{_resolve_path(f)}">' for f in files]
    return mark_safe('\n'.join(tags))


@register.simple_tag
def manifest_js_files(entry):
    return [_resolve_path(f) for f in get_js_files(entry)]


@register.simple_tag
def manifest_css_files(entry):
    return [_resolve_path(f) for f in get_css_files(entry)]
