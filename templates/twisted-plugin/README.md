{{project_name}}
========

{{project_name}}

服务
----

- `TCP:2013`: Echo 服务
- `UDP:2013`: Echo 服务
- `TCP:12013`: SSH 调试服务端口

文件
----

- `service`: 启动/停止脚本
- `settings/default.py`: 缺省配置文件
- `settings/{{project_name}}.py`: 配置文件
- `etc/passwd`: SSH 调试服务密码文件
- `{{project_name}}/share.py`: 保存共享变量的模块 

Monit 配置示例
--------------

	check process {{project_name}}
	    with pidfile "/var/run/{{project_name}}.pid"
	    start program = "<path_to_{{project_name}}>/service start"
	    stop program = "<path_to_{{project_name}}>/service stop"
	    if cpu > 20% for 2 cycles then restart
	    if mem > 32 MB for 2 cycles then restart
	    group {{project_name}}
