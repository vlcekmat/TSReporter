from batch import ask_for_prefix
from chromedrivers import check_for_duplicates, DriverHandler, log_into_mantis
from upload import upload_to_mantis
from selenium.common.exceptions import SessionNotCreatedException, NoSuchWindowException, WebDriverException
from information_compile import determine_bug_category, extract_asset_path
import copy


def report_bug(project, log_lines, version, images_folder_path, assign, username, password, browser='chrome'):
    # uploads stuff to Mantis or calls other methods to do that
    log_first = log_lines.popleft()
    print(f'CURRENT BUG: {log_first}')
    log_lines.appendleft(log_first)
    category = determine_bug_category(log_first)

    error_message = "Don't interact with browser during the process, trying again..."
    tried_duplicates = False
    duplicate_found = False
    a_path = None
    d_info = None
    if 'A' in category.upper():
        a_path = input('Enter DEBUG INFO or path to the asset:\n> ')
        if 'DEBUG INFO' in a_path or 'Position' in a_path or 'Object' in a_path:  # To accommodate only partial debug i.
            d_info = a_path
            a_path = extract_asset_path(a_path)

    while True:
        try:
            driver_handler = DriverHandler(headless=False, browser=browser)
            if not tried_duplicates:
                duplicate_found = check_for_duplicates(
                    username, password, bug_description=log_first, asset_path=a_path,
                    driver_handler=driver_handler, ask_input=True)
                tried_duplicates = True
            if duplicate_found == -1:
                return False  # For returning to menu during reporting
            elif duplicate_found == 0:
                use_log_lines = copy.deepcopy(log_lines)
                upload_to_mantis(
                    version, category, use_log_lines,
                    assign, project, username, password, browser,
                    path_to_asset=a_path, debug_info=d_info, web_driver=driver_handler
                )
                print("Bug reported successfully!\n")
            else:
                print('Reporting not needed')
                driver_handler.get_driver().quit()
            break
        except SessionNotCreatedException:
            print(error_message + ' SessionNotCreatedException')
        except NoSuchWindowException:
            print(error_message + ' NoSuchWindowException')
        except WebDriverException:
            print(error_message + ' WebDriverException')
        except AttributeError:
            print(error_message + ' AttributeError')
        except TypeError:
            print(error_message + ' TypeError')
        except NameError:
            print(error_message + ' NameError')
    return True


def batch_report_bugs(project, bugs_stack, version, images_folder_path, username, password, browser='chrome'):
    # This prefix will be added at the beginning of all summaries to save time
    # eg. writing "State - City -" at the beginning of each report
    prefix = ask_for_prefix()
    if prefix == "":
        return False
    print("Starting headless browser instance...")
    reporter_driver = DriverHandler(headless=True, browser=browser)
    print("Logging in to Mantis...")
    log_into_mantis(reporter_driver.get_driver(), username, password)
    print("Logged in successfully!")
    while len(bugs_stack) > 0:
        current_bug = bugs_stack.popleft()
        split_bug = current_bug[0].split('_', maxsplit=1)
        priority = get_full_priority(split_bug[0])
        current_bug[0] = prefix + ''.join(split_bug[1:])
        use_log_lines = copy.deepcopy(current_bug)
        upload_to_mantis(
            version, 'm', use_log_lines, "", project,
            username, password, browser, web_driver=reporter_driver, priority=priority
        )
    return True


def get_full_priority(priority):
    # List of legal priorities
    prio_dict = {
        "l": "low",
        "n": "normal",
        "h": "high",
        "u": "urgent",
        "i": "immediate"
    }
    return prio_dict[priority]
