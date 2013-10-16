# -*- coding: utf-8 -*-
import argparse
import os
import string
import sys
import time

_prog = 'recreate'
_version = '0.1'

def pretty_parser(parser):
    '''更好地显示帮助信息
    '''
    parser._optionals.title = u'可选参数'
    parser._positionals.title = u'位置参数'
    if not parser.add_help:
        parser.add_argument('-h', '--help', action='help', help=u'显示帮助信息')
    return parser

def parse_args():
    # 通用参数
    parser = pretty_parser(argparse.ArgumentParser(
        description=u'从模板创建新项目',
        add_help=False,
    ))

    # 创建子命令
    subparsers = parser.add_subparsers(title=u'子命令', dest='subcommand')

    # inspect 命令
    parser_inspect = pretty_parser(subparsers.add_parser(
        'inspect',
        add_help=False,
    ))
    parser_inspect.add_argument('template', help=u'源目录')

    # create 命令
    parser_create = pretty_parser(subparsers.add_parser(
        'create',
        add_help=False,
    ))
    parser_create.add_argument('template', help=u'源目录')
    parser_create.add_argument('destination', help=u'目标目录')
    parser_create.add_argument('--param', '-p', dest='params', metavar='PARAM', action='append', help=u'参数, 格式为: name=value')
    parser_create.add_argument('--test', '-t', dest='test', default=False, action='store_true', help=u'只输出信息，不创建实际目录和文件')
    parser_create.add_argument('--force', '-f', dest='force', default=False, action='store_true', help=u'不检查目标目录非空')

    return parser.parse_args()

def _inspect(s, context):
    tmpl = string.Template(s)
    while True:
        try:
            tmpl.substitute(context)
        except KeyError as e:
            name = e.args[0]
            context[name] = '-'
        else:
            break

def inspect(args):
    context = {}
    for dirpath, dirnames, filenames in os.walk(args.template):
        for dirname in dirnames:
            _inspect(dirname, context)
        for filename in filenames:
            _inspect(filename, context)
            _inspect(open(os.path.join(dirpath, filename)).read(), context)
    for name in sorted(context):
        print name

def normpath(path):
    '''去掉前面和后面的路径分隔符，如 \myproject\ ==> myproject
    '''
    return path.strip(os.path.sep)

def substitute(s, context):
    try:
        return string.Template(s).substitute(context)
    except KeyError as e:
        name = e.args[0]
        print u"参数未指定: %r, 试试 inspect 命令。" % name
        sys.exit(5)

def create(args):
    '''从模板创建新项目
    '''
    template = normpath(args.template)
    destination = normpath(args.destination)

    # 检查并创建目标目录
    if os.path.exists(destination):
        if not args.force:
            print u'目标目录已经存在: %r' % destination
            sys.exit(10)
    elif not args.test:
        os.makedirs(destination)

    # 构造 context
    project_name = os.path.split(destination)[1]
    context = {
        'project_name': project_name,
        'create_date': time.strftime('%Y-%m-%d'),
        'creator': '%s-%s' % (_prog, _version),
    }

    if not args.params:
        args.params = []

    for param in args.params:
        try:
            name, _, value = param.partition('=')
        except:
            print u'参数格式错误（name:value）: %r' % param
            sys.exit(20)
        context[name] = value

    # 拷贝目录和文件
    for dirpath, dirnames, filenames in list(os.walk(template)):
        # 标准化目录名
        dirpath = normpath(dirpath)
        if not dirpath.startswith(template):
            print u'错误: %r 应该以 %r 开头' % (dirpath, template)
            sys.exit(30)
        relpath = normpath(dirpath[len(template):])

        # 创建目录
        for dirname in dirnames:
            dest_dirname = os.path.join(destination, relpath, dirname)
            dest_dirname = substitute(dest_dirname, context)
            print u'创建目录: ', dest_dirname
            if not args.test:
                os.mkdir(dest_dirname)

        # 创建文件
        for filename in filenames:
            tmpl_filename = os.path.join(dirpath, filename)
            dest_filename = os.path.join(destination, relpath, filename)
            dest_filename = substitute(dest_filename, context)
            print u'创建文件: ', tmpl_filename, '->', dest_filename
            if not args.test:
                content = open(tmpl_filename, 'rb').read()
                content = substitute(content, context)
                open(dest_filename, 'wb').write(content)

if __name__ == '__main__':
    args = parse_args()
    if args.subcommand == 'inspect':
        inspect(args)
    elif args.subcommand == 'create':
        create(args)
    else:
        print args
