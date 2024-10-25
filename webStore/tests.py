from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import User


class UserModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="Grzesiuniunia",
            email="golon338@gmail.com",
            password="#sianko@123",
            first_name="Gregory",
            last_name="Befsztyk",
            phone_number="515-167-594",
            birthday="2000-01-01"
        )

    def test_validation_positive_scenario(self):
        self.assertNotEqual(self.user, None)
        self.assertEqual(self.user.first_name, "Gregory")
        self.assertFalse(self.user.is_admin)
        self.assertRegex(self.user.phone_number,
                         r'^\d{3}-\d{3}-\d{3}$')
        self.assertRegex(self.user.birthday,
                         r'^\d{4}-\d{2}-\d{2}$')

    def test_user_gender_validation(self):
        incorrect_gender = 'KASZTAN'

        with self.assertRaises(ValidationError) as error:
            self.user.gender = incorrect_gender
            self.user.clean()

        self.assertEqual(
            error.exception.messages,
            [f"{incorrect_gender} is not valid gender"]
        )
