from django.test import TestCase
from .business_logic.poster_image_name_logic import get_unique_image_name, SetUniqueImageNameException
from .business_logic.phone_number_logic import standardize_phone_number
from .business_logic.poster_currency_logic import validate_currency, ValidationError
from posters_app.models import Poster, PosterCategories, PosterImages
from django.contrib.auth.models import User
from decimal import Decimal
# Create your tests here.

class TestPosterImageNameLogic(TestCase):
    def setUp(self) -> None:
        self.test_data_default = {
            1: "test_image_name.jpg",
            2: "test_image_name.png",
            3: "test_image_name3.png",
        }

        return super().setUp()
    
    def test_set_unique_image_name_default(self) -> None:
        for case_number, test_data in self.test_data_default.items():
            self.assertNotEqual(get_unique_image_name(instance=None, image_filename=test_data), test_data)


class TestPhoneNumberLogic(TestCase):
    def setUp(self) -> None:
        self.test_data_default = {
            1: ('+79568457896', '+7 956 845-78-96'),
            2: ('79568457896','+7 956 845-78-96'),
            3: ('89568457896', '+7 956 845-78-96'),
        }

        return super().setUp()
    
    def test_standardize_phone_number(self) -> None:
        for case_number, test_data in self.test_data_default.items():
            self.assertEqual(standardize_phone_number(test_data[0]), test_data[1])


class TestPosterCurrencyLogic(TestCase):
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
                self.assertRaises(ValidationError, validate_currency(test_data))
            except ValidationError:
                pass


class TestPosterModels(TestCase):
    def setUp(self) -> None:
        PosterCategories.objects.create(name='Goods')
        PosterCategories.objects.create(name='Toys')
        PosterCategories.objects.create(name='Hardware')
        Poster.objects.create(
            owner=User.objects.get(id=1),
            phone_number='+79265847523',
            email='chabrovs.dev@gmail.com',
            header='An old computer',
            description="I would like to sell my old computer",
            category=PosterCategories.objects.get(name='Hardware').id,
            price = Decimal(420.20),
            currency = 'USD',
        )
        return super().setUp()
    
    def test_poster_categories(self) -> None:
        goods = PosterCategories.objects.all()
        posters = PosterCategories.objects.all()
        print(goods)
        print(posters)