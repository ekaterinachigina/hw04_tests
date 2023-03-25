from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group, get_user_model


User = get_user_model()

MAIN_PAGE = reverse('posts:main')

POST_CREATE = reverse('posts:post_create')


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Описание',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.post_detail = reverse('posts:post_detail',
                                  args={'post_id': cls.post.id})
        cls.group_list = reverse('posts:group_list',
                                 args={'slug': cls.group.slug})
        cls.post_edit = reverse('posts:post_edit',
                                args={'post_id': cls.post.id})
        cls.profile = reverse('posts:profile',
                              args=[PostsPagesTests.user.username])

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostsPagesTests.author)
        self.form_fields_post_create = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    def test_pages_uses_correct_template(self):
        template_pages_names = {
            MAIN_PAGE: 'posts/index.html',
            POST_CREATE: 'posts/post_create.html',
            self.post_detail: 'posts/post_detail.html',
            self.group_list: 'posts/group_list.html',
            self.profile: 'posts/profile.html',
            self.post_edit: 'posts/post_create.html',
        }
        for reverse_name, template in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                assert response.status_code == 200, response.status_code
                self.assertTemplateUsed(response, template)

    def test_create_post_page_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in self.form_fields_post_create.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_correct_context(self):
        response = self.author_client.get(reverse('posts:post_edit',
                                          args=[PostsPagesTests.post.id]))
        for value, expected in self.form_fields_post_create.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test User')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create()
        new_posts = [Post(author=cls.author, text='Тестовый пост',
                          group=cls.group,)for i in range(15)]
        cls.post = Post.objects.bulk_create(new_posts)

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:м'))
        self.assertEqual(len(response.context.get('page_obj').object_list), 10)

    def test_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page_obj').object_list), 5)
