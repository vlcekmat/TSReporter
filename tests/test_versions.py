import io
import os
import unittest
import shutil
from unittest import mock

import versions


class TestFindGameVersion(unittest.TestCase):
    def test_find_game_version_missing(self):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            with open("temp_game_log.txt", "w") as temp_log_file:
                temp_log_file.write("line1\nline2\3xaxaxaxa\n")
            version = versions.find_game_version("temp_game_log.txt")
            os.remove("temp_game_log.txt")
            self.assertEqual(version, -1)

    def test_find_game_version_present(self):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            with open("temp_game_log.txt", "w") as temp_log_file:
                temp_log_file.write(
                    r"""************ : log created on : Monday June 29 2020 @ 10:16:51
00:00:00.000 : [sys] running on x86_64 / Windows 10 x64 (version 10.0)
00:00:00.000 : [sys] Command line:  C:\TRUNK\ETS2\bin\win_x64_release\eurotrucks.exe -unlimitedlog -full_dump
00:00:00.000 : [cpu] CPU0: GenuineIntel [Intel(R) Core(TM) i7 CPU 930  @ 2.80GHz] with 4 cores (8 threads) at ~2834MHz.
00:00:00.000 : [sys] using 3 worker thread(s)
00:00:01.730 : Euro Truck Simulator 2 init ver.1.11 (rev. d1d813806abd)
00:00:01.731 : [gfx] Selected rendering device: gl"""
                )
            version = versions.find_game_version("temp_game_log.txt")
            os.remove("temp_game_log.txt")
            self.assertEqual(version, "1.11")


class TestFindTrunkVer(unittest.TestCase):
    def test_find_trunk_ver_missing(self):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            if os.path.isfile("ATS/CURRENT"):
                os.remove("ATS/CURRENT")
            trunk_ver = versions.find_trunk_version('A', '.')
            self.assertEqual(trunk_ver, -1)

    def test_find_trunk_ver_good(self):
        with mock.patch('sys.stdout', new_callable=io.StringIO) as fake_stdout:
            if not os.path.exists("ATS"):
                os.mkdir("ATS")
            with open("ATS/CURRENT", "w") as current_path:
                current_path.write("123456\n")
            trunk_ver = versions.find_trunk_version('A', '.')
            shutil.rmtree("ATS")
            self.assertEqual(trunk_ver, "[trunk at revision 123456]")
