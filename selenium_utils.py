import os
import requests
import re
from itertools import chain
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

download_path = os.getcwd() + '/downloads/'


def setup_selenium():
    opts = webdriver.ChromeOptions()
    opts.headless = True
    preferences = {"browser.helperApps.neverAsk.saveToDisk": "application/pdf",
                   'download.default_directory': download_path,
                   "browser.download.folderList": 2,
                   "browser.download.manager.showWhenStarting": False,
                   "plugins.always_open_pdf_externally": True}
    opts.add_experimental_option('prefs', preferences)
    browser = Chrome(options=opts)
    browser.set_window_size(1440, 900)
    enable_download_in_headless_chrome(browser, download_path)
    return browser


def enable_download_in_headless_chrome(browser, download_dir):
    browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    browser.execute("send_command", params)


def get_browser_cookies(browser):
    browser_cookies = browser.get_cookies()[0]
    return {browser_cookies['name']: browser_cookies['value']}


def get_file_path_from_response(response):
    content_disposition = response.headers['content-disposition']
    file_name = re.findall("filename=(.+)", content_disposition)[0].replace('"', '')
    path = '{}{}'.format(download_path, file_name)
    return path


def is_file_downloaded(browser, link):
    cookie_dict = get_browser_cookies(browser)
    file = requests.head(link, allow_redirects=True, cookies=cookie_dict)
    path = get_file_path_from_response(file)
    return os.path.exists(path), path


def download_resource(browser, link):
    is_downloaded = is_file_downloaded(browser, link)
    if is_downloaded[0]:
        return is_downloaded[1]
    cookie_dict = get_browser_cookies(browser)
    file = requests.get(link, allow_redirects=True, cookies=cookie_dict)
    path = get_file_path_from_response(file)
    open(path, 'wb').write(file.content)
    return path


def open_courses_login(browser):
    if not browser.current_url.startswith('https://courses.kntu.ac.ir/login/index.php'):
        browser.get('https://courses.kntu.ac.ir/login/index.php')


def open_course_home(browser):
    browser.get('https://courses.kntu.ac.ir')


def login(browser, username_input, password_input):
    username = WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.ID, 'username')))
    username.send_keys(username_input)

    password = browser.find_element_by_id('password')
    password.send_keys(password_input)

    submit_btn = browser.find_element_by_id('loginbtn')
    submit_btn.click()


def find_courses(browser):
    courses = browser.find_element_by_id('category-course-list')
    rows_classes = courses.find_elements_by_class_name('container-fluid')
    rows = list(map(lambda row_class: row_class.find_element_by_class_name('row'), rows_classes))
    cols = list(map(lambda row: row.find_elements_by_class_name('col-md-4'), rows))

    result = []
    for cols_per_row in cols:
        texts = list(map(lambda col: col.text.split('\n')[0], cols_per_row))
        links = list(map(lambda col: col.find_element_by_tag_name('a').get_attribute("href"), cols_per_row))
        zipped = list(zip(texts, links))
        result.append(zipped)

    return list(chain.from_iterable(result))


def find_topics(browser, link):
    browser.get(link)
    try:
        topics_container = browser.find_element_by_class_name('topics')
    except:
        topics_container = browser.find_element_by_class_name('course-content')

    topics = topics_container.find_elements_by_xpath('//*[contains(@id, "section")]')

    topics_names = list(map(lambda topic: topic.get_attribute('aria-label'), topics))
    ids = list(map(lambda topic: topic.get_attribute('id'), topics))
    zipped = list(zip(topics_names, ids))
    return zipped


def topic_activities(browser, topic_id):
    topic = browser.find_element_by_id(topic_id)
    content_container = topic.find_element_by_class_name('content')
    contents = content_container.find_elements_by_class_name('activityinstance')

    activities_texts = list(map(lambda activity: activity.text, contents))
    activities_links = list(map(lambda activity: activity.find_element_by_tag_name('a').get_attribute("href"), contents))
    zipped = list(zip(activities_texts, activities_links))
    return zipped


def get_assignment_status(browser, link):
    browser.get(link)
    status_container = browser.find_element_by_class_name('submissionstatustable')
    rows = status_container.find_elements_by_tag_name('tr')
    rows_texts = list(map(lambda row: row.find_elements_by_tag_name('td')[0].text, rows))
    rows_data = list(map(lambda row: row.find_elements_by_tag_name('td')[1].text, rows))
    zipped = list(zip(rows_texts, rows_data))
    status = ''
    for data in zipped:
        status += '<b>{}</b>: {}\n'.format(data[0], data[1])
    return status
