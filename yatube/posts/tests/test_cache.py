from django.test import TestCase, Client
from ..models import Post, Group, User
from django.urls import reverse
from django.core.cache import cache


class CacheIndexTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Тестовый пользователь')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый пост',
        )

    def test_index_cache(self):
        response_first = CacheIndexTest.authorized_client.get(reverse(
            'posts:index')).content
        Post.objects.get(pk=1).delete()
        response_second = CacheIndexTest.authorized_client.get(reverse(
            'posts:index')).content
        self.assertEqual(response_first, response_second)
        cache.clear()
        response_third = CacheIndexTest.authorized_client.get(reverse(
            'posts:index')).content
        self.assertNotEqual(response_first, response_third)
