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
def get_user_info_after_login():
    """Get user info immediately after login - reliable endpoint"""
    if frappe.session.user == "Guest":
        frappe.throw("Not logged in", frappe.AuthenticationError)
    
    try:
        user_email = frappe.session.user
        
        # Get basic user info từ User doctype
        user_doc = frappe.get_doc("User", user_email)
        
        # Tạo basic user info
        user_info = {
            "name": user_email,
            "full_name": user_doc.full_name or user_email,
            "email": user_email,
            "first_name": user_doc.first_name or user_doc.full_name.split(' ')[0] if user_doc.full_name else 'User',
            "user_image": user_doc.user_image or '',
            "avatar": user_doc.user_image or ''
        }
        
        # Thử get PP User để xác định role
        pp_user_data = frappe.db.get_value(
            "PP User", 
            {"user": user_email}, 
            ["sis_role", "person"], 
            as_dict=True
        )
        
        role = "Parent"  # Default role changed to Parent
        prefix = ""      # Default prefix for Parent
        pp_user_exists = bool(pp_user_data)
        
        if pp_user_data and pp_user_data.sis_role:
            if pp_user_data.sis_role == "Parent":
                role = "Parent" 
                prefix = ""
            elif pp_user_data.sis_role == "Teacher":
                role = "Teacher"
                prefix = "teacher"
            elif pp_user_data.sis_role == "Admin":
                role = "Teacher"  # Admin maps to Teacher in frontend
                prefix = "teacher"
                
            # Nếu có SIS Person, lấy thêm thông tin
            if pp_user_data.person:
                person_info = frappe.db.get_value(
                    "SIS Person",
                    pp_user_data.person,
                    ["first_name", "last_name", "full_name", "primary_role"],
                    as_dict=True
                )
                if person_info:
                    user_info.update({
                        "first_name": person_info.first_name or user_info["first_name"],
                        "full_name": person_info.full_name or user_info["full_name"]
                    })
        else:
            # Fallback: Tìm SIS Person trực tiếp qua email
            frappe.log_error(f"No PP User found for {user_email}, trying SIS Person lookup")
            
            sis_person = frappe.db.get_value(
                "SIS Person",
                {"email": user_email},
                ["name", "first_name", "last_name", "full_name", "primary_role"],
                as_dict=True
            )
            
            if sis_person:
                # Update user info from SIS Person
                user_info.update({
                    "first_name": sis_person.first_name or user_info["first_name"],
                    "full_name": sis_person.full_name or user_info["full_name"]
                })
                
                # Determine role from SIS Person primary_role
                if sis_person.primary_role:
                    if sis_person.primary_role.lower() in ['teacher', 'faculty', 'staff', 'instructor']:
                        role = "Teacher"
                        prefix = "teacher"
                    elif sis_person.primary_role.lower() in ['parent', 'guardian']:
                        role = "Parent"
                        prefix = ""
                
                frappe.log_error(f"Found SIS Person for {user_email}: {sis_person.primary_role} -> {role}")
                
        return {
            "user": user_email,
            "user_info": user_info,
            "role": role,
            "prefix": prefix,
            "session_valid": True,
            "pp_user_exists": pp_user_exists,
            "fallback_used": not pp_user_exists
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_user_info_after_login: {str(e)}")
        # Return safe fallback instead of error
        return {
            "user": frappe.session.user,
            "user_info": {
                "name": frappe.session.user,
                "full_name": frappe.session.user,
                "email": frappe.session.user,
                "first_name": "User",
                "user_image": "",
                "avatar": ""
            },
            "role": "Parent",
            "prefix": "", 
            "session_valid": True,
            "pp_user_exists": False,
            "error": str(e)
        }

@frappe.whitelist()
def get_current_user_info():
    pp_user = frappe.get_doc("PP User", {"user": frappe.session.user}, as_dict=True)
    if not pp_user:
        return frappe.throw("User not found")

    person_info = frappe.get_doc("SIS Person", pp_user.person)
    pp_user.person = person_info.as_dict()

    return pp_user


@frappe.whitelist(allow_guest=True)
def get_current_user_simple():
    """Simple endpoint to get current user info - works with allow_guest"""
    
    # Nếu là Guest, return empty data
    if frappe.session.user == "Guest":
        return {
            "user": "Guest",
            "user_info": {
                "name": "Guest",
                "full_name": "Guest",
                "email": "Guest",
                "first_name": "Guest",
                "user_image": "",
                "avatar": ""
            },
            "role": "Teacher",
            "prefix": "teacher",
            "session_valid": False,
            "is_guest": True
        }
    
    try:
        user_email = frappe.session.user
        
        # Get basic user info từ User doctype
        user_doc = frappe.get_doc("User", user_email)
        
        # Tạo basic user info
        user_info = {
            "name": user_email,
            "full_name": user_doc.full_name or user_email,
            "email": user_email,
            "first_name": user_doc.first_name or user_doc.full_name.split(' ')[0] if user_doc.full_name else 'User',
            "user_image": user_doc.user_image or '',
            "avatar": user_doc.user_image or ''
        }
        
        # Thử get PP User để xác định role
        pp_user_data = frappe.db.get_value(
            "PP User", 
            {"user": user_email}, 
            ["sis_role", "person"], 
            as_dict=True
        )
        
        role = "Parent"  # Default role changed to Parent for safety
        prefix = ""      # Default prefix for Parent
        
        frappe.log_error(f"PP User lookup for {user_email}: {pp_user_data}")
        
        if pp_user_data and pp_user_data.sis_role:
            if pp_user_data.sis_role == "Parent":
                role = "Parent" 
                prefix = ""
            elif pp_user_data.sis_role == "Teacher":
                role = "Teacher"
                prefix = "teacher"
            elif pp_user_data.sis_role == "Admin":
                role = "Teacher"  # Admin maps to Teacher
                prefix = "teacher"
                
            frappe.log_error(f"Role from PP User sis_role: {pp_user_data.sis_role} -> {role}")
        else:
            # Fallback: Try to find SIS Person directly
            sis_person = frappe.db.get_value(
                "SIS Person",
                {"email": user_email},
                ["name", "first_name", "last_name", "full_name", "primary_role"],
                as_dict=True
            )
            
            if sis_person and sis_person.primary_role:
                primary_role_lower = sis_person.primary_role.lower()
                if primary_role_lower in ['teacher', 'faculty', 'staff', 'instructor']:
                    role = "Teacher"
                    prefix = "teacher"
                elif primary_role_lower in ['parent', 'guardian']:
                    role = "Parent"
                    prefix = ""
                    
                frappe.log_error(f"Role from SIS Person primary_role: {sis_person.primary_role} -> {role}")
                
                # Update user_info with SIS Person data
                user_info.update({
                    "first_name": sis_person.first_name or user_info["first_name"],
                    "full_name": sis_person.full_name or user_info["full_name"]
                })
            else:
                frappe.log_error(f"No PP User or SIS Person found for {user_email}, using default role: {role}")
        
        # Nếu có SIS Person qua PP User, lấy thêm thông tin
        if pp_user_data and pp_user_data.person:
            person_info = frappe.db.get_value(
                "SIS Person",
                pp_user_data.person,
                ["first_name", "last_name", "full_name", "primary_role"],
                as_dict=True
            )
            if person_info:
                user_info.update({
                    "first_name": person_info.first_name or user_info["first_name"],
                    "full_name": person_info.full_name or user_info["full_name"]
                })
        
        return {
            "user": user_email,
            "user_info": user_info,
            "role": role,
            "prefix": prefix,
            "session_valid": True,
            "pp_user_exists": bool(pp_user_data),
            "is_guest": False
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_current_user_simple: {str(e)}")
        return {
            "user": frappe.session.user,
            "user_info": {
                "name": frappe.session.user,
                "full_name": frappe.session.user,
                "email": frappe.session.user,
                "first_name": "User",
                "user_image": "",
                "avatar": ""
            },
            "role": "Teacher",
            "prefix": "teacher", 
            "session_valid": True,
            "error": str(e),
            "is_guest": False
        }
