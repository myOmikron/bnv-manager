import json

from bnv_manager import settings
import requests


def get_domains():
    endpoint = settings.MAILCOW_API_URL + "/api/v1/get/domain/all"
    ret = requests.get(endpoint, headers={"X-API-Key": settings.MAILCOW_API_KEY})
    if ret.status_code == 200:
        return [x["domain_name"] for x in json.loads(ret.text)]
