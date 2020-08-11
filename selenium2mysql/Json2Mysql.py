import json
import pandas as pd
from dict import dict
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse


class Json2Mysql(object):
    def __init__(self, sql_db):
        self.__sql_db = sql_db
        self.__functions = {"bigint": self.html2int, "float": self.html2float, "double": self.html2float,
                            "datetime": self.html2datetime, "str": self.html2str, "text": self.html2text,
                            "tinyint(1)": self.html2bool}

    def str2dict(self, dict_str: str) -> dict:
        tmp_dict = json.loads(dict_str)
        tmp_head_dtype_dict = self.__sql_db.get_head_dtype_dict()
        tmp_set = set(key for key in tmp_dict.keys()) - set(key for key in tmp_head_dtype_dict.keys())
        self.__sql_db.insert_head_dtypes(list(tmp_set))
        tmp_head_dtype_dict = self.__sql_db.get_head_dtype_dict()
        for key in tmp_dict.keys():
            if "char" in tmp_head_dtype_dict[key]:
                tmp_dict[key] = self.__functions["str"](tmp_dict[key])
            else:
                tmp_dict[key] = self.__functions[tmp_head_dtype_dict[key]](tmp_dict[key])
        return tmp_dict

    def get_results_from_table(self, table_name: str, elapsed_time=15.5) -> pd.DataFrame:
        tmp_now = datetime.now()
        tmp_command = "select * from {} where created > \"{}\"".format(table_name,
                                                                       tmp_now - timedelta(minutes=elapsed_time))
        tmp_df = self.__sql_db.execute(tmp_command)
        tmp_df = tmp_df.to_numpy()
        tmp_list = list()
        for data_line in tmp_df:
            tmp_dict = {"url": data_line[0], "created": data_line[1]}
            tmp_dict.update(self.str2dict(data_line[2]))
            tmp_list.append(tmp_dict)
        return pd.DataFrame(tmp_list)

    @staticmethod
    def html2int(input_html: str) -> int:
        tmp_soup = BeautifulSoup(input_html, "lxml")
        tmp_str = tmp_soup.text.strip().replace(",", "")
        return int(tmp_str)

    @staticmethod
    def html2float(input_html: str) -> float:
        tmp_soup = BeautifulSoup(input_html, "lxml")
        tmp_str = tmp_soup.text.strip().replace(",", "")
        return float(tmp_str)

    @staticmethod
    def html2str(input_html: str) -> str:
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
