import bcrypt
import ldap
import ldap.modlist

from bnv_manager import settings


def hash_password(password):
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return f"{{CRYPT}}{hashed.decode('utf-8')}"


def add_user(username, firstname, lastname, mail, password):
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
    dn = f"cn={username},{settings.LDAP_USER_DN}"
    conn.add_s(dn, modlist=mod_list)
    conn.unbind_s()
    return dn


def get_user():
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    ret = conn.search_s(settings.AUTH_LDAP_USER_BASE, ldap.SCOPE_SUBTREE, "(objectClass=inetOrgPerson)")
    conn.unbind_s()
    return ret


def del_user(dn):
    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    conn.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    conn.delete_s(dn)


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
