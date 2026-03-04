from django.test import TestCase, Client
from django.urls import reverse
from .models import User
import json
from unittest.mock import patch

class ChatbotTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123', is_customer=True)
        self.client.login(username='testuser', password='password123')

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_chatbot_response_success(self, mock_model_class, mock_configure):
        # Mocking Gemini response
        mock_model_instance = mock_model_class.return_value
        mock_model_class.return_value = mock_model_instance # redundancy for clarity
        mock_response = type('Response', (), {'text': 'Step 1: Check the fuse.'})
        mock_model_instance.generate_content.return_value = mock_response

        # Mock settings.GOOGLE_API_KEY
        with self.settings(GOOGLE_API_KEY='test-key'):
            response = self.client.post(
                reverse('chatbot_response'),
                data=json.dumps({'message': 'How to fix a fuse?'}),
                content_type='application/json'
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn('Step 1: Check the fuse.', response.json()['response'])
        self.assertTrue(mock_configure.called)
        # Verify the correct model was initialized
        mock_model_class.assert_called_with('gemini-flash-latest')

    def test_chatbot_response_no_message(self):
        response = self.client.post(
            reverse('chatbot_response'),
            data=json.dumps({'message': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
