# DBMS_Python
利用python实现DBMS简易功能

1. ### 系统整体设计

   1. 用户登录系统流程图

      <img src="D:\PycharmProjects_\DatabaseManagementSystem\README.assets\user_login.png" alt="user_login" style="zoom: 67%;" />

   2. SQL主系统执行流程图

      <img src="D:\PycharmProjects_\DatabaseManagementSystem\README.assets\sql_system.png" alt="sql_system" style="zoom: 67%;" />

   3. 系统整合：

      设置User类，记录当前服务对象所有服务信息，包括，用户名、密码、活动路径、活动库、活动表等，保证DBMS全局信息一致。设置输入判断函数，监听、记录用户输入，根据不同的输入语句选择相应的代码：

2. SQL系统分模块设计

   1. 数据、元数据

      1. 选择.xls文件作为数据库数据存储文件，选择.json文件存储约束条件、视图、索引信息
      2. 调用xlwt、xlrd库进行.xls文件读写，调用json库进行.json文件读写，实现数据库中元数据以及约束条件、索引、视图等信息的存储。
      3. 逻辑数据以字典（哈希表）为逻辑结构存储在内存中。

   2. 建表

      1. 对`CREATE DATABASE 库名;` 语句进行解析，根据用户输入建立与之对应的数据文件

      2. 对`REATE TABLE 表名(列名称 数据类型, ...);`语句进行解析，根据用户输入建立与之对应的数据文件

      3. 建表流程图

         <img src="D:\PycharmProjects_\DatabaseManagementSystem\README.assets\cerate_table.png" alt="cerate_table" style="zoom:67%;" />

   3. 创建索引

      1. 解析、执行`CREATE index *;`语句，建立索引

      2. 建索引流程图

         ![creste_view](D:\PycharmProjects_\DatabaseManagementSystem\README.assets\creste_view.png)

   4. 创建试图

      1. 解析、执行`CREATE view *;`语句，建立试图

      2. 建试图流程图

         <img src="D:\PycharmProjects_\DatabaseManagementSystem\README.assets\create_view.png" alt="create_view" style="zoom:67%;" />

   5. 查询功能

      1. 对用户输入进行语义分析，如果为SELECT语句，则转入Select()类进行文件查询处理

      2. 查询流程图

         ![select](D:\PycharmProjects_\DatabaseManagementSystem\README.assets\select.png)

   6. 更新操作

      1. 修改操作

         <img src="D:\PycharmProjects_\DatabaseManagementSystem\README.assets\update.png" alt="update" style="zoom: 80%;" />

      2. 插入操作

         <img src="D:\PycharmProjects_\DatabaseManagementSystem\README.assets\insert.png" alt="insert" style="zoom:80%;" />

      3. 删除操作

         <img src="D:\PycharmProjects_\DatabaseManagementSystem\README.assets\delete.png" alt="delete" style="zoom:80%;" />

      4. 索引更新

         插入时，每插入一个数据，检查该表对应.json文件中的索引，对该行对应的所有索引进行更新。因为默认对主键建立索引，故插入时，对主键建立相应的{主键: 行号}映射。