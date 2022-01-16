# -*- codeing = utf-8 -*-
# @Time : 2020/12/3 20:32
# @Author : guanghao zhou
# @File : test.py
# Software : PyCharm
import copy
import re

import sqlparse

if __name__ == '__main__':
    # str = """create index SageIndex on Student (Sage);"""
    #
    # sql = sqlparse.format(str, reindent=True, keyword_case='upper')
    # # print(sql)
    #
    # sql_parsed = sqlparse.parse(sql)
    # print(sql_parsed[0].tokens[0].value)
    # print(sql_parsed[0].tokens[2].value)
    # print(sql_parsed[0].tokens[4].value)
    # print(sql_parsed[0].tokens[6].value)
    # print(sql_parsed[0].tokens[8].value)
    #
    # list_ = sql_parsed[0].tokens[8].value.replace(')', ' ').replace('(', ' ').split(' ')
    # while '' in list_:
    #     list_.remove('')
    # print(list_)

    # str_ = """create view view_name as select Sname, Sno from Student where Ssex = '男' and Sno < 2;"""
    # sql = sqlparse.format(str_, reindent=True, keyword_case='upper')
    # print(str_)
    # sql_parsed = sqlparse.parse(sql)
    # print(sql_parsed[0].tokens[0].value)  # CREATE
    # print(sql_parsed[0].tokens[2].value)  # VIEW
    # print(sql_parsed[0].tokens[4].value)  # view_name
    # print(sql_parsed[0].tokens[6].value)  # AS
    # print(sql_parsed[0].tokens[8].value)  # SELECT
    # print(sql_parsed[0].tokens[10].value)  # Sname form
    # print(sql_parsed[0].tokens[12].value)  # Student
    # print(sql_parsed[0].tokens[14].value)
    # print(sql_parsed[0].tokens[16].value)  # WHERE Ssex = '男' AND Sno < 2;

    str_ = 'help database;'
    sql = sqlparse.format(str_, reindent=True, keyword_case='upper')
    sql_parsed = sqlparse.parse(sql)
    print(sql_parsed[0].tokens[0].value)
    print(sql_parsed[0].tokens[2].value.upper())
    print(sql)

    str_ = "DATABASE帮助信息：\nCREATE DATABASE 库名;"
    print(str_)