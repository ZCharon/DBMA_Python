# -*- codeing = utf-8 -*-
# @Time : 2020/11/27 21:32
# @Author : guanghao zhou
# @File : insert_data.py
# Software : PyCharm
"""
插入数据
"""
import sqlparse
import re
import json
import xlrd
import os
import xlutils.copy
import copy


# 执行插入语句操作
class Insert:
    def __init__(self, sql_parse, user):
        self.__user = user  # 当前进行的用户
        self.__user_key = None  # user输入的table的key
        self.__user_value = []  # user输入table的value
        self.__table = None  # 当前活动的table
        self.__sql_parse = sql_parse  # 当前处理的sql语句
        self.__data_path = user.data_path  # 当前的文件路径
        self.__key_value_dict = {}  # 从json文件中读出的争取的键值与属性

    def insert(self):
        """
        执行插入操作
        :return:
        """
        try:
            self.__take_sql_parse()  # 对sql字符串进行处理，对部分变量进行初始化
            self.__read_json()  # 阅读对应库的json文件，获得table的属性信息
            self.__insert_data()  # 执行插入操作
        except KeyError:
            print("insert 参数出错，请查证后输入！")
        except PermissionError:
            print("insert 路径出错，请查证后输入！")
        except IOError:
            print("insert 路径出错，请查证后输入！")

    def __read_json(self):
        """
        从json文件中，读取所在table的列明及其属性
        :return:
        """
        json_path = self.__user.data_path.replace('.xls', '.json')
        with open(json_path, 'r+') as f:
            self.__key_value_dict = json.load(f)[self.__table]

    def __add_index(self, column, index):
        """
        向json文件添加索引
        :return:
        """
        json_path = self.__user.data_path.replace('.xls', '.json')
        with open(json_path, 'r') as f:
            val = json.load(f)
        with open(json_path, 'w') as f:
            table_dict = val[self.__table]
            if isinstance(table_dict[column][-2], dict):
                table_dict[column][-2] = dict(table_dict[column][-2], **index)
            else:
                table_dict[column].insert(-1, copy.deepcopy(index))
            json.dump(val, f, ensure_ascii=False, indent=4)
        return

    def __take_sql_parse(self):
        """
        对用户输入格式化后的sql语句进行信息提取
        table、keys、values
        :return: None
        """
        sql_parse = sqlparse.format(self.__sql_parse, reindent=True, keyword_case='upper')
        sql_prase = sql_parse.replace("\n", '')
        # 提取当前insert的table
        self.__table = sql_prase.split(' ')[3].rsplit('(')[0]
        # 利用正则表达式，提取括号中的内容
        strs = re.findall(r'[(](.*?)[)]', sql_prase)
        count = 0
        for item in strs:
            if count == 0:
                self.__user_key = item.replace(' ', '').split(",")  # 获得当前要插入的键
            else:
                self.__user_value.append(item.replace(' ', '').split(','))  # 获得当前要插入的值
            count += 1

    def __get_keys(self, user_table):
        """
        返回当前表的所有key值
        :param user_table: 当前表
        :return: set: key
        """
        key = set()
        nrows = user_table.nrows
        loc = 0
        for vals in self.__key_value_dict.values():
            for val in vals:
                if re.search('KEY', str(val), flags=0):
                    for i in range(nrows):
                        key.add(user_table.cell_value(i, loc))
            loc += 1
        return key

    def __insert_data(self):
        """
        根据self.user_key, self.user_value对.xls文件进行修改
        :return:
        """
        # 判断sql语句database是否存在，不存在抛出异常
        if not os.path.exists(self.__user.data_path):
            raise IOError
        # 进行xls文件的操作
        userinfo = xlrd.open_workbook(self.__data_path, formatting_info=True)
        user_table = userinfo.sheet_by_name(self.__table)

        user_copy = xlutils.copy.copy(userinfo)
        copy_sheet = user_copy.get_sheet(self.__table)

        if copy_sheet is not None:
            index = {}  # 建立索引
            tag = 0  # 各个属性的tag标记
            nrows = user_table.nrows  # 表的行数
            major = -1
            key = self.__get_keys(user_table)  # 获得当前表的所有key值
            temp_rows = nrows  # 插入的行定位

            # 寻找真正的最后一行
            if temp_rows > 0:
                while user_table.cell(temp_rows - 1, 0).value == "#####":
                    if temp_rows - 1 > 0:
                        temp_rows -= 1
                    else:
                        temp_rows = 0
                        break

            fail_count = 0  # 插入失败的数据数
            count = 1  # 插入操作计数器
            for values in self.__user_value:
                for i in range(len(self.__user_key)):
                    ifKey = False
                    # if self.user_key[i] in self.key_value_dict.keys():
                    if self.__key_value_dict.get(self.__user_key[i], 0) is not 0:
                        for item in self.__key_value_dict[self.__user_key[i]]:
                            if re.search('char', str(item), flags=0):
                                tag = 0  # 0代表字符串
                            elif re.search('int', str(item), flags=0):
                                tag = 1  # 1代表整形
                            elif re.search('float', str(item), flags=0):
                                tag = 2  # 2代表浮点型
                            elif re.search('KEY', str(item), flags=0):
                                major = self.__user_key[i]
                                ifKey = True

                        if tag == 1:
                            if ifKey:
                                if str(values[i].replace('\'', '')) in key or str(values[i].replace('\'', '')) == '':
                                    print("第" + str(count) + "条数据主键重复或为空，插入失败")
                                    temp_rows -= 1
                                    fail_count += 1
                                    break
                                else:
                                    key.add(int(values[i].replace('\'', '')))
                                    if str(values[i].replace('\'', '')) not in index.keys():
                                        index[str(values[i].replace('\'', ''))] = []
                                    index[str(values[i].replace('\'', ''))].append(temp_rows)
                            copy_sheet.write(temp_rows, int(self.__key_value_dict[self.__user_key[i]][-1]),
                                             int(values[i].replace('\'', '')))

                        elif tag == 2:
                            if ifKey:
                                if str(values[i].replace('\'', '')) in key or str(values[i].replace('\'', '')) == '':
                                    print("第" + str(count) + "条数据主键重复或为空，插入失败")
                                    temp_rows -= 1
                                    fail_count += 1
                                    break
                                else:
                                    key.add(str(values[i].replace('\'', '')))
                                    if str(values[i].replace('\'', '')) not in index.keys():
                                        index[str(values[i].replace('\'', ''))] = []
                                    index[str(values[i].replace('\'', ''))].append(temp_rows)
                            copy_sheet.write(temp_rows, int(self.__key_value_dict[self.__user_key[i]][-1]),
                                             float(values[i].replace('\'', '')))

                        else:
                            if ifKey:
                                if str(values[i].replace('\'', '')) in key or str(values[i].replace('\'', '')) == '':
                                    print("第" + str(count) + "条数据主键已存在或为空，插入失败")
                                    temp_rows -= 1
                                    fail_count += 1
                                    break
                                else:
                                    key.add(str(values[i].replace('\'', '')))
                                    if str(values[i].replace('\'', '')) not in index.keys():
                                        index[str(values[i].replace('\'', ''))] = []
                                    index[str(values[i].replace('\'', ''))].append(temp_rows)
                            copy_sheet.write(temp_rows, int(self.__key_value_dict[self.__user_key[i]][-1]),
                                             str(values[i].replace('\'', '')))
                    else:
                        raise AttributeError
                temp_rows += 1
                count += 1
            self.__add_index(major, index)  # 添加索引
            user_copy.save(self.__data_path)
            if count > 0:
                print("insert执行成功，共插入" + str(count - 1 - fail_count) + "条数据！")
        else:
            print('table不存在，请查证后输入！')
