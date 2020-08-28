from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException

import config
from information_compile import extract_location_filter
from information_compile import extract_asset_name
from config import read_config
from password import save_password


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


def check_for_duplicates(username, password, bug_description=None,
                         asset_path=None, driver_handler=None):
    # opens mantis so the user can check for duplicates

    if not driver_handler.is_active():
        driver = DriverHandler(browser=read_config("preferred browser")).get_driver()
        log_into_mantis(driver, username, password)

    driver = driver_handler.get_driver()
    log_into_mantis(driver, username, password)
    if asset_path and asset_path != '':
        final_filter = extract_asset_name(asset_path)
    else:
        final_filter = extract_location_filter(bug_description)

    # Interact with the website here
    driver.get('https://qa.scssoft.com/view_all_bug_page.php')
    driver.find_element_by_xpath("//a[@class='btn btn-sm btn-primary btn-white btn-round']").click()  # reset button
    driver.find_element_by_id('filter-search-txt').send_keys(final_filter)  # filter box
    driver.find_element_by_xpath("//input[@value='Apply Filter']").click()  # apply filter button


def gui_login(username, password):
    driver_handler = DriverHandler(config.read_config("preferred browser"), headless=True)
    log_into_mantis(driver_handler.get_driver(), username, password)
    try:
        driver_handler.get_driver().find_element_by_xpath('//div[@class="col-md-12 col-xs-12"]')
    except NoSuchElementException:
        return False
    except TypeError:
        return False
    else:
        if read_config("save password") == "True":
            save_password(password)
        return True


def log_into_mantis(driver, username, password):
    # uses the given credentials to log into mantis
    # CrYVhn7FSM
    driver.get('https://qa.scssoft.com/login_page.php')
    username_box = driver.find_element_by_id('username')
    username_box.send_keys(username)
    driver.find_element_by_xpath("//input[@type='submit']").click()
    id_box = driver.find_element_by_id('password')
    id_box.send_keys(password)
    driver.find_element_by_xpath("//input[@type='submit']").click()  # At this point the program is logged in
