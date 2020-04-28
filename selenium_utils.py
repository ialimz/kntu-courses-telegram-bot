from itertools import chain
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def setup_selenium():
    opts = webdriver.ChromeOptions()
    opts.headless = True
    preferences = {"browser.helperApps.neverAsk.saveToDisk": "application/pdf",
                    "browser.download.folderList": 2,
                    "browser.download.manager.showWhenStarting": False,
                    "plugins.always_open_pdf_externally": True}
    opts.add_experimental_option('prefs', preferences)
    browser = Chrome(options=opts)
    return browser


def expand_shadow_element(browser, element):
    shadow_root = browser.execute_script('return arguments[0].shadowRoot', element)
    return shadow_root


def every_downloads_chrome(driver):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")
    return driver.execute_script("""
        return document.querySelector('downloads-manager')
        .shadowRoot.querySelector('#downloadsList')
        .items.filter(e => e.state === 'COMPLETE')
        .map(e => e.filePath || e.file_path || e.fileUrl || e.file_url);
        """)


# TODO: Clear downloads
def clear_recent_downloads(browser):
    return
    # if not browser.current_url.startswith("chrome://downloads"):
    #     browser.get("chrome://downloads/")
    #
    # browser.get("chrome://downloads")
    # root1 = browser.find_element_by_tag_name('downloads-manager')
    # shadow_root1 = expand_shadow_element(browser, root1)
    #
    # root2 = shadow_root1.find_element_by_css_selector('downloads-toolbar')
    # shadow_root2 = expand_shadow_element(browser, root2)
    #
    # root3 = shadow_root2.find_element_by_css_selector('#moreActionsMenu')
    # shadow_root3 = expand_shadow_element(browser, root3)
    #
    # clear_button = shadow_root3.find_element_by_xpath('//*[@id="moreActionsMenu"]/button[1]')
    # clear_button.click()


def download_resource(browser, link):
    browser.get(link)
    paths = WebDriverWait(browser, 120, 0.5).until(every_downloads_chrome)
    return paths


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
