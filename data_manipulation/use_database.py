# -*- codeing = utf-8 -*-
# @Time : 2020/12/3 20:04
# @Author : guanghao zhou
# @File : use_database.py
# Software : PyCharm
"""
处理USE语句
"""
import os
import re


def use_database(sql_parse, user):
    try:
        current_database = sql_parse[0].tokens[2].value.replace(";", '')
        if re.search('.xls', user.data_path, flags=0):
            user.data_path = user.data_path[: user.data_path.rfind('/') + 1]
        data_path = user.data_path + current_database + '.xls'
        if os.path.exists(data_path):
            user.current_database = current_database
            user.data_path = data_path
        else:
            print("use路径错误，请查证后输入！")
    except AttributeError:
        print("use路径错误，请查证后输入！")
    except IndexError:
        print("use路径错误，请查证后输入！")
