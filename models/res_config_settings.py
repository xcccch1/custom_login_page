# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import str2bool


SHOW_LOGIN_PAGE_FOOTER_PARAM = 'custom_login_page.show_login_page_footer'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_login_page_footer = fields.Boolean(
        string='Show Login Page Footer',
        default=True, groups='base.group_system',
        help=('Show or hide the database management link and Odoo branding at '
              'the bottom of the login page.'))
    database_display_name = fields.Char(
        string='Database Display Name',
        config_parameter='custom_login_page.display_name',
        groups='base.group_system',
        help=(
            'Public name shown on login and database selection pages. Leave '
            'empty to show the technical database name.'
        ),
    )

    @api.model
    def get_values(self):
        values = super().get_values()
        parameter = self.env['ir.config_parameter'].sudo().get_param(
            SHOW_LOGIN_PAGE_FOOTER_PARAM,
            default='True',
        )
        values['show_login_page_footer'] = str2bool(parameter, default=True)
        return values

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            SHOW_LOGIN_PAGE_FOOTER_PARAM,
            'True' if self.show_login_page_footer else 'False',
        )
