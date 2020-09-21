from chromedrivers import DriverHandler, log_into_mantis
from upload import upload_to_mantis
from selenium.common.exceptions import SessionNotCreatedException, NoSuchWindowException, WebDriverException
from information_compile import determine_bug_category, extract_asset_path, extract_asset_name, extract_location_filter
import copy
from config import read_config

asset_path = None


def report_bug(project, log_lines, version, username, password, _driver_handler, priority=None,
               severity=None, late_image=None, prefix=None, rename_images=False, new_img_name=None):
    # oversees uploading to mantis using upload_to_mantis
    # used to call check_for_duplicates but GUI moved that to a different button
    browser = read_config("preferred browser")
    log_first = log_lines.popleft()
    log_lines.appendleft(log_first)
    category = determine_bug_category(log_first)

    error_message = "Don't interact with the browser during the process, trying again..."
    d_info = None
    a_path = asset_path
    if 'A' in category.upper() and a_path:
        if 'DEBUG INFO' in a_path or 'Position' in a_path or 'Object' in a_path:  # To accommodate only partial debug i.
            d_info = a_path
            a_path = extract_asset_path(a_path)
    while True:
        try:
            driver_handler = _driver_handler
            use_log_lines = copy.deepcopy(log_lines)
            upload_to_mantis(
                version, category, use_log_lines, project, username, password, browser,
                path_to_asset=a_path, debug_info=d_info, web_driver=driver_handler, priority=priority,
                severity=severity, late_image=late_image, prefix=prefix,
                rename_images=rename_images, new_img_name=new_img_name
            )
            break
        except (SessionNotCreatedException, NoSuchWindowException, WebDriverException,
                AttributeError, TypeError, NameError) as error:
            print(f'{error_message} {error}')
    return True


def check_for_duplicates(username, password, bug_description=None,
                         a_path=None, driver_handler=None):
    # opens mantis so the user can check for duplicates
    if not driver_handler.is_active():
        driver = DriverHandler(browser=read_config("preferred browser")).get_driver()
        log_into_mantis(driver, username, password)

    driver = driver_handler.get_driver()
    log_into_mantis(driver, username, password)
    if a_path and a_path != '':
        final_filter = extract_asset_name(a_path)
    else:
        final_filter = extract_location_filter(bug_description)

    driver.get('https://qa.scssoft.com/set_project.php?project_id=0')
    driver.find_element_by_xpath("//a[@class='btn btn-sm btn-primary btn-white btn-round']").click()  # reset button
    driver.find_element_by_id('filter-search-txt').send_keys(final_filter)  # filter box
    driver.find_element_by_xpath("//input[@value='Apply Filter']").click()  # apply filter button

# def batch_report_bugs(project, bugs_stack, version, username, password, browser='chrome'):
#     # This used to be the batch reporting mode. For now, it has been removed due to
#     # the prefix feature being added to the main mode
#     prefix = ask_for_prefix()
#     # This prefix will be added at the beginning of all summaries to save time
#     # eg. writing "State - City" at the beginning of each report
#     if prefix == "":
#         return False
#     reporter_driver = DriverHandler(headless=True, browser=browser)
#     log_into_mantis(reporter_driver.get_driver(), username, password)
#     while len(bugs_stack) > 0:
#         current_bug = bugs_stack.popleft()
#         split_bug = current_bug[0].split('_', maxsplit=1)
#         priority = get_full_priority(split_bug[0])
#         current_bug[0] = prefix + ''.join(split_bug[1:])
#         use_log_lines = copy.deepcopy(current_bug)
#         upload_to_mantis(
#             version, 'm', use_log_lines, "", project, username, password,
#             browser, web_driver=reporter_driver, priority=priority
#         )
#     return True
#
#
# def get_full_priority(priority):
#     # Dict of legal priorities
#     prio_dict = {
#         "l": "low",
#         "n": "normal",
#         "h": "high",
#         "u": "urgent",
#         "i": "immediate"
#     }
#     return prio_dict[priority]
