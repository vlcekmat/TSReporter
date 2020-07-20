import os

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from information_compile import generate_description, extract_location_filter
from information_compile import get_image
from collections import deque

browser_using = 'chrome'


def set_up_new_driver(headless=False):
    ch_options = webdriver.ChromeOptions()
    if headless:
        ch_options.headless = True
    ch_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    ch_options.add_argument('--start-maximized')
    driver = webdriver.Chrome('chromedriver.exe', options=ch_options)
    return driver


def log_into_mantis(driver, username, password):
    driver.get('https://qa.scssoft.com/login_page.php')
    username_box = driver.find_element_by_id('username')
    username_box.send_keys(username + '\n')
    id_box = driver.find_element_by_id('password')
    id_box.send_keys(password + '\n')  # At this point the program is logged in


def log_into_tsreporter(test_login_username):
    while True:
        password = input("PASSWORD: ")
        os.system('cls')
        # password = "CrYVhn7FSM"
        if password == "":
            print("No password entered, returning to menu")
            return ""
        print("Checking your login credentials")
        driver = set_up_new_driver(headless=True)
        try:
            log_into_mantis(driver, test_login_username, password)
            driver.find_element_by_id('sidebar-btn')
        except NoSuchElementException:
            print('Incorrect password or username')
            return ""
        else:
            print("Login successful!")
            driver.close()
            return password


# opens mantis so the user can check for duplicates
def check_for_duplicates(bug_description, username, password):
    print("Opening search for duplicates")
    driver = set_up_new_driver()
    log_into_mantis(driver, username, password)

    final_filter = extract_location_filter(bug_description)

    # Interact with the website here
    driver.get('https://qa.scssoft.com/view_all_bug_page.php')
    driver.find_element_by_xpath("//a[@class='btn btn-sm btn-primary btn-white btn-round']").click()
    driver.find_element_by_id('filter-search-txt').send_keys(final_filter + '\n')

    print('Did you find any duplicates? (Y/N)')
    while True:
        answer = input('> ')
        if answer.upper() == 'N':
            return False
        elif answer.upper() == 'Y':
            return True
        else:
            print('Answer Y or N')
            pass


# opens chrome browser, connects to mantis and uploads all of the gathered information
def upload_to_mantis(version, images_folder_path, category, log_lines, assign_to, project, username, password, no_vid):

    #region process information to insert in the form
    bug_descriptions = []
    first_path_to_asset = ''

    images = []

    first_loop = True
    if no_vid:
        first_loop_for_videos = False
    else:
        first_loop_for_videos = True

    video_link_entered = False
    video_link = ''

    while len(log_lines) > 0:
        line_to_process = log_lines.pop()
        if category == 'a' and first_loop:
            path_to_asset = input('Enter path to the problematic asset: ')
            if first_loop:
                first_path_to_asset = path_to_asset
                first_loop = False
            bug_descriptions.append(generate_description(line_to_process,
                                                         version,
                                                         category,
                                                         path_to_asset,
                                                         first_time=True))
        else:
            bug_descriptions.append(generate_description(line_to_process,
                                                         version,
                                                         category,
                                                         first_time=False))

        image_to_append = get_image(line_to_process, images_folder_path)

        # If an image is not found, gives the user the option to check for it again
        while True:
            if not image_to_append:
                print('No image found, try again? (Y/N)')
                answer = input('> ')
                if answer.upper() == 'Y':
                    image_to_append = get_image(line_to_process, images_folder_path)
                    continue
                elif answer.upper() == 'N':
                    break
                else:
                    print('Answer Y or N')
            else:
                break
        if image_to_append:
            images.append(image_to_append)

        # Asks user once to add a video
        if first_loop_for_videos:
            first_loop_for_videos = False
            while True:
                print('Add a video link? (Y/N)')
                answer = input('> ')
                if answer.upper() == 'Y':
                    video_link = input('Video link: ')
                    video_link_entered = True
                    break
                elif answer.upper() == 'N':
                    break
                else:
                    print('Answer Y or N')
                    continue
    #endregion

    driver = set_up_new_driver()
    log_into_mantis(driver, username, password)

    #region Filling up the report form
    driver.get('https://qa.scssoft.com/login_select_proj_page.php?ref=bug_report_page.php')
    select_project_box = driver.find_element_by_xpath(f"//select[1]/option[text()='{project}']")
    select_project_box.click()
    select_project_button = driver.find_element_by_xpath("//input[@type='submit']")
    select_project_button.click()
    for upload_me in images:
        driver.find_element_by_xpath("//input[@class='dz-hidden-input']").send_keys(str(upload_me))  # upload an image
    description_box = driver.find_element_by_xpath("//textarea[@class='form-control']")
    if len(bug_descriptions) <= 1:
        if video_link_entered:
            description_box.send_keys(str(''.join(bug_descriptions)) + "\n" + 'Video link: ' + video_link + '\n')
        else:
            description_box.send_keys(str(''.join(bug_descriptions)) + '\n')
    else:
        first_time = True
        for p in range(len(bug_descriptions)):
            if first_time:
                if video_link_entered:
                    description_box.send_keys(bug_descriptions[p] + "\n" + 'Video link: ' + video_link + '\n\n')
                    first_time = False
                else:
                    description_box.send_keys(bug_descriptions[p] + '\n\n')
                    first_time = False
            else:
                description_box.send_keys('Additional image ' + str((p - 1)) + ' : ' + bug_descriptions[p] + '\n')
    summary = bug_descriptions[0].split(';')[0]
    summary_box = driver.find_element_by_xpath(f"//input[@name='summary']")
    if category == 'a':
        summary_box.send_keys(summary + ' - ' + first_path_to_asset)
    else:
        summary_box.send_keys(summary)

    if assign_to != "":
        try:
            assign_to_option = driver.find_element_by_xpath(f"//option[text()='{assign_to}']")
            assign_to_option.click()
        except WebDriverException:
            print(f'Unable to find user named: {assign_to}')
    reproducibility_option = driver.find_element_by_xpath(f"//option[text()='always']")
    reproducibility_option.click()

    if category == 'm':
        driver.find_element_by_xpath(f"//option[text()='map']").click()
    elif category == 'a':
        driver.find_element_by_xpath(f"//option[text()='assets']").click()
    #endregion

    reporter_running = True
    while reporter_running:
        if driver.current_url is None:
            reporter_running = False
        pass
