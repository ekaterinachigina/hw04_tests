from django.test import TestCase
from django.urls import reverse

SLUG = 'slug'
USERNAME = 'auth'
POST_ID = 1

ROUTE_URLS = [
    ['/', 'index', []],
    [f'/group/{SLUG}/', 'group_posts', [SLUG]],
    [f'profile/{USERNAME}/', 'profile', [USERNAME]],
    [f'/posts/{POST_ID}/', 'post_detail' [POST_ID]],
    ['/create/', 'post_create', []],
    [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]],
]


class RouteURLTest(TestCase):
    def task_route_urls(self):
        for url, name_route in ROUTE_URLS:
            with self.subTest(name_route):
                self.assertEqual(url, reverse(
                    f'posts:{name_route}'))
