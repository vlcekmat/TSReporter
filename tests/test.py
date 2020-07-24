from unittest import mock
import unittest
import io
from collections import deque


import sector_seek
import utils
import versions
import batch
import information_compile
import bugs


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


class TestInformationCompile(unittest.TestCase):
    def test_determine_bug_category_good(self):
        log_line = "m_Idaho - I50 - collisions by road ;[03/07/2020 11:16] (sec-0020-0016)" \
                   ";-77652.6;66.7637;-62775.1;0.323015;-0.789071 "
        category = information_compile.determine_bug_category(log_line)
        self.assertEqual(category, "m")

    def test_determine_bug_category_empty(self):
        log_line = "Idaho - I50 - collisions by road ;[03/07/2020 11:16] (sec-0020-0016)" \
                   ";-77652.6;66.7637;-62775.1;0.323015;-0.789071 "
        category = information_compile.determine_bug_category(log_line)
        self.assertEqual(category, "")

    def test_determine_bug_category_wrong(self):
        log_line = "test_collisions by road ;[03/07/2020 11:16] (sec-0020-0016)" \
                   ";-77652.6;66.7637;-62775.1;0.323015;-0.789071 "
        category = information_compile.determine_bug_category(log_line)
        self.assertEqual(category, "")

    def test_determine_bug_category_wrong2(self):
        log_line = "u_Idaho - I50 - collisions by road ;[03/07/2020 11:16] (sec-0020-0016)" \
                   ";-77652.6;66.7637;-62775.1;0.323015;-0.789071 "
        category = information_compile.determine_bug_category(log_line)
        self.assertEqual(category, "")


class TestBugs(unittest.TestCase):
    def test_read_bug_lines(self):
        bug_lines = [
            "m_bad barrier ;[01/07/2020 17:01] (sec-0021-0008);-82432.3;85.1157;-28219.9;-0.166068;-0.766375\n",
            ".barrier 2 ;[03/07/2020 11:16] (sec-0020-0016);-77652.6;66.7637;-62775.1;0.323015;-0.789071\n",
            "!note ;[03/07/2020 11:16] (sec-0020-0016);-77652.6;66.7637;-62775.1;0.323015;-0.789071\n",
            "m_empty curve 1 ;[07/07/2020 10:32] (sec-0018-0009);-70468.5;96.2397;-34436.6;-0.0306614;-0.0693749\n",
            "a_missing invis wall ;[01/07/2020 11:37] (sec-0020-0008);-79469.4;76.7075;-31942.2;2.86773;-0.435756\n",
            ".missing wall 2 ;[30/06/2020 16:11] (sec-0019-0008);-72681.6;76.9917;-31622.3;-1.51981;-0.599002\n"
        ]
        all_bugs = bugs.read_bug_lines(bug_lines)
        self.assertEqual(len(all_bugs), 4)
        self.assertEqual(len(all_bugs[1]), 2)
        self.assertEqual(all_bugs[0][0][0], '!')


class TestBatch(unittest.TestCase):
    @mock.patch('builtins.input', side_effect=["Spain - Malaga - ", "y"])
    def test_ask_prefix_first(self, mock_input):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            prefix = batch.ask_for_prefix()
            self.assertEqual(prefix, "Spain - Malaga - ")

    @mock.patch('builtins.input', side_effect=["Spion - Mlogolo:", "n", "Spain - Malaga - ", "y"])
    def test_ask_prefix_multiple(self, mock_input):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            prefix = batch.ask_for_prefix()
            self.assertEqual(prefix, "Spain - Malaga - ")

    def test_check_batch_formats_priorities(self):
        all_bugs = deque()
        bug_lines = [
            "l_bad barrier ;[01/07/2020 17:01] (sec-0021-0008);-82432.3;85.1157;-28219.9;-0.166068;-0.766375\n",
            "n_collisions by road ;[03/07/2020 11:16] (sec-0020-0016);-77652.6;66.7637;-62775.1;0.323015;-0.789071\n",
            "h_empty curve 1 ;[07/07/2020 10:32] (sec-0018-0009);-70468.5;96.2397;-34436.6;-0.0306614;-0.0693749\n",
            "u_missing invis wall ;[01/07/2020 11:37] (sec-0020-0008);-79469.4;76.7075;-31942.2;2.86773;-0.435756\n",
            "i_bike w/o collision ;[30/06/2020 16:11] (sec-0019-0008);-72681.6;76.9917;-31622.3;-1.51981;-0.599002\n"
        ]
        formats_correct = batch.check_batch_formats(bug_lines, all_bugs)
        self.assertTrue(formats_correct)

    def test_check_batch_formats_all(self):
        all_bugs = deque()
        bug_lines = [
            "l_bad barrier ;[01/07/2020 17:01] (sec-0021-0008);-82432.3;85.1157;-28219.9;-0.166068;-0.766375\n",
            ".bad barrier 2 ;[01/07/2020 17:02] (sec-0021-0008);-82340.5;91.6007;-28261.9;-0.379157;-0.95645\n",
            "n_collisions by road ;[03/07/2020 11:16] (sec-0020-0016);-77652.6;66.7637;-62775.1;0.323015;-0.789071\n",
            "!note;[07/07/2020 10:33] (sec-0018-0009);-70566.5;92.3923;-34778.2;1.13854;-0.0175388\n",
            "h_empty curve 1 ;[07/07/2020 10:32] (sec-0018-0009);-70468.5;96.2397;-34436.6;-0.0306614;-0.0693749\n",
            "u_missing invis wall ;[01/07/2020 11:37] (sec-0020-0008);-79469.4;76.7075;-31942.2;2.86773;-0.435756\n",
            ";[02/07/2020 10:48] (sec-0021-0007);-83974.6;148.276;-26514.5;-1.93963;-0.892012\n",
            "i_bike w/o collision ;[30/06/2020 16:11] (sec-0019-0008);-72681.6;76.9917;-31622.3;-1.51981;-0.599002\n"
        ]
        formats_correct = batch.check_batch_formats(bug_lines, all_bugs)
        self.assertTrue(formats_correct)

    def test_check_batch_formats_wrong(self):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            all_bugs = deque()
            bug_lines = [
                "m_reportname 1 ;[01/07/2020 17:01] (sec-0021-0008);-82432.3;85.1157;-28219.9;-0.166068;-0.766375\n",
                "m_reportname 2 ;[03/07/2020 11:16] (sec-0020-0016);-77652.6;66.7637;-62775.1;0.323015;-0.789071\n",
                "m_reportname 3 ;[07/07/2020 10:32] (sec-0018-0009);-70468.5;96.2397;-34436.6;-0.0306614;-0.0693749\n",
                "u_reportname 4 ;[01/07/2020 11:37] (sec-0020-0008);-79469.4;76.7075;-31942.2;2.86773;-0.435756\n",
                "a_reportname 5 ;[30/06/2020 16:11] (sec-0019-0008);-72681.6;76.9917;-31622.3;-1.51981;-0.599002\n"
            ]
            formats_correct = batch.check_batch_formats(bug_lines, all_bugs)
            self.assertFalse(formats_correct)


if __name__ == '__main__':
    unittest.main()
