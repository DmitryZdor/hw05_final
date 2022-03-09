from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth',
                                            )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def setUp(self):
        self.group = PostModelTest.group
        self.post = PostModelTest.post

    def test_verbose_name(self):
        fields = (('author', 'АВТОР', 'help_user'),
                  ('group', 'ГРУППА', 'Выберите группу'),
                  ('text', 'ТЕКСТ ПОСТА', 'Введите текст поста'),
                  ('pub_date', 'ДАТА', 'help_date')
                  )
        for field in fields:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field[0]).verbose_name, field[1])
                self.assertEqual(
                    self.post._meta.get_field(field[0]).help_text, field[2])

    def test_models_have_correct_object_names(self):
        test_items = ((str(self.post), self.post.text[:15]),
                      (str(self.group), self.group.title)
                      )
        for value, expected in test_items:
            with self.subTest(value=value):
                self.assertEqual(value, expected)
