# -*- codeing = utf-8 -*-
# @Time : 2020/11/27 21:32
# @Author : guanghao zhou
# @File : delete_data.py
# Software : PyCharm
"""
删除数据
delete;
"""
import copy
import json
import os

import xlrd
import xlutils
import xlutils.copy

from data_manipulation.base_function import get_where_list
from data_manipulation.base_function import solve_bracket_sql
from data_manipulation.base_function import get_result_sql


class Delete:
    def __init__(self, sql_parsed, user):
        self.__user = user
        self.__sql_parsed = sql_parsed  # sqlparsed后的字符串
        self.__data_path = user.data_path  # 当前库的路径
        self.__table = self.__sql_parsed[0].tokens[4].value  # 当前库
        self.__val_key_dict = {}  # 用户修改的键值对
        self.__index = {}  # 用户建立的索引表
        self.__where_list = []  # where列表
        self.__where_list_revere = []
        self.__json_dict = {}  # 从json文件读取当前库的属性字典

    def delete(self):
        """
        执行update操作
        :return: None
        """
        try:
            self.__read_json()  # 读取json文件
            self.__where_list = get_where_list(self.__sql_parsed, 6)  # 得到where_list
            if len(self.__where_list) <= 2:
                print("delete where出错，请查证后输入！")
                return
            self.__get_index()
            self.__delete_data()  # 进行数据删除
        except PermissionError:
            print("delete 路径出错，请查证后输入！")
        except OSError:
            print("delete 路径出错，请查证后输入！")
        except IndexError:
            print("delete where出错，请查证后输入！")
        except KeyError:
            print("delete 参数出错，请查证后输入！")

    def __delete_data(self):
        """
        更新数据
        :return: None
        """
        if not os.path.exists(self.__user.data_path):
            raise IOError
        # 进行xls文件的操作
        userinfo = xlrd.open_workbook(self.__data_path, formatting_info=True)
        worksheet = userinfo.sheet_by_name(self.__table)
        user_copy = xlutils.copy.copy(userinfo)
        copy_sheet = user_copy.get_sheet(self.__table)

        if copy_sheet is not None:
            count = 0
            nrows = worksheet.nrows  # 表的行数
            self.__where_list_revere = solve_bracket_sql(self.__where_list)
            temp_rows = nrows
            row = 0
            while row < nrows:
                flag, _ = get_result_sql(worksheet, row, self.__where_list_revere, self.__json_dict)
                if flag:
                    count += 1
                    # 读取当前行
                    del_val = worksheet.row_values(row)
                    # 寻找第一个空行
                    while worksheet.cell(temp_rows - 1, 0).value == "#####":
                        if temp_rows - 1 > 0:
                            temp_rows -= 1
                        else:
                            temp_rows = 0
                            break
                    if temp_rows != 0:
                        temp_rows -= 1

                    last_val = worksheet.row_values(temp_rows)
                    col = 0
                    # 将最后一行的数据写入当前行，删除最后一行，同时修改索引表
                    for item in last_val:
                        copy_sheet.write(row, col, item)
                        col += 1
                    copy_sheet.write(temp_rows, 0, "#####")  # 结束标志位
                    last_val = worksheet.row_values(temp_rows)
                    # 更新索引
                    for index in self.__index:  # 遍历index中所有成索引的col
                        for i, ele in enumerate(last_val):  # 遍历last的所有值，更新关于其的所有索引
                            ele = str(ele)
                            if ele in self.__index[index].keys():
                                del self.__index[index][ele]  # 将当前行删除
                                if str(del_val[i]) in self.__index[index].keys():
                                    del self.__index[index][str(del_val[i])]
                                if str(del_val[i]) != ele:
                                    self.__index[index][ele] = []
                                    self.__index[index][ele].append(row)
                                self.__add_index(index, self.__index[index])

                    user_copy.save(self.__data_path)
                    userinfo = xlrd.open_workbook(self.__data_path, formatting_info=True)
                    worksheet = userinfo.sheet_by_name(self.__table)
                    user_copy = xlutils.copy.copy(userinfo)
                    copy_sheet = user_copy.get_sheet(self.__table)
                    if row >= 1:
                        row -= 1
                row += 1
            if count == 0:
                print("数据删除失败，查无此项！")
            else:
                print("数据删除成功，共删除{}条数据".format(count))

    def __read_json(self):
        """
        从json文件中，读取所在table的列明及其属性
        :return: None
        """
        json_path = self.__user.data_path.replace('.xls', '.json')
        with open(json_path, 'r+') as f:
            self.__json_dict = json.load(f)[self.__table]

    def __add_index(self, column, index):
        """
        向json文件添加索引
        :return: None
        """
        json_path = self.__user.data_path.replace('.xls', '.json')
        with open(json_path, 'r') as f:
            val = json.load(f)
        with open(json_path, 'w') as f:
            table_dict = val[self.__table]
            if isinstance(table_dict[column][-2], dict):
                table_dict[column][-2] = index
            else:
                table_dict[column].insert(-1, copy.deepcopy(index))
            json.dump(val, f, ensure_ascii=False, indent=4)

    def __get_index(self):
        for item in self.__json_dict:
            if item != '@@INDEX@@':
                if isinstance(self.__json_dict[item][-2], dict):
                    self.__index[item] = self.__json_dict[item][-2]  # 索引
