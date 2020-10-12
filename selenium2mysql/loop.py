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
                tmp_commands = "lock tables {} write;".format(queue_name)
                tmp_commands += "select {} from {} limit {};".format(target_head, queue_name, assignment_number)
                tmp_commands += "delete from {} limit {};".format(queue_name, assignment_number)
                tmp_commands += "unlock tables;"
                tmp_df = self.__queue.execute(tmp_commands)

                for x in tmp_df[target_head]:
                    tmp_obj = func(x)
                    if tmp_obj:
                        tmp_result_list.append(tmp_obj)
            return pd.DataFrame(tmp_result_list)

        return wrapper
