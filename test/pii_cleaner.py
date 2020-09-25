from copy import deepcopy

PII_FIELDS = [
    "first_name",
    "last_name",
    "surname",
    "middle_name",
    "initial",
    "first_initial",
    "email",
    "email_address",
    "address_line_1",
    "address_line_2",
    "admin_area_2",
    "admin_area_3",
    "delivery_instructions",
    "full_address",
    "notes",
    "additionalStreetInfo",
    "apartment",
    "building",
    "company",
    "country",
    "department",
    "email",
    "firstName",
    "lastName",
    "mobilePhone",
    "streetName",
    "streetNumber",
]


def find_and_clean_pii(event: dict) -> dict:
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
    return event
