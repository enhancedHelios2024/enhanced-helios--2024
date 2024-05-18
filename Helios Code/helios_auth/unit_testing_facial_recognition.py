from django.test import TestCase, Client
from helios_auth.views import *
from .utils import *
import unittest
import json
from PIL import Image
from helios_auth.base64_strings import base64_image1, base64_image2, base64_image3, base64_image_correct, c1_list, c2_list, r3_list, c1_list_correct,c2_list_correct, r3_list_correct
from helios_auth.models import User
from unittest.mock import patch
from unittest.mock import MagicMock

   


class FacialRecognitionTests(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.client.session['auth_return_url'] = '/'
        self.request = MagicMock()
        self.response = base64_image_correct
        existing_user = User.objects.filter(user_id='XXXXXXXXXXYYYYYYYYYYYYYY@gmail.com').first()
        if existing_user:
            existing_user.delete()
        self.test_user = User.objects.create(user_id='XXXXXXXXXXYYYYYYYYYYYYYY@gmail.com')
    
    @patch('helios_auth.views.psycopg2.connect')
    def test_get_other_shares(self, mock_connect):
        """ This unit test checks if the get_other_shares function returns the correct set of shares for a given user. """
        print("===========================================================================================================================================")
        print("")
        print("Unit Test: test_get_other_shares")
        print("This unit test checks if the get_other_shares function returns the correct set of shares for a given user.")
        user_email = 'testinghelios1234@gmail.com'
        url = reverse('get_other_shares')

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ('expected_c1_value', 'expected_c2_value', 'expected_r1_value')
        mock_connect.return_value.cursor.return_value = mock_cursor

        response = self.client.get(url, {user_email: ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        response_data = json.loads(response.content)
        c1_string = response_data['c1']
        c2_string = response_data['c2']
        r1_string = response_data['r1']

        self.assertEqual(c1_string, 'expected_c1_value')
        self.assertEqual(c2_string, 'expected_c2_value')
        self.assertEqual(r1_string, 'expected_r1_value')

    def test_combine_share_to_recreate_image(self):
        """ This unit test checks if the combine_shares_to_recreate_image function combines the shares correctly to recreate the original image base64 string representation. """
        print("===========================================================================================================================================")
        print("")
        print("Unit Test: test_combine_share_to_recreate_image")
        print("This unit test checks if the combine_shares_to_recreate_image function combines the shares correctly to recreate the original image base64 string representation.")
        test_s_list = [100, 200, 300, 400, 500]
        test_c1_list = [600, 700, 800, 900, 1000,'r']
        test_c2_list = [1100, 1200, 1300, 1400, 1500,'g']
        test_b_random_list = [1, 2, 3, 4, 5]
        test_r_random_list = [6, 7, 8, 9, 10]
        test_g_random_list = [11, 12, 13, 14, 15]
        reconstructed_base64_image = combine_shares_to_recreate_image(test_s_list, test_c1_list, test_c2_list,5,1,test_r_random_list,test_g_random_list,test_b_random_list)
        expected_base64_image = 'iVBORw0KGgoAAAANSUhEUgAAAAUAAAABCAIAAACZnPOkAAAADklEQVR4nGNMSUlhQAIAEIgBLiS5bRwAAAAASUVORK5CYII='
        self.assertEqual(reconstructed_base64_image, expected_base64_image)
        
    def test_compare_faces(self):
        """ This unit test checks if the compare_faces function returns a value between 0 and 1 representing the similarity between two images. """
        print("===========================================================================================================================================")
        print("")
        print("Unit Test: test_compare_faces")
        print("This unit test checks if the compare_faces function returns a value between 0 and 1 representing the similarity between two images.")
        result = compare_faces(base64_image1, base64_image3)
        # print(result)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 1)

    @patch('helios_auth.views.get_user')
    def test_max_attempts_reached_and_cooldown_time(self, mock_get_user):
        """ This unit test checks if the recombine_shares function returns the correct messages when an unsuccessful authentication occurs, the maximum number of attempts is reached (3), and the correct cooldown message after max attempts are reached. """
        print("===========================================================================================================================================")
        print("")
        print("Unit Test: test_max_attempts_reached_and_cooldown_time")
        print("This unit test checks if the recombine_shares function returns the correct messages when an unsuccessful authentication occurs, the maximum number of attempts is reached (3), and the co-rrect cooldown message after max attempts are reached.")
        url  = reverse('recombine_shares')
        email = 'testinghelios1234@gmail.com'
        profile = Profile.objects.filter(user__user_id=email).first()
        mock_get_user.return_value = profile.user
        data = {
            'file1Array': c1_list,  # Example data, replace with actual data
            'file2Array': c2_list,
            'file3Array': r3_list,
            'mainResponse' : base64_image1,
        }
        json_data = json.dumps(data)
        max_attempts = 3
        for i in range(max_attempts):
            response = self.client.post(url, json_data, content_type='application/json')
            content = json.loads(response.content)
            attempts_left = max_attempts - i 
            expected_message = f'Authentication unsuccessful. {attempts_left} attempts left.'
            self.assertEqual(content['message'], expected_message)
        response = self.client.post(url,json_data, content_type='application/json')
        content = json.loads(response.content)
        self.assertEqual(content['message'], 'Maximum attempts reached. Session ended.')

        response = self.client.post(url, json_data, content_type='application/json')
        content = json.loads(response.content)
        self.assertIn('Please wait', content['message'])
        self.assertIn('before attempting again.', content['message'])

    # def test_recombine_shares_success(self):
    @patch('helios_auth.views.get_user')
    def test_recombine_shares_success(self, mock_get_user):
        """ This unit test checks if the recombine_shares function returns the correct message when a successful authentication occurs. """
        print("===========================================================================================================================================")
        print("")
        print("Unit Test: test_recombine_shares_success")
        print("This unit test checks if the recombine_shares function returns the correct message when a successful authentication occurs.")
        url  = reverse('recombine_shares')
        email = 'testinghelios1234@gmail.com'
        profile = Profile.objects.filter(user__user_id=email).first()
        mock_get_user.return_value = profile.user
        data = {
            'file1Array': c1_list_correct,  # Example data, replace with actual data
            'file2Array': c2_list_correct,
            'file3Array': r3_list_correct,
            'mainResponse' : base64_image_correct,
        }
        json_data = json.dumps(data)
        response = self.client.post(url, json_data, content_type='application/json')
        content = json.loads(response.content)
        self.assertEqual(content['message'], 'Authentication successful.')
    
    def test_generate_vc_shares(self):
        """ This unit test checks if the generate_visual_cryptography_shares function returns the correct number, size, and format of shares for a given image. """
        print("===========================================================================================================================================")
        print("")
        print("Unit Test: test_generate_vc_shares")
        print("This unit test checks if the generate_visual_cryptography_shares function returns the correct number, size, and format of shares for a given image.")
        test_image = Image.new('RGB', (100, 100), color='white')
        test_image_data = test_image.getdata()
        server_list, client_list1, client_list2, r_random_list, g_random_list, b_random_list = generate_visual_cryptography_shares(test_image_data)

        expected_length = 100 * 100
        self.assertEqual(len(server_list), expected_length)
        self.assertEqual(len(client_list1), expected_length + 1)
        self.assertEqual(len(client_list2), expected_length + 1)
        self.assertEqual(len(r_random_list), expected_length)
        self.assertEqual(len(g_random_list), expected_length)
        self.assertEqual(len(b_random_list), expected_length)

        for i in range(expected_length):
            self.assertIsInstance(server_list[i], int)
            self.assertIsInstance(client_list1[i], int)
            self.assertIsInstance(client_list2[i], int)
    
    def test_classify_face(self):
        """ This unit test checks if the classify_face function saves the sets of shares correctly in the database servers. """
        print("===========================================================================================================================================")
        print("")
        print("Unit Test: test_classify_face")
        print("This unit test checks if the classify_face function saves the sets of shares correctly in the database servers.")
        # classify_face(self.test_user, self.request, self.response)
        connection_mock = MagicMock()
        # cursor_mock = MagicMock()
        cursor_mock = connection_mock.cursor.return_value
        self.test_user.save = MagicMock()
        # connection_mock.cursor.return_value.__enter__.return_value = cursor_mock
        with unittest.mock.patch('psycopg2.connect', return_value=connection_mock):
            classify_face(self.test_user, self.request, self.response)
            cursor_mock.execute.assert_called()
            connection_mock.commit.assert_called()
            cursor_mock.close.assert_called()
            connection_mock.close.assert_called()
            self.assertTrue(self.test_user.save.called)

            # messages = list(get_messages(self.request.wsgi_request))
            # self.assertEqual(str(messages[0]), 'Shares have been saved on the two different servers.') 

            # self.request.redirect.assert_called_with('/')
    
    @patch('helios_auth.views.get_user')
    def test_classify_face_view(self, mock_get_user):
        """ This unit test checks if the classify_face view saves the sets of shares correctly in the database servers, and returns the expected message (integrated with classify_face function). """
        print("===========================================================================================================================================")
        print("")
        print("Unit Test: test_classify_face_view")
        print("This unit test checks if the classify_face view saves the sets of shares correctly in the database servers, and returns the expected message (integrated with classify_face function).")
        existing_user = User.objects.filter(user_id='XXXXXXXXXXYYYYYYYYYYYYYY@gmail.com').first()
        if existing_user:
            existing_user.delete()
        test_user = User.objects.create(user_id='XXXXXXXXXXYYYYYYYYYYYYYY@gmail.com')
        mock_get_user.return_value = test_user
        
        connection_mock = MagicMock()
        cursor_mock = connection_mock.cursor.return_value
        test_user.save = MagicMock()

        with unittest.mock.patch('psycopg2.connect', return_value=connection_mock):
            url = reverse('classify_face')
            response = self.client.post(url, {'response': base64_image_correct})
            cursor_mock.execute.assert_called()
            connection_mock.commit.assert_called()
            cursor_mock.close.assert_called()
            connection_mock.close.assert_called()
            self.assertTrue(test_user.save.called)

        # print(response.content.decode())
        self.assertTrue('redirect_url' in response.content.decode())
        self.assertTrue('message1' in response.content.decode())
        self.assertEqual(response.json()['redirect_url'], '/')
        self.assertEqual(response.json()['message1'], 'Registration susccessful. You can now log in.')
    
    def run(self, result=None):
        super().run(result)

        if result.wasSuccessful():
            print("Result: Success ✅ ") 
            print("")
            # print("===============================================")
        else:
            print("Result: Failure ❌ ")
            print("")
            # print("===============================================")


        


        
    
    




    # def test_get_other_shares(self):
    #     user_email = 'testinghelios1234@gmail.com'
    #     url = reverse('get_other_shares')
    #     response = self.client.get(url, {user_email: ''})
    #     # response = self.client.get(url)
    #     # self.assertEqual(response.status_code, 200)
    #     # self.assertEqual(response['Content-Type'], 'application/json')
    #     response_data = json.loads(response.content)
    #     c1_string = response_data['c1']
    #     c2_string = response_data['c2']
    #     r1_string = response_data['r1']

    #     connection = psycopg2.connect(
    #         host="localhost",
    #         port="5433",
    #         database="postgresdb",
    #         user="postgresadmin",
    #         password="admin123"
    #     )
    #     cursor = connection.cursor()
    #     email_hash = hashlib.sha256(
    #         str(user_email).encode()).hexdigest()
    #     cursor.execute(
    #         "SELECT file1, file2, file3 FROM user_face_shares WHERE email_hash = %s", (email_hash,))
    #     record = cursor.fetchone()  # Fetch the first matching record
    #     expected_c1_value, expected_c2_value, expected_r1_value = record
    #     cursor.close()

    #     self.assertEqual(c1_string, expected_c1_value)
    #     self.assertEqual(c2_string, expected_c2_value)
    #     self.assertEqual(r1_string, expected_r1_value)

