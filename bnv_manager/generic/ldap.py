import hashlib
import os
from base64 import b64encode

import ldap
from ldap import modlist

from bnv_manager import settings


def make_secret(password):
    salt = os.urandom(4)
    h = hashlib.sha1(password.encode("utf-8"))
    h.update(salt)
    return "{SSHA}".encode("utf-8") + b64encode(h.digest() + salt)


def get_clubs():
    connection = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    connection.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    connection.unbind_s()


def add_club(club_name: str):
    connection = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    connection.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    mods = modlist.addModlist({
        "objectClass": ["groupOfNames".encode("utf-8"), "top".encode("utf-8")],
        "cn": [club_name.encode("utf-8")]
    })
    connection.add_s(f"cn={club_name},{settings.LDAP_GROUP_DN}", mods)
    connection.unbind_s()


def add_user_to_group(user_dn, group_dn):
    import ldap.modlist
    l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    l.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    group_name = group_dn.split(",")[0]
    results = l.search_s(settings.LDAP_GROUP_DN, ldap.SCOPE_SUBTREE, settings.LDAP_GROUP_FILTER)
    if group_dn not in [x[0] for x in results]:
        modlist = ldap.modlist.addModlist({
            "cn": [group_name.encode("utf-8")],
            "member": [user_dn.encode("utf-8")],
            "objectClass": ["groupOfNames".encode("utf-8"), "top".encode("utf-8")],
        })
        l.add_s(group_dn, modlist)
    else:
        old_entry = [x for x in results if x[0] == group_dn][0][1]["member"]
        new_entry = old_entry + [user_dn.encode("utf-8")]
        modlist = ldap.modlist.modifyModlist(
            {"member": old_entry},
            {"member": new_entry}
        )
        l.modify_s(group_dn, modlist)
    l.unbind_s()


def del_user_from_group(user_dn, group_dn):
    import ldap.modlist
    l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    l.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    results = l.search_s(settings.LDAP_GROUP_DN, ldap.SCOPE_SUBTREE, settings.LDAP_GROUP_FILTER)
    members = [x[1]["member"] for x in results if x[0] == group_dn]
    if len(members) == 1:
        l.delete_s(group_dn)
    else:
        old_entry = [x for x in results if x[0] == group_dn][0][1]["member"]
        new_entry = [x for x in old_entry if x != user_dn.encode("utf-8")]
        modlist = ldap.modlist.modifyModlist(
            {"member": old_entry},
            {"member": new_entry}
        )
        l.modify_s(group_dn, modlist)
    l.unbind_s()


def add_manager_user(username, firstname, lastname, mail, password, is_superuser=False):
    import ldap.modlist
    l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    l.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    modlist = ldap.modlist.addModlist(
        {
            "givenName": [firstname.encode("utf-8")],
            "sn": [lastname.encode("utf-8")],
            "mail": [mail.encode("utf-8")],
            "objectClass": ["inetOrgPerson".encode("utf-8"), "top".encode("utf-8")],
            "cn": [username.encode("utf-8")],
            "userPassword": [make_secret(password)],
        }
    )
    if not is_superuser:
        l.add_s(f"cn={username},{settings.LDAP_MANAGER_DN}", modlist=modlist)
    else:
        l.add_s(f"cn={username},{settings.LDAP_SUPERUSER_DN}", modlist=modlist)
        add_user_to_group(f"cn={username},{settings.LDAP_SUPERUSER_DN}", settings.LDAP_GROUP_SUPERUSER_DN)
    l.unbind_s()


def del_manager_user(username, is_superuser=False):
    import ldap.modlist
    l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    l.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    if is_superuser:
        del_user_from_group(f"cn={username},{settings.LDAP_SUPERUSER_DN}", settings.LDAP_GROUP_SUPERUSER_DN)
        l.delete_s(f"cn={username},{settings.LDAP_SUPERUSER_DN}")
    else:
        l.delete_s(f"cn={username},{settings.LDAP_MANAGER_DN}")
    l.unbind_s()


def reset_password(username, new_password, is_superuser=False):
    import ldap.modlist
    l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    l.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    new_entry = {"userPassword": [make_secret(new_password)]}
    if is_superuser:
        results = l.search_s(f"{settings.LDAP_SUPERUSER_DN}", ldap.SCOPE_SUBTREE, "(objectClass=inetOrgPerson)")
        user = [x for x in results if x[0] == f"{username},{settings.LDAP_SUPERUSER_DN}"][0]
    else:
        results = l.search_s(f"{settings.LDAP_MANAGER_DN}", ldap.SCOPE_SUBTREE, "(objectClass=inetOrgPerson)")
        user = [x for x in results if x[0] == f"cn={username},{settings.LDAP_MANAGER_DN}"][0]
    old_entry = {"userPassword": user[1]["userPassword"]}
    modlist = ldap.modlist.modifyModlist(old_entry, new_entry)
    if is_superuser:
        l.modify_s(f"cn={username},{settings.LDAP_SUPERUSER_DN}", modlist)
    else:
        l.modify_s(f"cn={username},{settings.LDAP_MANAGER_DN}", modlist)
    l.unbind_s()
