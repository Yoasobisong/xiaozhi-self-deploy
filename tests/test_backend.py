import unittest
import json
from backend import app

class BackendTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_chat_api(self):
        response = self.app.post('/api/chat', json={'message': '你好，模型！'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        print('模型回应:', data['response'])

    def test_chat_page(self):
        response = self.app.get('/chat')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'与模型对话', response.data)

if __name__ == '__main__':
    unittest.main()