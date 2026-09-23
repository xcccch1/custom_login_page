# -*- coding: utf-8 -*-

import logging

from odoo import http, sql_db
from odoo.http import request
from odoo.tools import str2bool

from odoo.addons.web.controllers import home as web_home
from odoo.addons.web.controllers import database as web_database


DATABASE_TEMPLATE_TARGET = '<t t-out="db" />'
DATABASE_TEMPLATE_REPLACEMENT = '<t t-out="database_display_names.get(db, db)" />'
DATABASE_DISPLAY_NAME_PARAM = 'custom_login_page.display_name'
SHOW_LOGIN_PAGE_FOOTER_PARAM = 'custom_login_page.show_login_page_footer'

_logger = logging.getLogger(__name__)


def get_database_display_name(db_name):
    """Return the configured public label for ``db_name``.

    Database selector requests do not have an Odoo environment because no
    database has been selected yet, so read the setting with an isolated SQL
    cursor. The database names passed here originate from ``http.db_list()``
    or ``request.db``, never directly from an unvalidated request parameter.
    """
    if not db_name:
        return db_name

    try:
        with sql_db.db_connect(db_name).cursor() as cr:
            cr.execute(
                """
                SELECT value
                  FROM ir_config_parameter
                 WHERE key = %s
                 LIMIT 1
                """,
                [DATABASE_DISPLAY_NAME_PARAM],
            )
            row = cr.fetchone()
    except Exception:
        _logger.warning(
            "Unable to read the database display name for %r; using the technical name",
            db_name,
            exc_info=True,
        )
        return db_name

    display_name = row[0].strip() if row and row[0] else ''
    return display_name or db_name


def get_database_display_names(databases):
    return {
        db: get_database_display_name(db)
        for db in (databases or [])
    }


def is_login_page_footer_visible(env):
    show_footer = env['ir.config_parameter'].sudo().get_param(
        SHOW_LOGIN_PAGE_FOOTER_PARAM,
        default='True',
    )
    return str2bool(show_footer, default=True)


class Home(web_home.Home):

    @http.route()
    def web_login(self, redirect=None, **kw):
        response = super().web_login(
            redirect=redirect,
            **kw
        )

        if getattr(response, 'is_qweb', False):
            current_db = (request.db or request.session.db)

            response.qcontext['database_name'] = current_db
            response.qcontext['database_display_name'] = (get_database_display_name(current_db))
            response.qcontext['disable_footer'] = (
                response.qcontext.get('disable_footer', False)
                or not is_login_page_footer_visible(request.env)
            )

        return response


class Database(web_database.Database):

    def _render_template(self, **d):
        d.setdefault('manage', True)
        d['insecure'] = web_database.odoo.tools.config.verify_admin_password('admin')
        d['list_db'] = web_database.odoo.tools.config['list_db']
        d['langs'] = web_database.odoo.service.db.exp_list_lang()
        d['countries'] = web_database.odoo.service.db.exp_list_countries()
        d['pattern'] = web_database.DBNAME_PATTERN
        try:
            d['databases'] = http.db_list()
            d['incompatible_databases'] = (
                web_database.odoo.service.db.list_db_incompatible(d['databases'])
            )
        except web_database.odoo.exceptions.AccessDenied:
            d['databases'] = [request.db] if request.db else []

        d['database_display_names'] = get_database_display_names(d['databases'])

        templates = {}

        with web_database.file_open("web/static/src/public/database_manager.qweb.html", "r") as fd:
            templates['database_manager'] = fd.read().replace(
                DATABASE_TEMPLATE_TARGET,
                DATABASE_TEMPLATE_REPLACEMENT,
            )
        with web_database.file_open("web/static/src/public/database_manager.master_input.qweb.html", "r") as fd:
            templates['master_input'] = fd.read()
        with web_database.file_open("web/static/src/public/database_manager.create_form.qweb.html", "r") as fd:
            templates['create_form'] = fd.read()

        def load(template_name):
            fromstring = (
                web_database.html.document_fromstring
                if template_name == 'database_manager'
                else web_database.html.fragment_fromstring
            )
            return (fromstring(templates[template_name]), template_name)

        return web_database.qweb_render('database_manager', d, load)
