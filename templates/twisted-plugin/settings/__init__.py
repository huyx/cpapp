# -*- coding: utf-8 -*-
from .default import *

try:
    from .{{project_name}} import *
except ImportError:
    import os
    filename = os.path.normpath('settings/{{project_name}}.py')
    print u'提示: 可以通过修改 %s 进行配置' % filename
