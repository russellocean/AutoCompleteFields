# -*- coding: utf-8 -*-
from trac.admin.api import IAdminPanelProvider
from trac.core import Component, implements
from trac.env import IEnvironmentSetupParticipant
from trac.util.presentation import to_json
from trac.util.translation import _
from trac.web.api import IRequestFilter, IRequestHandler
from trac.web.chrome import (
    Chrome,
    ITemplateProvider,
    add_notice,
    add_script,
    add_script_data,
    add_stylesheet,
    add_warning,
)

FIELDS_SECTION_NAME = "autocompletefields"
SCRIPT_FIELD_NAME = "autocomplete_fields"


class AutoCompleteFields(Component):
    implements(
        IRequestFilter,
        IRequestHandler,
        ITemplateProvider,
        IAdminPanelProvider,
        IEnvironmentSetupParticipant,
    )

    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info.rstrip("/") == "/autocompletefields"

    def process_request(self, req):
        field_type = req.args.get("field_type", "")
        items = []

        if field_type:
            items = self._get_items_for_field(field_type)

        content = to_json(items)
        self.log.debug("Content: {}".format(content))
        if isinstance(content, unicode):
            content = content.encode("utf-8")
        req.send(content, "application/json")

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename

        return [("autocompletefields", resource_filename(__name__, "htdocs"))]

    def get_templates_dirs(self):
        from pkg_resources import resource_filename

        return [resource_filename(__name__, "templates")]

    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, data, content_type):
        if template in ("ticket.html", "admin_perms.html", "query.html"):
            Chrome(self.env).add_jquery_ui(req)
            add_stylesheet(req, "autocompletefields/css/autocompletefields.css")
            add_script(req, "autocompletefields/js/autocompletefields.js")
            script_data = {
                "template": template,
                "multi_fields": {
                    "keywords": self._get_items_for_field("Keywords"),
                    "customers": self._get_items_for_field("Customer"),
                    "suppliers": self._get_items_for_field("Supplier"),
                    "sizes": self._get_items_for_field("Sizes"),
                },
                "url": req.href.autocompletefields(),  # Modify this line
            }
            add_script_data(req, {"autocompletefields": script_data})
        return template, data, content_type

    # Private methods
    def _get_items_for_field(self, field_type):
        # This method should return items from the database for the given field type.
        items = []
        table_name = None
        column_name = None

        self.log.debug("Items for field {}: {}".format(field_type, items))

        if field_type == "Keywords":
            table_name = "keywords"
            column_name = "keyword"
        elif field_type == "Supplier":
            table_name = "suppliers"
            column_name = "supplier_name"
        elif field_type == "Customer":
            table_name = "customers"
            column_name = "customer_name"
        elif field_type == "Sizes":
            table_name = "sizes"
            column_name = "size_name"

        if table_name and column_name:
            with self.env.db_query as db:
                cursor = db.cursor()
                cursor.execute("SELECT {} FROM {}".format(column_name, table_name))
                items = [row[0] for row in cursor]

        return items

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if "TRAC_ADMIN" in req.perm:
            yield (
                "general",
                _("General"),
                "autocompletefields",
                _("AutoComplete Fields"),
            )

    def render_admin_panel(self, req, category, page, path_info):
        if req.method == "POST":
            action = req.args.get("action")
            field_type = req.args.get("field_type")
            value = req.args.get("value")

            if action == "add":
                self._add_item(field_type, value)
                add_notice(req, _("Value has been added successfully."))
            elif action == "remove":
                self._remove_item(field_type, value)
                add_notice(req, _("Value has been removed successfully."))
            else:
                add_warning(req, _("Invalid action."))

        data = {
            "keywords": self._get_items_for_field("Keywords"),
            "suppliers": self._get_items_for_field("Supplier"),
            "customers": self._get_items_for_field("Customer"),
            "sizes": self._get_items_for_field("Sizes"),
        }

        return "admin_autocompletefields.html", data

    def _add_item(self, field_type, value):
        table_name = self._get_table_name(field_type)
        column_name = self._get_column_name(field_type)

        if table_name and column_name and value is not None:
            with self.env.db_transaction as db:
                cursor = db.cursor()
                query = "INSERT INTO {} ({}) VALUES ('{}')".format(
                    table_name, column_name, str(value)
                )
                cursor.execute(query)
                self.log.info(
                    "Added item: Field Type - {}, Value - {}".format(field_type, value)
                )
        else:
            self.log.error(
                "Failed to add item: Value is None. Field Type - {}, Value - {}".format(
                    field_type, value
                )
            )

    def _remove_item(self, field_type, value):
        table_name = self._get_table_name(field_type)
        column_name = self._get_column_name(field_type)

        if table_name and column_name:
            with self.env.db_transaction as db:
                cursor = db.cursor()
                query = "DELETE FROM {} WHERE {} = '{}'".format(
                    table_name, column_name, str(value)
                )
                cursor.execute(query)
                self.log.info(
                    "Removed item: Field Type - {}, Value - {}".format(
                        field_type, value
                    )
                )
        else:
            self.log.error(
                "Failed to remove item: Table or column not found. Field Type - {}, Value - {}".format(
                    field_type, value
                )
            )

    def _get_table_name(self, field_type):
        table_mapping = {
            "Keywords": "keywords",
            "Supplier": "suppliers",
            "Customer": "customers",
            "Sizes": "sizes",
        }
        return table_mapping.get(field_type)

    def _get_column_name(self, field_type):
        column_mapping = {
            "Keywords": "keyword",
            "Supplier": "supplier_name",
            "Customer": "customer_name",
            "Sizes": "size_name",
        }
        return column_mapping.get(field_type)

        # IEnvironmentSetupParticipant methods

    def environment_created(self):
        # This will be called when a new Trac environment is created
        self.upgrade_environment(self.env.get_db_cnx())

    def environment_needs_upgrade(self, db):
        cursor = db.cursor()

        tables = ["keywords", "suppliers", "customers", "sizes"]
        for table in tables:
            cursor.execute("PRAGMA table_info({})".format(table))
            result = cursor.fetchall()
            if not result:
                # If no result, it likely means that the table does not exist
                return True

        # If all tables exist
        return False

    def upgrade_environment(self, db):
        cursor = db.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS keywords (
                keyword TEXT
            );
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_name TEXT
            );
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_name TEXT
            );
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sizes (
                size_name TEXT
            );
        """
        )
