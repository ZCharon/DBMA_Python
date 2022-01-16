# -*- codeing = utf-8 -*-
# @Time : 2020/11/27 22:04
# @Author : guanghao zhou
# @File : create_table.py
# Software : PyCharm
"""
新建表/新建库
"""
import xlwt
import xlrd
import os
import xlutils.copy
import json
import re
from data_manipulation.base_function import get_where_list

"""
    创建类，对数据库执行创建操作
    create databases;
    create table;
    create index;
    create view;
"""


class Create:

    def __init__(self, sql_parse, user):
        """
        初始化函数
        :param sql_parse: 当前格式化后的sql语句
        :param user: 当前活动的对象
        """
        self.__sql_parse = sql_parse  # sqlparsed语句
        self.__user = user  # user类

    def create(self):
        """
        根据sql语句调用响应创建方法
        :return: null
        """
        if self.__sql_parse[0].tokens[2].value.upper() == 'TABLE':
            try:
                self.__create_table()
            except OSError:
                print("create table 路径出错，请查证后输入！")

        elif self.__sql_parse[0].tokens[2].value.upper() == 'DATABASE':
            try:
                self.__create_database()
            except PermissionError:
                print("create 路径出错，请查证后输入！")

        elif self.__sql_parse[0].tokens[2].value.upper() == 'INDEX':
            try:
                self.__create_index()
            except PermissionError:
                print("create index 路径出错，请查证后输入！")
            except KeyError:
                print("create index 参数出错，请查证后输入！")
            except IndexError:
                print("create index 参数出错，请查证后输入！")

        elif self.__sql_parse[0].tokens[2].value.upper() == 'VIEW':
            try:
                self.__create_view()
            except PermissionError:
                print("create view 路径输错，请查证后输入！")
            except IOError:
                print("create view 路径输错，请查证后输入！")

        else:
            print("create参数错误，请查证后输入！")

    def __create_view(self):
        """
        创建视图，构建json视图文件
        :return:
       """

        if not (self.__sql_parse[0].tokens[6].value == 'AS' and self.__sql_parse[0].tokens[12].value == 'FROM'):
            return
        # 得到视图的别名
        view_name = self.__sql_parse[0].tokens[4].value
        # 得到查询的表
        view_col_list = []
        for item in self.__sql_parse[0].tokens[10].value.replace('\n', '').replace(' ', '').split(','):
            view_col_list.append(item)
        view_table = self.__sql_parse[0].tokens[14].value  # 得到视图的table
        view_where_list = get_where_list(self.__sql_parse, 16)  # 得到where后缀表达式
        view_path = self.__user.data_path.replace('.xls', '_view.json')
        table_path = self.__user.data_path.replace('.xls', '.json')
        view_dict = {}
        view_struct = [view_table, view_col_list, view_where_list]
        view_dict[view_name] = view_struct

        with open(table_path, 'r', encoding="utf-8") as f:
            database_table = json.load(f)
        # 将view结构化后的数据存储在json文件中
        if os.path.exists(view_path):
            with open(view_path, 'r', encoding="utf-8") as f:
                val = json.load(f)
            if view_table not in val.keys() and view_table not in database_table.keys():
                print("create view table 不存在，请查证后输入！")
                return
            with open(view_path, 'w', encoding="utf-8") as f:
                val.update(view_dict)
                json.dump(val, f, indent=4, ensure_ascii=False)
        else:
            if view_table not in database_table.keys():
                print("create view table 不存在，请查证后输入！")
                return
            f = open(view_path, "w+", encoding="utf-8")
            jsondata = json.dumps(view_dict, indent=4, ensure_ascii=False)
            f.write(jsondata)
            f.close()

    def __create_database(self):
        """
        处理 CREATE DATABASE 库名;
        :return:
        """
        # 指定文件路径，无则创建
        temp_path = self.__user.data_path
        if re.search(".xls", self.__user.data_path, flags=0):
            self.__user.data_path = self.__user.data_path[:self.__user.data_path.rfind('/') + 1]
        database_path = self.__user.data_path + self.__sql_parse[0].tokens[4].value.lower().replace(";", '') + '.xls'
        if os.path.exists(database_path):
            self.__user.data_path = temp_path
            print("database已存在，创建失败！")
            return
        else:
            database = xlwt.Workbook(encoding='utf-8')  # 新建工作簿
            _ = database.add_sheet('default')
            database.save(database_path)  # 保存文件

    def __create_table(self):
        """
        处理create table;
        :return: null
        """
        # 指明文件路径
        if self.__user.data_path[-4:] == '.xls':
            database = xlrd.open_workbook(self.__user.data_path, formatting_info=True)
            sheets = database._sheet_names
            if self.__sql_parse[0].tokens[4].value in sheets:
                print("table已存在，创建失败")
                return
            database_copy = xlutils.copy.copy(database)
            self.__user.current_table = self.__sql_parse[0].tokens[4].value
            database_copy.add_sheet(self.__user.current_table)
            parameter = self.__sql_parse[0].tokens[5].value
            self.__parse_parameters(parameter)
            self.__add_default_information(self.__user.current_table)
            database_copy.save(self.__user.data_path)  # 保存文件
        else:
            raise IOError

    def __create_index(self):
        """
        创建index索引，在.json文件中插入相应的索引
        :return:
        """
        list_ = self.__sql_parse[0].tokens[8].value.replace(')', ' ').replace('(', ' ').split(' ')
        index_name = self.__sql_parse[0].tokens[4].value  # 索引名
        while '' in list_:
            list_.remove('')
        table = list_[0]  # 库名
        col_val = list_[1]  # 列名
        # 在json表中建立索引映射
        json_path = self.__user.data_path.replace('.xls', '.json')
        with open(json_path, 'r') as f:
            val = json.load(f)

        sheet_dirt = val[table]

        if isinstance(sheet_dirt[col_val][-2], dict):
            del sheet_dirt[col_val][-2]
        index = {}
        self.__add_index(index, sheet_dirt, table, col_val)
        sheet_dirt[col_val].insert(-1, index)

        with open(json_path, 'w') as f:
            sheet_dirt['@@INDEX@@'][index_name] = col_val
            json.dump(val, f, ensure_ascii=False, indent=4)

    def __add_index(self, index_dict, table_dict, table, col_val):
        """
        为索引表添加索引
        :param index_dict: 索引字典
        :param table_dict: 当前table的属性表
        :param table: 当前表
        :param col_val: 索引列的名字
        :return:
        """
        if not os.path.exists(self.__user.data_path):
            raise IOError

        # 进行xls文件的操作
        userinfo = xlrd.open_workbook(self.__user.data_path, formatting_info=True)
        worksheet = userinfo.sheet_by_name(table)
        nrows = worksheet.nrows

        tag = 0
        col_num = table_dict[col_val][-1]
        for row in range(nrows):
            current = worksheet.row_values(row)
            if current[col_num] not in index_dict.keys():
                index_dict[current[col_num]] = []

            for item in table_dict[col_val]:
                if re.search('int', item, flags=0):
                    tag = 1
                    break
                elif re.search('float', item, flags=0):
                    tag = 2
                    break
            if tag == 1:
                index_dict[int(current[col_num])].append(row)
            elif tag == 2:
                index_dict[float(current[col_num])].append(row)
            else:
                index_dict[current[col_num]].append(row)

    def __parse_parameters(self, parameter):
        """
        对初始的参数str进行处理
        :param parameter: str -> 未经处理的参数列表
        :return: str[]: 经过处理后的参数列表
        """
        parameter = parameter.replace('\n', '')
        parameters = parameter.split(',')
        for i in range(len(parameters)):
            parameters[i] = parameters[i].lstrip()
        parameters[0] = parameters[0].lstrip('(')
        parameters[-1] = parameters[-1].rstrip(')') + ')'
        value_dir = []
        key_value_dir = {}
        count = 0
        for item in parameters:
            items = item.split(' ')
            if not items[0] in key_value_dir:
                for i in items:
                    value_dir.append(i)
                value_dir.pop(0)
                key_value_dir[items[0]] = value_dir.copy()
                key_value_dir[items[0]].append(count)
                count += 1
            value_dir.clear()
        self.__key_value_dict = key_value_dir

    def __add_default_information(self, table):
        """
        创建.xls文件时，创建.json文件记录属性
        :param table:
        :return:
        """
        """
        对用户新建表进行解析，以当前库为文件名存取成json文件，进行记录
        并在相应的属性处建立索引
        :param table: str -> 当前所建库的库名
        :return: null
        """
        data_infor_path = self.__user.data_path.replace(".xls", ".json")
        key_value_dict = self.__key_value_dict
        key_value_dict['@@INDEX@@'] = {}
        table_direct = {table: key_value_dict}
        if not os.path.exists(data_infor_path):
            f = open(data_infor_path, "w+")
            json_data = json.dumps(table_direct, indent=4, ensure_ascii=False)
            f.write(json_data)
            f.close()
        else:
            with open(data_infor_path, 'r+') as f:
                old_data = json.load(f)
                old_data.update(table_direct)
            with open(data_infor_path, "w", encoding="utf-8") as f:
                json.dump(old_data, f, indent=4, ensure_ascii=False)

