import json
import pathlib
import random
import sys
from datetime import datetime
from pathlib import Path

from csv2sqllike.PseudoSQLFromCSV import PsuedoSQLFromCSV
from dict import dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm


class SeleniumCrawlerForPhantom(webdriver.PhantomJS):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8,ko;q=0.7,mt;q=0.6',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/85.0.4183.102 Safari/537.36',
        'Connection': 'keep-alive'
    }

    for key, value in headers.items():
        webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value
    webdriver.DesiredCapabilities.PHANTOMJS[
        'phantomjs.page.settings.useragent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (' \
                                               'KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 '
    del webdriver.DesiredCapabilities.PHANTOMJS['browserName']
    del webdriver.DesiredCapabilities.PHANTOMJS['version']

    def __init__(self, path2driver: str):
        super().__init__(path2driver)
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

    def crawl_site(self, queue_table_name: str, scanned_url_table=None, func=None, length=1000, sleep_time=0.3) -> None:
        tmp_command: str = "select * from {0} limit {1}".format(queue_table_name, str(length))
        if self.__sql_db is None:
            print("No sql_db exists")
        else:
            tmp_df = self.__sql_db.execute(tmp_command)
            if len(tmp_df) != 0:
                self.__sql_db.execute("lock tables {} write;".format(queue_table_name))
                tmp_command = "select * from {0} limit {1}".format(queue_table_name, length)
                tmp_df = self.__sql_db.execute(tmp_command)
                tmp_command = "delete from {0} limit {1}".format(queue_table_name, str(length))
                self.__sql_db.execute(tmp_command)
                self.__sql_db.execute("unlock tables;")
                tmp_df = tmp_df.to_numpy().tolist()

                tmp_heads_list, tmp_heads_dtype = self.__sql_db.get_heads_dtype(queue_table_name)

                tmp_sqllike = PsuedoSQLFromCSV("")
                tmp_sqllike.dtype = dict(table_name='str', url='str', created='datetime', dict='str')
                tmp_sqllike.header = ('table_name', 'url', 'created', 'dict')
                tmp_sqllike.data = list()

                if scanned_url_table:
                    tmp_sqllike_urls = PsuedoSQLFromCSV("")
                    tmp_sqllike_urls.dtype = dict(url='str')
                    tmp_sqllike_urls.header = ['url']
                    tmp_sqllike_urls.data = list()
                for data_line in tqdm(tmp_df):
                    tmp_table_list = self.__sql_db.get_tables()
                    if data_line[1] not in tmp_table_list:
                        tmp_command = "create table " + data_line[
                            1] + "(table_name varchar(50), url varchar(120), created datetime, dict " \
                                 "mediumtext); "
                        print(tmp_command)
                        self.__sql_db.execute(tmp_command)

                    tmp_order_list = list()
                    tmp_get_dict = dict()
                    tmp_click_dict = dict()
                    tmp_insert_dict = dict()
                    tmp_select_dict = dict()
                    tmp_xpath_dict = dict()
                    tmp_class_name_dict = dict()
                    tmp_datetime = datetime.now()

                    tmp_table_name = data_line[tmp_heads_list.index("table_name")]
                    if data_line[tmp_heads_list.index("order_list")] is not None:
                        tmp_order_list = json.loads(data_line[tmp_heads_list.index("order_list")])
                    if data_line[tmp_heads_list.index("get_dict")] is not None:
                        tmp_get_dict = json.loads(data_line[tmp_heads_list.index("get_dict")])
                    if data_line[tmp_heads_list.index("click_dict")] is not None:
                        tmp_click_dict = json.loads(data_line[tmp_heads_list.index("click_dict")])
                    if data_line[tmp_heads_list.index("insert_dict")] is not None:
                        tmp_insert_dict = json.loads(data_line[tmp_heads_list.index("insert_dict")])
                    if data_line[tmp_heads_list.index("select_dict")] is not None:
                        tmp_select_dict = json.loads(data_line[tmp_heads_list.index("select_dict")])
                    if data_line[tmp_heads_list.index("xpath_dict")] is not None:
                        tmp_xpath_dict = json.loads(data_line[tmp_heads_list.index("xpath_dict")])
                    if data_line[tmp_heads_list.index("class_dict")] is not None:
                        tmp_class_name_dict = json.loads(data_line[tmp_heads_list.index("class_dict")])

                    if not self.get_2(data_line[0]):
                        self.log_error()
                        continue
                    tmp_result = self.routine4selenium(order_list=tmp_order_list, get_dict=tmp_get_dict,
                                                       click_dict=tmp_click_dict,
                                                       insert_dict=tmp_insert_dict, select_dict=tmp_select_dict,
                                                       xpath_dict=tmp_xpath_dict,
                                                       class_dict=tmp_class_name_dict, sleep_time=sleep_time)
                    if tmp_result:
                        if not tmp_result["is_successful"]:
                            self.log_error()
                            continue

                        if func:
                            tmp_result["url"] = data_line[0]
                            func(tmp_result)
                            tmp_sqllike.data.append(list(tmp_result.values()))
                        else:
                            tmp_result = json.dumps(tmp_result)
                            tmp_sqllike.data.append([tmp_table_name, data_line[0], tmp_datetime, tmp_result])

                        if scanned_url_table:
                            tmp_sqllike_urls.data.append(data_line[0])

                try:
                    if func:
                        tmp_sqllike.header = list(tmp_result.keys())
                    self.__sql_db.insert_data(data_line[1], tmp_sqllike)
                except Exception:
                    tmp_sqllike.save_data_to_csv("test.csv")
                if scanned_url_table:
                    self.__sql_db.insert_data(scanned_url_table, tmp_sqllike_urls)

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
