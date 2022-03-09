from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from ..forms import PostForm
from ..models import Post, Group, User
from ..views import NUMBER_OF_POSTS

User = get_user_model()

NUMBER_OF_POSTS_FOR_TEST = 13


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        # Create 13 posts for pagination tests
        for post_num in range(NUMBER_OF_POSTS_FOR_TEST):
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text=f'Тестовый пост {post_num}',
            )
            cls.index_url = ('posts:index', 'posts/index.html', None)
            cls.group_url = ('posts:group_list', 'posts/group_list.html',
                             (cls.group.slug,))
            cls.profile_url = ('posts:profile', 'posts/profile.html',
                               (cls.user.username,))
            cls.post_url = ('posts:post_detail', 'posts/post_detail.html',
                            (cls.post.pk,))
            cls.new_post_url = ('posts:post_create', 'posts/create.html', None)
            cls.edit_post_url = ('posts:post_edit', 'posts/create.html',
                                 (cls.post.pk,))
            cls.paginated_urls = (cls.index_url, cls.group_url, cls.profile_url
                                  )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.posts = Post.objects.all()
        self.form = PostForm()

    def test_pages_uses_correct_template_guest(self):
        page_names = (self.index_url, self.group_url, self.profile_url,
                      self.post_url)
        for page in page_names:
            with self.subTest(page=page):
                response = self.guest_client.get(reverse(page[0],
                                                         args=page[2]))
                template = page[1]
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_authorized(self):
        page_names = (self.new_post_url, self.edit_post_url)
        for page in page_names:
            with self.subTest(page=page):
                response = self.authorized_client.get(reverse(page[0],
                                                              args=page[2]))
                template = page[1]
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context_and_ten_posts(self):
        for url in self.paginated_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(reverse(url[0], args=url[2]))
                expected = list(self.posts)[:NUMBER_OF_POSTS]
                self.assertEqual(list(response.context['page_obj']), expected)
                self.assertEqual(len(response.context['page_obj']),
                                 NUMBER_OF_POSTS)

    def test_second_page_index_show_three_posts(self):
        for url in self.paginated_urls:
            with self.subTest(url=url):
                response = list(
                    self.guest_client.get(reverse(url[0],
                                                  args=url[2])
                                          + '?page=2').context['page_obj']
                )
                self.assertEqual(len(response),
                                 NUMBER_OF_POSTS_FOR_TEST - NUMBER_OF_POSTS)

    def test_post_detail_show_correct_context(self):
        response = (
            self.authorized_client.get(
                reverse(self.post_url[0], args=self.post_url[2])).context[
                'post']).text
        expected = self.post.text
        self.assertEqual(response, expected)

    def test_post_create_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(self.new_post_url[0])).context['form']
        expected = self.form
        self.assertEqual(str(response), str(expected))

    def test_post_edit_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(self.edit_post_url[0], args=self.edit_post_url[2])
        ).context['form'].Meta
        expected = self.form.Meta
        self.assertEqual(response, expected)

    def test_new_post_creation_other_page(self):
        page_names = (self.index_url, self.group_url, self.profile_url,)
        expected = list(self.posts)[NUMBER_OF_POSTS_FOR_TEST - NUMBER_OF_POSTS]
        for page in page_names:
            with self.subTest(page=page):
                response_by_page = list(
                    self.authorized_client.get(reverse(page[0],
                                                       args=page[2])).context[
                        'page_obj'])
                if self.group is not None:
                    response_post = response_by_page[
                        NUMBER_OF_POSTS_FOR_TEST - NUMBER_OF_POSTS]
                    self.assertEqual(response_post, expected)
