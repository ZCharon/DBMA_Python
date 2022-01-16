# -*- codeing = utf-8 -*-
# @Time : 2020/12/20 19:45
# @Author : guanghao zhou
# @File : base_function.py
# Software : PyCharm
import copy
import re

"""
存储用于where判断函数，便于复用
"""


class Stack(object):
    """
    栈
    """

    def __init__(self):
        self._stack = []

    def pop(self):
        return self._stack.pop()

    def push(self, x):
        self._stack.append(x)

    def is_null(self):
        return len(self._stack) == 0


def get_type(list_):
    """
    遍历字典，返回当前列的属性
    0 -> str
    1 -> int
    2 -> float
    :param list_: 当前col的属性值
    :return: int: 类型标志
    """
    tag = 0  # 默认为
    for item in list_:
        if re.search('int', str(item), flags=0):
            tag = 1  # 整形
            break
        elif re.search('float', str(item), flags=0):
            tag = 2  # 浮点型
            break
    return tag


def solve_bracket_sql(where_list):
    """
    带括号，引入#运算符, 生成后缀表达式
    """
    out = []
    if len(out) <= 0:
        pro = {'=': 1, '<>': 1, '>': 1, '<': 1, '>=': 1, '<=': 1, 'AND': 0, 'OR': 0, "#": -1}
        out = []
        s = Stack()
        s.push('#')
        for x in where_list:
            if x == '(':  # 左括号 -- 直接入栈
                s.push(x)
            elif x == ')':  # 右括号 -- 输出栈顶，直至左括号(舍弃)
                t = s.pop()
                while t != '(':
                    out.append(t)
                    t = s.pop()
            elif x in pro.keys():  # ③运算符 -- 从栈顶开始，优先级不小于x的都依次弹出；然后x入栈
                while True:
                    t = s.pop()
                    if t == '(':  # 左括号入栈前优先级最高，而入栈后优先级最低！
                        s.push(t)
                        break
                    if pro[x] <= pro[t]:
                        out.append(t)
                    else:
                        s.push(t)
                        break
                s.push(x)
            else:  # ④运算数 -- 直接输出
                out.append(x)

        while not s.is_null():
            out.append(s.pop())

    return out


def get_where_list(sql_parsed, location):
    """
    得到用户修改的where条件，将其转化为list并返回
    :return: list
    """
    where = sql_parsed[0].tokens[location].value.replace("\n", ''). \
        replace('WHERE', '').replace("'", '').lstrip(' ').rstrip(' ')
    where_list = where.split(' ')

    index = 0
    while index < len(where_list):
        if re.search('\(', where_list[index], flags=0) is not None:
            var = where_list[index].replace('(', '( ').split(" ")
            length = len(var)
            for item in reversed(var):
                where_list.insert(index, item)
            del where_list[index + length]
        elif re.search('\)', where_list[index], flags=0) is not None:
            var = where_list[index].replace(')', ' ) ').split(" ")
            length = len(var)
            for item in reversed(var):
                if item is not '':
                    where_list.insert(index, item)
                else:
                    length -= 1
            del where_list[index + length]
        index += 1
    while '' in where_list:
        where_list.remove('')
    return where_list


def get_result_sql(worksheet, row, where_list_revere, json_dict):
    """
    根据后缀表达式求值
    :param row: 当前行
    :param worksheet: xls文件的sheet
     :param json_dict: json中读取的字典
    :param where_list_revere: where后缀表达式
    :return: bool true / false
    """
    where_list_revere = copy.deepcopy(where_list_revere)
    judge = {
        '=': lambda x, y: x == y,
        '<>': lambda x, y: x != y,
        '>': lambda x, y: x < y,
        '<': lambda x, y: x > y,
        '>=': lambda x, y: x <= y,
        '<=': lambda x, y: x >= y,
        'AND': lambda x, y: x and y,
        'OR': lambda x, y: x or y
    }

    s = Stack()
    select_where_set = set()
    for x in where_list_revere:
        # 确定符号映射
        symbol = {'=', '<>', '>', '<', '>=', '<=', 'AND', 'OR'}
        if x in symbol:
            # 根据列属性确定参数的值
            val1, val2 = s.pop(), s.pop()
            if val1 in json_dict.keys():
                select_where_set.add(val1)
                tag = get_type(json_dict[val1])
                val1 = worksheet.cell(row, json_dict[val1][-1]).value
                if tag == 0:
                    val1 = str(val1)
                    val2 = str(val2)
                elif tag == 1:
                    val1 = int(val1)
                    val2 = int(val2)
                else:
                    val1 = float(val1)
                    val2 = float(val2)
            if val2 in json_dict.keys():
                select_where_set.add(val2)
                tag = get_type(json_dict[val2])
                val2 = worksheet.cell(row, int(json_dict[val2][-1])).value
                if tag == 0:
                    val1 = str(val1)
                    val2 = str(val2)
                elif tag == 1:
                    val1 = int(val1)
                    val2 = int(val2)
                else:
                    val1 = float(val1)
                    val2 = float(val2)
            r = judge[x](val1, val2)
            s.push(r)
        else:
            s.push(x)
    s.pop()
    flag = s.pop()
    where_list_revere.clear()
    return flag, select_where_set


