app_name = "parent_portal"
app_title = "Parent Portal"
app_publisher = "Digital Learning Team"
app_description = "Wellspring Parent Portal"
app_email = "digital.learning@wellspringsaigon.edu.vn"
app_license = "agpl-3.0"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/parent_portal/css/parent_portal.css"
# app_include_js = "/assets/parent_portal/js/parent_portal.js"

# include js, css files in header of web template
# web_include_css = "/assets/parent_portal/css/parent_portal.css"
# web_include_js = "/assets/parent_portal/js/parent_portal.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "parent_portal/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "parent_portal/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {"PP User": "parent_portal"}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "parent_portal.utils.jinja_methods",
# 	"filters": "parent_portal.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "parent_portal.install.before_install"
after_install = "parent_portal.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "parent_portal.uninstall.before_uninstall"
# after_uninstall = "parent_portal.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "parent_portal.utils.before_app_install"
# after_app_install = "parent_portal.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "parent_portal.utils.before_app_uninstall"
# after_app_uninstall = "parent_portal.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "parent_portal.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "User": {
        # "after_insert": "parent_portal.parent_portal.doctype.pp_user.pp_user.add_user_to_pp",
        # "on_update": "parent_portal.parent_portal.doctype.pp_user.pp_user.add_user_to_pp",
        "on_trash": "parent_portal.parent_portal.doctype.pp_user.pp_user.remove_user_from_pp",
    },
	"SIS Student": {
		'onload': "parent_portal.sis.doctype.sis_student.sis_student.set_current_school_class"
	},
	"SIS Guardian Registry": {
		'onload': "parent_portal.sis.doctype.sis_guardian_registry.sis_guardian_registry.load_family_info"
	}

}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"parent_portal.tasks.all"
# 	],
# 	"daily": [
# 		"parent_portal.tasks.daily"
# 	],
# 	"hourly": [
# 		"parent_portal.tasks.hourly"
# 	],
# 	"weekly": [
# 		"parent_portal.tasks.weekly"
# 	],
# 	"monthly": [
# 		"parent_portal.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "parent_portal.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "parent_portal.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "parent_portal.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["parent_portal.utils.before_request"]
# after_request = ["parent_portal.utils.after_request"]

# Job Events
# ----------
# before_job = ["parent_portal.utils.before_job"]
# after_job = ["parent_portal.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"parent_portal.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

after_migrate = [
    "parent_portal.seeds.execute",
    "parent_portal.utils.role_utils.rebuild_roles"
]
# on_session_creation = "parent_portal.overrides.successful_login.redirect_user"


website_route_rules = [
    {"from_route": "/parent_portal/<path:app_path>", "to_route": "parent_portal"},
]

on_session_creation = "parent_portal.api.user_availability.set_user_active"
on_logout = "parent_portal.api.user_availability.set_user_inactive"

export_python_type_annotations = True
