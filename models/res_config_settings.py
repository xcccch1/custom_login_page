# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    database_display_name = fields.Char(
        string='Database Display Name',
        config_parameter='custom_database_display_name.display_name',
        groups='base.group_system',
        help=(
            'Public name shown on login and database selection pages. Leave '
            'empty to show the technical database name.'
        ),
    )
