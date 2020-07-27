import unittest
from unittest import mock

import utils


class TestUtils(unittest.TestCase):
    def test_is_int_yes(self):
        a = utils.is_int('1234')
        self.assertTrue(a)

    def test_is_int_no(self):
        b = utils.is_int("not an int")
        self.assertFalse(b)

    def test_ask_mode_first(self):
        user_input = "1"
        with mock.patch('builtins.input', side_effect=user_input):
            use_mode = utils.ask_use_mode()
            self.assertEqual(use_mode, 1)

    @mock.patch('builtins.input', side_effect=["aaa", "9", "hue1hue", "3 abcd 1", "4"])
    def test_ask_mode_multiple(self, mock_input):
        use_mode = utils.ask_use_mode()
        self.assertEqual(use_mode, 4)