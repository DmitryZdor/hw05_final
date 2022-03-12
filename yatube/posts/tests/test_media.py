import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.core.cache import cache
from django.urls import reverse
from ..forms import PostForm
from ..models import Post, Group, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class MediaCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug1',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
            image=cls.uploaded,
        )
        cls.form = PostForm()
        cls.index_url = ('posts:index', 'posts/index.html', None)
        cls.group_url = ('posts:group_list', 'posts/group_list.html',
                         (cls.group.slug,))
        cls.profile_url = ('posts:profile', 'posts/profile.html',
                           (cls.user.username,))
        cls.post_url = ('posts:post_detail', 'posts/post_detail.html',
                        (cls.post.pk,))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

    def test_pages_has_image(self):
        page_names = (self.index_url, self.group_url, self.profile_url,
                      )
        for page in page_names:
            with self.subTest(page=page):
                response = self.guest_client.get(reverse(page[0], args=page[2])
                                                 ).context['page_obj'][0].image
                self.assertEqual(response, self.post.image)

    def test_media_in_post_page(self):
        response = self.guest_client.get(reverse(self.post_url[0],
                                                 args=self.post_url[2])
                                         )
        self.assertEqual(response.context['post'].image, self.post.image)

    def test_post_with_media_exist(self):
        self.assertTrue(Post.objects.filter(text=self.post.text,
                                            image=self.post.image).exists()
                        )
