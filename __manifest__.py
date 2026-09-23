# -*- coding: utf-8 -*-
{
    'name': 'Custom Database Display Name',
    'version': '15.0.0.1',
    'license': 'LGPL-3',
    'category': 'Operations/Custom Frontend',
    'summary': 'Show mapped display names for databases on login screens',
    'depends': [
        'web',
    ],
    'data': [
        'views/webclient_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
