import json
import validators
from csv2sqllike.PseudoSQLFromCSV import PsuedoSQLFromCSV
from csv2sqllike.Transfer2SQLDB import Transfer2SQLDB


class QueueManager(Transfer2SQLDB):
    def __init__(self, info_dict=None):
        """
        db_info = dict(host=<ip_address>, user=<user_name>, password=<password>, db=<db_name>, charset='UTF8MB4', port=<port>)
        """
        super(QueueManager, self).__init__(info_dict)

    def make_queue(self, queue_table_name: str):
        tmp_table_list = self.get_tables()
        if queue_table_name not in tmp_table_list:
            tmp_command = "create table " + queue_table_name + "(table_name varchar(50), url varchar(200), order_list " \
                                                               "text, get_dict text, click_dict text, insert_dict " \
                                                               "text, selector_dict text); "
            self.execute(tmp_command)
        else:
            print(queue_table_name, "already exists")

    def fill2queue(self, url_list: list, queue_table: str, table_name: str, order_list=list(), get_dict=dict(),
                   click_dict=dict(), insert_dict=dict(), selector_dict=dict()) -> None:
        tmp_sqllike = PsuedoSQLFromCSV("")
        tmp_sqllike.dtype = {'url': 'str', 'table_name': 'str', 'order_list': 'str', 'get_dict': 'str',
                             'click_dict': 'str',
                             'insert_dict': 'str', 'selector_dict': 'str'}
        tmp_sqllike.header = ['url', 'table_name', 'order_list', 'get_dict', 'click_dict', 'insert_dict',
                              'selector_dict']
        tmp_sqllike.data = list()
        tmp_order_list = json.dumps(order_list)
        tmp_get_dict = json.dumps(get_dict)
        tmp_click_dict = json.dumps(click_dict)
        tmp_insert_dict = json.dumps(insert_dict)
        tmp_selector_dict = json.dumps(selector_dict)
        for tmp_url in url_list:
            if validators.url(tmp_url) is True:
                tmp_sqllike.data.append(
                    [tmp_url, table_name, tmp_order_list, tmp_get_dict, tmp_click_dict, tmp_insert_dict,
                     tmp_selector_dict])

        self.execute("lock tables " + queue_table + " write;")
        self.insert_data(queue_table, tmp_sqllike, exclude_history=True)
        self.execute("unlock tables;")
