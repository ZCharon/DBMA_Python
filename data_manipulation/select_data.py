# -*- codeing = utf-8 -*-
# @Time : 2020/11/27 21:32
# @Author : guanghao zhou
# @File : select_data.py
# Software : PyCharm
"""
查询语句
"""
import json
import os
import re
from prettytable import PrettyTable
import xlrd

from data_manipulation.base_function import get_where_list
from data_manipulation.base_function import solve_bracket_sql
from data_manipulation.base_function import get_result_sql


class Select:
    def __init__(self, sql_parsed, user):
        self.__user = user
        self.__sql_parsed = sql_parsed  # sqlparsed后的字符串
        self.__table = self.__sql_parsed[0].tokens[6].value  # 当前库
        self.__select_col_dict = {}  # 用户查询的键值对
        self.__index = {}  # 用户建立的索引表
        self.__where_list = []  # where列表
        self.__where_list_revere = []
        self.__json_dict = {}  # 从json文件读取当前库的属性字典
        self.count = 0  # 查询到的数据

    def select(self):
        """
        select主函数
        :return: dict: 查询后的结果集
        """
        try:
            view_where_list, view_col_set = self.__read_json()  # 读取json文件
            self.__get_select_col_dict()  # 得到查询的键值对
            if len(self.__select_col_dict) == 0:
                print("select参数错误，请查证后输入！")
                return None  # 查询失败，返回空指
            self.__where_list = get_where_list(self.__sql_parsed, 8)  # 得到where_list
            self.__get_index()
            self.__select_data(view_where_list, view_col_set)  # 进行数据查询
            return self.__select_col_dict  # 返回查询到的数据字典
        except KeyError:
            print("select 参数错误，请查证后输入！")
        except PermissionError:
            print("select 路径错误，请查证后输入！")
        except IOError:
            print("select 路径出错，请查证后输入！")
        except IndexError:
            print("delete 参数出错，请查证后输入！")

    def __select_data(self, view_where_list, view_col_set):
        """
        查询数据
        :return: None
        """
        if not os.path.exists(self.__user.data_path):
            raise IOError
        # 进行xls文件的操作
        userinfo = xlrd.open_workbook(self.__user.data_path, formatting_info=True)
        worksheet = userinfo.sheet_by_name(self.__table)

        # 如果当前表不为空
        if worksheet is not None:
            if len(view_where_list) > 0:
                # where条件进行拼接
                self.__where_list.insert(0, '(')
                self.__where_list.append(')')
                self.__where_list.append('AND')
                self.__where_list = self.__where_list + view_where_list
            self.__where_list_revere = solve_bracket_sql(self.__where_list)

            if len(view_col_set) > 0:
                # 查询表进行约束
                temp = []
                for item in self.__select_col_dict:
                    if item not in view_col_set:
                        temp.append(item)

                for item in temp:
                    del self.__select_col_dict[item]

            # 是否调用索引：
            _, where_select_set = get_result_sql(worksheet, 0, self.__where_list_revere, self.__json_dict)
            key_select = where_select_set.pop()
            key_index = None
            if not (len(where_select_set) == 0 and key_select in self.__index.keys()):  # 无索引时
                # 无索引时，使用主键索引
                # 寻找主键，进而寻找主键索引
                for item in self.__json_dict:
                    for i in self.__json_dict[item]:
                        if isinstance(i, str):
                            if re.search('KEY', i, flags=0):
                                key_index = item
            else:
                # 有索引，使用当前索引
                key_index = key_select
            for rows in sorted(self.__index[key_index].keys()):
                flag, _ = get_result_sql(worksheet, self.__index[key_index][rows][0], self.__where_list_revere, self.__json_dict)
                if flag:
                    for row in self.__index[key_index][rows]:
                        self.count += 1
                        # 读取当前行
                        current = worksheet.row_values(row)
                        # 遍历查询列表
                        for select in self.__select_col_dict:
                            # 将要查询的值加入该键的列表中
                            if select != '@@INDEX@@':
                                self.__select_col_dict[select].append(current[self.__json_dict[select][-1]])
            print("查询完成，共查到{}条数据！".format(self.count))
        return self.__select_col_dict

    def __get_select_col_dict(self):
        """
        得到用户需要查询的col
        :return: None
        """
        select_col = self.__sql_parsed[0].tokens[2].value.replace('\n', '').replace(' ', '').split(',')
        # 符合索引查询条件，
        if len(select_col) == 1 and select_col[0] == '*':
            for item in self.__json_dict.keys():
                self.__select_col_dict[item] = []
        else:
            for item in select_col:
                self.__select_col_dict[item] = []

    def __read_json(self):
        """
        从json文件中，读取所在table的列明及其属性
        :return: None
        """
        json_path = self.__user.data_path.replace('.xls', '.json')

        view_where_list = []
        view_col_set = set()
        # 如果存在视图
        view_path = self.__user.data_path.replace('.xls', '_view.json')
        if os.path.exists(view_path):
            with open(view_path, 'r', encoding='UTF-8') as f:
                view_dict = json.load(f)

            if self.__table in view_dict.keys():
                # 如果存在视图，进行视图嵌套
                if os.path.exists(view_path):
                    view_col_set = set(view_dict[self.__table][1])
                    view_where_list = view_dict[self.__table][2]
                    self.__table = view_dict[self.__table][0]
                    # 如果当前使用的是视图, 读取视图信息
                    while self.__table in view_dict.keys():
                        view_col_set = set(view_dict[self.__table][1]) & view_col_set  # 求交集
                        # 将表达式合并
                        view_dict[self.__table][2].insert(0, '(')
                        view_dict[self.__table][2].append(')')
                        view_dict[self.__table][2].append('AND')
                        view_where_list.insert(0, '(')
                        view_where_list.append(')')
                        view_where_list = view_dict[self.__table][2] + view_where_list
                        # 更新table
                        self.__table = view_dict[self.__table][0]

                    if len(view_where_list) > 0:
                        # 加括号
                        view_where_list.insert(0, '(')
                        view_where_list.append(')')
        with open(json_path, 'r+') as f:
            self.__json_dict = json.load(f)[self.__table]

        return view_where_list, view_col_set

    def __get_index(self):
        """
        获得当前表的索引
        :return:
        """
        for item in self.__json_dict:
            if item != '@@INDEX@@':
                if isinstance(self.__json_dict[item][-2], dict):
                    self.__index[item] = self.__json_dict[item][-2]  # 索引

    def print_table(self):
        """
        打印查询到的用户表
        :return:
        """
        if self.count > 0:
            table = PrettyTable()
            for item in self.__select_col_dict:
                if item != '@@INDEX@@':
                    table.add_column(item, self.__select_col_dict[item])
            print(table)
