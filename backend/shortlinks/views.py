from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET

from shortlinks.models import ShortLink


@require_GET
def redirect_to_recipe(request, code):
    """Перенаправление по короткой ссылке на оригинальный URL."""
    return redirect(get_object_or_404(ShortLink, short_code=code).original_url)
