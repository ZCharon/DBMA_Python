# -*- codeing = utf-8 -*-
# @Time : 2020/11/27 21:32
# @Author : guanghao zhou
# @File : update_data.py
# Software : PyCharm
"""
更新语句
"""
import json
import os

import xlrd
import xlutils
import xlutils.copy

from data_manipulation.base_function import get_type
from data_manipulation.base_function import get_where_list
from data_manipulation.base_function import solve_bracket_sql
from data_manipulation.base_function import get_result_sql


class Update:
    def __init__(self, sql_parsed, user):
        self.__user = user
        self.__sql_parsed = sql_parsed  # sqlparsed后的字符串
        self.__table = self.__sql_parsed[0].tokens[2].value  # 当前库
        self.__where_list_revere = []
        self.__val_key_dict = {}  # 用户修改的键值对
        self.__json_dict = {}  # 从json文件读取当前库的属性字典

    def update(self):
        """
        执行update操作
        :return:
        """
        try:
            self.__read_json()  # 读取json文件
            self.__get_val_key()  # 得到修改的键值对
            where_list = get_where_list(self.__sql_parsed, 8)  # 得到where_list
            if len(where_list) <= 2:
                print("update 参数错误，请查证后输入！")
                return
            self.__update_data(where_list)  # 进行数据修改
        except IndexError:
            print("update 参数错误，请查证后输入！")
        except PermissionError:
            print("update 路径错误，请查证后输入！")
        except IOError:
            print("update 路径错误，请查证后输入!")
        except KeyError:
            print("update 参数错误，请查证后输入！")
        except ValueError:
            print("update 参数错误，请查证后输入！")

    def __update_data(self, where_list):
        """
        更新数据
        :return:
        """
        if not os.path.exists(self.__user.data_path):
            raise IOError
        # 进行xls文件的操作
        userinfo = xlrd.open_workbook(self.__user.data_path, formatting_info=True)
        worksheet = userinfo.sheet_by_name(self.__table)
        user_copy = xlutils.copy.copy(userinfo)
        copy_sheet = user_copy.get_sheet(self.__table)

        if copy_sheet is not None:
            count = 0
            nrows = worksheet.nrows  # 表的行数
            self.__where_list_revere = solve_bracket_sql(where_list)
            for row in range(nrows):  # 顺序读取每一行
                flag, _ = get_result_sql(worksheet, row, self.__where_list_revere, self.__json_dict)
                if flag:
                    count += 1
                    for item in self.__val_key_dict.keys():
                        if item != '@@INDEX@@':
                            tag = get_type(self.__json_dict[item])
                            if tag == 0:
                                copy_sheet.write(row, int(self.__json_dict[item][-1]), str(self.__val_key_dict[item]))
                            elif tag == 1:
                                copy_sheet.write(row, int(self.__json_dict[item][-1]), int(self.__val_key_dict[item]))
                            elif tag == 2:
                                copy_sheet.write(row, int(self.__json_dict[item][-1]), float(self.__val_key_dict[item]))

            user_copy.save(self.__user.data_path)
            print("数据更新成功，共更新{}条数据".format(count))

    def __read_json(self):
        """
        从json文件中，读取所在table的列明及其属性
        :return:
        """
        json_path = self.__user.data_path.replace('.xls', '.json')
        with open(json_path, 'r+') as f:
            self.__json_dict = json.load(f)[self.__table]

    def __get_val_key(self):
        """
        得到用户需要修改的键值对
        :return:
        """
        strs = self.__sql_parsed[0].tokens[6].value.replace("\n", "").split(",")
        lists = []
        for item in strs:
            item_split = item.split("=")
            item_split[0] = item_split[0].lstrip(' ').lstrip("'").rstrip(' ').rstrip("'")
            item_split[1] = item_split[1].lstrip(' ').lstrip("'").rstrip(' ').rstrip("'")
            lists.append(item_split)
        for item in lists:
            self.__val_key_dict[item[0]] = item[1]
