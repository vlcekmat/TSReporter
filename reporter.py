from collections import deque
from chromedrivers import check_for_duplicates, upload_to_mantis, WebDriver
from selenium.common.exceptions import SessionNotCreatedException, NoSuchWindowException, WebDriverException
from information_compile import determine_bug_category, extract_asset_path
import copy


# uploads stuff to Mantis or calls other methods to do that
def report_bug(project, log_lines, version, images_folder_path, assign, username, password, browser='chrome'):
    log_first = log_lines.pop()
    print(f'CURRENT BUG: {log_first}')
    log_lines.append(log_first)
    category = determine_bug_category(log_first)
    error_message = "Don't interact with browser during the process, trying again..."

    tried_duplicates = False
    duplicate_found = False
    a_path = None
    d_info = None
    if 'A' in category.upper():
        a_path = input('Enter DEBUG INFO or path to the asset:\n> ')
        if 'DEBUG INFO' or 'Position' or 'Object' in a_path:
            d_info = a_path
            a_path = extract_asset_path(a_path)

    while True:
        try:
            web_driver = WebDriver(browser=browser)
            if not tried_duplicates:
                duplicate_found = check_for_duplicates(
                    username, password, bug_description=log_first,
                    asset_path=a_path, web_driver=web_driver, browser=browser)
                tried_duplicates = True
            if not duplicate_found:
                use_log_lines = copy.deepcopy(log_lines)
                upload_to_mantis(
                    version, images_folder_path, category, use_log_lines,
                    assign, project, username, password, browser,
                    path_to_asset=a_path, debug_info=d_info, web_driver=web_driver
                )
            else:
                print('Reporting not needed')
                web_driver.get_driver().quit()
            break
        except SessionNotCreatedException:
            print(error_message)
        except NoSuchWindowException:
            print(error_message)
        except WebDriverException:
            print(error_message)
        except AttributeError:
            print(error_message)
        except TypeError:
            print(error_message)
        except NameError:
            print(error_message)
