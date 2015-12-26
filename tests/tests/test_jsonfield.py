from decimal import Decimal
from django.test import TestCase
from ..models import JsonTestModel, get_default


class TestSendMail(TestCase):
    def test_default(self):
        obj = JsonTestModel()
        self.assertEqual(obj.json_1, None)
        self.assertEqual(obj.json_2, [])
        self.assertEqual(obj.json_3, {})
        self.assertEqual(obj.json_4, get_default())
        self.assertEqual(obj.json_5, {'a': 1})
        self.assertEqual(obj.json_6, None)
        self.assertEqual(obj.json_7, [])
        self.assertEqual(obj.json_8, {})
        self.assertEqual(obj.json_9, get_default())
        self.assertEqual(obj.json_10, {'a': 1})
        self.assertEqual(obj.json_11, None)
        self.assertEqual(obj.json_12, None)

    def test_save_load(self):
        obj1 = JsonTestModel()
        obj1.save()
        obj2 = JsonTestModel.objects.get(pk=obj1.pk)
        for f in ('json_1', 'json_2', 'json_3', 'json_4', 'json_5',
                  'json_6', 'json_7', 'json_8', 'json_9', 'json_10',
                  'json_11', 'json_12'):
            self.assertEqual(getattr(obj1, f), getattr(obj2, f))

    def test_float_and_deciaml(self):
        obj1 = JsonTestModel(json_1=[1.1], json_11=[Decimal('1.1'), 1.2])
        obj1.save()
        obj2 = JsonTestModel.objects.get(pk=obj1.pk)
        self.assertIsInstance(obj2.json_1[0], float)
        self.assertIsInstance(obj2.json_11[0], Decimal)
        self.assertIsInstance(obj2.json_11[1], Decimal)
