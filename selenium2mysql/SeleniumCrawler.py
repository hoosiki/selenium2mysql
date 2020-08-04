import json
from csv2sqllike.PseudoSQLFromCSV import PsuedoSQLFromCSV
from datetime import datetime
from dict import dict
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver import ActionChains
#from time import sleep


class SeleniumCrawler(webdriver.Chrome):

    def __init__(self, path2driver: str, visibility=False):
        self.__options = Options()
        if visibility is True:
            self.__options.add_argument("--headless")
        super(webdriver.Chrome, path2driver, options=self.__options)
        self.__sql_db = None

    def insert_word(self, selector: str, value: str, sleep_time=0.1):
        tmp_tag = self.find_element_by_css_selector(selector)
        try:
            tmp_tag.send_keys(value)
            self.dialog_block_wait()
            # sleep(sleep_time)
        except Exception:
            print("not found selector : ", selector, Exception)

    def click_button(self, button_selector: str, sleep_time=0.1):
        tmp_tag = self.find_element_by_css_selector(button_selector)
        try:
            tmp_tag.click()
            self.dialog_block_wait()
            # sleep(sleep_time)
        except Exception:
            print("not found selector : ", button_selector)

    def login_site(self, info_dict: dict, sleep_time=0.1):
        """
        tmp_page = driver.get(info_dict["login_page_url"])
        insert_word(info_dict["id_selector"], info_dict["id_str"], driver, sleep_time=sleep_time)
        insert_word(info_dict["pw_selector"], info_dict["pw_str"], driver, sleep_time=sleep_time)
        click_button(info_dict["login_button_selector"], driver, sleep_time=0.5)
        """
        tmp_page = self.get(info_dict["login_page_url"])
        self.dialog_block_wait()
        # sleep(sleep_time)
        self.insert_word(info_dict["id_selector"], info_dict["id_str"], sleep_time=sleep_time)
        self.insert_word(info_dict["pw_selector"], info_dict["pw_str"], sleep_time=sleep_time)
        self.click_button(info_dict["login_button_selector"], sleep_time=0.5)

    def crawl_site(self, queue_table_name: str, length=1000, sleep_time=0.1) -> None:
        tmp_command = "select * from " + queue_table_name + " limit " + str(length)
        tmp_df = self.__sql_db.execute(tmp_command)
        # print(tmp_df)
        if len(tmp_df) != 0:
            self.__sql_db.execute("lock tables ctl_queue write;")
            tmp_command = "select * from " + queue_table_name + " order by table_name limit " + str(length)
            tmp_df = self.__sql_db.execute(tmp_command)
            tmp_command = "delete from " + queue_table_name + " limit " + str(length)
            self.__sql_db.execute(tmp_command)
            self.__sql_db.execute("unlock tables;")
            tmp_df = tmp_df.to_numpy()
            tmp_table_list = self.__sql_db.get_tables()

            tmp_heads_list, tmp_heads_dtype = self.__sql_db.get_heads_dtype(queue_table_name, sql_transfer)

            tmp_sqllike = PsuedoSQLFromCSV("")
            tmp_sqllike.dtype = {'url': 'str', 'created': 'datetime', 'dict': 'str'}
            tmp_sqllike.header = ['url', 'created', 'dict']
            tmp_sqllike.data = list()
            for data_line in tmp_df:
                if data_line[1] not in tmp_table_list:
                    tmp_command = "create table " + data_line[1] + "(url varchar(1000), created datetime, dict text);"
                    self.__sql_db.execute(tmp_command)

                tmp_order_list = list()
                tmp_get_dict = dict()
                tmp_click_dict = dict()
                tmp_insert_dict = dict()
                tmp_selector_dict = dict()
                tmp_datetime = datetime.now()

                if data_line[tmp_heads_list.index("order_list")] is not None:
                    tmp_order_list = json.loads(data_line[tmp_heads_list.index("order_list")])
                if data_line[tmp_heads_list.index("get_dict")] is not None:
                    tmp_get_dict = json.loads(data_line[tmp_heads_list.index("get_dict")])
                if data_line[tmp_heads_list.index("click_dict")] is not None:
                    tmp_click_dict = json.loads(data_line[tmp_heads_list.index("click_dict")])
                if data_line[tmp_heads_list.index("insert_dict")] is not None:
                    tmp_insert_dict = json.loads(data_line[tmp_heads_list.index("insert_dict")])
                if data_line[tmp_heads_list.index("selector_dict")] is not None:
                    tmp_selector_dict = json.loads(data_line[tmp_heads_list.index("selector_dict")])

                self.get(data_line[0])
                self.dialog_block_wait()
                # sleep(sleep_time)
                tmp_result = self.routine4selenium(tmp_order_list, get_dict=tmp_get_dict, click_dict=tmp_click_dict,
                                                   insert_dict=tmp_insert_dict, selector_dict=tmp_selector_dict,
                                                   sleep_time=sleep_time)
                tmp_result = json.dumps(tmp_result)
                tmp_sqllike.data.append([data_line[0], tmp_datetime, tmp_result])
            self.__sql_db.insert_data(data_line[1], tmp_sqllike)

    def routine4selenium(self, order_list: list, get_dict=dict(), click_dict=dict(), insert_dict=dict(),
                         selector_dict=dict(), sleep_time=0.1) -> dict:
        """
        get_dict => click_dict => insert_dict => selector_dict
        """
        tmp_dict = dict()
        for key in order_list:
            if key in get_dict.keys():
                self.get(get_dict[key])
                self.dialog_block_wait()
                # sleep(sleep_time)
            if key in click_dict.keys():
                self.click_button(click_dict[key], sleep_time=sleep_time)
            if key in insert_dict.keys():
                tmp_tag = self.find_element_by_css_selector(insert_dict[key][0])
                tmp_tag.send_keys(insert_dict[key][1])
            if key in selector_dict.keys():
                tmp_tag = self.find_element_by_css_selector(selector_dict[key])
                tmp_dict[key] = tmp_tag.get_attribute("outerHTML")
        tmp_dict["is_successful"] = self.__is_successful(tmp_dict)
        return tmp_dict

    def routine4short(self, get_dict=dict(), selector_dict=dict(), sleep_time=0.1) -> dict:
        tmp_dict = dict()
        for key in selector_dict.keys():
            if key in get_dict.keys():
                self.get(get_dict[key])
                self.dialog_block_wait()
                # sleep(sleep_time)
            if key in selector_dict.keys():
                tmp_tag = self.find_element_by_css_selector(selector_dict[key])
                tmp_dict[key] = tmp_tag.get_attribute("outerHTML")
        tmp_dict["is_successful"] = self.__is_successful(tmp_dict)
        return tmp_dict

    def dialog_block_wait(self):
        try:
            wait = WebDriverWait(self, 5)
            # self.take_snapshot("dialog_block_wait_before.png")
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'ui-dialog')))
            # self.take_snapshot("dialog_block_wait_appear.png")
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'ui-dialog')))
            # self.take_snapshot("dialog_block_wait_disappear.png")
        except TimeoutException:
            pass

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
