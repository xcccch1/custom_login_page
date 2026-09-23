# -*- coding: utf-8 -*-
{
    'name': 'Login Page Settings',
    'author': 'xcccch1',
    'version': '19.0.1.3.1',
    'license': 'LGPL-3',
    'category': 'Operations/Custom Frontend',
    'summary': 'Manage login page settings, including public database names',
    'depends': [
        'base_setup',
        'web',
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/webclient_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
