from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, get_user_model


User = get_user_model()

POST_CREATE = reverse('posts:post_create')


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Ekaterina')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group
        )
        cls.new_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug_1',
            description='Описание'
        )
        cls.post_edit = reverse('posts:post_edit',
                                args=[PostFormTests.post.id])
        cls.second_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug_2',
            description='Описание'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_post_form_create_new_post(self):
        self.form_data = {'text': 'Другой текст',
                          'group': self.new_group.id, }
        posts_count = Post.objects.count()
        ids = list(Post.objects.all().values_list('id', flat=True))
        response = self.authorized_client.post(
            POST_CREATE,
            data=self.form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        posts = Post.objects.exclude(id__in=ids)
        self.assertEqual(posts.count(), 1)
        post = posts[0]
        self.assertEqual(self.form_data['text'], post.text,
                         'Текст не совпадает!')
        self.assertEqual(self.form_data['group'], post.group.id)
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': post.author}))

    def test_edit_post_in_form(self):
        self.form_data = {'text': 'Другой текст',
                          'group': self.second_group.id, }
        response = self.authorized_client.post(self.post_edit,
                                               data=self.form_data,
                                               follow=True)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, self.form_data['text'])
        self.assertEqual(self.post.group.id, self.form_data['group'])
        self.assertRedirects(response, reverse('posts:post_detail',
                                               args=[PostFormTests.post.id]))
