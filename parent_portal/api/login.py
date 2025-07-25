import frappe
import frappe.utils
from frappe import _
from frappe.auth import LoginManager
from frappe.rate_limiter import rate_limit
from frappe.utils import cint, get_url, now_datetime, sha256_hash
from frappe.utils.data import escape_html
from frappe.utils.html_utils import get_icon_html
from frappe.utils.oauth import (
    get_oauth2_authorize_url,
    get_oauth_keys,
    redirect_post_login,
)

from frappe.utils.password import get_decrypted_password, get_password_reset_limit

no_cache = True


@frappe.whitelist(allow_guest=True)
def get_context():

    redirect_to = frappe.local.request.args.get("redirect-to")
    context = {"provider_logins": []}
    providers = frappe.get_all(
        "Social Login Key",
        filters={"enable_social_login": 1},
        fields=[
            "name",
            "client_id",
            "base_url",
            "provider_name",
            "icon",
            "redirect_url",
        ],
        order_by="name",
    )

    for provider in providers:
        client_secret = get_decrypted_password(
            "Social Login Key", provider.name, "client_secret"
        )
        if not client_secret:
            continue

        icon = {"html": "", "src": "", "alt": ""}
        if provider.icon:
            if provider.provider_name == "Custom":
                icon["html"] = get_icon_html(provider.icon, small=True)
            else:
                icon["src"] = provider.icon
                icon["alt"] = provider.provider_name

        if provider.client_id and provider.base_url and get_oauth_keys(provider.name):

            context["provider_logins"].append(
                {
                    "name": provider.name,
                    "provider_name": provider.provider_name,
                    "auth_url": get_oauth2_authorize_url(provider.name, redirect_to),
                    "redirect_to": provider.redirect_url,
                    "icon": icon,
                }
            )
            context["social_login"] = True

    login_label = [_("Email")]
    if frappe.utils.cint(frappe.get_system_settings("allow_login_using_mobile_number")):
        login_label.append(_("Mobile"))

    if frappe.utils.cint(frappe.get_system_settings("allow_login_using_user_name")):
        login_label.append(_("Username"))

    context["login_label"] = f" {_('/')} ".join(login_label)

    context["login_with_email_link"] = frappe.get_system_settings(
        "login_with_email_link"
    )

    return context


@frappe.whitelist(allow_guest=True, methods=["POST"])
# @rate_limit(limit=get_password_reset_limit, seconds=60 * 60)
def reset_password(email: str, send_email: bool = False) -> str:
    from frappe.utils import get_url

    try:
        user = frappe.get_doc("User", email)
        if user.name == "Administrator":
            return "not allowed"
        if not user.enabled:
            return "disabled"

        user.validate_reset_password()

        key = frappe.generate_hash()
        hashed_key = sha256_hash(key)
        user.db_set("reset_password_key", hashed_key)
        user.db_set("last_reset_password_key_generated_on", now_datetime())

        url = "parent_portal/reset-password/" + key

        link = get_url(url)
        if send_email:
            user.password_reset_mail(link)

        return link
    except frappe.DoesNotExistError:
        frappe.local.response["http_status_code"] = 404
        frappe.clear_messages()
        return "not found"


@frappe.whitelist()
def get_current_user_info():
    pp_user = frappe.get_doc("PP User", {"user": frappe.session.user}, as_dict=True)
    if not pp_user:
        return frappe.throw("User not found")

    person_info = frappe.get_doc("SIS Person", pp_user.person)
    pp_user.person = person_info.as_dict()

    return pp_user
