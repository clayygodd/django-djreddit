from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.posts.models import Category, Thread, Comment
from slugify import slugify

# Create your tests here.
test_user = get_user_model()

class CategoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = test_user.objects.create(
            username="testuser",
            email="testuser@email.com",
            password="testpass123",
        )
        cls.category = Category.objects.create(title='Test Category')
        # create 3 threads
        cls.threads = [Thread.objects.create(title='Thread %s' % i,
                                            category=cls.category,
                                             op=Comment.objects.create(content="test comment", created_by=cls.user)) for i in range(1, 4)]


class ThreadModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = test_user.objects.create(
            username="testuser",
            email="testuser@email.com",
            password="testpass123",
        )
        cls.category = Category.objects.create(title='TestCat')
        cls.thread = Thread.objects.create(title='Test Thread', category=cls.category, op=Comment.objects.create(content="test comment1", created_by=cls.user))

    def testThreadSlugGeneration(self):
        thread = Thread.objects.create(title='Slug Test 1!', category=self.category, op=Comment.objects.create(content="test comment2", created_by=self.user))
        slug = slugify(thread.title, max_length=80)
        self.assertEqual(thread.slug, slug)

    def testThreadRelativeUrl(self):
        threadPageUrl = reverse('post:thread_detail', args=[self.category.title, self.thread.slug])
        self.assertEqual(self.thread.relativeUrl, threadPageUrl)


class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = test_user.objects.create(
            username="testuser",
            email="testuser@email.com",
            password="testpass123",
        )
        cls.post = Comment.objects.create(content="test comment op", created_by=cls.user)
        cls.thread = Thread.objects.create(title='Test Thread', category=Category.objects.create(title='Test Topic'), op=cls.post)
        cls.replies = [Comment.objects.create(content="test comment", parent=cls.post, created_by=cls.user) for _ in range(1, 4)]

    def testGetReplies(self):
        self.assertListEqual(self.replies, list(self.post.get_all_comments()))

    def testGetThread(self):
        self.assertEqual(self.thread, self.post.thread)
