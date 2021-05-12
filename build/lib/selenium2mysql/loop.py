class Loop(object):
    def __init__(self, queue):
        self.__queue = queue

    def __call__(self, func):
        def wrapper(queue_name="", target_head="url", assignment_number=100):
            tmp_command = "select exists(select * from {});".format(queue_name)
            tmp_cnt = self.__queue.execute(tmp_command).iloc[0, 0]
            tmp_result_list = list()
            if tmp_cnt != 0:
                tmp_commands = "lock tables {} write;".format(queue_name)
                tmp_commands += "select {} from {} limit {};".format(target_head, queue_name, assignment_number)
                tmp_commands += "delete from {} limit {};".format(queue_name, assignment_number)
                tmp_commands += "unlock tables;"
                tmp_df = self.__queue.execute(tmp_commands)
                if len(tmp_df) > 0:
                    for x in tmp_df[target_head]:
                        tmp_obj = func(x)
                        if tmp_obj:
                            tmp_result_list.append(tmp_obj)
            return tmp_result_list

        return wrapper
