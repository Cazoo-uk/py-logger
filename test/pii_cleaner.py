import logging
from copy import deepcopy

PII_FIELDS = [
    "first_name",
    "last_name",
    "surname",
    "email_address",
]


def find_and_clean_pii(event) -> dict:
    event_copy = deepcopy(event)
    if isinstance(event, dict):
        for k, v in event_copy.items():
            if isinstance(v, dict):
                event_copy[k] = find_and_clean_pii(v)
            if isinstance(v, list):
                event_copy[k] = [find_and_clean_pii(item) for item in v]
            else:
                if k in PII_FIELDS:
                    event_copy[k] = "PII REMOVED"
    return event_copy


class PiiFilter(logging.Filter):
    def filter(self, record) -> True:
        event = record.__dict__
        for item in event:
            event[item] = find_and_clean_pii(event[item])
        return True
