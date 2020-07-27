import io
import unittest
import os
from unittest import mock
from collections import deque


import batch


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
        bug_lines = [
            "l_bad barrier ;[01/07/2020 17:01] (sec-0021-0008);-82432.3;85.1157;-28219.9;-0.166068;-0.766375\n",
            "n_collisions by road ;[03/07/2020 11:16] (sec-0020-0016);-77652.6;66.7637;-62775.1;0.323015;-0.789071\n",
            "h_empty curve 1 ;[07/07/2020 10:32] (sec-0018-0009);-70468.5;96.2397;-34436.6;-0.0306614;-0.0693749\n",
            "u_missing invis wall ;[01/07/2020 11:37] (sec-0020-0008);-79469.4;76.7075;-31942.2;2.86773;-0.435756\n",
            "i_bike w/o collision ;[30/06/2020 16:11] (sec-0019-0008);-72681.6;76.9917;-31622.3;-1.51981;-0.599002\n"
        ]
        formats_correct = batch.check_batch_formats(bug_lines)
        self.assertTrue(formats_correct)

    def test_check_batch_formats_all(self):
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
        formats_correct = batch.check_batch_formats(bug_lines)
        self.assertTrue(formats_correct)

    def test_check_batch_formats_wrong(self):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            bug_lines = [
                "m_reportname 1 ;[01/07/2020 17:01] (sec-0021-0008);-82432.3;85.1157;-28219.9;-0.166068;-0.766375\n",
                "m_reportname 2 ;[03/07/2020 11:16] (sec-0020-0016);-77652.6;66.7637;-62775.1;0.323015;-0.789071\n",
                "m_reportname 3 ;[07/07/2020 10:32] (sec-0018-0009);-70468.5;96.2397;-34436.6;-0.0306614;-0.0693749\n",
                "u_reportname 4 ;[01/07/2020 11:37] (sec-0020-0008);-79469.4;76.7075;-31942.2;2.86773;-0.435756\n",
                "a_reportname 5 ;[30/06/2020 16:11] (sec-0019-0008);-72681.6;76.9917;-31622.3;-1.51981;-0.599002\n"
            ]
            formats_correct = batch.check_batch_formats(bug_lines)
            self.assertFalse(formats_correct)

    def test_batch_images_present(self):
        all_bugs = deque()
        temp_bug = deque()
        temp_bug.append("m_missing col on pylon ;[02/07/2020 10:18] ("
                              "sec-0021-0008);-80950.5;78.7729;-30575.7;2.74347;-0.419274")
        all_bugs.append(temp_bug)
        with open("bug_20200702_101838_-80950_79_-30576.jpg", "w"):
            pass
        images_missing = batch.check_batch_images(all_bugs, '.')
        os.remove("bug_20200702_101838_-80950_79_-30576.jpg")
        self.assertFalse(images_missing)

    @mock.patch('builtins.input', side_effect=["q"])
    def test_batch_images_missing(self, mock_input):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            all_bugs = deque()
            temp_bug = deque()
            temp_bug.append("m_missing col on pylon ;[02/07/2020 10:18] ("
                            "sec-0021-0008);-80950.5;78.7729;-30575.7;2.74347;-0.419274")
            all_bugs.append(temp_bug)
            with open("temp_image.jpg", "w"):
                pass
            images_missing = batch.check_batch_images(all_bugs, '.')
            os.remove("temp_image.jpg")
            self.assertTrue(images_missing)

    @mock.patch('builtins.input', side_effect=["y", "y", "n"])
    def test_batch_images_repeated(self, mock_input):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            all_bugs = deque()
            temp_bug = deque()
            temp_bug.append("m_missing col on pylon ;[02/07/2020 10:18] ("
                            "sec-0021-0008);-80950.5;78.7729;-30575.7;2.74347;-0.419274")
            all_bugs.append(temp_bug)
            with open("temp_image.jpg", "w"):
                pass
            images_missing = batch.check_batch_images(all_bugs, '.')
            os.remove("temp_image.jpg")
            self.assertFalse(images_missing)

