# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

from odoo.addons.web.controllers import home as web_home
from odoo.addons.web.controllers import database as web_database


DATABASE_TEMPLATE_TARGET = '<t t-out="db" />'
DATABASE_TEMPLATE_REPLACEMENT = '<t t-out="database_display_names.get(db, db)" />'


DATABASE_DISPLAY_NAME_MAP = {
    'odoo18': '中文odoo18',
    'odoo18_test': '中文odoo18_test',
}

def get_database_display_name(db_name):
    return DATABASE_DISPLAY_NAME_MAP.get(db_name, db_name)


def get_database_display_names(databases):
    return {
        db: get_database_display_name(db)
        for db in (databases or [])
    }


class Home(web_home.Home):

    @http.route()
    def web_login(self, redirect=None, **kw):
        response = super().web_login(
            redirect=redirect,
            **kw
        )

        if getattr(response, 'is_qweb', False):
            current_db = (
                request.params.get('db')
                or request.db
                or request.session.db
            )
            databases = response.qcontext.get('databases') or []

            response.qcontext['database_name'] = current_db
            response.qcontext['database_display_name'] = (
                get_database_display_name(current_db)
            )
            response.qcontext['database_display_names'] = (
                get_database_display_names(databases)
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

    @http.route()
    def selector(self, **kw):
        return self._render_template(manage=False)

    @http.route()
    def manager(self, **kw):
        return self._render_template()
