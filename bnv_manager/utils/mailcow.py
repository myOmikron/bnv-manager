import json
from os.path import join
from pprint import pprint

import requests

import utils.ldap
from bnv_manager import settings
from generic.models import Domain
from utils.ldap import hash_password

header = {"X-API-Key": settings.MAILCOW_API_KEY}


def add_mailbox(firstname, lastname, mail, password, hash_pw=True):
    if hash_pw:
        pw = hash_password(password)
    else:
        pw = password
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


def del_mailbox(mail):
    ret = requests.post(join(settings.MAILCOW_API_URI, "api/v1/delete/mailbox"), json=[mail], headers=header)
    return True if ret.status_code == 200 else False


def set_password(mail, password):
    pw = utils.ldap.hash_password(password)
    data = {
        "items": [
            mail
        ],
        "attr": {
            "password": pw,
            "password2": pw
        }
    }
    ret = requests.post(join(settings.MAILCOW_API_URI, "api/v1/edit/mailbox"), json=data, headers=header)
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
        return [x for x in aliases if x["goto"].endswith(filter_domain) and x["address"].endswith(filter_domain)]
    return aliases


def get_domains():
    ret = requests.get(join(settings.MAILCOW_API_URI, "api/v1/get/domain/all"), headers=header)
    if ret.status_code == 200:
        domains = [x["domain_name"] for x in json.loads(ret.text)]
        db_domains = []
        for domain in domains:
            d, created = Domain.objects.get_or_create(domain=domain)
            db_domains.append(d)
        for x in Domain.objects.all():
            if x.domain not in domains:
                x.delete()
        return db_domains


def create_domain_admin(username, domains, password):
    data = {
        "username": username,
        "domains": domains,
        "password": password,
        "password2": password,
        "active": "1"
    }
    ret = requests.post(join(settings.MAILCOW_API_URI, "api/v1/add/domain-admin"), json=data, headers=header)
    return True if ret.status_code == 200 else False


def get_domain_admins():
    ret = requests.get(join(settings.MAILCOW_API_URI, "api/v1/get/domain-admin/all"), headers=header)
    if ret.status_code == 200:
        return json.loads(ret.text)


def del_domain_admin(username):
    ret = requests.post(join(settings.MAILCOW_API_URI, "api/v1/delete/domain-admin"), json=[username], headers=header)
    return True if ret.status_code == 200 else False


def set_domain_for_domain_admin(username, domains):
    data = {
        "items": [
            username
        ],
        "attr": {
            "domains": domains
        }
    }
    ret = requests.post(join(settings.MAILCOW_API_URI, "api/v1/edit/domain-admin"), json=data, headers=header)
    return True if ret.status_code == 200 else False
