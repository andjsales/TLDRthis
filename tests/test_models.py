from app import app
import os
from unittest import TestCase
from models import db, User, Summary, Folder

os.environ['DATABASE_URL'] = "postgresql:///tldrthis_test"


class UserModelTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Set up before all tests
        """
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """
        Clean up after all tests
        """
        db.session.rollback()
        db.drop_all()

    def setUp(self):
        """
        Set up before each test
        """
        User.query.delete()
        Folder.query.delete()
        Summary.query.delete()

    def tearDown(self):
        """
        Clean up after each test
        """
        db.session.rollback()

    def test_user_creation(self):
        """
        Test user creation
        """
        user = User(username='testuser',
                    email='test@test.com', password='password')
        db.session.add(user)
        db.session.commit()
        self.assertEqual(len(User.query.all()), 1)


if __name__ == '__main__':
    import unittest
    unittest.main()
