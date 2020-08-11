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
from tqdm import tqdm
from time import sleep


class SeleniumCrawler(webdriver.Chrome):

    def __init__(self, path2driver: str, visibility=False):
        self.__options = Options()
        if visibility is False:
            self.__options.add_argument("--headless")
            self.__options.add_argument('--no-sandbox')
            self.__options.add_argument('--disable-dev-shm-usage')
        super().__init__(path2driver, options=self.__options)
        self.__sql_db = None

    def insert_word(self, xpath: str, value: str, sleep_time=0.1):
        self.dialog_block_wait(xpath)
        tmp_tag = self.find_element_by_xpath(xpath)
        try:
            tmp_tag.send_keys(value)
        except Exception:
            print("not found xpath : ", xpath, Exception)

    def click_button(self, button_xpath: str, sleep_time=0.1):
        self.dialog_block_wait(button_xpath)
        tmp_tag = self.find_element_by_xpath(button_xpath)
        try:
            tmp_tag.click()
        except Exception:
            print("not found xpath : ", button_xpath)

    def login_site(self, info_dict: dict, sleep_time=0.1):
        """
        tmp_page = driver.get(info_dict["login_page_url"])
        insert_word(info_dict["id_xpath"], info_dict["id_str"], driver, sleep_time=sleep_time)
        insert_word(info_dict["pw_xpath"], info_dict["pw_str"], driver, sleep_time=sleep_time)
        click_button(info_dict["login_button_xpath"], driver, sleep_time=0.5)
        """
        tmp_page = self.get(info_dict["login_page_url"])
        self.dialog_block_wait(info_dict["id_xpath"])
        # sleep(sleep_time)
        self.insert_word(info_dict["id_xpath"], info_dict["id_str"], sleep_time=sleep_time)
        self.insert_word(info_dict["pw_xpath"], info_dict["pw_str"], sleep_time=sleep_time)
        self.click_button(info_dict["login_button_xpath"], sleep_time=0.5)

    def crawl_site(self, queue_table_name: str, length=1000, sleep_time=0.3) -> None:
        tmp_command: str = "select * from crawler.{0} limit {1}".format(queue_table_name, str(length))
        if self.__sql_db is None:
            print("No sql_db exists")
        else:
            tmp_df = self.__sql_db.execute(tmp_command)
            # print(tmp_df)
            if len(tmp_df) != 0:
                self.__sql_db.execute("lock tables {} write;".format(queue_table_name))
                tmp_command = "select * from crawler.{0} order by table_name limit {1}".format(queue_table_name,
                                                                                               str(length))
                tmp_df = self.__sql_db.execute(tmp_command)
                tmp_command = "delete from crawler.{0} limit {1}".format(queue_table_name, str(length))
                self.__sql_db.execute(tmp_command)
                self.__sql_db.execute("unlock tables;")
                tmp_df = tmp_df.to_numpy()

                tmp_heads_list, tmp_heads_dtype = self.__sql_db.get_heads_dtype(queue_table_name)

                tmp_sqllike = PsuedoSQLFromCSV("")
                tmp_sqllike.dtype = dict(url='str', created='datetime', dict='str')
                tmp_sqllike.header = ('url', 'created', 'dict')
                tmp_sqllike.data = list()
                for data_line in tqdm(tmp_df):
                    tmp_table_list = self.__sql_db.get_tables()
                    if data_line[1] not in tmp_table_list:
                        tmp_command = "create table " + data_line[1] + "(url varchar(1000), created datetime, dict " \
                                                                       "text); "
                        print(tmp_command)
                        self.__sql_db.execute(tmp_command)

                    tmp_order_list = list()
                    tmp_get_dict = dict()
                    tmp_click_dict = dict()
                    tmp_insert_dict = dict()
                    tmp_xpath_dict = dict()
                    tmp_datetime = datetime.now()

                    if data_line[tmp_heads_list.index("order_list")] is not None:
                        tmp_order_list = json.loads(data_line[tmp_heads_list.index("order_list")])
                    if data_line[tmp_heads_list.index("get_dict")] is not None:
                        tmp_get_dict = json.loads(data_line[tmp_heads_list.index("get_dict")])
                    if data_line[tmp_heads_list.index("click_dict")] is not None:
                        tmp_click_dict = json.loads(data_line[tmp_heads_list.index("click_dict")])
                    if data_line[tmp_heads_list.index("insert_dict")] is not None:
                        tmp_insert_dict = json.loads(data_line[tmp_heads_list.index("insert_dict")])
                    if data_line[tmp_heads_list.index("xpath_dict")] is not None:
                        tmp_xpath_dict = json.loads(data_line[tmp_heads_list.index("xpath_dict")])

                    self.get(data_line[0])
                    sleep(sleep_time)
                    tmp_result = self.routine4selenium(tmp_order_list, get_dict=tmp_get_dict, click_dict=tmp_click_dict,
                                                       insert_dict=tmp_insert_dict, xpath_dict=tmp_xpath_dict,
                                                       sleep_time=sleep_time)
                    tmp_result = json.dumps(tmp_result)
                    tmp_sqllike.data.append([data_line[0], tmp_datetime, tmp_result])
                self.__sql_db.insert_data(data_line[1], tmp_sqllike)

    def routine4selenium(self, order_list: list, get_dict=dict(), click_dict=dict(), insert_dict=dict(),
                         xpath_dict=dict(), sleep_time=0.2) -> dict:
        """
        get_dict => click_dict => insert_dict => xpath_dict
        """
        tmp_dict = dict()
        for key in order_list:
            if key in get_dict.keys():
                self.get(get_dict[key])
            if key in click_dict.keys():
                self.click_button(click_dict[key], sleep_time=sleep_time)
            if key in insert_dict.keys():
                self.insert_word(insert_dict[key][0], insert_dict[key][1])
            if key in xpath_dict.keys():
                self.dialog_block_wait(xpath_dict[key])
                tmp_tag = self.find_element_by_xpath(xpath_dict[key])
                tmp_dict[key] = tmp_tag.get_attribute("outerHTML")
        tmp_dict["is_successful"] = self.__is_successful(tmp_dict)
        return tmp_dict

    def routine4short(self, get_dict=dict(), xpath_dict=dict(), sleep_time=0.2) -> dict:
        tmp_dict = dict()
        for key in xpath_dict.keys():
            if key in get_dict.keys():
                self.get(get_dict[key])
            if key in xpath_dict.keys():
                self.dialog_block_wait(xpath_dict[key])
                tmp_tag = self.find_element_by_xpath(xpath_dict[key])
                tmp_dict[key] = tmp_tag.get_attribute("outerHTML")
        tmp_dict["is_successful"] = self.__is_successful(tmp_dict)
        return tmp_dict

    def dialog_block_wait(self, xpath: str):
        try:
            wait = WebDriverWait(self, 5)
            wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
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
