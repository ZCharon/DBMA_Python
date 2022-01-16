# -*- codeing = utf-8 -*-
# @Time : 2020/11/27 19:51
# @Author : guanghao zhou
# @File : login_register.py
# Software : PyCharm
"""
登录验证
"""
import xlwt
import xlrd
import os
import xlutils.copy


def get_input():
    """
    获取用户登录输入
    :return: string -> username, password
    """
    print("--请输入用户名：")
    username = input("---")
    print("--请输入密码：")
    password = input("---")
    return username, password


def add_user(user):
    """
    在用户信息中添加该用户的信息，并为其创建文件夹
    :return:None
    """
    if not os.path.exists(user.login_path):
        book = xlwt.Workbook(encoding='utf-8')  # 新建工作簿
        _ = book.add_sheet('userinfo')  # 新建userinfo表
        book.save(user.login_path)  # 保存文件
    userinfo = xlrd.open_workbook(user.login_path, formatting_info=True)
    userinfo_table = userinfo.sheets()[0]
    users = set()
    for row in range(userinfo_table.nrows):
        users.add(userinfo_table.cell(row, 0).value)
    user_copy = xlutils.copy.copy(userinfo)
    copy_sheet = user_copy.get_sheet(0)

    nrows = userinfo_table.nrows
    if user.username in users:
        print('该用户已存在，请查证后输入！')
        return False
    copy_sheet.write(nrows, 0, user.username)
    copy_sheet.write(nrows, 1, user.password)
    user_copy.save(user.login_path)
    if not os.path.exists(user.data_path):
        os.makedirs(user.data_path)
    return True


def login_and_register(user):
    """
    输出欢迎语句
    进行用户登录验证
    :return: None
    """
    print("-----------------------------------------------------------------")
    print("欢迎进入DBMS：")
    print("-----------------------------------------------------------------")
    print("登录 -- > login")
    print("注册 --> register")
    flag = True
    while flag:
        operation = input("-->")
        if operation == "login":
            username, password = get_input()
            if login_check(username, password, user.login_path):
                print("登录成功！！！")
                user.data_path = user.base_data_path + username + "/"
                break
            else:
                print("登录失败，请重新输入：")
        elif operation == "register":
            username, password = get_input()
            user.password = password
            user.username = username
            user.data_path = user.base_data_path + username + "/"
            if add_user(user):
                break
        else:
            print("输入有误请重新输入：")
            print("登录 -- > login")
            print("注册 --> register")


def login_check(username, password, login_path):
    """
    登录检验，判断用户名是否输入正确以及该用户是否为新用户
    :param login_path:
    :param username: string -> 用户名
    :param password: string -> 密码
    :return: bool -> 登录验证是否成功
    """
    flag = False
    if os.path.exists(login_path):
        workbook = xlrd.open_workbook(login_path)
        table = workbook.sheets()[0]
        rows = table.nrows
        for row in range(rows):
            if username == table.cell(row, 0).value and password == table.cell(row, 1).value:
                flag = True
                break
    return flag




