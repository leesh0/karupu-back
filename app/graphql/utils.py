from dataclasses import asdict

from strawberry.arguments import UNSET


def input_dict(input_obj):
    return {k: v for k, v in asdict(input_obj).items() if not isinstance(v, type(UNSET))}
