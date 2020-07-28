import io
import unittest
from unittest import mock

import sector_seek


class TestSectorSeek(unittest.TestCase):
    def test_clean_sector(self):
        sec = sector_seek.clean_sector("sign without collision ;[02/07/2020 11:39] "
                                       "(sec-0021-0008);-80542.1;61.4683;-30887.9;-2.91773;-0.518367")
        self.assertEqual(sec, "sec-0021-0008")

    def test_request_sector_owner_ats(self):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            owner = sector_seek.request_sector_owner("sec-0023-0023", "A")
            self.assertEqual(owner, "nemiro")

    def test_request_sector_owner_wrong(self):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            owner = sector_seek.request_sector_owner("sec-0050-0000", "A")
            self.assertEqual(owner, "")

    @mock.patch('builtins.input', side_effect=["r"])
    def test_ask_asset_type_first(self, mock_input):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            a_type = sector_seek.ask_asset_type()
            self.assertEqual(a_type, 'r')

    @mock.patch('builtins.input', side_effect=["reeeeee", "1", "rvarcvrac", "r"])
    def test_ask_asset_type_multiple(self, mock_input):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            a_type = sector_seek.ask_asset_type()
            self.assertEqual(a_type, 'r')