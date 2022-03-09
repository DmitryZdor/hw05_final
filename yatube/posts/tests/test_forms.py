from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from ..forms import PostForm, CommentForm
from ..models import Post, Group, User, Comment

User = get_user_model()


class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.comments = CommentForm()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='auth')
        cls.user_un_auth = User.objects.create_user(username='auth1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )
        cls.post_count = Post.objects.count()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_un_auth = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_un_auth.force_login(self.user_un_auth)
        self.posts = Post.objects.all()
        self.form = PostForm()
        self.comments = CommentForm()

    def test_post_create_exist(self):
        form_data = {'text': 'Тестовый текст 2'}
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': 'auth'}))
        self.assertEqual(self.posts.count(), self.post_count + 1)
        self.assertTrue(Post.objects.filter(text='Тестовый текст 2').exists())

    def test_edit_post_done(self):
        form_data = {'text': 'Тестовый текст 2', }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'pk': self.post.pk}),
            data=form_data, follow=True,
        )
        self.assertNotEqual(response.context, self.post.text)
        self.assertTrue(Post.objects.filter(text='Тестовый текст 2').exists())

    def test_unauth_user_cant_publish_post(self):
        form_data = {'text': 'Тестовый текст 2', }
        response = self.authorized_client_un_auth.post(
            reverse('posts:post_edit', kwargs={'pk': self.post.pk}),
            data=form_data, follow=False,
        )
        self.assertFalse(Post.objects.filter(text='Тестовый текст 2').exists())
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'pk': self.post.pk}),
                             )

    def test_user_can_publish_comment(self):
        comment = Comment.objects.create(author=self.user, text='Комментарий',
                                         post=self.post)
        comment_count = Comment.objects.count()
        form_data = {'text': 'Комментарий', }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'pk': self.post.pk}),
            author=self.user,
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'pk': self.post.pk}),)
        self.assertEqual(comment.post, self.post)
