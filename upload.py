from selenium.common.exceptions import WebDriverException
from time import sleep

from chromedrivers import DriverHandler, log_into_mantis
from information_compile import generate_description, get_image, generate_no_version_des, extract_asset_name, \
    clean_debug_info


def ask_for_missing_image(line_to_process):
    while True:
        print('No image found, try again? (Y/N)')
        answer = input('> ')
        if answer.upper() == 'Y':
            image_to_return = get_image(line_to_process)
        elif answer.upper() == 'N':
            return ""
        else:
            print('Answer Y or N')
            continue
        if image_to_return:
            return image_to_return


def upload_to_mantis(version, category, log_lines, assign_to, project, username, password,
                     browser, path_to_asset=None, debug_info=None, web_driver=None, priority=None,
                     severity=None, late_image=None):
    # Opens chrome browser, connects to mantis and uploads all of the gathered information
    # If priority is not None, it will treat the report as a batch report = will not as for image if its missing and
    #       will submit it automatically

    # region process information to insert in the form
    bug_descriptions = []
    first_path_to_asset = ''
    images = []
    first_loop = True

    if debug_info is not None:
        debug_info = clean_debug_info(debug_info)
        path_to_asset = f"{path_to_asset}\n{debug_info}"
    if late_image:
        images.append(late_image)
    while len(log_lines) > 0:
        if ']' in log_lines:
            line_to_process = log_lines
        else:
            line_to_process = log_lines.popleft()
        if category == 'a' and first_loop:
            if first_loop:
                first_path_to_asset = path_to_asset
                first_loop = False
            bug_descriptions.append(
                generate_description(line_to_process, version, category, path_to_asset, first_time=True)
            )
        else:
            bug_descriptions.append(
                generate_description(line_to_process, version, category, first_time=False)
            )

        image_to_append = get_image(line_to_process)

        # If an image is not found, gives the user the option to check for it again
        if not image_to_append and not priority:
            image_to_append = ask_for_missing_image(line_to_process)
        elif not image_to_append and priority:
            print(f"No image added to bug: {line_to_process}")
        if image_to_append:
            images.append(image_to_append)

    # endregion
    driver = web_driver.get_driver()

    if not web_driver.is_active():
        driver = DriverHandler(browser=browser).get_driver()
        log_into_mantis(driver, username, password)

    # region Filling up the report form
    driver.get('https://qa.scssoft.com/login_select_proj_page.php?ref=bug_report_page.php')
    driver.find_element_by_xpath(f"//select[1]/option[text()='{project}']").click()
    driver.find_element_by_xpath("//input[@type='submit']").click()
    for upload_me in images:
        driver.find_element_by_xpath("//input[@class='dz-hidden-input']").send_keys(str(upload_me))  # upload an image
    description_box = driver.find_element_by_xpath("//textarea[@class='form-control']")
    if len(bug_descriptions) <= 1:
        no_ver_description = generate_no_version_des(bug_descriptions)
        description_box.send_keys(str(no_ver_description) + '\n')
    else:
        first_time = True
        for p in range(len(bug_descriptions)):
            no_ver_description = generate_no_version_des(bug_descriptions[p])
            if first_time:
                description_box.send_keys(no_ver_description + '\n')
                first_time = False
            else:
                description_box.send_keys(no_ver_description)

    if category == 'a' and path_to_asset != None:
        asset_name = extract_asset_name(first_path_to_asset)
        no_ver_summary = generate_no_version_des(bug_descriptions[0].split(';')[0])
        summary = f'{version} - {asset_name} - {no_ver_summary}'
    else:
        summary = bug_descriptions[0].split(';')[0]

    summary_box = driver.find_element_by_xpath(f"//input[@name='summary']")
    summary_box.send_keys(summary)

    if assign_to != "":
        try:
            driver.find_element_by_xpath(f"//option[text()='{assign_to}']").click()
        except WebDriverException:
            print(f'Unable to find user named: {assign_to}, leaving blank')
    driver.find_element_by_xpath(f"//option[text()='always']").click()

    if category == 'm':
        driver.find_element_by_xpath(f"//option[text()='map']").click()
    elif category == 'a':
        driver.find_element_by_xpath(f"//option[text()='assets']").click()

    if priority:
        if priority != 'normal':
            driver.find_element_by_xpath(f"//select[@name='priority']/option[text()='{priority}']").click()
        if severity is not None:
            if priority != "low":
                driver.find_element_by_xpath(f"//select[@name='severity']/option[text()='major']").click()
    # endregion

    #if priority:  # if in batch reporter mode
    #    sleep(1)
    #    driver.find_element_by_xpath("//input[@value='Submit Issue']").click()
    #    print(f'Reported bug "{summary.split("] - ")[1]}"')
    #    sleep(1)
    #else:
    #    # This waits for the user to close the browser window after submitting the bug
    #    while True:
    #        try:
    #            current_url = driver.current_url
    #        except WebDriverException:
    #            break
