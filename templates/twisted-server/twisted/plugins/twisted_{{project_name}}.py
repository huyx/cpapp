# -*- coding: utf-8 -*-
from twisted.application.service import ServiceMaker

serviceMaker = ServiceMaker(
    '{{project_name}}',
    '{{project_name}}.tap',
    'description of {{project_name}}',
    '{{tapname=}}' or '{{project_name}}'
)
