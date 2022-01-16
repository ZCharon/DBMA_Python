# -*- codeing = utf-8 -*-
# @Time : 2020/12/22 13:12
# @Author : guanghao zhou
# @File : help_user.py
# Software : PyCharm
"""
处理help语句，输出帮助信息
"""
import json

import sqlparse
import xlrd


class Help:
    def __init__(self, strs, user):
        self.__user = user
        self.__strs = strs

    def help_user(self):
        sql = sqlparse.format(self.__strs, reindent=True, keyword_case='upper')
        sql_parsed = sqlparse.parse(sql)
        try:
            param = sql_parsed[0].tokens[2].value.upper()
        except IndexError:
            print("HELP 参数出错，请查证后输入！")
            return
        str_split = sql.split(' ')
        if param == "DATABASE":
            try:
                self.__help_database()
            except PermissionError:
                print("Help Database 路径出错，请查证后输入！")
            except AttributeError:
                print("Help Database 参数出错，请查证后输入！")
            except KeyError:
                print("Help Database 参数出错，请查证后输入！")
        elif param == "TABLE":
            try:
                self.__help_table(str_split[2])
            except PermissionError:
                print("Help Table 路径出错，请查证后输入！")
            except AttributeError:
                print("Help Table 参数出错，请查证后输入！")
            except KeyError:
                print("Help Table 参数出错，请查证后输入！")
        elif param == "VIEW":
            try:
                self.__help_view(str_split[2])
            except KeyError:
                print("Help View 参数出错，请查证后输入！")
            except AttributeError:
                print("Help View 参数出错，请查证后输入！")
            except PermissionError:
                print("Help Table 参数出错，请查证后输入！")
        # elif param == "INDEX":
        #     self.__help_index(str_split[2])
        else:
            print("HELP 参数出错，请查证后输入！")

    def __help_database(self):
        """
        输入“help database”命令，输出所有数据表、视图和索引的信息，同时显示其对象类型
        :return:
        """
        userinfo = xlrd.open_workbook(self.__user.data_path, formatting_info=True)
        sheet_names = userinfo._sheet_names  # 所有表的信息
        json_path = self.__user.data_path.replace('.xls', '.json')
        with open(json_path, 'r+') as f:
            val = json.load(f)
        json_path_view = self.__user.data_path.replace('.xls', '_view.json')
        with open(json_path_view, 'r+') as f:
            val_view = json.load(f)

        for item in sheet_names:
            print("table: ", item)
            print("索引：")
            if item != "default":
                for index_key in val[item]['@@INDEX@@']:
                    print(index_key, " --> ", val[item]['@@INDEX@@'][index_key])

        # 输出视图
        print("视图：")
        if len(val_view) == 0:
            print("None")
        else:
            for item in val_view:
                print(item, " --> ", val_view[item][0])

    def __help_table(self, param):
        json_path = self.__user.data_path.replace('.xls', '.json')
        with open(json_path, 'r+') as f:
            val = json.load(f)
        table_json = val[param]
        col_val = {}
        for item in table_json:
            if item != '@@INDEX@@':
                col_val[item] = []
                if isinstance(table_json[item][-2], dict):
                    col_val[item] = col_val[item] + table_json[item][: -2]
                else:
                    col_val[item] = col_val[item] + table_json[item][: -1]

        for item in col_val:
            print(item, " --> ", end=" ")
            for i in col_val[item]:
                print(i, end=' ')
            print()

    def __help_view(self, param):
        """
        “help view 视图名”命令，输出视图的定义语句
        :param param:
        :return:
        """

        str_ = "CREATE VIEW {} \nAS \nSELECT {}\nFROM {} \nWHERE {}"
        json_path_view = self.__user.data_path.replace(".xls", "_view.json")
        with open(json_path_view, 'r+') as f:
            val_view = json.load(f)
        view_item = val_view[param]
        view_name = view_item[0]
        view_col = ""
        view_col = view_col + view_item[1][0]
        for i, ele in enumerate(view_item[1]):
            if i > 0:
                view_col = view_col + ", " + ele

        view_where = ''
        view_where = view_where + view_item[2][0]
        for i, ele in enumerate(view_item[2]):
            if i > 0:
                view_where = view_where + " " + ele

        print(str_.format(param, view_col, view_name, view_where))

    # def __help_index(self, param):
    #     """
    #     输入“help index 索引名”命令，输出索引的详细信息。
    #     :param param:
    #     :return:
    #     """
    #     json_path_index = self.__user.data_path
    #     with open(json_path_index, 'r+') as f:
    #         val_view = json.load(f)

