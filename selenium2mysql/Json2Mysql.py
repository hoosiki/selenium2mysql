import json
import pandas as pd
from dict import dict
from .QueueManager import QueueManager
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.parser import parse


class Json2Mysql(object):
    def __init__(self, sql_db):
        self.__sql_db = sql_db
        self.__functions = {"int": self.html2int, "float": self.html2float, "datetime": self.html2datetime,
                            "str": self.html2str, "text": self.html2text, "bool": self.html2bool}

    def str2dict(self, dict_str: str):
        tmp_dict = json.loads(dict_str)
        tmp_keyword_dtype_dict = self.__sql_db.get_keyword_dtype_dict()
        for key in tmp_dict.keys():
            tmp_dict[key] = self.__functions[tmp_keyword_dtype_dict[key]](tmp_dict[key])
        return tmp_dict

    def __get_results_from_table(self, table_name:str, elapsed_time=15.5) -> pd.DataFrame:
        tmp_now = datetime.now()
        tmp_command = "select * from {} where created > {}".format(table_name, )
        tmp_df = self.__sql_db.bring_data_from_table(table_name)
        tmp_df = tmp_df.to_numpy()
        tmp_list = list()
        for data_line in tmp_df:
            tmp_dict = {"url": data_line[0], "create": data_line[1]}
            tmp_dict.update(crawler.json.str2dict(data_line[2]))
            tmp_list.append(tmp_dict)


    @staticmethod
    def html2int(input_html: str) -> int:
        tmp_soup = BeautifulSoup(input_html, "lxml")
        tmp_str = tmp_soup.text.strip().replace(",", "")
        return int(tmp_str)

    @staticmethod
    def html2float(input_html: str) -> int:
        tmp_soup = BeautifulSoup(input_html, "lxml")
        tmp_str = tmp_soup.text.strip().replace(",", "")
        return float(tmp_str)

    @staticmethod
    def html2str(input_html: str) -> int:
        tmp_soup = BeautifulSoup(input_html, "lxml")
        tmp_str = tmp_soup.text.strip()
        return tmp_str

    @staticmethod
    def html2datetime(input_html: str) -> datetime:
        tmp_soup = BeautifulSoup(input_html, "lxml")
        tmp_str = tmp_soup.text.strip()
        return parse(tmp_str)

    @staticmethod
    def html2text(input_html: str) -> str:
        return input_html.replace("\t", "")

    @staticmethod
    def html2bool(input_html) -> bool:
        if input_html is True or input_html is False:
            return input_html
        else:
            return False



    @property
    def sql_db(self):
        return self.__sql_db

    @sql_db.setter
    def sql_db(self, sql_db):
        self.__sql_db = sql_db
