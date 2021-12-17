import bcrypt
import ldap
import ldap.modlist

from bnv_manager import settings


def hash_password(password):
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return f"{{CRYPT}}{hashed.decode('utf-8')}"


def add_user(username, firstname, lastname, mail, password, dn):
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    mod_list = ldap.modlist.addModlist(
        {
            "givenName": [firstname.encode("utf-8")],
            "sn": [lastname.encode("utf-8")],
            "mail": [mail.encode("utf-8")],
            "objectClass": ["inetOrgPerson".encode("utf-8"), "top".encode("utf-8")],
            "cn": [username.encode("utf-8")],
            "userPassword": [hash_password(password).encode("utf-8")],
        }
    )
    dn = f"cn={username},{dn}"
    conn.add_s(dn, modlist=mod_list)
    conn.unbind_s()
    return dn


def get_user(dn=None):
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    if dn:
        ret = conn.read_s(dn)
        return ret
    ret = conn.search_s(settings.AUTH_LDAP_USER_BASE, ldap.SCOPE_SUBTREE, "(objectClass=inetOrgPerson)")
    conn.unbind_s()
    return ret


def del_dn(dn):
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    conn.delete_s(dn)
    conn.unbind_s()


def set_password(dn, password):
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    new_entry = {"userPassword": [hash_password(password).encode("utf-8")]}
    results = conn.search_s(dn, ldap.SCOPE_SUBTREE, "(objectClass=inetOrgPerson)")
    user = results[0]
    old_entry = {"userPassword": user[1]["userPassword"]}
    mod_list = ldap.modlist.modifyModlist(old_entry, new_entry)
    conn.modify_s(dn, mod_list)
    conn.unbind_s()


def get_club_admins(club=None, invert=False):
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    if club:
        search = f"(&(objectClass=inetOrgPerson)(memberOf=cn={club},{settings.LDAP_GROUP_DN}))"
        if invert:
            search = f"(&(objectClass=inetOrgPerson)(!(memberOf=cn={club},{settings.LDAP_GROUP_DN})))"
        results = conn.search_s(settings.AUTH_LDAP_CLUB_ADMIN_BASE, ldap.SCOPE_SUBTREE, search)
    else:
        results = conn.search_s(settings.AUTH_LDAP_CLUB_ADMIN_BASE, ldap.SCOPE_SUBTREE, "(objectClass=inetOrgPerson)")
    conn.unbind_s()
    return [{
        "dn": x[0],
        "username": x[1]["cn"][0].decode("utf-8"),
        "firstname": x[1]["givenName"][0].decode("utf-8"),
        "surname": x[1]["sn"][0].decode("utf-8"),
    } for x in results]


def get_club_for_user(dn):
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    results = conn.read_s(dn, attrlist=["memberOf"])
    conn.unbind_s()
    return [x.decode("utf-8") for x in results["memberOf"]][0] if "memberOf" in results else None


def get_club_users(club, search_base=settings.AUTH_LDAP_USER_BASE):
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    search = f"(&(objectClass=inetOrgPerson)(memberOf=cn={club},{settings.LDAP_GROUP_DN}))"
    results = conn.search_s(search_base, ldap.SCOPE_SUBTREE, search)
    conn.unbind_s()
    return [
        {
            "firstname": x[1]["givenName"][0].decode("utf-8"),
            "surname": x[1]["sn"][0].decode("utf-8"),
            "mail": x[1]["mail"][0].decode("utf-8"),
            "username": x[1]["cn"][0].decode("utf-8"),
            "dn": x[0]
        } for x in results
    ]


def check_unique_mail(mail):
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    search = f"(&(objectClass=inetOrgPerson)(mail={mail}))"
    results = conn.search_s(settings.LDAP_GLOBAL_SEARCH_BASE, ldap.SCOPE_SUBTREE, search)
    conn.unbind_s()
    return not any(results)


