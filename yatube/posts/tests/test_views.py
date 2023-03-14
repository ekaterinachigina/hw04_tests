from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group


User = get_user_model()


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
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', args=(self.group.slug,)):
                'posts/group_list.html',
            reverse('posts:profile',
                    args=[PostsPagesTests.user.username]):
                'posts/profile.html',
            reverse('posts:post_detail', args=(self.post.id,)):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', args=(self.post.id,)):
                'posts/post_create.html'
        }
        for reverse_name, template in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                assert response.status_code == 200, response.status_code
                self.assertTemplateUsed(response, template)

    def test_index_page_correct_context(self):
        response = self.guest_client.get(reverse('posts:index'))
        context_index = response.context.get('page_obj')
        post_list = Post.objects.all()
        self.assertQuerysetEqual(context_index, post_list,
                                 transform=lambda x: x)

    def test_group_list_page_correct_context(self):
        response = self.guest_client.get(
            reverse('posts:group_list', args=[PostsPagesTests.group.slug]))
        context_group_list = response.context.get('page_obj')
        group_list = list(self.group.posts.all())
        self.assertQuerysetEqual(context_group_list, group_list,
                                 transform=lambda x: x)

    def test_group_list_pages_not_show_new_post(self):
        response = self.guest_client.get(
            reverse('posts:group_list', args=[PostsPagesTests.group.slug]))
        self.assertTrue(self.group not in response.context['page_obj'])

    def test_profile_page_correct_context(self):
        response = self.guest_client.get(reverse('posts:profile',
                                         kwargs={'username':
                                                 self.post.author}))
        context_profile = response.context['page_obj'][0]
        self.assertEqual(context_profile.text, self.post.text)

    def test_post_detail_page_correct_context(self):
        response = self.guest_client.get(reverse('posts:post_detail',
                                         args=[PostsPagesTests.post.id]))
        context_post_detail = response.context.get('post')
        self.assertEqual(context_post_detail.text, 'Тестовый пост')

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


class paginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test User')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        for count in range(15):
            cls.post = Post.objects.create(
                text=f'Тестовый пост номер {count}',
                author=cls.user)

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page_obj').object_list), 10)

    def test_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page_obj').object_list), 5)
