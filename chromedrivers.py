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
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
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
