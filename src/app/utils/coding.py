import json

from fastapi.encoders import jsonable_encoder

def obj_to_json(obj):
    return json.dumps(jsonable_encoder(obj))

def bytes_to_str(data):
    return " ".join(f"{byte:02x}" for byte in data)

def int_to_bytes(val, length):
    return val.to_bytes(length, "big")