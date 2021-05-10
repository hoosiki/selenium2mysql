import pathlib
import random
import sys
from pathlib import Path

from dict import dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class SeleniumCrawler(webdriver.Chrome):

    def __init__(self, path2driver: str, visibility=False, download_path=None):
        self.__options = Options()
        if visibility is False:
            self.__options.add_argument("--headless")
            self.__options.add_argument('--no-sandbox')
            self.__options.add_argument('--disable-dev-shm-usage')
            self.__options.add_argument('--dns-prefetch-disable')
        self.__options.add_argument('disable-gpu')
        self.__options.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/85.0.4183.102 Safari/537.36')
        self.__options.add_argument('--lang=ko')
        self.__options.add_argument('connection=keep-alive')

        if download_path is not None:
            profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
                       # Disable Chrome's PDF Viewer
                       "download.default_directory": download_path, "download.extensions_to_open": "applications/pdf"}
            self.__options.add_experimental_option("prefs", profile)
        super().__init__(path2driver, options=self.__options)
        self.__timeout = 3
        self.implicitly_wait(self.__timeout)
        self.set_page_load_timeout(3)
        self.__sql_db = None
        self.implicitly_wait(self.__timeout)
        self.set_window_size(1920, 1080)

    def insert_word(self, xpath: str, value: str, sleep_time=0.1):
        self.dialog_block_wait_xpath(xpath)
        try:
            tmp_tag = self.find_element_by_xpath(xpath)
            tmp_tag.send_keys(value)
        except Exception:
            print("can not send key to target : ", xpath, Exception)

    def scroll_down_xpath(self, xpath):
        try:
            self.execute_script("arguments[0].scrollIntoView(true);", WebDriverWait(self, self.__timeout).until(
                EC.visibility_of_element_located((By.XPATH, xpath))))
            self.execute_script("window.scrollBy(0, -150);")
            return True
        except Exception:
            print("can not find element : {}".format(xpath))
            return False

    def scroll_down_class_name(self, class_name):
        try:
            self.execute_script("arguments[0].scrollIntoView(true);", WebDriverWait(self, self.__timeout).until(
                EC.visibility_of_element_located((By.CLASS_NAME, class_name))))
            self.execute_script("window.scrollBy(0, -150);")
            return True
        except Exception:
            print("can not find element : {}".format(class_name))
            return False

    def scroll2bottom(self):
        try:
            self.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            return True
        except Exception:
            print("can not scroll to bottom")
            return False

    def scroll2top(self):
        try:
            self.execute_script("window.scrollTo(document.body.scrollHeight, 0);")
            return True
        except Exception:
            print("can not scroll to top")
            return False

    def click_button(self, button_xpath: str, sleep_time=0.1):
        self.dialog_block_wait_xpath(button_xpath)
        try:
            tmp_tag = self.find_element_by_xpath(button_xpath)
            self.implicitly_wait(self.__timeout + random.uniform(0, 1))
            tmp_tag.click()
        except Exception:
            print("can not click xpath : ", button_xpath)

    def login_site(self, info_dict: dict, sleep_time=0.1):
        """
        driver.get(info_dict["login_page_url"])
        insert_word(info_dict["id_xpath"], info_dict["id_str"], driver, sleep_time=sleep_time)
        insert_word(info_dict["pw_xpath"], info_dict["pw_str"], driver, sleep_time=sleep_time)
        click_button(info_dict["login_button_xpath"], driver, sleep_time=0.5)
        """
        if not self.get_2(info_dict["login_page_url"]):
            self.log_error()
        self.dialog_block_wait_xpath(info_dict["id_xpath"])
        # sleep(sleep_time)
        self.insert_word(info_dict["id_xpath"], info_dict["id_str"], sleep_time=sleep_time)
        self.insert_word(info_dict["pw_xpath"], info_dict["pw_str"], sleep_time=sleep_time)
        self.click_button(info_dict["login_button_xpath"], sleep_time=0.5)

    def routine4selenium(self, order_list=list(), get_dict=dict(), click_dict=dict(), insert_dict=dict(),
                         select_dict=dict(), xpath_dict=dict(), class_dict=dict(), sleep_time=0.2) -> dict:
        """
        get_dict => click_dict => insert_dict => select_dict => xpath_dict
        """
        tmp_dict = dict()
        for key in order_list:
            if key in get_dict.keys():
                if not self.get_2(get_dict[key]):
                    self.log_error()
                    return None
            if key in click_dict.keys():
                if not self.scroll_down_xpath(click_dict[key]):
                    self.log_error()
                    return None
                self.click_button(click_dict[key], sleep_time=sleep_time)
            if key in insert_dict.keys():
                self.insert_word(insert_dict[key][0], insert_dict[key][1])
            if key in select_dict.keys():
                if not self.scroll_down_xpath(select_dict[key][0]):
                    self.log_error()
                    return None
                if not self.input_select_into_dropdown(select_dict[key][0], select_dict[key][1]):
                    return None
            if key in xpath_dict.keys():
                if not self.scroll_down_xpath(xpath_dict[key]):
                    self.log_error()
                    return None
                self.dialog_block_wait_xpath(xpath_dict[key])
                tmp_tag = self.find_element_by_xpath(xpath_dict[key])
                tmp_dict[key] = tmp_tag.get_attribute("outerHTML")
            if key in class_dict.keys():
                if not self.scroll_down_class_name(class_dict[key]):
                    self.log_error()
                    return None
                self.dialog_block_wait_class_name(class_dict[key])
                tmp_tag = self.find_element_by_class_name(class_dict[key])
                tmp_dict[key] = tmp_tag.get_attribute("outerHTML")
        tmp_dict["is_successful"] = self.__is_successful(tmp_dict)
        return tmp_dict

    def routine4short(self, get_dict=dict(), xpath_dict=dict(), sleep_time=0.2) -> dict:
        tmp_dict = dict()
        for key in xpath_dict.keys():
            if key in get_dict.keys():
                self.get_2(get_dict[key])
            if key in xpath_dict.keys():
                self.dialog_block_wait_xpath(xpath_dict[key])
                tmp_tag = self.find_element_by_xpath(xpath_dict[key])
                tmp_dict[key] = tmp_tag.get_attribute("outerHTML")
        tmp_dict["is_successful"] = self.__is_successful(tmp_dict)
        return tmp_dict

    def dialog_block_wait_xpath(self, xpath: str):
        try:
            wait = WebDriverWait(self, self.__timeout)
            wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        except Exception:
            print("can not find element within timeout : {}".format(xpath))

    def dialog_block_wait_class_name(self, class_name: str):
        try:
            wait = WebDriverWait(self, self.__timeout)
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
        except Exception:
            print("can not find element within timeout : {}".format(class_name))

    def get_2(self, url: str) -> bool:
        try:
            self.implicitly_wait(self.__timeout + random.uniform(0, 1))
            self.get(url)
            return True
        except Exception:
            print("load page failed : {}".format(url))
            return False

    def input_select_into_dropdown(self, xpath: str, menu_name: str) -> bool:
        try:
            tmp_tag = self.find_element_by_xpath(xpath)
            tmp_tag.click()
            self.find_element_by_xpath("//*[contains(text(), '{}')]".format(menu_name)).click()
            return True
        except Exception:
            print("selection failed in dropdown menu: {}".format(xpath))
            return False

    def click_then_select_from_dropdown(self, click_area_xpath: str, input_area_xpath: str, value: str):
        try:
            if self.scroll_down_xpath(click_area_xpath):
                self.find_element_by_xpath(click_area_xpath).click()
                if self.input_select_into_dropdown(input_area_xpath, value):
                    return True
            return False
        except Exception as e:
            print(e)
            return False

    def sequential_click_fro_dropdown(self, first_click_area_xpath: str, second_click_area_xpath: str, tag: str, value: str):
        try:
            tmp_check_flag = False
            for _ in range(2):
                self.click_button(first_click_area_xpath)
                tmp_tag = self.find_element_by_xpath(second_click_area_xpath)
                tmp_tag_list = list(tmp_tag.find_elements_by_tag_name(tag))
                for x in tmp_tag_list:
                    if x.text == value:
                        x.click()
                        tmp_check_flag = True
                        break
            return tmp_check_flag
        except Exception as e:
            return False

    def set_timeout(self, timeout) -> None:
        self.set_page_load_timeout(timeout)
        self.__timeout = timeout
        self.implicitly_wait(self.__timeout)

    def log_error(self):
        self.__sql_db.execute(
            f"insert into metainfo_share.error_log(main, url) values (\"{pathlib.os.path.basename(Path(sys.argv[0]))}\", \"{self.current_url}\")")

    @staticmethod
    def __is_successful(result_dict: dict) -> bool:
        for key in result_dict.keys():
            if result_dict[key] == "":
                return False
        return True

    @property
    def sql_db(self):
        return self.__sql_db

    @sql_db.setter
    def sql_db(self, sql_db):
        self.__sql_db = sql_db

    @property
    def options(self):
        return self.__options

    @options.setter
    def options(self, options):
        self.__options = options
