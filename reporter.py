from collections import deque
from chromedrivers import check_for_duplicates, WebDriver, log_into_mantis
from upload import upload_to_mantis
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


def batch_report_bugs(project, bugs_stack, version, images_folder_path, username, password, browser='chrome'):
    prefix = ask_for_prefix()
    if prefix == "":
        return False
    # reporter_driver = WebDriver(browser, headless=True)
    reporter_driver = WebDriver(browser)
    log_into_mantis(reporter_driver.driver, username, password)
    while len(bugs_stack) > 0:
        current_bug = bugs_stack.pop()
        split_bug = current_bug[0].split('_', maxsplit=1)
        priority = get_full_priority(split_bug[0])
        current_bug[0] = prefix + ''.join(split_bug[1:])
        use_log_lines = copy.deepcopy(current_bug)
        upload_to_mantis(
            version, images_folder_path, 'm', use_log_lines, "", project,
            username, password, browser, web_driver=reporter_driver, priority=priority
        )


def ask_for_prefix():
    while True:
        out_prefix = input("Choose your prefix\n> ")
        if out_prefix == "":
            print("No prefix selected, returning to menu")
            return ""
        print(f"Double check your prefix, you won't be able to change it later!")
        print(out_prefix)
        answer = input("Is your prefix correct(Y/N)?\n> ")
        if answer.upper() == 'Y':
            return out_prefix


def get_full_priority(prio):
    prio_dict = {
        "l": "low",
        "n": "normal",
        "h": "high",
        "u": "urgent",
        "i": "immediate"
    }
    return prio_dict[prio]
