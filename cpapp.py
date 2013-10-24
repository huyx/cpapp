# -*- coding: utf-8 -*-
import argparse
import fnmatch
import os
import re
import sys
import time

_prog = 'cpapp'
_version = '0.1'

def normpath(path):
    '''去掉前面和后面的路径分隔符，如 \myproject\ ==> myproject
    '''
    return path.strip(os.path.sep)


class Template(object):
    def __init__(self, begin, end):
        # 格式 {{name=default # comment}}
        pattern = ''.join((
            re.escape(begin),
            '(?P<name>\w*)',
            '(?:=(?P<default>\w*))?',
            '(?:\s*--\s*(?P<comment>.*?))?',
            re.escape(end)
        ))
        self.pattern = re.compile(pattern)

    def substitute(self, string, context):
        def repl(m):
            default = m.group('default')
            if default is not None:
                return context.get(m.group('name'), default)
            return context[m.group('name')]
        return self.pattern.sub(repl, string)


class Configure(object):
    def __init__(self, source, inspect=False):
        if inspect:
            self.ignores = []
        else:
            self.ignores = ['_cpapp.conf']

        filename = os.path.join(source, '_cpapp.conf')
        if not os.path.exists(filename):
            return

        for line in open(filename):
            # 去掉注释
            if '#' in line:
                line = line.partition('#')[0]

            line = line.strip()
            if not ':' in line:
                continue
            cmd, _, value = line.partition(':')
            cmd = cmd.strip()
            value = value.strip()

            if cmd == 'ignore':
                self.ignores.append(value)
            elif cmd == 'variable':
                pass
            else:
                print u'ERR: 未知命令 %r' % line

    def ignore(self, name):
        for pat in self.ignores:
            if fnmatch.fnmatch(name, pat):
                return True
        return False


def to_unicode(s, coding=None):
    if coding:
        return s.decode(coding)
    try:
        return s.decode('utf-8')
    except:
        pass
    try:
        return s.decode('gbk')
    except:
        pass


class Variable(object):
    default = None
    comment = None

    def __init__(self, name):
        self.name = name

    def __str__(self):
        if self.default is not None:
            default = '(%s)' % self.default
        else:
            default = ''
        item = '%s%s' % (self.name, default)
        return '%-20s%s' % (item, self.comment or '')


class Recreater(object):
    def pretty_parser(self, parser):
        '''更好地显示帮助信息
        '''
        parser._optionals.title = u'可选参数'
        parser._positionals.title = u'位置参数'
        if not parser.add_help:
            parser.add_argument('-h', '--help', action='help', help=u'显示帮助信息')
        return parser

    def parse_args(self):
        # 通用参数
        parser = self.pretty_parser(argparse.ArgumentParser(
            description=u'从模板创建新项目',
            add_help=False,
        ))

        # 指定分析用的标签
        parser.add_argument('-b', '--begin', default='{{', help=u'起始标签(缺省为 {{)')
        parser.add_argument('-e', '--end', default='}}', help=u'结束标签(缺省为 }})')

        # 创建子命令
        subparsers = parser.add_subparsers(title=u'子命令', dest='subcommand')

        # inspect 命令
        parser_inspect = self.pretty_parser(subparsers.add_parser(
            'inspect',
            add_help=False,
        ))
        parser_inspect.add_argument('source', help=u'源目录')

        # create 命令
        parser_create = self.pretty_parser(subparsers.add_parser(
            'create',
            add_help=False,
        ))
        parser_create.add_argument('source', help=u'源目录')
        parser_create.add_argument('destination', help=u'目标目录')
        parser_create.add_argument('-p', '--params', dest='params', metavar='P', help=u'参数, 格式为: name=value,name=value')
        parser_create.add_argument('-t', '--test', dest='test', default=False, action='store_true', help=u'只输出信息，不创建实际目录和文件')
        parser_create.add_argument('-f', '--force', dest='force', default=False, action='store_true', help=u'不检查目标目录非空')

        self.args = parser.parse_args()

        self.post_parse_args()

    def post_parse_args(self):
        self.template = Template(self.args.begin, self.args.end)

    def _inspect(self, string, variables):
        for m in self.template.pattern.finditer(string):
            name = m.group('name')
            v = variables.setdefault(name, Variable(name))
            v.default = v.default or m.group('default')
            v.comment = v.comment or to_unicode(m.group('comment'))

    def inspect(self, args):
        source = normpath(args.source)
        config = Configure(source, True)

        variables = {}

        for dirpath, dirnames, filenames in os.walk(source):
            # 标准化目录名
            dirpath = normpath(dirpath)
            if not dirpath.startswith(source):
                print u'错误: %r 应该以 %r 开头' % (dirpath, source)
                sys.exit(30)
            relpath = normpath(dirpath[len(source):])
            for dirname in dirnames:
                dirname = os.path.join(relpath, dirname)
                if config.ignore(dirname):
                    continue
                self._inspect(dirname, variables)
            for filename in filenames:
                if config.ignore(os.path.join(relpath, filename)):
                    continue
                filename = os.path.join(dirpath, filename)
                self._inspect(filename, variables)
                self._inspect(open(filename).read(), variables)
        for _name, v in sorted(variables.iteritems()):
            print v

    def substitute(self, string, context):
        try:
            return self.template.substitute(string, context)
        except KeyError as e:
            name = e.args[0]
            print u"参数未指定: %r, 试试 inspect 命令。" % name
            sys.exit(5)

    def create(self, args):
        '''从模板创建新项目
        '''
        source = normpath(args.source)
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

        params = args.params or ''

        for param in params.split(','):
            try:
                name, _, value = param.partition('=')
            except:
                print u'参数格式错误（name=value,name=value）: %r' % param
                sys.exit(20)
            context[name] = value

        # 拷贝目录和文件
        for dirpath, dirnames, filenames in list(os.walk(source)):
            # 标准化目录名
            dirpath = normpath(dirpath)
            if not dirpath.startswith(source):
                print u'错误: %r 应该以 %r 开头' % (dirpath, source)
                sys.exit(30)
            relpath = normpath(dirpath[len(source):])

            # 创建目录
            for dirname in dirnames:
                dest_dirname = os.path.join(destination, relpath, dirname)
                dest_dirname = self.substitute(dest_dirname, context)
                print u'创建目录: ', dest_dirname
                if not args.test:
                    if not os.path.exists(dest_dirname):
                        os.mkdir(dest_dirname)

            # 创建文件
            for filename in filenames:
                tmpl_filename = os.path.join(dirpath, filename)
                dest_filename = os.path.join(destination, relpath, filename)
                dest_filename = self.substitute(dest_filename, context)
                print u'创建文件: ', dest_filename
                if not args.test:
                    content = open(tmpl_filename, 'rb').read()
                    content = self.substitute(content, context)
                    open(dest_filename, 'wb').write(content)

    def main(self):
        self.parse_args()

        args = self.args
        if args.subcommand == 'inspect':
            self.inspect(args)
        elif args.subcommand == 'create':
            self.create(args)
        else:
            raise Exception(u'未知子命令: %r' % args.subcommand)

if __name__ == '__main__':
    import sys
    reload(sys)
    if sys.platform.startswith('win'):
        sys.setdefaultencoding('gbk')
    else:
        sys.setdefaultencoding('utf-8')
    Recreater().main()
