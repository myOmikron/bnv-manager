import ldap
from ldap import modlist

from bnv_manager import settings


def get_clubs():
    connection = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    connection.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    connection.unbind_s()


def add_club(club_name: str):
    connection = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    connection.bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
    print(connection.search_s(settings.LDAP_GROUP_DN, scope=ldap.SCOPE_SUBTREE, filterstr=settings.LDAP_GROUP_FILTER))
    mods = modlist.addModlist({
        "objectClass": ["groupOfNames".encode("utf-8"), "top".encode("utf-8")],
        "cn": [club_name.encode("utf-8")]
    })
    connection.add_s(f"cn={club_name},{settings.LDAP_GROUP_DN}", mods)
    connection.unbind_s()
