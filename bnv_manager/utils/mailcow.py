import json
from os.path import join

import requests

from bnv_manager import settings
from utils.ldap import hash_password

header = {"X-API-Key": settings.MAILCOW_API_KEY}


def add_mailbox(firstname, lastname, mail, password):
    pw = hash_password(password)
    data = {
        "active": "1",
        "domain": mail.split("@")[1],
        "local_part": mail.split("@")[0],
        "name": f"{firstname} {lastname}",
        "password": pw,
        "password2": pw,
        "quota": "512",
        "force_pw_update": "0",
        "tls_enforce_in": "1",
        "tls_enforce_out": "1"
    }
    ret = requests.post(join(settings.MAILCOW_API_URI, "api/v1/add/mailbox"), json=data, headers=header)
    return True if ret.status_code == 200 else False


def add_alias(mail, alias):
    data = {
        "active": "1",
        "address": alias,
        "goto": mail
    }
    ret = requests.post(join(settings.MAILCOW_API_URI, "api/v1/add/alias"), json=data, headers=header)
    return True if ret.status_code == 200 else False


def del_alias(alias_id):
    data = [str(alias_id)]
    ret = requests.post(join(settings.MAILCOW_API_URI, "api/v1/delete/alias"), json=data, headers=header)
    return True if ret.status_code == 200 else False


def get_aliases(filter_mail="", filter_domain=""):
    ret = requests.get(join(settings.MAILCOW_API_URI, "api/v1/get/alias/all"), headers=header)
    aliases = json.loads(ret.text)
    if filter_mail:
        return [x for x in aliases if x["goto"] == filter_mail]
    if filter_domain:
        print(aliases)
        return [x for x in aliases if x["goto"].endswith(filter_domain) and x["address"].endswith(filter_domain)]
    return aliases
