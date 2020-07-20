from unittest import mock
import unittest
import io


import sector_seek
import utils
import versions


class TestCleanSector(unittest.TestCase):
    def test_clean_sector(self):
        sec = sector_seek.clean_sector("sign without collision ;[02/07/2020 11:39] (sec-0021-0008);-80542.1;61.4683;-30887.9;-2.91773;-0.518367")
        self.assertEqual(sec, "sec-0021-0008")

    def test_request_sector_owner_ats(self):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            owner = sector_seek.request_sector_owner("sec-0023-0023", "A")
            self.assertEqual(owner, "nemiro")


class TestUtils(unittest.TestCase):
    def test_is_int_yes(self):
        a = utils.is_int('1234')
        self.assertTrue(a)

    def test_is_int_no(self):
        b = utils.is_int("not an int")
        self.assertFalse(b)


class TestVersions(unittest.TestCase):

    def test_get_project_good(self):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            user_input = "1"
            with mock.patch('builtins.input', side_effect=user_input):
                version = versions.get_project_from_user()
            self.assertEqual(version, "ATS - INTERNAL")

    def test_get_project_repeated(self):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            user_input = "9\nabc\n4"
            with mock.patch('builtins.input', side_effect=user_input):
                version = versions.get_project_from_user()
            self.assertEqual(version, "ETS 2 - INTERNAL")


if __name__ == '__main__':
    unittest.main()
