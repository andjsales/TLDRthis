from app import app
import os
from unittest import TestCase
from models import db, connect_db, User, Summary, Folder

os.environ['DATABASE_URL'] = "postgresql:///tldrthis"


app.config['TESTING'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///tldrthis"
app.config['SQLALCHEMY_ECHO'] = False

connect_db(app)


class AppRoutesTestCase(TestCase):

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

    def test_homepage(self):
        """
        Test the homepage
        """
        with app.test_client() as client:
            res = client.get('/')
            self.assertEqual(res.status_code, 200)
            self.assertIn('too lazy to read ?', res.data.decode())


if __name__ == '__main__':
    import unittest
    unittest.main()
