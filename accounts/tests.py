from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse

from rest_framework.utils import json


class UserRegistrationTestCase(APITestCase):
    url = reverse("accounts:register")
    url_login = reverse("token_obtain_pair")

    def test_user_registration(self):
        """
            Register with happy path
        """

        data = {
            "username" : "admin",
            "password": "admin"
        }

        response = self.client.post(self.url, data)
        self.assertEqual(201, response.status_code)

    def test_user_invalid_password(self):
        """
            Invalid password registration.
        """

        data = {
            "username" : "admin",
            "password": "1"
        }

        response = self.client.post(self.url, data)
        self.assertEqual(400, response.status_code)

    def test_user_unique_name(self):
        """
            Unique username test
        """

        self.test_user_registration()
        data = {
            "username" : "admin",
            "password": "dsfdf34"
        }

        response = self.client.post(self.url, data)
        self.assertEqual(400, response.status_code)

    def test_user_authenticated_registration(self):
        """
            Session login user must be restricted
        """

        self.test_user_registration()
        self.client.login(username = 'admin', password = 'admin123')

        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)


    def test_user_authenticated_token_registration(self):
        """
            User with token must be restricted
        """

        self.test_user_registration()

        data = {
            "username": "admin",
            "password": "admin123"
        }

        response = self.client.post(self.url_login, data)
        self.assertEqual(200 , response.status_code)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION= 'Bearer '+ token)
        response_2 = self.client.get(self.url)
        self.assertEqual(403, response_2.status_code)


class UserLogin(APITestCase):
    url_login = reverse("token_obtain_pair")

    def setUp(self):
        self.username = "admin"
        self.password = "pass123"
        self.user = User.objects.create_user(username = self.username, password=self.password)

    def test_user_token(self):
        response = self.client.post(self.url_login, {"username": "admin", "password": "test123"})
        self.assertEqual(200, response.status_code)
        self.assertTrue("access" in json.loads(response.content))

    def test_user_invalid_data(self):
        response = self.client.post(self.url_login, {"username": "asasdzxczxc", "password": "sifre1234"})
        self.assertEqual(401, response.status_code)

    def test_user_empty_data(self):
        response = self.client.post(self.url_login, {"username": "", "password": ""})
        self.assertEqual(400, response.status_code)


class UserPasswordChange(APITestCase):
    url = reverse("account:change-password")
    url_login = reverse("token_obtain_pair")

    def setUp(self):
        self.username = "admin"
        self.password = "adminnewpass"
        self.user = User.objects.create_user(username = self.username, password=self.password)

    def login_with_token(self):
        data = {
            "username" : "admin",
            "password" : "adminnewpass"
        }

        response = self.client.post(self.url_login, data)
        self.assertEqual(200, response.status_code)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_is_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(401, response.status_code)

    def test_with_valid_informations(self):
        self.login_with_token()

        data = {
            "old_password": "sifre1234",
            "new_password": "asdasdas123456"
        }

        response = self.client.put(self.url, data)
        self.assertEqual(204, response.status_code)

    def test_with_wrong_informations(self):
        self.login_with_token()

        data = {
            "old_password": "asdasd",
            "new_password": "asdasdas123456"
        }

        response = self.client.put(self.url, data)
        self.assertEqual(400, response.status_code)

    def test_with_empty_informations(self):
        self.login_with_token()

        data = {
            "old_password": "",
            "new_password": ""
        }

        response = self.client.put(self.url, data)
        self.assertEqual(400, response.status_code)


class UserProfileUpdate(APITestCase):
    url = reverse("accounts:me")
    url_login = reverse("token_obtain_pair")

    def setUp(self):
        self.username = "admin"
        self.password = "sifre1234"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def login_with_token(self):
        data = {
            "username": "admin",
            "password": "sifre1234"
        }

        response = self.client.post(self.url_login, data)
        self.assertEqual(200, response.status_code)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_is_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(401, response.status_code)

    def test_with_valid_informations(self):
        self.login_with_token()

        data = {
            "id": 1,
            "first_name": "sdad",
            "last_name": "sdsda",
            "profile": {
                "id": 1,
                "about": "note",
                "twitter": "asdas"
            }
        }


        response = self.client.put(self.url, data, format='json')
        self.assertEqual(200, response.status_code)
        # print(json.loads(response.content))
        self.assertEqual(json.loads(response.content), data)

    def test_with_empty_informations(self):
        self.login_with_token()

        data = {
            "id": 1,
            "first_name": "",
            "last_name": "",
            "profile": {
                "id": 1,
                "note": "",
                "twitter": ""
            }
        }

        response = self.client.put(self.url, data, format='json')
        self.assertEqual(200, response.status_code)
