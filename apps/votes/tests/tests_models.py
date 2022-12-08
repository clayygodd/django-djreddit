from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.posts.models import Category, Thread, Comment
from apps.votes.models import Vote


# Create your tests here.
test_user = get_user_model()

class VoteModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = test_user.objects.create(
            username="testuser",
            email="testuser@email.com",
            password="testpass123",
        )
        cls.category = Category.objects.create(title='Test Category')
        cls.comment = Comment.objects.create(content="test comment", created_by=cls.user)
        cls.threads = Thread.objects.create(title='Thread 1',
                                            category=cls.category,
                                            op=cls.comment)

    def test_print_model_with_id(self):
        Vote.vote_manager.record_vote(self.comment, self.user, +1)
        expected = f"testuser: 1 on {self.comment}"
        result = Vote.objects.all()[0]
        self.assertEqual(str(result), expected)

    def test_novotes(self):
        result = Vote.vote_manager.get_score(self.comment)
        self.assertEqual(result, {"score": 0, "num_votes": 0})

    def test_oneupvote(self):
        Vote.vote_manager.record_vote(self.comment, self.user, +1)
        result = Vote.vote_manager.get_score(self.comment)
        self.assertEqual(result, {"score": 1, "num_votes": 1})

    def test_onedownvote(self):
        Vote.vote_manager.record_vote(self.comment, self.user, -1)
        result = Vote.vote_manager.get_score(self.comment)
        self.assertEqual(result, {"score": -1, "num_votes": 1})

    def test_onenovote(self):
        Vote.vote_manager.record_vote(self.comment, self.user, 0)
        result = Vote.vote_manager.get_score(self.comment)
        self.assertEqual(result, {"score": 0, "num_votes": 0})

