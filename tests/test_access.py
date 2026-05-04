import unittest
from app import create_app


class AccessControlTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_my_tickets_requires_login(self):
        response = self.client.get('/my_tickets', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Сначала выполните вход в систему.'.encode('utf-8'), response.data)

    def test_admin_requires_login(self):
        response = self.client.get('/admin', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Сначала выполните вход в систему.'.encode('utf-8'), response.data)


if __name__ == '__main__':
    unittest.main()