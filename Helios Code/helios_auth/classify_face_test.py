from django.test import TestCase, Client
from helios_auth.views import *
from .utils import *
import unittest
import json
import psycopg2
import hashlib
import base64
import io
from PIL import Image
from helios_auth.base64_strings import base64_image1, base64_image2, base64_image3, base64_image_correct, c1_list, c2_list, r3_list, c1_list_correct,c2_list_correct, r3_list_correct
from helios_auth.models import User
from unittest.mock import patch
from unittest.mock import MagicMock
from django.contrib.messages import get_messages
from django.test import RequestFactory


class ClassifyFaceViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.session['auth_return_url'] = '/'
        self.request = MagicMock()
        self.response = base64_image_correct
        existing_user = User.objects.filter(user_id='XXXXXXXXXXYYYYYYYYYYYYYY@gmail.com').first()
        if existing_user:
            existing_user.delete()
        self.test_user = User.objects.create(user_id='XXXXXXXXXXYYYYYYYYYYYYYY@gmail.com')
    
    @patch('helios_auth.views.get_user')
    def test_classify_face_view(self, mock_get_user):
        # existing_user = User.objects.filter(user_id='XXXXXXXXXXYYYYYYYYYYYYYY@gmail.com').first()
        # if existing_user:
        #     existing_user.delete()
        # test_user = User.objects.create(user_id='XXXXXXXXXXYYYYYYYYYYYYYY@gmail.com')
        mock_get_user.return_value = self.test_user
        
        connection_mock = MagicMock()
        cursor_mock = connection_mock.cursor.return_value
        self.test_user.save = MagicMock()

        with unittest.mock.patch('psycopg2.connect', return_value=connection_mock):
            url = reverse('classify_face')
            response = self.client.post(url, {'response': base64_image_correct})
            cursor_mock.execute.assert_called()
            connection_mock.commit.assert_called()
            cursor_mock.close.assert_called()
            connection_mock.close.assert_called()
            self.assertTrue(self.test_user.save.called)

        print(response.content.decode())
        self.assertTrue('redirect_url' in response.content.decode())
        self.assertTrue('message1' in response.content.decode())
        self.assertEqual(response.json()['redirect_url'], '/')
        self.assertEqual(response.json()['message1'], 'Registration susccessful. You can now log in.')
