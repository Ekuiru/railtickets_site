import unittest
from werkzeug.security import generate_password_hash, check_password_hash


class AuthLogicTestCase(unittest.TestCase):
    def test_password_hash(self):
        password = 'test1234'
        password_hash = generate_password_hash(password)
        self.assertTrue(check_password_hash(password_hash, password))

    def test_wrong_password(self):
        password_hash = generate_password_hash('correct_password')
        self.assertFalse(check_password_hash(password_hash, 'wrong_password'))


if __name__ == '__main__':
    unittest.main()