import os

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
# import getpass

from information_compile import extract_location_filter
from information_compile import extract_asset_name


class DriverHandler:
    driver = None

    def __init__(self, browser='chrome', headless=False):
        if browser == 'chrome':
            options = webdriver.ChromeOptions()
            if headless:
                options.headless = True
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_argument('--start-maximized')
            self.driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)
        elif browser == 'firefox':
            options = webdriver.FirefoxOptions()
            if headless:
                options.headless = True
            self.driver = webdriver.Firefox(executable_path='geckodriver.exe', options=options)
            self.driver.maximize_window()

    def get_driver(self):
        return self.driver

    def is_active(self):
        try:
            test = self.driver.current_url
        except WebDriverException:
            return False
        else:
            return True


    # creates a new web driver session

def check_for_duplicates(username, password, bug_description=None, asset_path=None, web_driver=None, browser=None):
    # opens mantis so the user can check for duplicates
    print("Opening search for duplicates")

    if not web_driver.is_active():
        driver = DriverHandler(browser=browser).get_driver()
        log_into_mantis(driver, username, password)

    driver = web_driver.get_driver()
    log_into_mantis(driver, username, password)
    if asset_path is not None:
        final_filter = extract_asset_name(asset_path)
    else:
        final_filter = extract_location_filter(bug_description)

    # Interact with the website here
    driver.get('https://qa.scssoft.com/view_all_bug_page.php')
    driver.find_element_by_xpath("//a[@class='btn btn-sm btn-primary btn-white btn-round']").click()  # reset button
    driver.find_element_by_id('filter-search-txt').send_keys(final_filter)  # filter box
    driver.find_element_by_xpath("//input[@value='Apply Filter']").click()  # apply filter button

    print('Did you find any duplicates? (Y/N)')
    while True:
        answer = input('> ')
        if answer.upper() == 'N':
            try:
                pass
            except WebDriverException:
                pass
            return False
        elif answer.upper() == 'Y':
            try:
                pass
            except WebDriverException:
                pass
            return True
        else:
            print('Answer Y or N')
            pass


def log_into_tsreporter(test_login_username, browser='chrome'):
    # first try to log into mantis, so we now that the login credentials are correct
    while True:
        password = input("PASSWORD: ")
        os.system('cls')
        # password = getpass.getpass()
        # password = "CrYVhn7FSM"
        if password == "":
            print("No password entered, returning to menu")
            return ""
        print("Checking your login credentials")
        driver = DriverHandler(browser=browser, headless=True).get_driver()
        try:
            log_into_mantis(driver, test_login_username, password)
            driver.find_element_by_id('sidebar-btn')
        except NoSuchElementException:
            print('Incorrect password or username')
            return ""
        else:
            print("Login successful!")
            driver.quit()
            return password


def log_into_mantis(driver, username, password):
    # uses the given credentials to log into mantis
    driver.get('https://qa.scssoft.com/login_page.php')
    username_box = driver.find_element_by_id('username')
    username_box.send_keys(username)
    driver.find_element_by_xpath("//input[@type='submit']").click()
    id_box = driver.find_element_by_id('password')
    id_box.send_keys(password)
    driver.find_element_by_xpath("//input[@type='submit']").click()  # At this point the program is logged in
