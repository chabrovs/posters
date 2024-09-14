from django.test import TestCase, SimpleTestCase
from .business_logic.poster_image_name_logic import GetUniqueImageName, SetUniqueImageNameException, DEFAULT_IMAGE_FULL_PATH
from .business_logic.phone_number_logic import standardize_phone_number
from .business_logic.poster_currency_logic import validate_currency, ValidationError
from .business_logic.posters_lite_logic import get_expire_timestamp, POSTERLITE_LIFETIME
from .business_logic.process_images_logic import ensure_image_exists, get_fk_field_name, get_fk_field_name
from posters_app.models import Poster, PosterCategories, PosterImages, PosterLite, PosterLiteImages
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from decimal import Decimal
import datetime
from django.utils import timezone

# Create your tests here.


class TestPosterImageNameLogic(SimpleTestCase):
    def setUp(self) -> None:
        self.test_data_default = {
            1: "test_image_name.jpg",
            2: "test_image_name.png",
            3: "test_image_name3.png",
        }

        return super().setUp()

    def test_set_unique_image_name_default(self) -> None:
        for case_number, test_data in self.test_data_default.items():
            self.assertNotEqual(GetUniqueImageName(media_subdirectory='poster_images').__call__(
                instance=None, image_filename=test_data), test_data)


class TestPhoneNumberLogic(SimpleTestCase):
    def setUp(self) -> None:
        self.test_data_default = {
            1: ('+79568457896', '+7 956 845-78-96'),
            2: ('79568457896', '+7 956 845-78-96'),
            3: ('89568457896', '+7 956 845-78-96'),
        }

        return super().setUp()

    def test_standardize_phone_number(self) -> None:
        for case_number, test_data in self.test_data_default.items():
            self.assertEqual(standardize_phone_number(
                test_data[0]), test_data[1])


