from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError

from .models import User
from .forms import UserRegistrationForm


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

    def test_user_email_validation(self):
        potential_wrong_domain_tld = "kaczka"
        potential_incorrect_email = "poklosie"

        with self.assertRaises(ValidationError) as tld_error:
            self.user.email = self.user.email.replace(
                self.user.email[-3:], potential_wrong_domain_tld)
            self.user.clean()

        with self.assertRaises(ValidationError) as domain_error:
            self.user.email = potential_incorrect_email
            self.user.clean()

        self.assertEqual(
            domain_error.exception.messages,
            ["Email address has to contain at sign"]
        )
        self.assertEqual(
            tld_error.exception.messages,
            ["Given TLD not recognized"]
        )

    def test_user_phone_number_validation(self):
        wrong_number_length = "12345678912012310301"

        with self.assertRaises(ValidationError) as length_error:
            self.user.phone_number = wrong_number_length
            self.user.clean()

        self.assertEqual(
            length_error.exception.messages,
            ["Phone number without dashes must have length of 9 signs"]
        )


class UserRegistrationFormTest(TestCase):

    def setUp(self):
        self.current_users = User.objects.all()
        self.example_form_data= {
            'first_name': 'Jacek',
            'last_name': 'Wariacik',
            'email': 'newuser@example.com', #TODO To test
            'password': '#123SafePassword123',  #TODO to test
            'phone_number': '123123123',  #TODO to test
        }
        for user in self.current_users:
            if user.is_admin:
                self.admin_user = user
            else:
                print(f"Regular user: {user}")

    def test_user_registration_form_fields_uniqueness_validation(self):
        not_existing_email = "not_existing_one@gmail.com"
        email_filter = list(filter(lambda user: user.email != not_existing_email, self.current_users))
        if len(email_filter) == 0:
            form_data = {
                "email": not_existing_email
            }
        # TODO to be continued

    def test_user_registration_for_email_fields_uniqueness_validation(self):
        existing_email = self.admin_user.email
        if existing_email is not None:
            form_data ={
                "email": existing_email
            }
        # TODO to be continued

    class CategoryModelTest(TestCase):

        def setUp(self):
            pass

    class ProductModelTest(TestCase):

        def setUp(self):
            pass

    class RateModelTest(TestCase):

        def setUp(self):
            pass

    class OrderModelTest(TestCase):

        def setUp(self):
            pass

    class OrderProductModelTest(TestCase):

        def setUp(self):
            pass

    class ReactionModelTest(TestCase):

        def setUp(self):
            pass

    class UserProductVisibilityModelTest(TestCase):

        def setUp(self):
            pass

    class UserReactionVisibilityModelTest(TestCase):

        def setUp(self):
            pass
