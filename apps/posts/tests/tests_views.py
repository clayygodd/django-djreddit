from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.posts.models import Category, Thread, Comment

test_user = get_user_model()


class CatListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(title='TestCat')
        cls.url = reverse('posts:category_list')

    def test_category_list_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TestCat")


class ThreadListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = test_user.objects.create(
            username="testuser",
            email="testuser@email.com",
            password="testpass123",
        )
        cls.comment = Comment.objects.create(content="test comment", created_by=cls.user)
        cls.category = Category.objects.create(title='TestCat')
        cls.thread = Thread.objects.create(
            title='Test Topic', category=cls.category, op=cls.comment)
        cls.url = reverse('posts:thread_list', args=[cls.category.title])

    def test_thread_list_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Topic")

    def test_not_exist_thread_list_view(self):
        url = reverse('posts:thread_list', args=["NotExistCat"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ThreadViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = test_user.objects.create(
            username="testuser",
            email="testuser@email.com",
            password="testpass123",
        )
        cls.comment = Comment.objects.create(content="test comment", created_by=cls.user)
        cls.category = Category.objects.create(title='TestCat')
        cls.thread = Thread.objects.create(
            title='Test Topic', category=cls.category, op=cls.comment)
        cls.url = reverse('posts:thread_detail', args=[cls.category.title, cls.thread.slug])
        cls.create_url = reverse('posts:thread_create')

    def thread_detail_view_test(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Topic")
        self.assertContains(response, "test comment")

    def not_exist_thread_detail_view_test(self):
        url = reverse('posts:thread_detail', args=[self.category.title, "not-exist-thread"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def thread_without_login_comment_create_view(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "%s?next=%s" % (reverse("account_login"), self.create_url))
        response = self.client.get(
            "%s?next=%s" % (reverse("account_login"), self.create_url))
        self.assertContains(response, "Log In")

    def test_login_thread_create_view(self):
        self.client.force_login(self.user)
        category = Category.objects.get(title='TestCat')
        data = {"title": "Test New Thread", "category": category, "content":"test content"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        print(response["Location"])
        #self.assertEqual(
         #   response["Location"], reverse("posts:thread_detail", args=[self.category.title, "Test-New-Thread"]))


class CommentCreateEditViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = test_user.objects.create(
            username="testuser1",
            email="testuser1@email.com",
            password="testpass123",
        )
        cls.user2 = test_user.objects.create(
            username="testuser2",
            email="testuser2@email.com",
            password="testpass123",
        )
        cls.op =  Comment.objects.create(content="test op comment", created_by=cls.user1)
        cls.comment = Comment.objects.create(content="test comment", created_by=cls.user1)
        cls.category = Category.objects.create(title='TestCat')
        cls.thread = Thread.objects.create(
            title='Test Topic', category=cls.category, op=cls.op)
        cls.create_url = reverse('posts:comment_create', args=[cls.op.id])
        cls.edit_url = reverse('posts:comment_edit', args=[cls.op.id])

    def test_without_login_comment_create_view(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "%s?next=%s" % (reverse("account_login"),self.create_url))
        response = self.client.get(
            "%s?next=%s" % (reverse("account_login"),self.create_url))
        self.assertContains(response, "Log In")

    def test_login_comment_create_view(self):
        self.client.force_login(self.user1)
        data = {"content": "test content"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response["Location"], reverse("posts:thread_detail", args=[self.category.title, self.thread.slug]))

    def test_without_login_comment_edit_view(self):
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")

    def test_login_comment_self_edit_view(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.edit_url)
        self.assertContains(response, "test op comment")
        data = {"content": "test content"}
        response = self.client.post(self.edit_url, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response["Location"], reverse("posts:thread_detail", args=[self.category.title, self.thread.slug]))
        response = self.client.get(reverse("posts:thread_detail", args=[self.category.title, self.thread.slug]))
        self.assertContains(response, "test content")

    def test_login_comment_other_edit_view(self):
        self.client.force_login(self.user2)
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")


class UserProfileViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = test_user.objects.create(
            username="testuser1",
            email="testuser1@email.com",
            password="testpass123",
        )
        cls.op =  Comment.objects.create(content="test op comment", created_by=cls.user)
        cls.comment = Comment.objects.create(content="test comment", created_by=cls.user)
        cls.category = Category.objects.create(title='TestCat')
        cls.thread = Thread.objects.create(
            title='Test Topic', category=cls.category, op=cls.op)
        cls.url = reverse('posts:user_profile', args=[cls.user.username])

    def not_exist_user_profile_view_test(self):
        url = reverse('posts:user_profile', args=["not-exist-user"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def without_login_user_profile_view_test(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "%s?next=%s" % (reverse("account_login"), self.url))
        response = self.client.get(
            "%s?next=%s" % (reverse("account_login"), self.url))
        self.assertContains(response, "Log In")

    def login_user_profile_view_test(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response.context["threads"], self.thread)
        self.assertContains(response.context["threads"], self.comment)






