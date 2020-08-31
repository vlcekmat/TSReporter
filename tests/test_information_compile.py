import unittest

import information_compile


class TestCleanDebugInfo(unittest.TestCase):
    def test_clean_debug_info_clean(self):
        debug_info = "DEBUG INFO: Object ' 0x3302ADF8C04729A5 " \
                     "'/model/vehicle/parked_cars_groups/static/parked_cars_5x1.pmd''  Position [" \
                     "-63941.2;59.5;-32751.8]  sec-0016-0009 "
        c_debug_info = information_compile.clean_debug_info(debug_info)
        self.assertEqual(debug_info, c_debug_info)

    def test_clean_debug_info_dirty(self):
        debug_info = "06:27:26.460 : DEBUG INFO: Object ' 0x3302ADF8C04729A5 " \
                     "'/model/vehicle/parked_cars_groups/static/parked_cars_5x1.pmd''  Position [" \
                     "-63941.2;59.5;-32751.8]  sec-0016-0009 "
        debug_info_good = "DEBUG INFO: Object ' 0x3302ADF8C04729A5 " \
                          "'/model/vehicle/parked_cars_groups/static/parked_cars_5x1.pmd''  Position [" \
                          "-63941.2;59.5;-32751.8]  sec-0016-0009 "
        c_debug_info = information_compile.clean_debug_info(debug_info)
        self.assertEqual(debug_info_good, c_debug_info)


class TestDetermineBugCategory(unittest.TestCase):
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


class TestExtractAssetName(unittest.TestCase):
    def test_extract_location_filter(self):
        log_line = "m_bad barrier ;[01/07/2020 17:01] (sec-0021-0008);-82432.3;85.1157;-28219.9;-0.166068;-0.766375\n"
        loc_filter = information_compile.extract_location_filter(log_line)
        self.assertEqual(loc_filter, "(sec-0021-0008);-82")

    def test_extract_asset_name(self):
        asset_path = "/model2/building/logistic/parking_roof_01_ibe.pmd"
        asst_name = information_compile.extract_asset_name(asset_path)
        self.assertEqual(asst_name, "parking_roof_01_ibe")

    def test_extract_asset_path_long(self):
        debug_info = "06:27:26.460 : DEBUG INFO: Object ' 0x3302ADF8C04729A5 " \
                     "'/model/vehicle/parked_cars_groups/static/parked_cars_5x1.pmd''  Position [" \
                     "-63941.2;59.5;-32751.8]  sec-0016-0009 "
        asset_path = information_compile.extract_asset_path(debug_info)
        self.assertEqual(asset_path, "/model/vehicle/parked_cars_groups/static/parked_cars_5x1.pmd")

    def test_extract_asset_path_short(self):
        debug_info = "DEBUG INFO: Object ' 0x3302ADF8C04729A5 " \
                     "'/model/vehicle/parked_cars_groups/static/parked_cars_5x1.pmd''  Position [" \
                     "-63941.2;59.5;-32751.8]  sec-0016-0009 "
        asset_path = information_compile.extract_asset_path(debug_info)
        self.assertEqual(asset_path, "/model/vehicle/parked_cars_groups/static/parked_cars_5x1.pmd")