class TestPosterLiteLogic(SimpleTestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_get_expire_timestamp(self) -> None:
        current_time = timezone.now()
        set_delta = POSTERLITE_LIFETIME
        expected_expire_timestamp = current_time + set_delta
        tested_method_expire_timestamp = get_expire_timestamp()
        abs_time_difference_in_seconds = abs(
            (expected_expire_timestamp - tested_method_expire_timestamp).total_seconds())

        self.assertAlmostEqual(abs_time_difference_in_seconds, 0, delta=1)


class TestPosterCurrencyLogic(SimpleTestCase):
    def setUp(self) -> None:
        self.test_data_default = {
            1: 'USD',
            2: 'RUB',
            3: 'GBP',
        }
        self.test_data_exception = {
            1: 'PPP',
            2: 'WWW',
            3: 'OPW',
        }
        return super().setUp()

    def test_validate_currency_pass(self) -> None:
        for case_number, test_data in self.test_data_default.items():
            self.assertRaises(ValidationError, validate_currency(test_data))

    def test_validate_currency_pass(self) -> None:
        for case_number, test_data in self.test_data_exception.items():
            try:
                self.assertRaises(
                    ValidationError, validate_currency(test_data))
            except ValidationError:
                pass


class TestPosterModels(TestCase):
    def setUp(self) -> None:
        PosterCategories.objects.create(name='Goods')
        PosterCategories.objects.create(name='Toys')
        PosterCategories.objects.create(name='Hardware')
        User.objects.create(username='sergei')
        Poster.objects.create(
            owner=User.objects.get(username='sergei'),
            phone_number='+79265847523',
            email='chabrovs.dev@gmail.com',
            header='An old computer',
            description="I would like to sell my old computer",
            category=PosterCategories.objects.get(name='Hardware'),
            price=Decimal(420.2),
            currency='USD',
        )
        return super().setUp()

    def test_poster_categories(self) -> None:
        categories = PosterCategories.objects.all()
        current_categories = ['Goods', 'Toys', 'Hardware']
        for cat_name in categories:
            self.assertIn(cat_name.name, current_categories)

    def test_User(self) -> None:
        username = User.objects.get(username='sergei')  # Username
        user_id = User.objects.filter(username='sergei').values_list(
            'id', flat=True).first()  # User id

        self.assertEqual(username.__str__(), 'sergei')
        self.assertEqual(user_id, 5)

    def test_poster(self) -> None:
        my_poster = Poster.objects.get(
            owner=User.objects.get(username='sergei').id)
        # my_poster = Poster.objects.get(id=2)
        my_poster_owner = my_poster.owner
        my_poster_status = my_poster.status
        my_poster_created = my_poster.created
        my_poster_deleted = my_poster.deleted
        my_poster_phone_number = my_poster.phone_number
        my_poster_email = my_poster.email
        my_poster_client = my_poster.client
        my_poster_header = my_poster.header
        my_poster_description = my_poster.description
        my_poster_category = my_poster.category
        my_poster_price = my_poster.price
        my_poster_currency = my_poster.currency

        # Value checking
        self.assertEqual(my_poster_owner, User.objects.get(username='sergei'))
        self.assertEqual(my_poster_status, True)
        self.assertEqual(my_poster_phone_number, '+7 926 584-75-23')
        self.assertEqual(my_poster_email, 'chabrovs.dev@gmail.com')
        self.assertEqual(my_poster_client, None)
        self.assertEqual(my_poster_header, 'An old computer')
        self.assertEqual(my_poster_description,
                         'I would like to sell my old computer')
        self.assertEqual(my_poster_category,
                         PosterCategories.objects.get(name='Hardware'))
        self.assertEqual(my_poster_price, round(Decimal(420.2000), 5))
        self.assertEqual(my_poster_currency, 'USD')

        # Type checking
        self.assertEqual(isinstance(my_poster_owner, User), True)
        self.assertEqual(isinstance(my_poster_status, bool), True)
        self.assertEqual(isinstance(my_poster_phone_number, str), True)
        self.assertEqual(isinstance(
            my_poster_category, PosterCategories), True)
        self.assertEqual(isinstance(my_poster_price, Decimal), True)
        self.assertEqual(isinstance(my_poster_currency, str), True)


class TestPosterLiteModels(TestCase):
    def setUp(self):
        current_time = datetime.datetime.now(datetime.timezone.utc)
        time_delta = datetime.timedelta(days=14)
        PosterCategories.objects.create(name='Hardware')
        Session.objects.create(
            session_data='some session data',
            expire_date=current_time + time_delta
        )
        PosterLite.objects.create(
            owner=Session.objects.first(),
            phone_number='+79265553322',
            email='chabrovs.dev@gmail.com',
            header='An old phone',
            description="I would like to sell my old phone",
            category=PosterCategories.objects.get(name='Hardware'),
            price=Decimal(180.5),
            currency='GBP',
        )

        return super().setUp()

    def test_poster_lite(self) -> None:
        my_poster = PosterLite.objects.first()
        # my_poster = Poster.objects.get(id=2)
        my_poster_owner = my_poster.owner
        my_poster_status = my_poster.status
        my_poster_created = my_poster.created
        my_poster_deleted = my_poster.deleted
        my_poster_phone_number = my_poster.phone_number
        my_poster_email = my_poster.email
        my_poster_client = my_poster.client
        my_poster_header = my_poster.header
        my_poster_description = my_poster.description
        my_poster_category = my_poster.category
        my_poster_price = my_poster.price
        my_poster_currency = my_poster.currency

        # Value checking
        self.assertEqual(my_poster_owner, Session.objects.first())
        self.assertEqual(my_poster_status, True)
        self.assertEqual(my_poster_phone_number, '+7 926 555-33-22')
        self.assertEqual(my_poster_email, 'chabrovs.dev@gmail.com')
        self.assertEqual(my_poster_client, None)
        self.assertEqual(my_poster_header, 'An old phone')
        self.assertEqual(my_poster_description,
                         'I would like to sell my old phone')
        self.assertEqual(my_poster_category,
                         PosterCategories.objects.get(name='Hardware'))
        self.assertEqual(my_poster_price, round(Decimal(180.5), 5))
        self.assertEqual(my_poster_currency, 'GBP')

        # Type checking
        self.assertEqual(isinstance(my_poster_owner, Session), True)
        self.assertEqual(isinstance(my_poster_status, bool), True)
        self.assertEqual(isinstance(my_poster_phone_number, str), True)
        self.assertEqual(isinstance(
            my_poster_category, PosterCategories), True)
        self.assertEqual(isinstance(my_poster_price, Decimal), True)
        self.assertEqual(isinstance(my_poster_currency, str), True)


class TestImageProcessLogic(TestCase):
    def setUp(self):
        # Create a poster instance for testing
        PosterCategories.objects.create(name='Hardware')
        User.objects.create(username='sergei2')
        self.poster = Poster.objects.create(
            owner=User.objects.get(username='sergei2'),
            phone_number='+79265847523',
            email='chabrovs.dev@gmail.com',
            header='An old computer',
            description="I would like to sell my old computer",
            category=PosterCategories.objects.get(name='Hardware'),
            price=Decimal(420.2),
            currency='USD',
        )
        return super().setUp()

    def test_get_fk_field_name(self) -> None:
        self.assertEqual(get_fk_field_name(Poster, PosterImages), 'poster_id')

    def test_adds_default_image_when_no_images_exist(self):
        """
        Test that the function adds a default image when no images exist for a poster.
        """
        # Ensure no images exist for this poster
        self.assertFalse(PosterImages.objects.filter(
            poster_id=self.poster).exists())

        # Call the function to ensure a default image
        ensure_image_exists(
            instance=self.poster,
            related_field='poster_images',
            image_model=PosterImages,
        )

        # # Verify that the default image has been added
        self.assertTrue(PosterImages.objects.filter(
            poster_id=self.poster).exists())
        default_image = PosterImages.objects.get(poster_id=self.poster)
        self.assertEqual(default_image.image_path, DEFAULT_IMAGE_FULL_PATH)

    def test_raises_error_if_no_foreign_key_relationship(self):
        """
        Test that the function raises an error if no foreign key relationship is found in the image model.
        """
        # Define a model without a relationship to Poster (for testing purposes)
        class DummyMeta:
            fields = ['i_do_not_exist']
        class DummyImageModel:
            _meta = DummyMeta()

        # Ensure an error is raised when the function is called with an invalid image model
        with self.assertRaises(ValueError):
            ensure_image_exists(
                instance=self.poster,
                related_field='poster_images',
                image_model=DummyImageModel,  # This model doesn't have a ForeignKey to Poster
                default_image_path=DEFAULT_IMAGE_FULL_PATH
            )

    def test_does_not_add_image_if_images_exist(self):
        """
        Test that the function does not add a new default image if images already exist.
        """
        # Create an image for the poster
        PosterImages.objects.create(poster_id=self.poster, image_path='path/to/existing/image.jpg')

        # Call the function
        ensure_image_exists(
            instance=self.poster,
            related_field='poster_images',
            image_model=PosterImages,
            default_image_path=DEFAULT_IMAGE_FULL_PATH
        )

        # Ensure no new image was added
        self.assertEqual(PosterImages.objects.filter(poster_id=self.poster).count(), 1)
        existing_image = PosterImages.objects.get(poster_id=self.poster)
        self.assertEqual(existing_image.image_path, 'path/to/existing/image.jpg')