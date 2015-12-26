from django.db import models
from dju_common.fields.json import JSONField, JSONCharField


def get_default():
    return [1, 2, 3]


class JsonTestModel(models.Model):
    json_1 = JSONField()  # default=None
    json_2 = JSONField(default=[])
    json_3 = JSONField(default={})
    json_4 = JSONField(default=get_default)
    json_5 = JSONField(default={'a': 1})

    json_6 = JSONCharField(max_length=255)  # default=None
    json_7 = JSONCharField(max_length=255, default=[])
    json_8 = JSONCharField(max_length=255, default={})
    json_9 = JSONCharField(max_length=255, default=get_default)
    json_10 = JSONCharField(max_length=255, default={'a': 1})

    json_11 = JSONField(use_decimal=True)
    json_12 = JSONField(null=True)
