import frappe
#from frappe.core.doctype.permission_manager.permission_manager import add_permission, get_permission_list
#from frappe.core.doctype.role.role import RolePermissionManager


def rebuild_roles():
    roles = [{'role_name': 'PP User', 'desk_access' : 0, 'home_page' : '/parent_portal'}, 
             {'role_name': 'PP Desk', 'desk_access' : 1},
            ]

    for role in roles:
        get_role = frappe.get_all('Role', filters={'role_name': role['role_name']})
        if not get_role:
            doc = frappe.get_doc({
                'doctype': 'Role',
                'role_name': role['role_name'], 
                "desk_access": role['desk_access'],
                'home_page' : role['home_page'] if 'home_page' in role else None
            })
            doc.insert(ignore_permissions=True)
        else:
            doc = frappe.get_doc('Role', role['role_name'])
            print('update role:' + role['role_name'] + "," + doc.name)
            print(role['desk_access'])
            doc.desk_access = role['desk_access']
            doc.home_page = role['home_page'] if 'home_page' in role else None
            doc.save()
            # doc.update({ "desk_access": role['desk_access']})
    frappe.db.commit()