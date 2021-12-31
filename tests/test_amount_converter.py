from unittest import TestCase

from service import AmountConverter


class AmountConverterTests(TestCase):
    def assertFloatEquals(self, expected: float, actual: float):
        self.assertTrue(abs(expected - actual) <= 0.005, f'{actual} does not match {expected}')

    def test_serializing_values(self):
        self.assertFloatEquals(0.5,   AmountConverter.serialize_value('1/2'))
        self.assertFloatEquals(0.333, AmountConverter.serialize_value('1/3'))
        self.assertFloatEquals(0.75,  AmountConverter.serialize_value('3/4'))
        self.assertFloatEquals(0.571, AmountConverter.serialize_value('4/7'))
        self.assertFloatEquals(3.0, AmountConverter.serialize_value('3'))
        self.assertFloatEquals(3.25, AmountConverter.serialize_value('3 1/4'))
        self.assertFloatEquals(7.75, AmountConverter.serialize_value('31/4'))

    def test_deserializing_values(self):
        self.assertEqual('1/2',   AmountConverter.deserialize_value(0.5))
        self.assertEqual('1/3', AmountConverter.deserialize_value(0.333))
        self.assertEqual('3/4',  AmountConverter.deserialize_value(0.75))
        self.assertEqual('4/7', AmountConverter.deserialize_value(0.571))
        self.assertEqual('5', AmountConverter.deserialize_value(5.00))
        self.assertEqual('3 1/4', AmountConverter.deserialize_value(3.25))
