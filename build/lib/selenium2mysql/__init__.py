#from .crawltools import *
from .info import __VERSION__, __version__
from .json2mysql import Json2Mysql
from .loop import Loop
from .queue_manager import QueueManager
from .selenium_crawler import SeleniumCrawler
from .selenium_crawler_for_phantom import SeleniumCrawlerForPhantom


class Crawler(object):
    def __init__(self, path2driver: str, db_info: dict, visibility=False, download_path=None):
        if "phantom" in path2driver:
            self.__driver = SeleniumCrawlerForPhantom(path2driver)
        else:
            self.__driver = SeleniumCrawler(path2driver, visibility=visibility, download_path=download_path)
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


def get_crawler(path2driver: str, db_info: dict, visibility=False, download_path=None):
    return Crawler(path2driver, db_info, visibility=visibility, download_path=download_path)
