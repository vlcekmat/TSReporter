import os

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
# import getpass

from information_compile import extract_location_filter
from information_compile import extract_asset_name


class WebDriver:
    driver = None

    def __init__(self, browser='chrome', headless=False):
        WebDriver.driver = set_up_new_driver(browser_using=browser, headless=headless)

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
def set_up_new_driver(headless=False, browser_using='chrome'):
    if browser_using == 'chrome':
        options = webdriver.ChromeOptions()
        if headless:
            options.headless = True
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)
        return driver
    elif browser_using == 'firefox':
        # binary = FirefoxBinary('path/to/installed firefox binary')
        options = webdriver.FirefoxOptions()
        if headless:
            options.headless = True
        driver = webdriver.Firefox(executable_path='geckodriver.exe', options=options)
        driver.maximize_window()
        return driver


# opens mantis so the user can check for duplicates
def check_for_duplicates(username, password, bug_description=None, asset_path=None, web_driver=None, browser=None):
    print("Opening search for duplicates")

    if not web_driver.is_active():
        driver = WebDriver(browser=browser).get_driver()
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


# first try to log into mantis, so we now that the login credentials are correct
def log_into_tsreporter(test_login_username, browser='chrome'):
    while True:
        password = input("PASSWORD: ")
        os.system('cls')
        # password = getpass.getpass()
        # password = "CrYVhn7FSM"
        if password == "":
            print("No password entered, returning to menu")
            return ""
        print("Checking your login credentials")
        driver = WebDriver(browser=browser, headless=True).get_driver()
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


# uses the given credentials to log into mantis
def log_into_mantis(driver, username, password):
    driver.get('https://qa.scssoft.com/login_page.php')
    username_box = driver.find_element_by_id('username')
    username_box.send_keys(username)
    driver.find_element_by_xpath("//input[@type='submit']").click()
    id_box = driver.find_element_by_id('password')
    id_box.send_keys(password)
    driver.find_element_by_xpath("//input[@type='submit']").click()  # At this point the program is logged in