from django.shortcuts import render

from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    now = datetime.now().year
    context = {
        'year': now,
    }
    return render(request, context)
