import pandas as pd


class Loop(object):
    def __init__(self, queue):
        self.__queue = queue

    def __call__(self, func):
        def wrapper(queue_name="", target_head="url", assignment_number=100):
            tmp_command = "select `TABLE_ROWS` from information_schema.TABLES where `TABLE_NAME` = '{}';".format(
                queue_name)
            tmp_list = self.__queue.execute(tmp_command).to_numpy().tolist()
            tmp_result_list = list()
            tmp_df = None
            if tmp_list and tmp_list[0]:
                self.__queue.execute("lock tables {} write;".format(queue_name))
                tmp_df = self.__queue.execute(
                    "select {} from {} limit {}".format(target_head, queue_name, assignment_number))
                self.__queue.execute("delete from {} limit {}".format(queue_name, assignment_number))
                self.__queue.execute("unlock tables;")
                for x in tmp_df[target_head]:
                    tmp_obj = func(x)
                    if tmp_obj:
                        tmp_result_list.append(tmp_obj)
            return pd.DataFrame(tmp_result_list)

        return wrapper
