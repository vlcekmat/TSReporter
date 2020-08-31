import io
import unittest
from unittest import mock

import sector_seek


class TestSectorSeek(unittest.TestCase):
    def test_request_sector_owner_ats(self):
        # This uses an assigned sector that's out of the way, in canada. If unassigned, this case will break!
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            owner = sector_seek.request_sector_owner("sec-0023-0023", "A")
            self.assertEqual(owner, "nemiro")

    def test_request_sector_owner_wrong(self):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            owner = sector_seek.request_sector_owner("sec-0050-0000", "A")
            self.assertEqual(owner, "")


class TestCleanSector(unittest.TestCase):
    def test_clean_sector(self):
        sec = sector_seek.clean_sector("sign without collision ;[02/07/2020 11:39] "
                                       "(sec-0021-0008);-80542.1;61.4683;-30887.9;-2.91773;-0.518367")
        self.assertEqual(sec, "sec-0021-0008")


class TestFindAssignTo(unittest.TestCase):
    def test_assign_no_category(self):
        line = "report;stuff;stuff;blah"
        line2 = "a_report;stuff;stuff"
        assign_to = sector_seek.find_assign_to(line, "A")
        assign_to2 = sector_seek.find_assign_to(line2, "E")
        self.assertEqual(assign_to, "")
        self.assertEqual(assign_to2, "")

    def test_assign_good(self):
        # Not writing a test for map bug lines, sector owners change
        line = "av_report;stuff;stuff"
        line2 = "aa_report;stuff;stuff"
        assign_to = sector_seek.find_assign_to(line, "A")
        assign_to2 = sector_seek.find_assign_to(line2, "A")
        assign_to3 = sector_seek.find_assign_to(line2, "E")
        self.assertEqual(assign_to, "Arthur")
        self.assertEqual(assign_to2, "jupiter")
        self.assertEqual(assign_to3, "martin.vocet")
