import frappe


def set_user_active():
    print("Setting the user as active", frappe.session.user)
    frappe.cache().set_value(
        f"user_session_{frappe.session.user}",
        frappe.session.user,
        expires_in_sec=900,
    )

    # # Get PP User
    # pp_user = frappe.get_value(
    #     "PP User", {"user": frappe.session.user}, ["name", "sis_role"], as_dict=True
    # )

    # if pp_user and pp_user.sis_role == "Parent":
    #     frappe.local.response["redirect_to"] = "/parent_portal"
    #     frappe.cache.hdel("redirect_after_login", frappe.session.user)
    # else:
    #     # Set the user's session ID in the cache
    #     print("Setting the user as active", frappe.session.user)
    #     frappe.cache().set_value(
    #         f"user_session_{frappe.session.user}",
    #         frappe.session.user,
    #         expires_in_sec=900,
    #     )


def set_user_inactive():
    # Remove the user's session ID from the cache
    print("Setting the user as inactive", frappe.session.user)
    frappe.cache().delete_key(f"user_session_{frappe.session.user}")


@frappe.whitelist()
def get_active_users():
    # Get all the cache keys that match the pattern 'user_session_*'
    user_session_keys = frappe.cache().get_keys("user_session_*")
    # Decode the keys and split them to get the key name
    decoded_keys = [key.decode("utf-8").split("|")[1] for key in user_session_keys]
    # Get the user IDs from the cache
    user_ids = [frappe.cache().get_value(key) for key in decoded_keys]

    return user_ids


@frappe.whitelist()
def refresh_user_active_state(deactivate=False):
    if isinstance(deactivate, str):
        deactivate = True if deactivate.lower() == "true" else False
    if deactivate:
        set_user_inactive()
    else:
        set_user_active()

    frappe.publish_realtime(
        "pp:user_active_state_updated",
        {"user": frappe.session.user, "active": not deactivate},
    )

    return "ok"


@frappe.whitelist()
def get_person_by_current_user():
    user = frappe.session.user
    person = frappe.db.get_value("PP User", user, "person")
    return frappe.get_doc("Person", person)
