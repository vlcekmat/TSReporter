import unittest
import io
import sys
import os
from unittest import mock
from collections import deque

import bugs


class TestReadBugLines(unittest.TestCase):
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
        self.assertEqual(len(all_bugs[0]), 2)
        self.assertEqual(all_bugs[1][0][0], '!')


class TestReadBugsFile(unittest.TestCase):
    def test_read_bugs_file_missing(self):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            if os.path.isfile("bugs.txt"):
                os.remove("bugs.txt")
            bug_lines = bugs.read_bugs_file('.', sys.stdout)
            self.assertIsNone(bug_lines)

    def test_read_bugs_file_empty(self):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            with open("bugs.txt", "w"):
                pass
            bug_lines = bugs.read_bugs_file('.', sys.stdout)
            os.remove("bugs.txt")
            self.assertIsNone(bug_lines)
            self.assertEqual(fake_stdout.getvalue(), "No bugs to report from bugs.txt\n")

    def test_read_bugs_file_dot(self):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            with open("bugs.txt", "w") as bugs_file:
                bugs_file.write(".report")
            bug_lines = bugs.read_bugs_file('.', sys.stdout)
            os.remove("bugs.txt")
            self.assertIsNone(bug_lines)

    def test_read_bugs_file_good(self):
        with open("bugs.txt", "w") as bugs_file:
            bugs_file.write("report0\nreport1\n")
        bug_lines = bugs.read_bugs_file('.', sys.stdout)
        os.remove("bugs.txt")
        self.assertEqual(bug_lines[0], "report0\n")
        self.assertEqual(bug_lines[1], "report1\n")


class TestArchiveBug(unittest.TestCase):
    def test_archive_bug(self):
        with open("bugs.txt", "w") as bugs_file:
            bugs_file.write("report1\nreport2\nreport3\n")
        with open("bugs_archive.txt", "w") as bugs_file:
            bugs_file.write("report0\n")
        current_bug = deque()
        current_bug.append("report1\n")
        current_bug.append("report2\n")
        bugs.archive_bug(current_bug, '.')
        with open("bugs.txt", "r") as bugs_file:
            bugs_final = bugs_file.readlines()
        with open("bugs_archive.txt", "r") as bugs_file:
            archive_final = bugs_file.readlines()
        os.remove("bugs.txt")
        os.remove("bugs_archive.txt")
        self.assertEqual(bugs_final[0], "report3\n")
        self.assertEqual(archive_final[0], "report0\n")
        self.assertEqual(archive_final[2], "report2\n")

