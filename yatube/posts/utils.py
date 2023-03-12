from django.core.paginator import Paginator

from yatube.settings import POSTS_PER_PAGE


def get_paginator(request, items_list):
    paginator = Paginator(items_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
