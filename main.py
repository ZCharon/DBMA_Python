import sqlparse

from data_manipulation.create_table import Create
from data_manipulation.delete_data import Delete
from data_manipulation.help_user import Help
from data_manipulation.insert_data import Insert
from data_manipulation.select_data import Select
from data_manipulation.update_data import Update
from data_manipulation.use_database import use_database
from login_register import login_and_register


class User:
    """
    User类，记录当前登录用户
    """
    username = ""  # 当前用户名
    password = ""  # 当前用户登录密码
    base_data_path = r"data/"  # 当前用户的数据库基路径
    login_path = r"login_data/login.xls"  # 当前用户的注册信息
    data_path = r"data/"  # 当前用户的数据库路径
    current_database = ''  # 当前活动的数据库
    current_table = ''  # 当前活动的表


def get_input():
    """
    得到用户输入，只有最后为 ; 时才结束读取
    :return: str -> 用户输入的字符串
    """
    strs = ""
    str_ = input(">>>")
    if len(str_) == 0:
        strs += "&"  # 填充字符串
    strs += str_
    strs += " "
    while "; " != strs[-2:]:
        str_ = input("->")
        str_ += " "
        strs += str_

    if strs[0] == "&":
        strs = strs.replace('&', '')
    return strs


def string_parse(user):
    """
    根据用户输入，运用sqlparse进行代码格式化，调用相关的数据库相关函数
    :return:
    """
    # 得到用户输入字符串
    str_ = get_input().replace(";", '')
    if str_ == '':
        return
    # 将字符串进行格式化，关键字大写
    sql = sqlparse.format(str_, reindent=True, keyword_case='upper')
    # 对多条语句进行分割
    sql_strs = sql.split(str_)
    # 解析sql语句
    sql_parsed = sqlparse.parse(sql_strs[0])
    # 获取tag值，根据tag值判断要调用的函数
    try:
        tag = sql_parsed[0].tokens[0].value.upper()
    except IndexError:
        return

    if tag == 'SELECT':  # 查找
        select = Select(sql_parsed, user)
        select.select()
        select.print_table()

    elif tag == 'CREATE':  # 创建类
        create = Create(sql_parsed, user)
        create.create()

    elif tag == 'UPDATE':  # 更新
        update = Update(sql_parsed, user)
        update.update()

    elif tag == 'DELETE':  # 删除
        delete = Delete(sql_parsed, user)
        delete.delete()

    elif tag == 'INSERT':  # 插入
        insert = Insert(sql, user)
        insert.insert()

    elif tag == 'USE':  # USE
        use_database(sql_parsed, user)

    elif tag.upper() == "HELP":  # 帮助信息
        help_user = Help(str_, user)
        help_user.help_user()

    else:
        print("语法错误，请查证后重新输入！")


if __name__ == '__main__':
    user = User()  # 创建当前对象实例
    login_and_register(user)  # 进行用户登录验证
    while True:
        # 用户登录验证成功，进入DBMS主系统
        string_parse(user)
