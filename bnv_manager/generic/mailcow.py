import json

from bnv_manager import settings
import requests

from generic.models import Domain


def get_domains():
    endpoint = settings.MAILCOW_API_URL + "/api/v1/get/domain/all"
    ret = requests.get(endpoint, headers={"X-API-Key": settings.MAILCOW_API_KEY})
    if ret.status_code == 200:
        domains = [x["domain_name"] for x in json.loads(ret.text)]
        db_domains = Domain.objects.all()
        for y in [x for x in db_domains if x.name not in domains]:
            y.delete()
        for y in [x for x in domains if x not in [z.name for z in db_domains]]:
            domain = Domain(name=y)
            domain.save()
        return domains
