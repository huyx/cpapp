从模板创建新项目
================

模板语法:

- 文件内容: {{varname}}
- 文件名和目录名: 同上

可定制模板， 如定制模板为 `${varname}`，可以使用下面的语法:

    recreate.py -b '${' -e '}' ...

支持的命令:

- inspect: 可以提取模板文件中的变量
- create: 根据模板目录创建新项目

inspect
-------

用法:

	recreate.py inspect [-h] source

参数:

	source      源目录
	-h, --help  显示帮助信息

create
------

用法:

	recreate.py create [-h] [-p P] [-t] [-f] source destination

位置参数:

    source            源目录
    destination       目标目录

可选参数:

    -h, --help        显示帮助信息
    -p P, --params P  参数, 格式为: name=value
    -t, --test        只输出信息，不创建实际目录和文件
    -f, --force       不检查目标目录非空

内置参数
--------

内置参数不需要另外指定，但也可以通过 `-p` 设置新的参数值:

    project_name	项目名称, 缺省为目录名
    create_date		创建日期
	creator			创建者，缺省为程序名

示例
----

提取变量:

	recreate.py inspect templates\python

生成新项目:

	recreate.py create templates\python b -f -p author=huyx -p "hello=World"