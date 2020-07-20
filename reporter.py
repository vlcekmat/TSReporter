from collections import deque
from chromedrivers import check_for_duplicates, upload_to_mantis
from selenium.common.exceptions import SessionNotCreatedException, NoSuchWindowException, WebDriverException
from information_compile import determine_bug_category
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

    while True:
        try:
            if not tried_duplicates:
                duplicate_found = check_for_duplicates(log_first, username, password, browser)
                tried_duplicates = True
                continue
            if not duplicate_found:
                use_log_lines = copy.deepcopy(log_lines)
                upload_to_mantis(
                    version, images_folder_path, category, use_log_lines,
                    assign, project, username, password, True, browser
                )
            else:
                print('Reporting not needed')
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
