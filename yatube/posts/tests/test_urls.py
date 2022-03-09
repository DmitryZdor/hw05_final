from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.core.cache import cache

from ..models import Post, Group, User

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create(username='Smith')
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(author=cls.user, text='Тестовый пост')
        cls.post_url = f'/posts/{cls.post.id}/'
        cls.post_edit_url = f'/posts/{cls.post.id}/edit/'
        cls.public_urls = (
            ('/', 'posts/index.html'),
            (f'/group/{cls.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{cls.user.username}/', 'posts/profile.html'),
            (cls.post_url, 'posts/post_detail.html'),)
        cls.private_urls = (
            ('/create/', 'posts/create.html'),
            (cls.post_edit_url, 'posts/create.html')
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_index_exists_at_desired_location(self):
        for url in self.public_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url[0])
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_un_exists_page(self):
        response = self.guest_client.get('/un_exist/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_exists_at_desired_location_non_author(self):
        response = self.authorized_client.get(self.private_urls[0][0])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.private_urls[0][1])

    def test_urls_uses_correct_template(self):
        cache.clear()
        for url in self.public_urls:
            with self.subTest(url):
                response = self.authorized_client.get(url[0])
                self.assertTemplateUsed(response, url[1])

    def test_create_exists_at_desired_location_authorized_author(self):
        response = self.authorized_client.get(self.post_edit_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.private_urls[1][1])
