# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers import main as web_main


DATABASE_DISPLAY_NAME_MAP = {
    'odoo15': '中文odoo15',
    'odoo15_test': '中文odoo15_test',
}

DATABASE_TEMPLATE_TARGET = '<t t-out="db" />'
DATABASE_TEMPLATE_REPLACEMENT = '<t t-out="database_display_names.get(db, db)" />'


def get_database_display_name(db_name):
    return DATABASE_DISPLAY_NAME_MAP.get(db_name, db_name)


def get_database_display_names(databases):
    return {
        db_name: get_database_display_name(db_name)
        for db_name in databases or []
    }


try:
    from odoo.addons.odoo_user_login_security.controller.main import Home as LoginSecurityHome
except ImportError:
    LoginSecurityHome = None

BaseHome = LoginSecurityHome or web_main.Home


class Home(BaseHome):

    def _should_use_login_security(self):
        if LoginSecurityHome is None:
            return False
        if not (request.db or request.session.db):
            return False
        try:
            return (
                'session.session' in request.env.registry.models
                and 'last_password_reset' in request.env['res.partner']._fields
            )
        except Exception:
            return False

    @http.route()
    def web_login(self, redirect=None, **kw):
        if self._should_use_login_security():
            response = super(Home, self).web_login(redirect=redirect, **kw)
        else:
            response = web_main.Home.web_login(self, redirect=redirect, **kw)
        if getattr(response, 'is_qweb', False) and response.template == 'web.login':
            current_db = request.params.get('db') or request.db or request.session.db
            response.qcontext['database_display_name'] = get_database_display_name(current_db)
            response.qcontext['database_display_names'] = get_database_display_names(
                response.qcontext.get('databases')
            )
        return response


class Database(web_main.Database):

    def _render_template(self, **d):
        d.setdefault('manage', True)
        d['insecure'] = web_main.odoo.tools.config.verify_admin_password('admin')
        d['list_db'] = web_main.odoo.tools.config['list_db']
        d['langs'] = web_main.odoo.service.db.exp_list_lang()
        d['countries'] = web_main.odoo.service.db.exp_list_countries()
        d['pattern'] = web_main.DBNAME_PATTERN
        d['databases'] = []
        d['incompatible_databases'] = []
        try:
            d['databases'] = http.db_list()
            d['incompatible_databases'] = web_main.odoo.service.db.list_db_incompatible(d['databases'])
        except web_main.odoo.exceptions.AccessDenied:
            monodb = web_main.db_monodb()
            if monodb:
                d['databases'] = [monodb]

        d['database_display_names'] = get_database_display_names(d['databases'])

        templates = {}

        with web_main.file_open("web/static/src/public/database_manager.qweb.html", "r") as fd:
            template = fd.read()
        template = template.replace(DATABASE_TEMPLATE_TARGET, DATABASE_TEMPLATE_REPLACEMENT)

        with web_main.file_open("web/static/src/public/database_manager.master_input.qweb.html", "r") as fd:
            templates['master_input'] = fd.read()
        with web_main.file_open("web/static/src/public/database_manager.create_form.qweb.html", "r") as fd:
            templates['create_form'] = fd.read()

        def load(template_name, options):
            return (web_main.html.fragment_fromstring(templates[template_name]), template_name)

        return web_main.qweb_render(web_main.html.document_fromstring(template), d, load=load)

    @http.route()
    def selector(self, **kw):
        request._cr = None
        return self._render_template(manage=False)

    @http.route()
    def manager(self, **kw):
        request._cr = None
        return self._render_template()
