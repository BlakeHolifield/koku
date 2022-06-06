from decimal import Decimal

test_dict = {
    "2022-06": {
        "OCP-on-AWS": {
            "node_1": {"koku": Decimal("7261362362082.205546710000000")},
            "node_2": {"koku-dev": Decimal("512155826043.239699520000000")},
            "node_3": {"koku-stage": Decimal("4895795886245.926032170000000")},
        },
        "OCP-on-GCP": {
            "node_0": {"koku-prod": Decimal("6432634332969.635328630000000")},
            "node_1": {"default": Decimal("3837217685363.884528360000000")},
            "node_2": {"koku": Decimal("5332851969333.810632140000000")},
        },
        "OCP-on-Prem": {
            "node_0": {"koku-perf": Decimal("1820331538165.081397540000000")},
            "node_1": {"koku-prod": Decimal("3983103374006.533019220000000")},
            "node_4": {"koku-stage": Decimal("4479458428089.117606870000000")},
        },
        "Others": {"Others": {"Others": Decimal("291.340710000000000")}},
    }
}


def _update_nested_dict(self, original, new):
    """
    Update a nested dictionary or similar mapping.
    Modify ``source`` in place.
    """
    if isinstance(new, dict):
        for key, value in new.items():
            if original.get(key):
                returned = self._update_nested_dict(original.get(key, {}), value)
                original[key] = returned
            else:
                original[key] = new[key]
    return original


def find_key_order(dikt, ordering=[], group_len=3):
    print("\n\n\n\n")
    for key, val in dikt.items():
        if not isinstance(val, dict):
            print("DO SOMETHING HERE!")
            print(ordering)
            print(key, val)
            return val
        else:
            print(ordering, group_len)
            if len(ordering) > group_len:
                ordering = []
            ordering.append(key)
            returned = find_key_order(val, ordering)

    return returned


find_key_order(test_dict.get("2022-06"))