def add_users_to_group(user_dns: list, group):
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    results = conn.search_s(
        settings.LDAP_GROUP_DN,
        ldap.SCOPE_SUBTREE,
        f"(&(cn={group})(objectClass=groupOfNames))"
    )
    dn = f"cn={group},{settings.LDAP_GROUP_DN}"
    if len(results) == 0:
        # Create group if not existent
        mod_list = ldap.modlist.addModlist(
            {
                "cn": [group.encode("utf-8")],
                "member": [x.encode("utf-8") for x in user_dns],
                "objectClass": ["groupOfNames".encode("utf-8"), "top".encode("utf-8")],
            }
        )
        conn.add_s(dn, modlist=mod_list)
    else:
        old_entry = {"member": results[0][1]["member"]}
        new_entry = {"member": list({*old_entry["member"], *[x.encode("utf-8") for x in user_dns]})}
        mod_list = ldap.modlist.modifyModlist(old_entry, new_entry)
        conn.modify_ext_s(dn, mod_list)
    conn.unbind_s()


def add_user_to_group(dn, group):
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    results = conn.search_s(
        settings.LDAP_GROUP_DN,
        ldap.SCOPE_SUBTREE,
        f"(&(cn={group})(objectClass=groupOfNames))"
    )
    group_dn = f"cn={group},{settings.LDAP_GROUP_DN}"
    if len(results) == 0:
        # Create group if not existent
        mod_list = ldap.modlist.addModlist(
            {
                "cn": [group.encode("utf-8")],
                "member": dn.encode("utf-8"),
                "objectClass": ["groupOfNames".encode("utf-8"), "top".encode("utf-8")],
            }
        )
        conn.add_s(group_dn, modlist=mod_list)
    else:
        mod_list = [(ldap.MOD_ADD, "member", dn.encode("utf-8"))]
        conn.modify_ext_s(group_dn, mod_list)
    conn.unbind_s()


def remove_users_from_group(user_dns, group):
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    results = conn.search_s(
        settings.LDAP_GROUP_DN,
        ldap.SCOPE_SUBTREE,
        f"(&(cn={group})(objectClass=groupOfNames))"
    )
    dn = f"cn={group},{settings.LDAP_GROUP_DN}"
    encoded_dns = [y.encode("utf-8") for y in user_dns]
    for group in results:
        old_entry = {"member": group[1]["member"]}
        new_entry = {"member": [x for x in old_entry["member"] if x not in encoded_dns]}
        if len(new_entry["member"]) == 0:
            conn.delete_s(dn)
        else:
            mod_list = ldap.modlist.modifyModlist(old_entry, new_entry)
            conn.modify_s(dn, mod_list)
    conn.unbind_s()


def remove_user_from_group(dn, group):
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    results = conn.search_s(
        settings.LDAP_GROUP_DN,
        ldap.SCOPE_SUBTREE,
        f"(&(cn={group})(objectClass=groupOfNames))"
    )
    group_dn = f"cn={group},{settings.LDAP_GROUP_DN}"
    encoded_dn = dn.encode("utf-8")
    for group in results:
        if len([x for x in group[1]["member"] if x not in encoded_dn]) == 0:
            conn.delete_s(group_dn)
        else:
            mod_list = [(ldap.MOD_DELETE, "member", encoded_dn)]
            conn.modify_s(group_dn, mod_list)
    conn.unbind_s()


def generate_username(firstname, surname):
    username = f"{firstname.lower()}.{surname.lower()}"
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    results = conn.search_s(settings.LDAP_GLOBAL_SEARCH_BASE, ldap.SCOPE_SUBTREE, f"(cn={username}*)")
    conn.unbind_s()
    cns = [x[0].split(",")[0] for x in results if x[0].split(",")[0].startswith(f"cn={username}")]
    counter = 1
    while f"cn={username}" in cns:
        username = f"{firstname.lower()}.{surname.lower()}{counter}"
        counter += 1
    return username


def get_hash_for_user(dn):
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    result = conn.read_s(dn)
    conn.unbind_s()
    return result.get("userPassword")[0].decode("utf-8")

