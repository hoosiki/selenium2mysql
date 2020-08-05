from .info import __VERSION__, __version__
from .Json2Mysql import Json2Mysql
from .QueueManager import QueueManager
from .SeleniumCrawler import SeleniumCrawler


class Crawler(object):
    def __init__(self, path2driver:str, db_info:dict, visibility=False):
        self.__driver = SeleniumCrawler(path2driver, visibility=visibility)
        self.__queue = QueueManager(db_info)
        self.__json = Json2Mysql(self.__queue)
        self.__driver.sql_db = self.__queue

    @property
    def driver(self):
        return self.__driver

    @property
    def queue(self):
        return self.__queue

    @property
    def json(self):
        return self.__json
