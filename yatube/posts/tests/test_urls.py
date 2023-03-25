from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, get_user_model


User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-description',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='test-text',
            group=cls.group,
        )

        cls.templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': cls.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': cls.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': cls.post.id}):
                'posts/post_create.html'
        }

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_url_for_author_user(self):
        for reverse_name in self.templates_url_names.keys():
            with self.subTest():
                response = self.author_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_for_authorized_user(self):
        for reverse_name in self.templates_url_names.keys():
            with self.subTest():
                if reverse_name == reverse(
                        'posts:post_edit',
                        kwargs={'post_id': self.post.id}):
                    response = self.authorized_client.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                else:
                    response = self.authorized_client.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_for_guest_user(self):
        for reverse_name in self.templates_url_names.keys():
            with self.subTest():
                if reverse_name == reverse('posts:post_create'):
                    response = self.guest_client.get(reverse_name)
                    print(response)
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                elif reverse_name == reverse('posts:post_edit',
                                             kwargs={'post_id': self.post.id}):
                    response = self.guest_client.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                else:
                    response = self.guest_client.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)
